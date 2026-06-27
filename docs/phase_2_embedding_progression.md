# Embedding Model Progression

Tracking the embedding models tested in Phase 2 exploration (`notebooks/phase2_exploration.ipynb`).

Each model is evaluated by inspecting the t-SNE visualisation of the Chroma vector store to see how well document types cluster.

**Knowledge base:** 76 documents → 413 chunks (chunk_size=1000, chunk_overlap=200)
**Colors:** blue=products, green=employees, red=contracts, orange=company

---

## 1. all-MiniLM-L6-v2

**Type:** HuggingFace (local, free)
**Dimensions:** 384
**Vectors:** 413

```python
HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
```

**Visualisations:** `../assets/phase2/all-MiniLM-L6-v2/`

| File | Description |
|------|-------------|
| `2d_tsne.png` | 2D t-SNE scatter plot |
| `3d_tsne.png` | 3D t-SNE scatter plot |

![2D t-SNE](../assets/phase2/all-MiniLM-L6-v2/2d_tsne.png)
![3D t-SNE](../assets/phase2/all-MiniLM-L6-v2/3d_tsne.png)

**Notes:**
- Lightweight model, runs entirely locally
- Good baseline for comparison

---

## 2. text-embedding-3-small

**Type:** OpenAI
**Dimensions:** 1,536
**Vectors:** 413

```python
OpenAIEmbeddings(model="text-embedding-3-small")
```

**Visualisations:** `../assets/phase2/text-embedding-3-small/`

| File | Description |
|------|-------------|
| `2d_tsne.png` | 2D t-SNE scatter plot |
| `3d_tsne.png` | 3D t-SNE scatter plot |

![2D t-SNE](../assets/phase2/text-embedding-3-small/2d_tsne.png)
![3D t-SNE](../assets/phase2/text-embedding-3-small/3d_tsne.png)

**Notes:**
- OpenAI hosted model, requires API key
- 4× more dimensions than all-MiniLM-L6-v2 (1,536 vs 384)

---

## 3. text-embedding-3-large

**Type:** OpenAI
**Dimensions:** 3,072
**Vectors:** 413

```python
OpenAIEmbeddings(model="text-embedding-3-large")
```

**Visualisations:** `../assets/phase2/text-embedding-3-large/`

| File | Description |
|------|-------------|
| `2d_tsne.png` | 2D t-SNE scatter plot |
| `3d_tsne.png` | 3D t-SNE scatter plot |

![2D t-SNE](../assets/phase2/text-embedding-3-large/2d_tsne.png)
![3D t-SNE](../assets/phase2/text-embedding-3-large/3d_tsne.png)

**Notes:**
- OpenAI's highest-dimension embedding model
- 2× more dimensions than text-embedding-3-small (3,072 vs 1,536)

---

## 4. _(next model)_

> Add entry here when you switch embedding models in the notebook.

**Visualisations:** `../assets/phase2/<model-name>/`
