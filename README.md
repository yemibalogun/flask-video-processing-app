# Video Processing Application Documentation

## Overview
The Video Processing Application allows users to upload a video and a watermark, then generate multiple unique versions of the video with the watermark applied. The processed videos are zipped and made available for download. This application is built using Flask, a lightweight web framework for Python.

## Features
- Upload video files in formats such as MP4, MOV, AVI, and MKV.
- Upload watermark images in PNG, JPG, or JPEG formats.
- Specify the number of unique video versions to generate.
- Process videos in parallel for efficiency.
- Download all processed videos as a single ZIP file.

## Prerequisites
Before running the application, ensure you have the following installed:
- Python 3.6 or higher
- FFmpeg and FFprobe (for video processing)
- Flask library (can be installed via pip)

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**:
   Install the required Python packages using pip:
   ```bash
   pip install Flask
   ```

3. **Install FFmpeg**:
   Ensure that FFmpeg is installed on your system. You can install it using the package manager of your choice or download it from the [official FFmpeg website](https://ffmpeg.org/download.html).

4. **Directory Structure**:
   Ensure the following directory structure is created:
   ```
   /your_project_directory
   ├── main.py
   ├── utils.py
   ├── static/
   │   └── videos/
   └── uploads/
       └── videos/
   ```

## Usage

1. **Run the Application**:
   Start the Flask application by running:
   ```bash
   python main.py
   ```
   By default, the application runs on `http://127.0.0.1:5000`.

2. **Access the Web Interface**:
   Open your web browser and navigate to `http://127.0.0.1:5000`. You will see the upload form.

3. **Upload Video and Watermark**:
   - Use the form to upload a video file and a watermark image.
   - Specify the number of variations you want to generate (default is 50).

4. **Process Videos**:
   Click the "Process Video" button. A loading spinner will indicate that the videos are being processed.

5. **Download Processed Videos**:
   After processing, a download link will appear. Click it to download the ZIP file containing all processed videos.

## File Descriptions

### `main.py`
This is the main application file that defines the Flask web server, handles HTTP requests, and manages the video processing workflow.
- **Routes**:
  - `GET /`: Displays the upload form.
  - `POST /`: Handles file uploads and triggers video processing.
  - `GET /download/<filename>`: Serves the generated ZIP file for download.

### `utils.py`
Contains utility functions for video processing, including:
- **`allowed_file(filename)`**: Checks if the uploaded file has an allowed extension.
- **`generate_unique_videos(video_path, watermark_path, output_folder, num_versions)`**: Generates multiple unique versions of a video using a watermark.
- **`process_single_video(i, video_path, watermark_path, output_folder, width, height)`**: Processes a single video by applying the watermark and adjusting properties.
- **`get_video_dimensions(video_path)`**: Retrieves the dimensions of the video file using `ffprobe`.

### `upload.html`
This is the HTML template that provides the user interface for uploading videos and watermarks. It includes:
- File input fields for selecting a video and watermark.
- An input field for specifying the number of video variations.
- A loading spinner that displays during video processing.
- A dynamic download link for the processed ZIP file.

## Error Handling
The application provides user-friendly error messages for:
- Missing file uploads.
- Unsupported file types.
- File size limits (maximum of 100MB).
- Internal server errors during processing.

## License
This application is open source and available for modification and redistribution. Please refer to the LICENSE file for more information.

## Contribution
Feel free to contribute to the project by submitting issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.

## Contact
For questions or support, please contact the application maintainer at yemibalogun@jaybalo.com
