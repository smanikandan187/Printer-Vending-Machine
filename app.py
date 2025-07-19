import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

import os

# Get the absolute path to the directory where app.py is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the path to the templates folder relative to basedir
templates_dir = os.path.join(basedir, 'templates')

# Initialize Flask app, explicitly telling it where to find templates
app = Flask(__name__, template_folder=templates_dir)


# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
            
            # Create uploads directory if it doesn't exist
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            # Save the file to the uploads folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            return f'File "{filename}" successfully uploaded and saved!'
        else:
            return 'Upload failed: File type not allowed. Allowed types: txt, pdf, png, jpg, jpeg, gif, doc, docx, xls, xlsx, ppt, pptx'
    
    return 'Upload failed'

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
