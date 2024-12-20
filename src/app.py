import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from plagiarism_checker import check_plagiarism

# Ensure data directory exists
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(data_dir, exist_ok=True)

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = data_dir

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_plagiarism', methods=['POST'])
def upload_documents():
    # Check if files are present
    if 'document1' not in request.files or 'document2' not in request.files:
        return jsonify({'error': 'Two documents are required'}), 400
    
    doc1 = request.files['document1']
    doc2 = request.files['document2']
    
    # Check if filename is empty
    if doc1.filename == '' or doc2.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if file is allowed
    if not (allowed_file(doc1.filename) and allowed_file(doc2.filename)):
        return jsonify({'error': 'File type not allowed. Supported types: txt, pdf, docx, md'}), 400
    
    # Secure filenames
    filename1 = secure_filename(doc1.filename)
    filename2 = secure_filename(doc2.filename)
    
    # Save temporary files
    doc1_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_doc1_{filename1}')
    doc2_path = os.path.join(app.config['UPLOAD_FOLDER'], f'temp_doc2_{filename2}')
    
    try:
        # Save files
        doc1.save(doc1_path)
        doc2.save(doc2_path)
        
        # Run plagiarism check
        result = check_plagiarism(doc1_path, doc2_path)
        
        # Clean up temporary files
        os.remove(doc1_path)
        os.remove(doc2_path)
        
        return jsonify(result)
    
    except Exception as e:
        # Clean up files if they exist
        if os.path.exists(doc1_path):
            os.remove(doc1_path)
        if os.path.exists(doc2_path):
            os.remove(doc2_path)
        
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
