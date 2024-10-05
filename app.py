import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

app = Flask(__name__)

# configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and \
      filename .rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# home route
@app.route('/')
def home():
    return render_template('index.html')
    

# upload and convert route
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Handle the file upload
        if 'file' not in request.files:
            return 'No file part in the request', 400

        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Extract text from PDF using PyPDF2
            reader = PdfReader(filepath)
            text = ''
            for page in reader.pages:
                text += page.extract_text()

            # Save the extracted text to a text file
            text_filename = filename.rsplit('.', 1)[0] + '.txt'
            text_filepath = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
            with open(text_filepath, 'w') as text_file:
                text_file.write(text)

            # Render the upload.html template with dynamic values
            return render_template('upload.html', filename=filename, text_filename=text_filename, extracted_text=text), 200
    
    # If it's a GET request, render the form again
    return render_template('index.html'), 200


# route to download the text file
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True), 200


# run app
if __name__ == '__main__':
    app.run(debug=True)