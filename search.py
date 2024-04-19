import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

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
        return {"Title": url, "Text": text}
    else:
        return None

# Function to search indexed data
def search_indexed_data(user_query, indexed_data):
    # Placeholder function for query_vector_db and create_embedding
    # Replace this with your actual implementation
    def query_vector_db(embedding):
        return {'list_of_sources': ['Source 1', 'Source 2'], 'list_of_knowledge_base': ['Knowledge 1', 'Knowledge 2']}

    def create_embedding(query):
        # Placeholder for embedding creation
        return query

    embedding = create_embedding(user_query)
    result = query_vector_db(embedding)

    st.write("Sources:")
    for source in result['list_of_sources']:
        st.write(source)

    knowledge_base = "\n".join(result['list_of_knowledge_base'])

    # Ask the user query using chat prompt
    response = ask_chatgpt(knowledge_base, user_query)  # Placeholder for ask_chatgpt

    return {
        'sources': result['list_of_sources'],
        'response': response
    }

def main():
    st.title("Chat Prompt Search Engine")

    # Load or create DataFrame
    if 'data' not in st.session_state:
        st.session_state.data = pd.DataFrame(columns=['Title', 'Text'])

    # Chat prompt to index website
    url = st.text_input("Enter website URL:")
    if st.button("Index Website"):
        if url:
            indexed_data = index_website(url)
            if indexed_data:
                indexed_df = pd.DataFrame(indexed_data, index=[0])  # Create DataFrame with single row
                st.session_state.data = pd.concat([st.session_state.data, indexed_df], ignore_index=True)
                st.success("Website indexed successfully!")
            else:
                st.error("Failed to index website.")

    # Chat prompt to search indexed data
    user_query = st.text_input("Enter your query:")
    if st.button("Search"):
        if user_query:
            search_result = search_indexed_data(user_query, st.session_state.data)
            st.write("Search Results:")
            st.write(search_result['sources'])
            st.write("Response:")
            st.write(search_result['response'])

    # Display indexed data
    if not st.session_state.data.empty:
        st.subheader("Indexed Data:")
        st.write(st.session_state.data)

if __name__ == "__main__":
    main()
