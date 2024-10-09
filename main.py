import os
import zipfile
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
from utils import allowed_file, process_video, generate_unique_videos

import hashlib

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/videos/'
app.config['OUTPUT_FOLDER'] = 'static/videos/'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB limit

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(f"Request method: {request.method}")  # Debug
        
        if 'video' not in request.files or 'watermark' not in request.files:
            print("No file part")
            flash('No file part')
            return redirect(url_for('upload_file'))
        
        video = request.files['video']
        watermark = request.files['watermark']
        
        if video and watermark:
            video_filename = secure_filename(video.filename)
            watermark_filename = secure_filename(watermark.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], watermark_filename)
            
            # Debug: Print save paths
            print(f"Saving video to {video_path}")
            print(f"Saving watermark to {watermark_path}")
            
            try:
                video.save(video_path)
                watermark.save(watermark_path)
            except Exception as e:
                print(f"Error saving files: {str(e)}")
                flash(f"Error saving files: {str(e)}")
                return redirect(request.url)
            
            # Generate unique videos
            unique_videos = generate_unique_videos(video_path, watermark_path, app.config['OUTPUT_FOLDER'], num_versions=50)
            
            # Create a zip file containing all processed videos
            zip_filename = f"processed_videos.zip"
            zip_filepath = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for video in unique_videos:
                    zipf.write(video, os.path.basename(video))
                    
            return render_template('upload.html', zip_file=zip_filename)
        
    return render_template('upload.html')

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)

if __name__=='__main__':
    app.run(debug=True)
    
    

