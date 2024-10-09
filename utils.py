import os
import subprocess
import random 



ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video(input_video, watermark, output_video):
    # FFmpeg command to clean metadata, add white background, and watermark 
    command = [
        'ffmpeg', '-i', input_video,
        '-vf', f"scale=iw:-1, pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white,overlay=W-w-10:H-h-10",
        '-c:a', 'copy',
        '-metadata', 'comment=', '-metadata', 'title=', # Clean metadata
        '-metadata', 'author=',
        output_video
    ]
    subprocess.run(command)
    
def generate_unique_videos(video_path, watermark_path, output_folder, num_versions=50):
    """Generate multiple unique versions of the video with slight variations."""
    unique_videos = []
    
    for i in range(num_versions):
        output_video = os.path.join(output_folder, f"video_{i}.mp4")
        
        # Adjust brightness and contrast slightly for each version 
        brightness = random. uniform(0.95, 1.05)
        contrast = random.uniform(0.95, 1.05)
        
        # Apply unique metadata and filters
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_path,
            '-i', watermark_path,
            '-filter_complex', f"eq=brightness={brightness}:contrast={contrast},scale=iw:-1,pad=ceil(iw/2)*2:ceil(ih/2)*2:color=white,overlay=W-w-10:H-h-10",
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-y',  # Overwrite output files without asking
            output_video
        ]
        
        # Execute the command
        try:
            subprocess.run(ffmpeg_command, check=True)
            unique_videos.append(output_video)
        except subprocess.CalledProcessError as e:
            print(f"Error processing video {i}: {e}")
        
    return unique_videos
    