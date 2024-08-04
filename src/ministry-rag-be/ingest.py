import os
import time
import argparse
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from langchain_community.document_loaders import DirectoryLoader,TextLoader
from langchain_chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Set up argument parser
parser = argparse.ArgumentParser(description="Ingest documents and add to vector store.")
parser.add_argument('--ingest', action='store_true', help='Run ingestion process')
args = parser.parse_args()

persist_directory="./vector_db"


#print(all_splits[0].page_content)
#embeddingModel = AzureOpenAIEmbeddings(model="text-embedding-3-large", azure_deployment="text-embedding-3")
embeddingModel = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_type="azure",
                api_version="2023-05-15",
                model_name="text-embedding-3-large"
            )



persistent_client = chromadb.PersistentClient(path=persist_directory)
lifestudy_collection = persistent_client.get_or_create_collection(name="lifestudy_collection", embedding_function=embeddingModel)
print(f"Embeddings in collection: {lifestudy_collection.count()}")

if args.ingest:
    text_loader_kwargs={'autodetect_encoding': True}
    loader = DirectoryLoader("../../Data", glob="**/*.txt", loader_cls=TextLoader, loader_kwargs=text_loader_kwargs, use_multithreading=False, show_progress=True)
    docs = loader.load()
    print(len(docs))


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)

    print(f"Number of splits: {len(all_splits)}")

    ids = [str(i) for i in range(len(all_splits))]
    metadata = [split.metadata for split in all_splits]
    documents = [split.page_content for split in all_splits]

    for i in range(len(all_splits)//500 + 1):
        print(f"Adding documents {i*500} to {(i+1)*500}")
        start_index = i*500
        stop_index = min((i+1)*500, len(all_splits))
        lifestudy_collection = persistent_client.get_or_create_collection(name="lifestudy_collection", embedding_function=embeddingModel)
        lifestudy_collection.add(ids=ids[start_index: stop_index], documents=documents[start_index: stop_index], metadatas=metadata[start_index: stop_index])
        print(f"Added documents {start_index} to {stop_index} out of {len(all_splits)}")
        print(f"Embeddings in collection: {lifestudy_collection.count()}")
        print("~~~~~~~Sleeping for 60 seconds~~~~~~~")
        time.sleep(60)

#vectorstore = Chroma(persist_directory=persist_directory)
#vectorstore.add_documents(documents=all_splits[:500], embedding=embeddingModel, persist_directory=persist_directory)

#retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

#retrieved_docs = retriever.invoke("Which chapter in Genesis does Jehovah appear to Abraham for the first time?")
retrieved_docs = lifestudy_collection.query(query_texts=["Which chapter in Genesis does Jehovah appear to Abraham for the first time?"], n_results=5)
for d in retrieved_docs['documents'][0]:
    print(d)
    print("-----------------------------------")
