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
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request has the file part
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    # If the user does not select a file
    if file.filename == '':
        return 'No selected file', 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # extract text from PDF using PyPDF2
        reader = PdfReader(filepath)
        text = ''

        for page in reader.pages:
            text += page.extract_text()

        # save the extracted text to a text file
        text_filename = filename.rsplit('.', 1)[0] + '.txt'
        text_filepath = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
        with open(text_filepath, 'w') as text_file:
            text_file.write(text)

        # provide download link for the text file
        return f'File "{filename}" uploaded and converted successfully!<br><a href="/download/{text_filename}">Download extracted text</a><br>Extracted Text: <br><pre>{text}<pre>', 200

    else:
        return 'Invalid file format. Only PDF files are allowed.', 400

# route to download the text file
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


# run app
if __name__ == '__main__':
    app.run(debug=True)