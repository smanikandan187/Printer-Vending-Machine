import os
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuration
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:5000')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Handle signup logic here
        flash("Signup functionality not implemented yet", "info")
        return redirect(url_for("index"))
    return render_template("signup.html") if os.path.exists("templates/signup.html") else "Signup Page"

@app.route("/home")
def home():
    return render_template("home.html") if os.path.exists("templates/home.html") else "Home Page"

@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        # Check if the post request has the file part
        if 'document' not in request.files:
            flash("No file selected", "error")
            return redirect(request.url)
        
        file = request.files['document']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash("No file selected", "error")
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Get form data
                copies = int(request.form.get('copies', 1))
                priority = request.form.get('priority', 'normal')
                printer_name = request.form.get('printer_name', 'default')
                auto_print = request.form.get('auto_print') == 'on'
                
                # Prepare files and data for backend
                files = {'file': (file.filename, file.stream, file.mimetype)}
                data = {
                    'copies': copies,
                    'priority': priority,
                    'printer_name': printer_name,
                    'auto_print': str(auto_print).lower()
                }
                
                # Send to backend
                response = requests.post(
                    f'{BACKEND_URL}/api/upload',
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        success_message = f"File '{result['original_name']}' uploaded successfully!"
                        
                        if result.get('queued_for_printing'):
                            success_message += f" Queued for printing (Job ID: {result['job_id']}, Position: {result['queue_position']})"
                        
                        return render_template('upload_success.html', 
                                             result=result, 
                                             message=success_message) if os.path.exists("templates/upload_success.html") else f'''
                        <h2>✅ File Successfully Uploaded!</h2>
                        <div style="max-width: 600px; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                            <p><strong>Original Filename:</strong> {result['original_name']}</p>
                            <p><strong>Stored Filename:</strong> {result['filename']}</p>
                            <p><strong>File Size:</strong> {result['file_size']} bytes ({round(result['file_size']/(1024*1024), 2)} MB)</p>
                            <p><strong>Copies:</strong> {result['copies']}</p>
                            <p><strong>Priority:</strong> {result['priority']}</p>
                            
                            {f'<p><strong>✅ Queued for Printing:</strong> Yes</p><p><strong>Job ID:</strong> {result["job_id"]}</p><p><strong>Queue Position:</strong> {result["queue_position"]}</p>' if result.get('queued_for_printing') else '<p><strong>Queued for Printing:</strong> No</p>'}
                            
                            <div style="margin-top: 20px;">
                                <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px;">Upload Another File</a>
                                <a href="/status" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; margin-left: 10px;">View Status</a>
                                <a href="/queue" style="background: #ffc107; color: black; padding: 10px 20px; text-decoration: none; border-radius: 3px; margin-left: 10px;">View Queue</a>
                            </div>
                        </div>
                        '''
                    else:
                        flash(f"Upload failed: {result.get('error', 'Unknown error')}", "error")
                        return redirect(url_for('index'))
                else:
                    error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                    flash(f"Upload failed: {error_data.get('error', 'Server error')}", "error")
                    return redirect(url_for('index'))
                    
            except requests.exceptions.Timeout:
                flash("Upload timed out. Please try again.", "error")
                return redirect(url_for('index'))
            except requests.exceptions.ConnectionError:
                flash("Cannot connect to backend server. Please try again later.", "error")
                return redirect(url_for('index'))
            except Exception as e:
                flash(f"Upload failed: {str(e)}", "error")
                return redirect(url_for('index'))
        else:
            flash(f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', "error")
            return redirect(url_for('index'))
    
    flash("Invalid request", "error")
    return redirect(url_for('index'))

@app.route("/queue-file", methods=["POST"])
def queue_file():
    """Queue an already uploaded file for printing"""
    try:
        data = request.get_json()
        
        response = requests.post(
            f'{BACKEND_URL}/api/queue-file',
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Failed to queue file'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/status")
def status():
    """Show server status"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/status', timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            
            return render_template('status.html', status=status_data) if os.path.exists("templates/status.html") else f'''
            <h2>🖨️ Print Server Status</h2>
            <div style="max-width: 600px; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <p><strong>Server Status:</strong> {status_data.get('server_status', 'Unknown')}</p>
                <p><strong>Queue Size:</strong> {status_data.get('queue_size', 0)} jobs</p>
                <p><strong>Currently Printing:</strong> {'Yes' if status_data.get('printing') else 'No'}</p>
                <p><strong>Current Job:</strong> {status_data.get('current_job', 'None')}</p>
                <p><strong>Total Uploaded:</strong> {status_data.get('total_uploaded', 0)} files</p>
                <p><strong>Total Printed:</strong> {status_data.get('total_printed', 0)} files</p>
                <p><strong>Server Started:</strong> {status_data.get('server_start_time', 'Unknown')}</p>
                
                <div style="margin-top: 20px;">
                    <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px;">Upload File</a>
                    <a href="/queue" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; margin-left: 10px;">View Queue</a>
                    <a href="/files" style="background: #ffc107; color: black; padding: 10px 20px; text-decoration: none; border-radius: 3px; margin-left: 10px;">View Files</a>
                </div>
            </div>
            '''
        else:
            return f"<h2>❌ Cannot connect to backend server</h2><p>Status code: {response.status_code}</p><a href='/'>Go Back</a>"
            
    except Exception as e:
        return f"<h2>❌ Error connecting to backend</h2><p>{str(e)}</p><a href='/'>Go Back</a>"

@app.route("/queue")
def queue():
    """Show print queue"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/queue', timeout=10)
        
        if response.status_code == 200:
            queue_data = response.json()
            
            return render_template('queue.html', queue=queue_data) if os.path.exists("templates/queue.html") else f'''
            <h2>📋 Print Queue</h2>
            <div style="max-width: 800px; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <p><strong>Queue Size:</strong> {queue_data.get('queue_size', 0)} jobs</p>
                <p><strong>Currently Printing:</strong> {'Yes' if queue_data.get('printing') else 'No'}</p>
                <p><strong>Current Job:</strong> {queue_data.get('current_job', 'None')}</p>
                
                <h3>Queued Jobs:</h3>
                {''.join([f'''
                <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px;">
                    <strong>{job["filename"]}</strong> - {job["copies"]} copies - Priority: {job["priority"]}<br>
                    <small>Job ID: {job["job_id"]} | Uploaded: {job["uploaded_at"]} | Status: {job["status"]}</small>
                </div>
                ''' for job in queue_data.get('jobs', [])]) if queue_data.get('jobs') else '<p>No jobs in queue</p>'}
                
                <div style="margin-top: 20px;">
                    <a href="/" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px;">Upload File</a>
                    <a href="/status" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; margin-left: 10px;">View Status</a>
                    <button onclick="location.reload()" style="background: #6c757d; color: white; padding: 10px 20px; border: none; border-radius: 3px; margin-left: 10px; cursor: pointer;">Refresh</button>
                </div>
            </div>
            '''
        else:
            return f"<h2>❌ Cannot connect to backend server</h2><p>Status code: {response.status_code}</p><a href='/'>Go Back</a>"
            
    except Exception as e:
        return f"<h2>❌ Error connecting to backend</h2><p>{str(e)}</p><a href='/'>Go Back</a>"

@app.route("/files")
def files():
    """Show uploaded files"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/files', timeout=10)
        
        if response.status_code == 200:
            files_data = response.json()
            
            return render_template('files.html', files=files_data) if os.path.exists("templates/files.html") else f'''
            <h2>📁 Uploaded Files</h2>
            <div style="max-width: 900px; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <p><strong>Total Files:</strong> {files_data.get('total_files', 0)}</p>
                <p><strong>Total Size:</strong> {files_data.get('total_size_mb', 0)} MB</p>
                
                <h3>Files:</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background: #f8f9fa;">
                            <th style="padding: 8px; border: 