import os
import subprocess
import random
import time 
import logging 
from concurrent.futures import ProcessPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'jpg', 'png', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_single_video(i, video_path, watermark_path, output_folder, width, height):
    output_video = os.path.join(output_folder, f"video_{i}.mp4")
    brightness = random.uniform(0.95, 1.05)
    contrast = random.uniform(0.95, 1.05)
    
    # Start logging the video processing
    logging.info(f"Processing video {i}: {video_path}")
    start_time = time.time()

    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-i', watermark_path,
        '-filter_complex',
        f"color=white:{width}x{height}[bg];"
        f"[0]scale={width}:{height}:force_original_aspect_ratio=decrease[video];"
        f"[bg][video]overlay=x=(W-w)/2:y=(H-h)/2[with_bg];"
        f"[1]scale=150:84[wm];"
        f"[with_bg][wm]overlay=W-w-10:H-h-10,"
        f"eq=brightness={brightness}:contrast={contrast}",
        '-vsync', 'cfr',  # Ensure a constant frame rate
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '23',
        '-c:a', 'copy',
        '-movflags', '+faststart',
        '-y',
        output_video
    ]

    # Log the FFmpeg command
    logging.info(f"FFmpeg command for video {i}: {' '.join(ffmpeg_command)}")

    try:
        subprocess.run(ffmpeg_command, check=True, stderr=subprocess.PIPE)
        elapsed_time = time.time() - start_time
        logging.info(f"Video {i} processed successfully in {elapsed_time:.2f} seconds.")
        return output_video
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing video {i}: {e}")
        logging.error(f"FFmpeg error output: {e.stderr.decode()}")
        return None

def get_video_dimensions(video_path):
    logging.info(f"Getting video dimensions for {video_path}")
    probe_cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-select_streams', 'v:0', 
        '-count_packets',
        '-show_entries', 'stream=width,height', 
        '-of', 'csv=p=0', 
        video_path
    ]
    
    start_time = time.time()
    
    try:
        dimensions = subprocess.check_output(probe_cmd, stderr=subprocess.PIPE).decode().strip().split(',')
        elapsed_time = time.time() - start_time
        logging.info(f"Got video dimensions ({dimensions[0]}x{dimensions[1]}) for {video_path} in {elapsed_time:.2f} seconds.")
        return map(int, dimensions)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting video dimensions: {e}")
        logging.error(f"FFprobe error output: {e.stderr.decode()}")
        return None, None

def generate_unique_videos(video_path, watermark_path, output_folder, num_versions):
    """Generate multiple unique versions of the video with slight variations using parallel processing."""
    logging.info(f"Starting to generate {num_versions} unique videos from {video_path} with watermark {watermark_path}")
    start_time = time.time()
    
    unique_videos = []
    
    width, height = get_video_dimensions(video_path)
    if width is None or height is None:
        logging.error("Failed to get video dimensions. Aborting process.")
        return []
    
    os.makedirs(output_folder, exist_ok=True)
    
    max_workers = os.cpu_count()  # Dynamic worker count based on CPU cores
    with ProcessPoolExecutor(max_workers) as executor:
        futures = [
            executor.submit(process_single_video, i, video_path, watermark_path, output_folder, width, height)
            for i in range(num_versions)
        ]
        
        for future in futures:
            result = future.result()
            if result:
                unique_videos.append(result)
            else:
                print("One of the processes failed.")
                
    total_time = time.time() - start_time
    logging.info(f"Generated {len(unique_videos)} videos in {total_time:.2f} seconds.")

    return unique_videos
