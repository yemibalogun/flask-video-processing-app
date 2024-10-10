import os
import subprocess
import random
from concurrent.futures import ProcessPoolExecutor

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_single_video(i, video_path, watermark_path, output_folder, width, height):
    output_video = os.path.join(output_folder, f"video_{i}.mp4")
    brightness = random.uniform(0.95, 1.05)
    contrast = random.uniform(0.95, 1.05)

    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-i', watermark_path,
        '-filter_complex',
        f"color=white:{width}x{height}[bg];"
        f"[0]scale={width}:{height}:force_original_aspect_ratio=decrease[video];"
        f"[bg][video]overlay=x=(W-w)/2:y=(H-h)/2[with_bg];"
        f"[1]scale=150:84[wm];[wm]colorkey=0xFFFFFF:0.3:0.1[wmclean];"
        f"[with_bg][wmclean]overlay=W-w-10:H-h-10,"
        f"eq=brightness={brightness}:contrast={contrast}",
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '23',  # Balance between quality and file size
        '-c:a', 'copy',  # Copy audio without re-encoding
        '-movflags', '+faststart',  # Optimize for web streaming
        '-y',
        output_video
    ]

    try:
        subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE)
        return output_video
    except subprocess.CalledProcessError as e:
        print(f"Error processing video {i}: {e}")
        print(f"FFmpeg error output: {e.stderr.decode()}")
        return None

def get_video_dimensions(video_path):
    probe_cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-count_packets',
        '-show_entries', 'stream=width,height', 
        '-of', 'csv=p=0', 
        video_path
    ]
    try:
        dimensions = subprocess.check_output(probe_cmd, stderr=subprocess.PIPE).decode().strip().split(',')
        return map(int, dimensions)
    except subprocess.CalledProcessError as e:
        print(f"Error getting video dimensions: {e}")
        print(f"FFprobe error output: {e.stderr.decode()}")
        return None, None

def generate_unique_videos(video_path, watermark_path, output_folder, num_versions):
    """Generate multiple unique versions of the video with slight variations using parallel processing."""
    unique_videos = []
    
    width, height = get_video_dimensions(video_path)
    if width is None or height is None:
        print("Failed to get video dimensions. Aborting process.")
        return []
    
    os.makedirs(output_folder, exist_ok=True)
    
    with ProcessPoolExecutor(max_workers=4) as executor:  # Use 4 workers
        futures = [
            executor.submit(process_single_video, i, video_path, watermark_path, output_folder, width, height)
            for i in range(num_versions)
        ]
        
        for future in futures:
            result = future.result()
            if result:
                unique_videos.append(result)
    
    return unique_videos