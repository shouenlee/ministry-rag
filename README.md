# ministry-rag
LLM applied to the lifestudies.

pip install -r requirements.txt

###Ingestion pipeline
python ingest.py --ingest

###Chroma Server
chroma run --path ./vector_db

###UX
python app.py
