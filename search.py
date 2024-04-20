import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Function to scrape website content
def scrape_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text content from HTML
            text = " ".join([p.text for p in soup.find_all('p')])
            return text
        else:
            st.error(f"Failed to fetch website content. Error code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Load dataset
@st.cache
def load_data():
    return pd.read_csv("data.csv")

# Preprocess text
def preprocess_text(text):
    # Implement text preprocessing steps if needed (e.g., lowercase, remove punctuation)
    return text

# Create TF-IDF vectorizer
def create_vectorizer(data):
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', preprocessor=preprocess_text)
    tfidf_matrix = tfidf_vectorizer.fit_transform(data)
    return tfidf_vectorizer, tfidf_matrix

# Search documents
def search_documents(query, data, vectorizer, matrix):
    query_vec = vectorizer.transform([query])
    cosine_similarities = cosine_similarity(query_vec, matrix).flatten()
    document_scores = [(score, idx) for idx, score in enumerate(cosine_similarities)]
    document_scores.sort(reverse=True)
    return document_scores

def main():
    st.title("Chat Prompt Search Engine")

    # Load data
    data = load_data()

    # Create TF-IDF vectorizer
    vectorizer, matrix = create_vectorizer(data['text'])

    # Chat prompt
    query = st.text_input("Type your query here:")

    if st.button("Search"):
        if query:
            # Search documents
            results = search_documents(query, data['text'], vectorizer, matrix)
            st.subheader("Search Results:")
            for score, idx in results:
                st.write(f"- Document #{idx}: {data['title'][idx]} (Score: {score:.2f})")

if __name__ == "__main__":
    main()
