import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)

# Configuration for Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Configuration for file uploads
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
                # Upload file to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    file,
                    public_id=f"documents/{filename}",  # Organize files in a folder
                    resource_type="auto"  # Automatically detect file type
                )
                
                # Get the secure URL of the uploaded file
                file_url = upload_result['secure_url']
                public_id = upload_result['public_id']
                
                return f'''
                <h2>File Successfully Uploaded to Cloud!</h2>
                <p><strong>Filename:</strong> {filename}</p>
                <p><strong>File URL:</strong> <a href="{file_url}" target="_blank">{file_url}</a></p>
                <p><strong>Public ID:</strong> {public_id}</p>
                <br>
                <a href="/">Upload Another File</a>
                '''
                
            except Exception as e:
                return f'Upload failed: {str(e)}'
        else:
            return 'Upload failed: File type not allowed. Allowed types: txt, pdf, png, jpg, jpeg, gif, doc, docx, xls, xlsx, ppt, pptx'
    
    return 'Upload failed'

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
