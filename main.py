import os
import shutil
import zipfile
from flask import Flask, render_template, request, after_this_request, redirect, jsonify, url_for, flash, send_file
from werkzeug.utils import secure_filename
from utils import generate_unique_videos, allowed_file

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/videos/'
app.config['OUTPUT_FOLDER'] = 'static/videos/'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 100MB limit
app.config['SECRET_KEY'] = os.urandom(24) # Generates a random 24-byte key

# Create folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('File too large. Maximum upload size is 100MB.')
    return redirect(url_for('upload_file'))

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(f"Request method: {request.method}")  # Debug

        if 'video' not in request.files or 'watermark' not in request.files:
            return jsonify({'error': 'Please upload both a video and a watermark.'}), 400
        
        video = request.files['video']
        watermark = request.files['watermark']

        # Check for allowed file types
        if not allowed_file(video.filename) or not allowed_file(watermark.filename):
            print(f'video file type: {video.filename} and watermark file type: {watermark.filename}')
            flash('Invalid file format.')
            return jsonify({'error': 'Invalid file type. Only MP4, MOV, AVI, and MKV are allowed.'}), 400

        # Get and validate num_versions
        try:
            num_versions = int(request.form.get('num_versions', 50))  # Get the number of versions from the form 
            if num_versions <= 0:
                raise ValueError("Number of versions must be positive.")
        except ValueError:
            return jsonify({'error': 'Please enter a valid positive number for the number of versions.'}), 400

        try:
            video_filename = secure_filename(video.filename)
            watermark_filename = secure_filename(watermark.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], watermark_filename)

            video.save(video_path)
            watermark.save(watermark_path)

            # Generate unique videos
            unique_videos = generate_unique_videos(video_path, watermark_path, app.config['OUTPUT_FOLDER'], num_versions)

            # Create a zip file containing all processed videos
            zip_filename = "processed_videos.zip"
            zip_filepath = os.path.join(app.config['OUTPUT_FOLDER'], zip_filename)
            with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                for video in unique_videos:
                    zipf.write(video, os.path.basename(video))

            return jsonify({'zip_file': zip_filename}), 200

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 500  # Internal Server Error

    return render_template('upload.html')


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    
    # Send the requested file for download
    response = send_file(file_path, as_attachment=True)
    
    # Clean up the specific zip file after sending the response
    @after_this_request
    def remove_file(response):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)  # Only remove the downloaded file
                print(f"Removed file: {file_path}")
        except Exception as e:
            print(f"Error cleaning up: {e}")
        return response
    
    return response


if __name__=='__main__':
    app.run(debug=True)
    
    

