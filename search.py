import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import math
from common_helper import create_embedding
from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymilvus import MilvusClient
import openai

load_dotenv()

class Indexer:
  
    MODEL_CHUNK_SIZE = 8192

    def __init__(self, milvus_client, milvus_collection_name):
        self.milvus_client = milvus_client
        self.milvus_collection_name = milvus_collection_name
  
    def get_html_sitemap(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "xml")
        links = []
        locations = soup.find_all("loc")
        for location in locations:
            url = location.get_text()
            links.append(url)
        return links
  
    def get_html_body_content(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        body = soup.body
        inner_text = body.get_text()
        return inner_text
  
    def index_website(self, website_url):
        limit = 5
        links = self.get_html_sitemap(website_url)
        for link in links[:limit]:
            print(link)
            try:
                content = self.get_html_body_content(link)
                self.add_html_to_vectordb(content, link)
            except:
                print("unable to process: " + link)
  
    def add_html_to_vectordb(self, content, path):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.MODEL_CHUNK_SIZE,
            chunk_overlap  = math.floor(self.MODEL_CHUNK_SIZE/10)
        )
        docs = text_splitter.create_documents([content])
        for doc in docs:
            embedding = create_embedding(doc.page_content)
            self.insert_embedding(embedding, doc.page_content, path)
  
    def insert_embedding(self, embedding, text, path):
        row = {
            'vector': embedding,
            'text': text,
            'path': path
        }
        self.milvus_client.insert(self.milvus_collection_name, data=[row])


class SearchEngine:
    def __init__(self, milvus_client, milvus_collection_name):
        self.milvus_client = milvus_client
        self.milvus_collection_name = milvus_collection_name
  
    def query_milvus(self, embedding):
        result_count = 3
        result = self.milvus_client.search(
            collection_name=self.milvus_collection_name,
            data=[embedding],
            limit=result_count,
            output_fields=["path", "text"])
        list_of_knowledge_base = list(map(lambda match: match['entity']['text'], result[0]))
        list_of_sources = list(map(lambda match: match['entity']['path'], result[0]))
        return {
            'list_of_knowledge_base': list_of_knowledge_base,
            'list_of_sources': list_of_sources
        }
  
    def query_vector_db(self, embedding):
        return self.query_milvus(embedding)
  
    def ask_chatgpt(self, knowledge_base, user_query):
        system_content = """You are an AI coding assistant designed to help users with their programming needs based on the Knowledge Base provided.
        If you dont know the answer, say that you dont know the answer. You will only answer questions related to fly.io, any other questions, you should say that its out of your responsibilities.
        Only answer questions using data from knowledge base and nothing else.
        """
        user_content = f"""
            Knowledge Base:
            ---
            {knowledge_base}
            ---
            User Query: {user_query}
            Answer:
        """
        system_message = {"role": "system", "content": system_content}
        user_message = {"role": "user", "content": user_content}
        chatgpt_response = openai.ChatCompletion.create(model="gpt-3.5-turbo-0613", messages=[system_message, user_message])
        return chatgpt_response.choices[0].message.content
  
    def search(self, user_query):
        embedding = create_embedding(user_query)
        result = self.query_vector_db(embedding)
        print("sources")
        for source in result['list_of_sources']:
            print(source)
        knowledge_base = "\n".join(result['list_of_knowledge_base'])
        response = self.ask_chatgpt(knowledge_base, user_query)
        return {
            'sources': result['list_of_sources'],
            'response': response
        }


milvus_client = MilvusClient(
    uri=os.getenv("MILVUS_ENDPOINT"),
    token=os.getenv("MILVUS_API_KEY")
)

milvus_collection_name = 'test'

indexer = Indexer(milvus_client, milvus_collection_name)
searchEngine = SearchEngine(milvus_client, milvus_collection_name)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS method
    allow_headers=["*"],
)

class Msg(BaseModel):
    msg: str

@app.get("/")
async def root():
    return {"message": "/search, /create_index"}

@app.post("/search")
async def search(inp: Msg):
    result = searchEngine.search(inp.msg)
    return result

@app.post("/create_index")
async def create_index(inp: Msg):
    result = indexer.index_website(inp.msg)
    return { "message": "Indexing complete" }
