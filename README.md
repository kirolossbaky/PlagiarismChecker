# AI-Powered Plagiarism Checker 🕵️‍♂️📄

## Overview
An advanced plagiarism detection tool that uses machine learning and natural language processing to compare document similarities across multiple file types.

## Features
- 📂 Supports multiple file types: txt, pdf, docx, md
- 🧠 Advanced text preprocessing
- 📊 Multiple similarity metrics
- 🔍 Detailed plagiarism analysis

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/PlagiarismChecker.git
cd PlagiarismChecker
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Download additional resources
```bash
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords
```

## Running the Application
```bash
python src/app.py
```
Access the application at `http://localhost:8000`

## How It Works
The plagiarism checker uses:
- TF-IDF Cosine Similarity
- Semantic Similarity
- Fuzzy String Matching
- Levenshtein Distance

## Contributing
Pull requests are welcome. For major changes, please open an issue first.

## License
[MIT](https://choosealicense.com/licenses/mit/)
