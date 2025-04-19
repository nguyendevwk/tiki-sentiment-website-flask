import pandas as pd
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from flask import Flask, jsonify, request
from services.tiki_service import TikiService
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Hàm tạo embedding từ dữ liệu sản phẩm
def create_product_embeddings(csv_file):
    logger.debug(f"Starting to create product embeddings from {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        required_columns = ["product_id", "name", "short_description", "price",
                           "original_price", "discount_rate", "rating_average",
                           "review_count", "category_name", "brand_name", "url", "image_url"]

        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"Column {col} not found in CSV")

        df['product_id'] = pd.to_numeric(df['product_id'], errors='coerce')
        df = df.dropna(subset=['product_id'])
        df['product_id'] = df['product_id'].astype(int)

        df['combined_text'] = df['name'].fillna('') + ' ' + df['short_description'].fillna('') + ' ' + \
                             df['category_name'].fillna('') + ' ' + df['brand_name'].fillna('')

        logger.debug("Loading SentenceTransformer model...")
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        logger.debug("Encoding product texts to embeddings...")
        embeddings = model.encode(df['combined_text'].tolist(), show_progress_bar=True)

        logger.debug("Creating FAISS index...")
        dimension = embeddings.shape[1]
        embeddings = embeddings.astype('float32')
        index = faiss.IndexFlatL2(dimension)
        faiss.normalize_L2(embeddings)
        index.add(embeddings)

        output_dir = 'vector_db'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        faiss.write_index(index, f"{output_dir}/product_index.faiss")
        df_to_save = df.drop(columns=['combined_text'])
        df_to_save.to_pickle(f"{output_dir}/product_data.pkl")
        product_ids = df['product_id'].tolist()
        with open(f"{output_dir}/product_ids.pkl", 'wb') as f:
            pickle.dump(product_ids, f)

        logger.debug(f"Vector database saved to {output_dir}")
        return index, df_to_save, product_ids
    except Exception as e:
        logger.error(f"Failed to create product embeddings: {str(e)}")
        raise

# Hàm để lấy gợi ý sản phẩm dựa trên ID sản phẩm, sử dụng API Tiki
def get_similar_products_by_id(product_id, index, df, product_ids, model, tiki_service, top_k=10):
    logger.debug(f"--- Starting get_similar_products_by_id for product_id: {product_id} ---")
    try:
        # Bước 1: Kiểm tra product_id
        logger.debug(f"Checking if product_id {product_id} exists in product_ids")
        product_id_exists = product_id in product_ids
        logger.debug(f"Product_id exists in vector database: {product_id_exists}")

        # Bước 2: Gọi API Tiki
        logger.debug(f"Fetching product details from Tiki API for product_id: {product_id}")
        product_details = tiki_service.get_product_details(product_id)
        logger.debug(f"Tiki API response: {product_details}")

        if not product_details or 'error' in product_details:
            logger.warning(f"Failed to fetch product details for ID {product_id} from Tiki API")
            return []

        # Bước 3: Trích xuất dữ liệu
        logger.debug("Extracting product details")
        name = product_details.get('name', '')
        short_description = product_details.get('short_description', '')
        category_name = product_details.get('categories', {}).get('name', '')
        brand_name = product_details.get('brand', {}).get('name', '')
        logger.debug(f"Name: {name}")
        logger.debug(f"Short_description: {short_description}")
        logger.debug(f"Category_name: {category_name}")
        logger.debug(f"Brand_name: {brand_name}")

        # Bước 4: Tạo combined_text
        combined_text = f"{name} {short_description} {category_name} {brand_name}"
        logger.debug(f"Combined text: {combined_text}")
        if not combined_text.strip():
            logger.warning(f"No valid text data for product_id: {product_id}")
            return []

        # Bước 5: Tạo embedding
        logger.debug("Encoding combined text to embedding")
        query_embedding = model.encode([combined_text])[0].astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        logger.debug(f"Query embedding shape: {query_embedding.shape}")

        # Bước 6: Tìm kiếm FAISS
        logger.debug(f"Searching FAISS index with top_k: {top_k + 1}")
        distances, indices = index.search(query_embedding, top_k + 1)
        logger.debug(f"FAISS search results - distances: {distances.tolist()}")
        logger.debug(f"FAISS search results - indices: {indices.tolist()}")

        # Bước 7: Lọc product_id gốc và lấy danh sách
        result_product_ids = [product_ids[idx] for idx in indices[0] if product_ids[idx] != product_id][:top_k]
        logger.debug(f"Filtered result_product_ids: {result_product_ids}")

        # Bước 8: Lấy thông tin sản phẩm từ DataFrame
        similar_products = []
        for pid in result_product_ids:
            logger.debug(f"Checking product_id {pid} in DataFrame")
            if pid in df['product_id'].values:
                product = df[df['product_id'] == pid].iloc[0].to_dict()
                similar_products.append(product)
                logger.debug(f"Added product {pid} to similar_products")
            else:
                logger.warning(f"Product ID {pid} not found in DataFrame")

        logger.debug(f"Final similar_products count: {len(similar_products)}")
        logger.debug(f"--- Completed get_similar_products_by_id for product_id: {product_id} ---")
        return similar_products
    except Exception as e:
        logger.error(f"Error in get_similar_products_by_id for ID {product_id}: {str(e)}")
        return []


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        logger.error("Usage: python product_recommendation.py <csv_file_path>")
        sys.exit(1)
    csv_file = sys.argv[1]
    create_product_embeddings(csv_file)
