import webview
import os
import sys
import tempfile
import json
import base64
from pathlib import Path
import pygame
import threading
import time
import shutil

class PyResumeAPI:
    def __init__(self):
        self.analysis_results = None
        self.job_description = ""  # Store job description as string
        self.uploaded_files = []   # Track uploaded files
        self.saved_file_path = ""  # Store the path of the saved file
    
    def save_uploaded_file(self, file_data):
        """
        Save the uploaded file to the same directory as the Python script
        """
        try:
            # Extract file data
            file_name = file_data.get('name', 'uploaded_file')
            file_content = file_data.get('content', '')  # Base64 encoded content
            
            # Decode base64 content
            if file_content.startswith('data:'):
                # Remove data URL prefix if present
                file_content = file_content.split(',', 1)[1]
            
            file_bytes = base64.b64decode(file_content)
            
            # Get the directory where pyresume_app.py is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, file_name)
            
            # Ensure we don't overwrite existing files
            counter = 1
            name, ext = os.path.splitext(file_name)
            while os.path.exists(file_path):
                file_name = f"{name}_{counter}{ext}"
                file_path = os.path.join(script_dir, file_name)
                counter += 1
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            # Store the file path
            self.uploaded_files.append(file_path)
            self.saved_file_path = file_path  # Store the path for further use
            
            return json.dumps({'status': 'success', 'message': f'File saved as {file_name}', 'path': file_path})
            
        except Exception as e:
            return json.dumps({'status': 'error', 'message': f'Error saving file: {str(e)}'})
    
    def set_job_description(self, job_desc):
        """
        Store the job description as a string
        """
        try:
            self.job_description = job_desc
            return json.dumps({'status': 'success', 'message': 'Job description saved'})
        except Exception as e:
            return json.dumps({'status': 'error', 'message': f'Error saving job description: {str(e)}'})
    
    def get_job_description(self):
        """
        Retrieve the stored job description
        """
        return json.dumps({'status': 'success', 'data': self.job_description})
    
    def analyze_resume(self, file_data, job_description):
        """
        This method will be called from JavaScript to analyze the resume
        """
        try:
            # First save the uploaded file
            file_result = json.loads(self.save_uploaded_file(file_data))
            if file_result['status'] == 'error':
                return json.dumps({'status': 'error', 'message': file_result['message']})
            
            # Save the job description
            job_result = json.loads(self.set_job_description(job_description))
            if job_result['status'] == 'error':
                return json.dumps({'status': 'error', 'message': job_result['message']})
            
            # Print the stored information for verification
            print(f"File saved at: {self.saved_file_path}")
            print(f"Job description stored: {len(self.job_description)} characters")
            
            # Here you would implement your actual resume analysis logic
            # For now, we'll return mock data similar to your JavaScript function
            
            # Simulate processing time
            time.sleep(2)
            
            # Generate mock results (replace with your actual analysis)
            skills = ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS', 'Git', 'REST APIs']
            matched_skills = skills[:4]  # First 4 skills as matched
            missing_skills = skills[4:]  # Remaining as missing
            
            result = {
                'fileName': file_data.get('name', 'resume.pdf'),
                'overallScore': 87,
                'matchedSkills': matched_skills,
                'missingSkills': missing_skills,
                'experience': '6 years',
                'education': 'Bachelor\'s in Computer Science',
                'recommendations': [
                    'Strong technical background in Python development',
                    'Good match for senior-level positions',
                    'Consider additional cloud training for AWS'
                ],
                'savedFilePath': self.saved_file_path,
                'jobDescription': self.job_description
            }
            
            self.analysis_results = result
            return json.dumps({'status': 'success', 'data': result})
            
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def get_results(self):
        """
        Retrieve the analysis results
        """
        if self.analysis_results:
            return json.dumps({'status': 'success', 'data': self.analysis_results})
        return json.dumps({'status': 'error', 'message': 'No analysis results available'})

# The rest of your Python code remains the same...
def play_background_music():
    """
    Play background music in a loop until the application closes
    """
    try:
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Try to load the music file (you'll need to provide this file)
        music_file = "background_music.mp3"
        
        # Get the directory where pyresume_app.py is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_path = os.path.join(script_dir, music_file)
        
        # Check if music file exists
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            
            print("Background music started...")
            
            # Keep the thread alive while music is playing
            while pygame.mixer.music.get_busy():
                time.sleep(1)
        else:
            print(f"Music file '{music_file}' not found. Continuing without background music.")
            
    except Exception as e:
        print(f"Error playing background music: {e}")

def load_html_content():
    """
    Load the HTML content from the index.html file
    """
    # Get the directory where pyresume_app.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(script_dir, 'index.html')
    
    # Check if index.html exists in the same directory
    if os.path.exists(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # If index.html doesn't exist, create a temporary one
    return create_fallback_html()

def create_fallback_html():
    """
    Create a fallback HTML if index.html is not found
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>PyResume AI - File Not Found</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .error-container {
                text-align: center;
                padding: 2rem;
                background: rgba(0, 0, 0, 0.5);
                border-radius: 10px;
                max-width: 500px;
            }
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>PyResume AI</h1>
            <p>index.html file not found. Please make sure it's in the same directory as the Python script.</p>
        </div>
    </body>
    </html>
    """

def create_temp_html(html_content):
    """
    Create a temporary HTML file with the provided content
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    html_file = os.path.join(temp_dir, 'index.html')
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

if __name__ == '__main__':
    # Load HTML content
    html_content = load_html_content()
    
    # Create API instance
    api = PyResumeAPI()
    
    # Create temporary HTML file
    html_file = create_temp_html(html_content)
    
    # Start background music in a separate thread
    music_thread = threading.Thread(target=play_background_music, daemon=True)
    music_thread.start()
    
    # Create and start webview window
    window = webview.create_window(
        'PyResume AI - Intelligent Resume Analysis',
        f'file:///{html_file.replace(os.sep, "/")}',
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
        text_select=True
    )
    
    print("Starting PyResume AI Application...")
    print("Close the window to exit the application.")
    
    try:
        # Start the application
        webview.start(debug=False)
    finally:
        # Stop music when application closes
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        print("Application closed. Background music stopped.")