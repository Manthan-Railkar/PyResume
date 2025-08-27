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
        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where script is located
    
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
            
            # Create file path in the same directory as script
            file_path = os.path.join(self.script_dir, file_name)
            
            # Ensure we don't overwrite existing files
            counter = 1
            name, ext = os.path.splitext(file_name)
            while os.path.exists(file_path):
                file_name = f"{name}_{counter}{ext}"
                file_path = os.path.join(self.script_dir, file_name)
                counter += 1
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            # Store the file path and add to tracking list
            self.uploaded_files.append(file_path)
            self.saved_file_path = file_path
            
            print(f"✓ File saved successfully: {file_path}")
            print(f"✓ File size: {len(file_bytes)} bytes")
            
            return json.dumps({
                'status': 'success', 
                'message': f'File saved as {file_name}', 
                'path': file_path,
                'size': len(file_bytes)
            })
            
        except Exception as e:
            error_msg = f'Error saving file: {str(e)}'
            print(f"✗ {error_msg}")
            return json.dumps({'status': 'error', 'message': error_msg})
    
    def set_job_description(self, job_desc):
        """
        Store the job description as a string
        """
        try:
            self.job_description = job_desc.strip()
            print(f"✓ Job description stored: {len(self.job_description)} characters")
            return json.dumps({
                'status': 'success', 
                'message': 'Job description saved',
                'length': len(self.job_description)
            })
        except Exception as e:
            error_msg = f'Error saving job description: {str(e)}'
            print(f"✗ {error_msg}")
            return json.dumps({'status': 'error', 'message': error_msg})
    
    def get_job_description(self):
        """
        Retrieve the stored job description
        """
        return json.dumps({
            'status': 'success', 
            'data': self.job_description,
            'length': len(self.job_description)
        })
    
    def get_saved_file_path(self):
        """
        Get the path of the saved file
        """
        return json.dumps({
            'status': 'success',
            'data': self.saved_file_path,
            'exists': os.path.exists(self.saved_file_path) if self.saved_file_path else False
        })
    
    def analyze_resume(self, file_data, job_description):
        """
        This method will be called from JavaScript to analyze the resume.
        It saves the file, stores the job description, and performs analysis.
        """
        try:
            print("=" * 60)
            print("🐍 PyResume AI - Starting Analysis")
            print("=" * 60)
            
            # First save the uploaded file
            print("📄 Saving uploaded file...")
            file_result = json.loads(self.save_uploaded_file(file_data))
            if file_result['status'] == 'error':
                return json.dumps({'status': 'error', 'message': file_result['message']})
            
            # Save the job description
            print("💼 Storing job description...")
            job_result = json.loads(self.set_job_description(job_description))
            if job_result['status'] == 'error':
                return json.dumps({'status': 'error', 'message': job_result['message']})
            
            # Print the stored information for verification
            print(f"✓ File saved at: {self.saved_file_path}")
            print(f"✓ File exists: {os.path.exists(self.saved_file_path)}")
            print(f"✓ Job description length: {len(self.job_description)} characters")
            print(f"✓ Job description preview: {self.job_description[:100]}..." if len(self.job_description) > 100 else f"✓ Job description: {self.job_description}")
            
            print("\n🔍 Starting resume analysis...")
            
            # Simulate processing time for realistic experience
            time.sleep(1.5)
            
            # Here you would implement your actual resume analysis logic
            # For now, we'll return enhanced mock data with the actual file info
            
            # Extract file information
            file_info = {
                'name': file_data.get('name', 'resume.pdf'),
                'size': file_data.get('size', 0),
                'type': file_data.get('type', 'application/pdf')
            }
            
            # Generate analysis results based on job description keywords
            analysis_result = self._perform_analysis(file_info, self.job_description)
            
            # Store results
            self.analysis_results = analysis_result
            
            print("✓ Analysis completed successfully!")
            print(f"✓ Overall match score: {analysis_result['overallScore']}%")
            print(f"✓ Matched skills: {len(analysis_result['matchedSkills'])}")
            print(f"✓ Missing skills: {len(analysis_result['missingSkills'])}")
            print("=" * 60)
            
            return json.dumps({'status': 'success', 'data': analysis_result})
            
        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error during analysis: {error_msg}")
            return json.dumps({'status': 'error', 'message': error_msg})
    
    def _perform_analysis(self, file_info, job_desc):
        """
        Perform the actual resume analysis logic.
        This is where you would implement your AI/ML algorithms.
        """
        # Keywords to look for in job description (you can expand this)
        skill_keywords = {
            'Python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'JavaScript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'Java': ['java', 'spring', 'hibernate'],
            'C++': ['c++', 'cpp'],
            'SQL': ['sql', 'mysql', 'postgresql', 'database'],
            'Docker': ['docker', 'container', 'containerization'],
            'AWS': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
            'Git': ['git', 'github', 'version control'],
            'Machine Learning': ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch'],
            'REST API': ['rest', 'api', 'restful', 'web service'],
        }
        
        job_desc_lower = job_desc.lower()
        
        # Find skills mentioned in job description
        required_skills = []
        for skill, keywords in skill_keywords.items():
            if any(keyword in job_desc_lower for keyword in keywords):
                required_skills.append(skill)
        
        # Mock skill matching (in real implementation, you'd parse the resume)
        import random
        random.seed(42)  # For consistent results
        
        # Simulate which skills the candidate has
        matched_skills = []
        missing_skills = []
        
        for skill in required_skills:
            # 70% chance of having each required skill
            if random.random() > 0.3:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Calculate overall score
        if required_skills:
            score = int((len(matched_skills) / len(required_skills)) * 100)
        else:
            score = 75  # Default score if no specific skills identified
        
        # Add some randomness to make it more realistic
        score += random.randint(-10, 15)
        score = max(0, min(100, score))  # Ensure score is between 0-100
        
        # Generate recommendations
        recommendations = []
        if score >= 80:
            recommendations.append("Strong candidate with excellent skill match")
            recommendations.append("Suitable for senior-level positions")
        elif score >= 60:
            recommendations.append("Good candidate with solid foundation")
            recommendations.append("Consider for mid-level positions")
        else:
            recommendations.append("Candidate needs additional training")
            recommendations.append("Consider for junior positions with mentoring")
        
        if missing_skills:
            recommendations.append(f"Training needed in: {', '.join(missing_skills)}")
        
        return {
            'fileName': file_info['name'],
            'fileSize': file_info['size'],
            'fileType': file_info['type'],
            'overallScore': score,
            'matchedSkills': matched_skills,
            'missingSkills': missing_skills,
            'requiredSkills': required_skills,
            'experience': f"{random.randint(2, 8)} years",
            'education': 'Bachelor\'s in Computer Science',
            'recommendations': recommendations,
            'savedFilePath': self.saved_file_path,
            'jobDescriptionLength': len(self.job_description),
            'analysisTimestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_results(self):
        """
        Retrieve the analysis results
        """
        if self.analysis_results:
            return json.dumps({'status': 'success', 'data': self.analysis_results})
        return json.dumps({'status': 'error', 'message': 'No analysis results available'})
    
    def cleanup_files(self):
        """
        Clean up uploaded files (optional, call when needed)
        """
        try:
            cleaned_files = []
            for file_path in self.uploaded_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_files.append(file_path)
            
            self.uploaded_files.clear()
            self.saved_file_path = ""
            
            return json.dumps({
                'status': 'success',
                'message': f'Cleaned up {len(cleaned_files)} files',
                'files': cleaned_files
            })
        except Exception as e:
            return json.dumps({'status': 'error', 'message': f'Error cleaning up files: {str(e)}'})

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
            
            print("🎵 Background music started...")
            
            # Keep the thread alive while music is playing
            while pygame.mixer.music.get_busy():
                time.sleep(1)
        else:
            print(f"🎵 Music file '{music_file}' not found. Continuing without background music.")
            
    except Exception as e:
        print(f"🎵 Error playing background music: {e}")

def load_html_content():
    """
    Load the HTML content from the index.html file
    """
    # Get the directory where pyresume_app.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(script_dir, 'index.html')
    
    # Check if index.html exists in the same directory
    if os.path.exists(html_file):
        print(f"📄 Loading HTML from: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    # If index.html doesn't exist, create a temporary one
    print("⚠️  index.html not found, creating fallback HTML")
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
            <h1>🐍 PyResume AI</h1>
            <p>index.html file not found. Please make sure it's in the same directory as the Python script.</p>
            <p>Expected location: {script_dir}/index.html</p>
        </div>
    </body>
    </html>
    """.format(script_dir=os.path.dirname(os.path.abspath(__file__)))

def create_temp_html(html_content):
    """
    Create a temporary HTML file with the provided content
    """
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    html_file = os.path.join(temp_dir, 'index.html')
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"📄 Temporary HTML created: {html_file}")
    return html_file

if __name__ == '__main__':
    print("🐍 PyResume AI - Intelligent Resume Analysis Platform")
    print("=" * 60)
    
    # Get script directory for reference
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Script directory: {script_dir}")
    
    # Load HTML content
    html_content = load_html_content()
    
    # Create API instance
    api = PyResumeAPI()
    print("✓ PyResume API initialized")
    
    # Create temporary HTML file
    html_file = create_temp_html(html_content)
    
    # Start background music in a separate thread
    music_thread = threading.Thread(target=play_background_music, daemon=True)
    music_thread.start()
    
    # Create and start webview window
    print("🚀 Starting PyResume AI Application...")
    window = webview.create_window(
        'PyResume AI - Intelligent Resume Analysis',
        f'file:///{html_file.replace(os.sep, "/")}',
        js_api=api,
        width=1200,
        height=800,
        min_size=(800, 600),
        text_select=True
    )
    
    print("📋 Instructions:")
    print("   1. Upload a resume (PDF or DOC)")
    print("   2. Enter job description (minimum 50 characters)")
    print("   3. Click 'Analyze with PyResume AI'")
    print("   4. Files will be saved in:", script_dir)
    print("   5. Close the window to exit")
    print("=" * 60)
    
    try:
        # Start the application
        webview.start(debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"\n💥 Error starting application: {e}")
    finally:
        # Stop music when application closes
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        print("🎵 Background music stopped")
        print("👋 PyResume AI Application closed")
        
        # Optionally clean up files on exit
        # api.cleanup_files()  # Uncomment if you want to auto-cleanup