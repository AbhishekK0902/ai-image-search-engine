import os
import torch
import numpy as np
from transformers import CLIPProcessor, CLIPModel

class ImageSearchEngine:
    def __init__(self, embeddings_path="embeddings/image_embeddings.npy", 
                 filenames_path="embeddings/filenames.npy"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "openai/clip-vit-base-patch32"
        
        self.model = CLIPModel.from_pretrained(self.model_id).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_id)
        
        self.image_embeddings = np.load(embeddings_path)
        self.filenames = np.load(filenames_path)

    def search(self, query_text: str, top_k: int = 5):
        inputs = self.processor(text=[query_text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_outputs = self.model.text_model(**inputs)
            text_features = self.model.text_projection(text_outputs[1])
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
            text_emb = text_features.cpu().numpy().flatten()

        similarities = np.dot(self.image_embeddings, text_emb)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [
            {"filename": self.filenames[idx], "score": float(similarities[idx])}
            for idx in top_indices
        ]