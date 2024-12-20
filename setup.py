from setuptools import setup, find_packages

setup(
    name='ai-plagiarism-checker',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask',
        'scikit-learn',
        'numpy',
        'pandas',
        'nltk',
        'spacy',
        'tensorflow',
        'sentence-transformers'
    ],
    entry_points={
        'console_scripts': [
            'plagiarism-checker=app:main',
        ],
    },
    author='Your Name',
    description='An AI-powered assignment plagiarism checker',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/plagiarism-checker',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
