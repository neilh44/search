import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

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

# Function to index website information
def index_website(url):
    text = scrape_website(url)
    if text:
        return {"URL": url, "Text": text}
    else:
        return None

# Function to search indexed data and answer questions using LLM
def search_and_answer(user_query, indexed_data):
    # Initialize a question answering pipeline with a pre-trained model
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

    # Retrieve the most relevant URL from indexed data
    top_url = indexed_data.iloc[0]['URL']  # Assuming the first URL is the most relevant

    # Provide the URL's text as context to the language model along with the user query
    answer = qa_pipeline({
        'question': user_query,
        'context': indexed_data.iloc[0]['Text']
    })

    return answer['answer']

def main():
    st.title("Website Crawling and Question Answering")

    # Load or create DataFrame to store indexed data
    if 'indexed_data' not in st.session_state:
        st.session_state.indexed_data = pd.DataFrame(columns=['URL', 'Text'])

    # Chat prompt to index website
    url = st.text_input("Enter website URL:")
    if st.button("Index Website"):
        if url:
            indexed_data = index_website(url)
            if indexed_data:
                indexed_df = pd.DataFrame(indexed_data, index=[0])  # Create DataFrame with single row
                st.session_state.indexed_data = pd.concat([st.session_state.indexed_data, indexed_df], ignore_index=True)
                st.success("Website indexed successfully!")
            else:
                st.error("Failed to index website.")

    # Chat prompt to ask questions
    user_query = st.text_input("Ask a question:")
    if st.button("Ask"):
        if user_query and not st.session_state.indexed_data.empty:
            answer = search_and_answer(user_query, st.session_state.indexed_data)
            st.write("Answer:", answer)

    # Display indexed data
    if not st.session_state.indexed_data.empty:
        st.subheader("Indexed Data:")
        st.write(st.session_state.indexed_data)

if __name__ == "__main__":
    main()
    
