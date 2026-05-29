3. Technical Requirements (Mandatory)

Every project must include the following components:

·         Deployment (Flask or FastAPI): Serve your model via a API. Build a Streamlit front-end that accepts real user input and returns a meaningful prediction or response.

·         RAG Pipeline OR Multimodal Input (at least one): RAG: Implement a retrieval-augmented generation pipeline using FAISS or ChromaDB or others over a domain-specific corpus.
Multimodal: Combine at least two input modalities (e.g., image + text) in a unified model pipeline.

·         Transformer-based Model: Integrate at least one pre-trained Transformer model (e.g., BERT, ViT, T5, LLaMA, BioGPT). Fine-tuning is encouraged; prompt engineering or feature extraction are also acceptable.

·         Rigorous Evaluation: Report domain-appropriate metrics with a proper Train / Validation / Test split:
• Classification: Accuracy, F1-Score, AUC-ROC,…
• Generation / QA: QA Accuracy = Number of Correct/Relevant Answers}
• Retrieval: Hit Rate @K (K=3, 5): The percentage of queries where the truly relevant document appears in the top $K$ retrieved results.

Submission:

•    Final Notebook (.ipynb): A clean, reproducible notebook running end-to-end. 
•    Deployed Application (app.py).
•    Project Report: A structured report (minimum 8 pages) covering: problem statement, methodology, results, discussion, and conclusion.
•    Presentation: A slide presentation + 5-minute Q&A.