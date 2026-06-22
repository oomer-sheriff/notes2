# Task P8-2: Embeddings and RAG Retrieval

**Goal:** Prove that text embeddings geometrically encode semantic meaning, and build the core components of a RAG retrieval system.

Create a Jupyter Notebook in `homework/lab-files/`.

## Part 1: Embedding Space Visualization
1. `pip install sentence-transformers scikit-learn matplotlib seaborn`
2. Load a Bi-Encoder: `model = SentenceTransformer('all-MiniLM-L6-v2')`
3. Create a list of 10 sentences. Make sure there are 3 distinct topics (e.g., 3 about pets, 3 about finance, 4 about programming).
4. Get the embeddings for all 10 sentences.
5. Compute the Cosine Similarity matrix (`10x10`) between all pairs of sentences.
6. Plot this matrix as a heatmap using `seaborn`.
7. **Observation:** You should see clear bright squares along the diagonal corresponding to your 3 topic clusters. The model inherently knows that "cat" is closer to "kitten" than to "stock market", even though the words share no characters!

## Part 2: Nearest Neighbor Retrieval (Mini Vector DB)
1. Write a function `retrieve(query, document_embeddings, top_k=2)` that takes a string query, embeds it, calculates the cosine similarity against all document embeddings, and returns the indices of the `top_k` most similar documents.
2. Test it by searching for a query that shares no exact words with the target document (e.g., query: "equity prices dropped", target: "The stock market crashed today").
3. **Question:** Why does dense retrieval (embeddings) succeed here where a keyword search (like BM25 or TF-IDF) would fail completely?

## Part 3: Cross-Encoder Reranking
1. Load a Cross-Encoder: `reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')`
2. Take a slightly ambiguous query like `"apple price"`.
3. Take two documents: `"An apple is a red fruit with a price of $1"` and `"Apple stock price drops after earnings report"`.
4. Run the Cross-Encoder. You must pass them as pairs: `reranker.predict([("apple price", doc1), ("apple price", doc2)])`.
5. Compare the results. The Cross-Encoder is much more precise than the Bi-Encoder because it can apply self-attention *between* the query and the document simultaneously!
