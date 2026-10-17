# AI-Powered Image Search Engine

An AI-powered semantic image search platform developed during the 8-Week Deep Learning & Computer Vision Internship at Indian Institute of Technology (IIT) Bhubaneswar under the guidance of Dr. Debi Prosad Dogra.

## Project Overview
This project converts natural language queries into semantic vector embeddings using OpenAI's pretrained CLIP model (clip-vit-base-patch32) and retrieves relevant images from a privately assigned dataset using Cosine Similarity ranking.

## System Pipeline
1. **Dataset & Captioning (Week 1):** Objective manual captioning following Subject + Action + Setting rules.
2. **Vision-Language Embeddings (Week 4):** Precomputing 512-dimensional feature vectors for dataset images using the CLIP Vision Encoder.
3. **Semantic Retrieval Engine (Weeks 5 & 6):** Encoding text search queries via CLIP Text Encoder and computing Cosine Distance matrix operations.
4. **Interactive Frontend (Week 7):** Modern web user interface built with Streamlit.

## Repository Structure
- app.py: Streamlit web application interface
- search_engine.py: Modular backend search engine
- generate_embeddings.py: CLIP embedding extraction script
- requirements.txt: Python dependencies
- .gitignore: Data privacy rules

## How to Run Locally

### 1. Install Dependencies
`ash
pip install -r requirements.txt
``n
### 2. Generate Image Embeddings
`ash
python generate_embeddings.py
``n
### 3. Launch Web Application
`ash
streamlit run app.py
``n
## Data Confidentiality Notice
In compliance with the IIT Bhubaneswar Data Confidentiality & Handling Policy, private dataset images, manual captions, and generated vector files (.npy) are stored locally and excluded from public version control.
