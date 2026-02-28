# CMU Advanced NLP Assignment 2: End-to-end RAG System

This repository contains the codebase for an end-to-end Retrieval-Augmented Generation (RAG) system capable of answering factual questions about Pittsburgh and Carnegie Mellon University.

## Dependencies

The package requirements are specified in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
```

Additionally, NLTK stopwords and punkt tokenizers are required for chunking and BM25 processing. These are automatically downloaded by the scripts, but if you run into environment issues, ensure NLTK can fetch them.

## Running the Data Pipeline

The data ingestion pipeline handles scraping external URLs, reading provided baseline documents, segmenting the text with sentence-aware chunking, and evaluating dense/sparse retrieval vectors.

To run the entire data pipeline end-to-end, simply execute:
```bash
python data_pipeline/run_pipeline.py
```

This master script performs the following four steps automatically:
1. **Scrape Websites:** Reads verification schemas (`verified_urls.json`, `data_url.json`) and pulls down raw HTML and PDF datasets into `scraped_data/`.
2. **Create Database:** Reads both the raw `baseline_data/` and the newly `scraped_data/`, chunks it, and creates `data/knowledge_base.jsonl`.
3. **Build Dense Index:** Embeds chunks using `BAAI/bge-small-en-v1.5` and compiles a FAISS flat IP index inside `data/`.
4. **Build Sparse Index:** Builds a stemming-aware BM25 sparse retrieval index using `bm25s` inside `data/bm25_index/`.

*Note: You may also run the specific modules manually (e.g., `python data_pipeline/scrape_websites.py` or `python RAG/document_query_embedder.py`) if you only wish to test a specific subsystem.*

## Running the LLM Evaluation

Once the data indices are populated, you can evaluate the test queries utilizing our `HybridRetriever` (which computes a Reciprocal Rank Fusion / Weighted average of the retrieved context parameters) and our generation model (`Qwen/Qwen2.5-1.5B-Instruct`).

To run inferences across the test set (`test_set_day_2.json`), run:
```bash
python LLM/run_evaluation.py
```

The system outputs will be serialized to `system_outputs/system_output_day_2.json`, formatted and ready for submission scoring.

## Running on Google Colab

Hardware limits (VRAM constraints on local Macbooks or standard PCs) make the LLM generation step very slow or cause memory faults. To circumvent this, the codebase can be zipped into an uploadable format for use on Google Colab (with A100/T4 GPUs).

### Zipping the Repository

Before uploading, package the repository. This excludes Python caches and virtual environments which inflate the archive size. Run the following command at the repository root:

```bash
zip -r hw2_colab.zip data data_pipeline LLM RAG baseline_data scraped_data system_outputs requirements.txt test_set_day_2.json test_set_day_2.txt data_url.json leaderboard_queries.json final_urls_to_scrape.json verified_urls.json -x "*__pycache__*" -x "*.DS_Store*"
```

### Setup on Colab
1. Upload `hw2_colab.zip` to your Colab workspace and run: 
   ```bash
   !unzip -q hw2_colab.zip -d /content/hw2_colab
   %cd /content/hw2_colab
   ```
2. Make sure you enable the GPU runtime (**Runtime > Change runtime type > T4 / A100 GPU**).
3. Install dependencies:
   ```bash
   !pip install -r requirements.txt
   ```
4. Optional: If you haven't built the faiss index locally and included it in the zip, build it via the pipeline.
5. Finally, run the evaluation:
   ```bash
   !python LLM/run_evaluation.py
   ```
6. Download the generated output file from `/content/hw2_colab/system_outputs/system_output_day_2.json` to submit.

An Example Notebook is provided in `example_notebook.ipynb`
