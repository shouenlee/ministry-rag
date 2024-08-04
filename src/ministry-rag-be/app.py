import os
import subprocess
import time
import requests
import chromadb
from chromadb import QueryResult
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv
from azure_client import AzureClient
import chromadb.utils.embedding_functions as embedding_functions

class Server:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.startup()
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/prompt', 'prompt', self.prompt, methods=['POST'])
        self.azure_client = AzureClient()

    def get_embedding_model(self):
        #TODO: Key based auth is disabled. Investigate managed identities.
        embedding_model = embedding_functions.OpenAIEmbeddingFunction(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_type="azure",
            api_version="2023-05-15",
            model_name="text-embedding-3-large"
        )
        self.embedding_model = embedding_model
        print("Embedding model initialized.")

    def get_vectordb_client(self):
        vectordb_client = chromadb.HttpClient(host='localhost', port=8000)
        self.vectordb_client = vectordb_client
        print("VectorDB client initialized.")

    def start_chroma_server(self):
        self.chromadb_process = subprocess.Popen(['chroma', 'run', '--path', './vector_db'])
        print("ChromaDB server started.")
        while True:
            try:
                response = requests.get('http://localhost:8000/')
                break
            except requests.ConnectionError:
                pass
            time.sleep(1)

    def startup(self):
        load_dotenv()
        self.start_chroma_server()
        self.get_embedding_model()
        self.get_vectordb_client()
        print("Startup function executed.")

    def shutdown(self, exception=None):
        if self.chromadb_process:
            self.chromadb_process.terminate()
            self.chromadb_process.wait()
            print("ChromaDB server terminated.")
        print("Shutdown function executed.")

    def home(self):
        return "Hello, Flask!"

    def prompt(self):
        data = request.get_json()
        question = data.get('question', '')
        collection = self.vectordb_client.get_or_create_collection(name="lifestudy_collection", embedding_function=self.embedding_model)
        retrieved_context = collection.query(query_texts=question, n_results=5)
        chat_completion_response = self.azure_client.get_completion(question, self.format_context(retrieved_context))
        response = {"response": f"{chat_completion_response}"}
        return jsonify(response)
    
    def format_context(self, context: QueryResult) -> str:
        formatted_context = ""
        zipped = zip([s['source'] for s in context['metadatas'][0]], context['documents'][0])
        for i, (ref, doc) in enumerate(zipped):
            formatted_context += f"Context {i}: \n \t Reference: {ref} \n \t Document: {doc}\n"

        return formatted_context

    def run(self):
        self.app.run(debug=True, port=5000)

if __name__ == '__main__':
    server = Server()
    server.run()
    server.shutdown()
    print("exiting")
