import os
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from plagiarism_checker import check_plagiarism

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    # Log incoming request
    logger.info(f"Received plagiarism check request")
    
    # Check if files are present
    if 'document1' not in request.files or 'document2' not in request.files:
        logger.warning("Two documents are required")
        return jsonify({'error': 'Two documents are required'}), 400
    
    doc1 = request.files['document1']
    doc2 = request.files['document2']
    
    # Check if filename is empty
    if doc1.filename == '' or doc2.filename == '':
        logger.warning("No file selected")
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if file is allowed
    if not (allowed_file(doc1.filename) and allowed_file(doc2.filename)):
        logger.warning(f"Unsupported file types: {doc1.filename}, {doc2.filename}")
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
        
        logger.info(f"Saved temporary files: {doc1_path}, {doc2_path}")
        
        # Run plagiarism check
        result = check_plagiarism(doc1_path, doc2_path)
        
        # Log plagiarism check result
        logger.info(f"Plagiarism check result: {result}")
        
        # Clean up temporary files
        os.remove(doc1_path)
        os.remove(doc2_path)
        
        return jsonify(result)
    
    except Exception as e:
        # Log the error
        logger.error(f"Error during plagiarism check: {str(e)}", exc_info=True)
        
        # Clean up files if they exist
        if os.path.exists(doc1_path):
            os.remove(doc1_path)
        if os.path.exists(doc2_path):
            os.remove(doc2_path)
        
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Log application startup
    logger.info("Starting Plagiarism Checker application")
    app.run(host='0.0.0.0', port=8000, debug=True)
