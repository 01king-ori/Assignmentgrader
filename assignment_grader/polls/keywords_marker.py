

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())

    # Remove stop words and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]

    # Stemming
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(word) for word in tokens]

    return tokens

def calculate_similarity(answer, expected_keywords):
    # Preprocess both the answer and expected keywords
    answer_tokens = preprocess_text(answer)
    expected_tokens = preprocess_text(' '.join(expected_keywords))

    # Calculate Jaccard similarity
    intersection = set(answer_tokens).intersection(expected_tokens)
    union = set(answer_tokens).union(expected_tokens)
    similarity = len(intersection) / len(union)

    return similarity

def mark_assignment(answer, expected_keywords):
    answer_tokens = preprocess_text(answer)
    expected_tokens = preprocess_text(' '.join(expected_keywords))

    # Calculate the number of keywords found in the student's answer
    found_keywords = set(answer_tokens).intersection(expected_tokens)
    marks = len(found_keywords) * 5

    return marks
