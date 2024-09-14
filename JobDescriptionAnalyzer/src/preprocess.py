import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download('stopwords')

def load_data(file_path):
    return pd.read_csv(file_path)

def preprocess_text(text):
    # Tokenize words, convert to lowercase, remove punctuation and stopwords
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word not in string.punctuation and word not in stop_words]
    return ' '.join(words)

def preprocess_job_descriptions(df):
    df['processed_description'] = df['Job Description'].apply(preprocess_text)
    return df