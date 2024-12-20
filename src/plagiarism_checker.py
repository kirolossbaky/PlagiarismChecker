import os
import numpy as np
import nltk
import spacy
import chardet
import textdistance
from fuzzywuzzy import fuzz
from langdetect import detect
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'plagiarism_checker.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Additional imports for file handling
import PyPDF2
import docx

# Download necessary NLTK resources
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Try to download spaCy model, if not already present
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy model...")
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

def detect_encoding(file_path):
    """
    Detect file encoding
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        str: Detected encoding
    """
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
    return result['encoding'] or 'utf-8'

def extract_text_from_file(file_path):
    """
    Extract text from various file types
    
    Args:
        file_path (str): Path to the file
    
    Returns:
        str: Extracted text
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    try:
        if file_extension == '.txt':
            # For text files, use standard file reading
            with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
                return f.read()
        
        elif file_extension == '.pdf':
            # For PDF files
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                return text
        
        elif file_extension == '.docx':
            # For Word documents
            doc = docx.Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        
        elif file_extension == '.md':
            # For Markdown files
            with open(file_path, 'r', encoding=detect_encoding(file_path)) as f:
                return f.read()
        
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    except Exception as e:
        raise ValueError(f"Error extracting text from {file_path}: {str(e)}")

def clean_text(text):
    """
    Clean text by removing HTML tags, extra whitespaces
    
    Args:
        text (str): Input text
    
    Returns:
        str: Cleaned text
    """
    # Remove HTML tags
    soup = BeautifulSoup(text, 'html.parser')
    text = soup.get_text(separator=' ')
    
    # Remove extra whitespaces
    text = ' '.join(text.split())
    
    return text

def preprocess_text(text):
    """
    Comprehensive text preprocessing
    
    Args:
        text (str): Input text
    
    Returns:
        str: Preprocessed text
    """
    # Clean text
    text = clean_text(text)
    
    # Tokenize
    tokens = nltk.word_tokenize(text)
    
    # Remove stopwords and perform basic preprocessing
    stop_words = set(nltk.corpus.stopwords.words('english'))
    tokens = [token.lower() for token in tokens if token.isalnum() and token.lower() not in stop_words]
    
    # Lemmatization
    doc = nlp(' '.join(tokens))
    lemmatized_tokens = [token.lemma_ for token in doc]
    
    return ' '.join(lemmatized_tokens)

def calculate_similarities(text1, text2):
    """
    Calculate multiple similarity metrics
    
    Args:
        text1 (str): First text
        text2 (str): Second text
    
    Returns:
        dict: Similarity scores
    """
    # TF-IDF Cosine Similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    
    # Semantic Similarity (using a lightweight model)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    semantic_embeddings1 = model.encode([text1])
    semantic_embeddings2 = model.encode([text2])
    semantic_sim = cosine_similarity(semantic_embeddings1, semantic_embeddings2)[0][0]
    
    # Fuzzy String Matching
    fuzzy_ratio = fuzz.ratio(text1, text2) / 100.0
    
    # Levenshtein Distance
    levenshtein_sim = 1 - (textdistance.levenshtein.distance(text1, text2) / 
                           max(len(text1), len(text2)))
    
    return {
        'cosine_similarity': float(cosine_sim),
        'semantic_similarity': float(semantic_sim),
        'fuzzy_similarity': float(fuzzy_ratio),
        'levenshtein_similarity': float(levenshtein_sim)
    }

def check_plagiarism(doc1_path, doc2_path, threshold=0.7):
    """
    Comprehensive plagiarism check
    
    Args:
        doc1_path (str): Path to first document
        doc2_path (str): Path to second document
        threshold (float): Similarity threshold for plagiarism
    
    Returns:
        dict: Plagiarism detection results
    """
    logger.info(f"Starting plagiarism check for {doc1_path} and {doc2_path}")
    
    # Extract text from files
    text1 = extract_text_from_file(doc1_path)
    text2 = extract_text_from_file(doc2_path)
    
    logger.info(f"Extracted text from {doc1_path} and {doc2_path}")
    
    # Preprocess texts
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    logger.info(f"Preprocessed text for {doc1_path} and {doc2_path}")
    
    # Calculate similarities
    similarities = calculate_similarities(processed_text1, processed_text2)
    
    logger.info(f"Calculated similarities for {doc1_path} and {doc2_path}")
    
    # Combine similarities (weighted average)
    combined_similarity = (
        0.3 * similarities['cosine_similarity'] +
        0.3 * similarities['semantic_similarity'] +
        0.2 * similarities['fuzzy_similarity'] +
        0.2 * similarities['levenshtein_similarity']
    )
    
    logger.info(f"Combined similarities for {doc1_path} and {doc2_path}")
    
    # Determine plagiarism
    is_plagiarized = combined_similarity > threshold
    
    logger.info(f"Plagiarism detected: {is_plagiarized}")
    
    return {
        **similarities,
        'combined_similarity': float(combined_similarity),
        'is_plagiarized': bool(is_plagiarized),
        'plagiarism_threshold': threshold
    }

if __name__ == '__main__':
    # Example usage
    result = check_plagiarism('sample1.txt', 'sample2.txt')
    logger.info(f"Plagiarism check result: {result}")
    print(result)
