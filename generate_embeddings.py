import os
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "openai/clip-vit-base-patch32"
print(f"Loading CLIP model on {device}...")

model = CLIPModel.from_pretrained(model_id).to(device)
processor = CLIPProcessor.from_pretrained(model_id)

IMAGE_DIR = "images"
OUTPUT_DIR = "embeddings"
os.makedirs(OUTPUT_DIR, exist_ok=True)

image_embeddings = []
filenames = []

valid_exts = (".jpg", ".jpeg", ".png", ".bmp")
all_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(valid_exts)])

print(f"Extracting embeddings for {len(all_files)} images...")
for fname in all_files:
    img_path = os.path.join(IMAGE_DIR, fname)
    try:
        image = Image.open(img_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        
        with torch.no_grad():
            vision_outputs = model.vision_model(**inputs)
            img_features = model.visual_projection(vision_outputs[1])
            img_features = img_features / img_features.norm(dim=-1, keepdim=True)
        
        image_embeddings.append(img_features.cpu().numpy().flatten())
        filenames.append(fname)
    except Exception as e:
        print(f"Error reading {fname}: {e}")

np.save(os.path.join(OUTPUT_DIR, "image_embeddings.npy"), np.array(image_embeddings))
np.save(os.path.join(OUTPUT_DIR, "filenames.npy"), np.array(filenames))
print(f"Successfully saved embeddings for {len(filenames)} images!")