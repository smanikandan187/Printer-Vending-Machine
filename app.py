import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
        return redirect(url_for("index"))
    return "Signup Page (You can add signup.html later)"

@app.route("/home")
def home():
    return "Home Page (You can add home.html later)"

@app.route("/upload", methods=["POST"])
def upload_file():
    if request.method == "POST":
        # Check if the post request has the file part
        if 'document' not in request.files:
            return redirect(request.url)
        file = request.files['document']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Secure the filename to prevent directory traversal attacks
            filename = secure_filename(file.filename)
            
            try:
                # Save file to local uploads directory
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                return f'''
                <h2>File Successfully Uploaded to Server!</h2>
                <p><strong>Filename:</strong> {filename}</p>
                <p><strong>File saved to:</strong> {file_path}</p>
                <p><strong>File size:</strong> {os.path.getsize(file_path)} bytes</p>
                <br>
                <a href="/">Upload Another File</a>
                '''
                
            except Exception as e:
                return f'Upload failed: {str(e)}'
        else:
            return 'Upload failed: File type not allowed. Allowed types: txt, pdf, png, jpg, jpeg, gif, doc, docx, xls, xlsx, ppt, pptx'
    
    return 'Upload failed'

@app.route("/files")
def list_files():
    """List all uploaded files."""
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        if not files:
            return "<h2>No files uploaded yet</h2><br><a href='/'>Upload a file</a>"
        
        file_list = "<h2>Uploaded Files:</h2><ul>"
        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
            file_size = os.path.getsize(file_path)
            file_list += f"<li><strong>{file}</strong> - {file_size} bytes</li>"
        file_list += "</ul><br><a href='/'>Upload Another File</a>"
        
        return file_list
    except Exception as e:
        return f"Error listing files: {str(e)}"

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

