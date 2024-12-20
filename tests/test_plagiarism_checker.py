import unittest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.plagiarism_checker import (
    check_plagiarism, 
    preprocess_text, 
    detect_encoding, 
    clean_text, 
    calculate_similarities,
    extract_text_from_file
)

class TestPlagiarismChecker(unittest.TestCase):
    def setUp(self):
        # Create sample text files for testing
        with open('test_doc1.txt', 'w', encoding='utf-8') as f1, \
             open('test_doc2.txt', 'w', encoding='utf-8') as f2:
            f1.write("This is a sample document about machine learning and artificial intelligence.")
            f2.write("This is another document discussing machine learning techniques and AI.")

    def tearDown(self):
        # Remove test files
        os.remove('test_doc1.txt')
        os.remove('test_doc2.txt')

    def test_detect_encoding(self):
        encoding = detect_encoding('test_doc1.txt')
        self.assertIsInstance(encoding, str)
        self.assertTrue(encoding.lower() in ['utf-8', 'ascii'])

    def test_clean_text(self):
        html_text = "<p>Hello, <b>world</b>!</p>"
        cleaned = clean_text(html_text)
        self.assertEqual(cleaned, "Hello, world!")

    def test_preprocess_text(self):
        text = "Hello, world! This is a test document about AI."
        processed = preprocess_text(text)
        self.assertIsInstance(processed, str)
        self.assertTrue(len(processed) > 0)
        
        # Check that stop words and punctuation are removed
        self.assertNotIn("hello", processed.lower())
        self.assertNotIn("world", processed.lower())

    def test_calculate_similarities(self):
        text1 = "This is a sample document about machine learning."
        text2 = "This is another document discussing machine learning techniques."
        
        similarities = calculate_similarities(text1, text2)
        
        # Check keys
        expected_keys = [
            'cosine_similarity', 
            'semantic_similarity', 
            'fuzzy_similarity', 
            'levenshtein_similarity'
        ]
        for key in expected_keys:
            self.assertIn(key, similarities)

        # Check value types and ranges
        for key, value in similarities.items():
            self.assertIsInstance(value, float)
            self.assertTrue(0 <= value <= 1)

    def test_check_plagiarism(self):
        result = check_plagiarism('test_doc1.txt', 'test_doc2.txt')
        
        # Check result keys
        expected_keys = [
            'cosine_similarity', 
            'semantic_similarity', 
            'fuzzy_similarity', 
            'levenshtein_similarity',
            'combined_similarity', 
            'is_plagiarized', 
            'plagiarism_threshold'
        ]
        for key in expected_keys:
            self.assertIn(key, result)

        # Check value types
        self.assertIsInstance(result['combined_similarity'], float)
        self.assertIsInstance(result['is_plagiarized'], bool)

    def test_plagiarism_threshold(self):
        # Test different thresholds
        low_threshold_result = check_plagiarism('test_doc1.txt', 'test_doc2.txt', threshold=0.5)
        high_threshold_result = check_plagiarism('test_doc1.txt', 'test_doc2.txt', threshold=0.9)
        
        # Ensure threshold affects plagiarism detection
        self.assertTrue(low_threshold_result['is_plagiarized'])
        self.assertFalse(high_threshold_result['is_plagiarized'])

    def test_extract_text_from_file(self):
        text = extract_text_from_file('test_doc1.txt')
        self.assertIsInstance(text, str)
        self.assertTrue(len(text) > 0)

    def test_unsupported_file_type(self):
        with self.assertRaises(ValueError):
            extract_text_from_file('test_doc1.xyz')

if __name__ == '__main__':
    unittest.main()
