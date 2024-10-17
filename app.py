import os
from flask import Flask, request, render_template, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter

app = Flask(__name__)

# configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

# home route
@app.route('/')
def home():
    return render_template('index.html')

# upload and convert route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Validate file type on the server side
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract text from PDF using PyPDF2
        reader = PdfReader(filepath)

        if reader.is_encrypted:
            return jsonify({"encrypted": True, "filename": filename}), 200

        text = ''
        for page in reader.pages:
            text += page.extract_text()

        # Save the extracted text to a text file
        text_filename = filename.rsplit('.', 1)[0] + '.txt'
        text_filepath = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
        with open(text_filepath, 'w') as text_file:
            text_file.write(text)

        # Return a response with the text file and PDF filename
        return jsonify({"encrypted": False, "filename": filename, "text_filename": text_filename}), 200
    else:
        return 'Invalid file type. Please upload a PDF file.', 400

@app.route('/submit_password', methods=['POST'])
def submit_password():
    data = request.json
    filename = data['filename']
    password = data['password']

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    reader = PdfReader(filepath)

    # Try decrypting the PDF with the provided password
    if reader.is_encrypted:
        if reader.decrypt(password):
            text = ''
            for page in reader.pages:
                text += page.extract_text()

            # Save the extracted text to a text file
            text_filename = filename.rsplit('.', 1)[0] + '.txt'
            text_filepath = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
            with open(text_filepath, 'w') as text_file:
                text_file.write(text)

            return jsonify({"success": True, "filename": filename, "text_filename": text_filename}), 200
        else:
            return jsonify({"success": False}), 400
    else:
        return 'File is not encrypted', 400

@app.route('/show_result/<filename>/<text_filename>')
def show_result(filename, text_filename):
    text_filepath = os.path.join(app.config['UPLOAD_FOLDER'], text_filename)
    
    # Read the extracted text to display it on the result page
    with open(text_filepath, 'r') as text_file:
        extracted_text = text_file.read()
    
    return render_template('result.html', filename=filename, text_filename=text_filename, extracted_text=extracted_text)

# route to download the text file
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)