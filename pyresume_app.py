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
import mimetypes

class PyResumeAPI:
    def __init__(self):
        self.analysis_results = None
        self.job_description = ""  # Store job description as string
        self.uploaded_files = []   # Track uploaded files
        self.saved_file_path = ""  # Store the path of the saved file
        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # Directory where script is located
        
        # Create uploads folder in script directory
        self.uploads_dir = os.path.join(self.script_dir, "uploads")
        if not os.path.exists(self.uploads_dir):
            try:
                os.makedirs(self.uploads_dir)
                print(f"📁 Created uploads directory: {self.uploads_dir}")
            except Exception as e:
                print(f"⚠️  Could not create uploads directory: {e}")
                self.uploads_dir = self.script_dir  # Fall back to script directory
        
        # Ensure the directory is writable
        print(f"📁 Script directory: {self.script_dir}")
        print(f"📁 Uploads directory: {self.uploads_dir}")
        print(f"📁 Directory writable: {os.access(self.uploads_dir, os.W_OK)}")
    
    def save_uploaded_file(self, file_data):
      """
      Save the uploaded file to the uploads directory - FIXED VERSION
      """
      try:
          print("\n" + "="*50)
          print("📄 STARTING FILE SAVE PROCESS")
          print("="*50)
          
          # Extract and validate file data
          if not file_data:
              print("❌ No file data provided")
              return json.dumps({'status': 'error', 'message': 'No file data provided'})
          
          print(f"📄 Received file_data keys: {list(file_data.keys())}")
          
          file_name = file_data.get('name', 'uploaded_file.pdf')
          file_content = file_data.get('content', '')
          file_type = file_data.get('type', 'application/pdf')
          file_size = file_data.get('size', 0)
          
          print(f"📄 Original filename: {file_name}")
          print(f"📄 File type: {file_type}")
          print(f"📄 Original size: {file_size} bytes")
          print(f"📄 Content length: {len(file_content)} characters")
          print(f"📄 Content starts with: {file_content[:100]}...")
          
          if not file_content:
              print("❌ File content is empty")
              return json.dumps({'status': 'error', 'message': 'File content is empty'})
          
          # Handle base64 content - IMPROVED LOGIC
          if file_content.startswith('data:'):
              # Split data URL to get the base64 part
              try:
                  if ',' not in file_content:
                      print("❌ Invalid data URL format - no comma separator")
                      return json.dumps({'status': 'error', 'message': 'Invalid data URL format - no comma separator'})
                  
                  header_part, base64_part = file_content.split(',', 1)
                  print(f"📄 Data URL header: {header_part}")
                  print(f"📄 Base64 content length: {len(base64_part)} characters")
                  print(f"📄 Base64 starts with: {base64_part[:50]}...")
                  
                  if len(base64_part) == 0:
                      print("❌ Base64 part is empty")
                      return json.dumps({'status': 'error', 'message': 'Base64 content is empty'})
                      
              except ValueError as ve:
                  print(f"❌ Error splitting data URL: {ve}")
                  return json.dumps({'status': 'error', 'message': f'Invalid data URL format: {str(ve)}'})
          else:
              base64_part = file_content
              print(f"📄 Direct base64 content length: {len(base64_part)} characters")
          
          # Clean and validate base64 content
          base64_part = base64_part.strip()
          if len(base64_part) == 0:
              print("❌ Base64 part is empty after stripping")
              return json.dumps({'status': 'error', 'message': 'Base64 content is empty'})
          
          # Decode the base64 content - IMPROVED ERROR HANDLING
          try:
              # Remove any whitespace and newlines
              base64_part = ''.join(base64_part.split())
              
              # Add padding if needed (base64 strings must be multiple of 4)
              missing_padding = len(base64_part) % 4
              if missing_padding:
                  base64_part += '=' * (4 - missing_padding)
                  print(f"📄 Added {4 - missing_padding} padding characters")
              
              print(f"📄 Final base64 length: {len(base64_part)}")
              print(f"📄 Attempting to decode base64...")
              
              file_bytes = base64.b64decode(base64_part, validate=True)
              print(f"📄 Decoded file size: {len(file_bytes)} bytes")
              
              if len(file_bytes) == 0:
                  print("❌ Decoded file is empty")
                  return json.dumps({'status': 'error', 'message': 'Decoded file is empty'})
                  
              # Validate file content by checking file signature
              if file_name.lower().endswith('.pdf') and not file_bytes.startswith(b'%PDF'):
                  print("⚠️  Warning: PDF file doesn't start with PDF signature")
              
          except base64.binascii.Error as decode_error:
              print(f"❌ Base64 decode error (binascii): {decode_error}")
              return json.dumps({'status': 'error', 'message': f'Invalid base64 content: {str(decode_error)}'})
          except Exception as decode_error:
              print(f"❌ Base64 decode error (general): {decode_error}")
              return json.dumps({'status': 'error', 'message': f'Failed to decode file content: {str(decode_error)}'})
          
          # Sanitize filename - remove problematic characters
          import re
          safe_name = re.sub(r'[<>:"/\\|?*]', '_', file_name)
          if safe_name != file_name:
              print(f"📄 Sanitized filename: {file_name} -> {safe_name}")
              file_name = safe_name
          
          # Create unique file path to avoid overwrites
          file_path = os.path.join(self.uploads_dir, file_name)
          counter = 1
          original_name = file_name
          name, ext = os.path.splitext(file_name)
          
          while os.path.exists(file_path):
              file_name = f"{name}_{counter}{ext}"
              file_path = os.path.join(self.uploads_dir, file_name)
              counter += 1
              print(f"📄 File exists, trying: {file_name}")
          
          print(f"📄 Final file path: {file_path}")
          print(f"📄 Directory exists: {os.path.exists(self.uploads_dir)}")
          print(f"📄 Directory writable: {os.access(self.uploads_dir, os.W_OK)}")
          
          # Write the file with error handling
          try:
              print(f"📄 Writing {len(file_bytes)} bytes to disk...")
              with open(file_path, 'wb') as f:
                  bytes_written = f.write(file_bytes)
                  f.flush()  # Force write to disk
                  os.fsync(f.fileno())  # Force OS to write to disk
              
              print(f"📄 File write completed, {bytes_written} bytes written")
              
          except PermissionError as pe:
              print(f"❌ Permission denied: {pe}")
              return json.dumps({'status': 'error', 'message': f'Permission denied writing to {file_path}'})
          except OSError as os_error:
              print(f"❌ OS error: {os_error}")
              return json.dumps({'status': 'error', 'message': f'OS error writing file: {str(os_error)}'})
          except Exception as write_error:
              print(f"❌ File write error: {write_error}")
              return json.dumps({'status': 'error', 'message': f'Failed to write file: {str(write_error)}'})
          
          # Verify the file was actually created and has correct size
          if os.path.exists(file_path):
              actual_size = os.path.getsize(file_path)
              is_readable = os.access(file_path, os.R_OK)
              
              print("✅ FILE SAVE SUCCESS:")
              print(f"   - Path: {file_path}")
              print(f"   - Size: {actual_size} bytes")
              print(f"   - Expected: {len(file_bytes)} bytes")
              print(f"   - Readable: {is_readable}")
              print(f"   - Size match: {actual_size == len(file_bytes)}")
              
              if actual_size != len(file_bytes):
                  print(f"⚠️  SIZE MISMATCH! Expected: {len(file_bytes)}, Actual: {actual_size}")
                  return json.dumps({'status': 'error', 'message': f'File size mismatch. Expected: {len(file_bytes)}, Actual: {actual_size}'})
              
              # Store the file path and add to tracking list
              self.uploaded_files.append(file_path)
              self.saved_file_path = file_path
              
              # Also create a relative path for display
              rel_path = os.path.relpath(file_path, self.script_dir)
              
              return json.dumps({
                  'status': 'success', 
                  'message': f'File saved successfully as {file_name}', 
                  'path': file_path,
                  'relative_path': rel_path,
                  'size': actual_size,
                  'original_name': original_name,
                  'readable': is_readable,
                  'bytes_written': len(file_bytes)
              })
          else:
              print("❌ File verification failed - file does not exist after write")
              return json.dumps({'status': 'error', 'message': 'File was not created successfully - file does not exist after write operation'})
              
      except Exception as e:
          error_msg = f'Unexpected error saving file: {str(e)}'
          print(f"❌ {error_msg}")
          import traceback
          print("Full traceback:")
          traceback.print_exc()
          return json.dumps({'status': 'error', 'message': error_msg})
      finally:
          print("="*50)
          print("📄 FILE SAVE PROCESS COMPLETED")
          print("="*50 + "\n")
    
    def set_job_description(self, job_desc):
        """
        Store the job description as a string
        """
        try:
            self.job_description = str(job_desc).strip() if job_desc else ""
            print(f"✅ Job description stored: {len(self.job_description)} characters")
            if len(self.job_description) > 0:
                preview = self.job_description[:100] + "..." if len(self.job_description) > 100 else self.job_description
                print(f"✅ Preview: {preview}")
            return json.dumps({
                'status': 'success', 
                'message': 'Job description saved',
                'length': len(self.job_description)
            })
        except Exception as e:
            error_msg = f'Error saving job description: {str(e)}'
            print(f"❌ {error_msg}")
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
    
    def list_directory_files(self):
        """
        List all files in the uploads directory for debugging
        """
        try:
            files = []
            directories_to_check = [self.uploads_dir, self.script_dir]
            
            result = {'directories': {}}
            
            for directory in directories_to_check:
                dir_files = []
                if os.path.exists(directory):
                    for item in os.listdir(directory):
                        item_path = os.path.join(directory, item)
                        if os.path.isfile(item_path):
                            dir_files.append({
                                'name': item,
                                'size': os.path.getsize(item_path),
                                'path': item_path,
                                'modified': time.ctime(os.path.getmtime(item_path))
                            })
                
                result['directories'][directory] = {
                    'exists': os.path.exists(directory),
                    'files': dir_files,
                    'count': len(dir_files)
                }
            
            return json.dumps({
                'status': 'success',
                'data': result
            })
        except Exception as e:
            return json.dumps({'status': 'error', 'message': str(e)})
    
    def analyze_resume(self, file_data, job_description):
        """
        This method will be called from JavaScript to analyze the resume.
        It saves the file, stores the job description, and performs analysis.
        """
        try:
            print("\n" + "="*60)
            print("🐍 PyResume AI - Starting Analysis")
            print("="*60)
            
            # Print received data info
            print("📥 Received data:")
            print(f"   - File data keys: {list(file_data.keys()) if file_data else 'None'}")
            print(f"   - Job description length: {len(job_description) if job_description else 0}")
            
            # First save the uploaded file
            print("\n📄 Step 1: Saving uploaded file...")
            file_result = json.loads(self.save_uploaded_file(file_data))
            if file_result['status'] == 'error':
                print(f"❌ File save failed: {file_result['message']}")
                return json.dumps({'status': 'error', 'message': f"File save failed: {file_result['message']}"})
            else:
                print(f"✅ File saved successfully: {file_result.get('path', 'Unknown path')}")
            
            # Save the job description
            print("\n💼 Step 2: Storing job description...")
            job_result = json.loads(self.set_job_description(job_description))
            if job_result['status'] == 'error':
                print(f"❌ Job description save failed: {job_result['message']}")
                return json.dumps({'status': 'error', 'message': f"Job description save failed: {job_result['message']}"})
            else:
                print(f"✅ Job description saved: {job_result.get('length', 0)} characters")
            
            # List directory contents for verification
            print("\n📁 Step 3: Verifying file system...")
            dir_result = json.loads(self.list_directory_files())
            if dir_result['status'] == 'success':
                for directory, info in dir_result['data']['directories'].items():
                    print(f"📁 {directory}: {info['count']} files")
                    for file_info in info['files']:
                        print(f"   - {file_info['name']} ({file_info['size']} bytes)")
            
            print(f"\n✅ Current saved file: {self.saved_file_path}")
            print(f"✅ File exists: {os.path.exists(self.saved_file_path) if self.saved_file_path else False}")
            
            # Simulate processing time
            print("\n🔍 Step 4: Processing analysis...")
            time.sleep(1.0)
            
            # Generate analysis results
            file_info = {
                'name': file_data.get('name', 'resume.pdf') if file_data else 'resume.pdf',
                'size': file_data.get('size', 0) if file_data else 0,
                'type': file_data.get('type', 'application/pdf') if file_data else 'application/pdf'
            }
            
            analysis_result = self._perform_analysis(file_info, self.job_description)
            self.analysis_results = analysis_result
            
            print("✅ Analysis completed successfully!")
            print("="*60 + "\n")
            
            return json.dumps({'status': 'success', 'data': analysis_result})
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error during analysis: {error_msg}")
            import traceback
            traceback.print_exc()
            return json.dumps({'status': 'error', 'message': error_msg})
    
    def _perform_analysis(self, file_info, job_desc):
        """
        Perform the actual resume analysis logic.
        """
        # Keywords to look for in job description
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
        
        job_desc_lower = job_desc.lower() if job_desc else ""
        
        # Find skills mentioned in job description
        required_skills = []
        for skill, keywords in skill_keywords.items():
            if any(keyword in job_desc_lower for keyword in keywords):
                required_skills.append(skill)
        
        # Mock skill matching (in real implementation, you'd parse the resume)
        import random
        random.seed(42)  # For consistent results
        
        matched_skills = []
        missing_skills = []
        
        for skill in required_skills:
            if random.random() > 0.3:
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Calculate overall score
        if required_skills:
            score = int((len(matched_skills) / len(required_skills)) * 100)
        else:
            score = 75
        
        score += random.randint(-10, 15)
        score = max(0, min(100, score))
        
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
            'savedFileExists': os.path.exists(self.saved_file_path) if self.saved_file_path else False,
            'uploadsDirectory': self.uploads_dir,
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
        Clean up uploaded files
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
        pygame.mixer.init()
        music_file = "background_music.mp3"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        music_path = os.path.join(script_dir, music_file)
        
        if os.path.exists(music_path):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)
            print("🎵 Background music started...")
            
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(script_dir, 'index.html')
    
    if os.path.exists(html_file):
        print(f"📄 Loading HTML from: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as f:
            return f.read()
    
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
    print(f"📁 Directory exists: {os.path.exists(script_dir)}")
    print(f"📁 Directory writable: {os.access(script_dir, os.W_OK)}")
    
    # Load HTML content
    html_content = load_html_content()
    
    # Create API instance
    api = PyResumeAPI()
    print("✅ PyResume API initialized")
    
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
    print("   2. Enter job description (minimum 1 character)")
    print("   3. Click 'Analyze with PyResume AI'")
    print("   4. Files will be saved in: uploads/ subdirectory")
    print("   5. Check console for detailed debugging info")
    print("   6. Close the window to exit")
    print("=" * 60)
    
    try:
        webview.start(debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"\n💥 Error starting application: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        print("🎵 Background music stopped")
        print("👋 PyResume AI Application closed")
        
        # api.cleanup_files()  # Uncomment to auto-cleanup