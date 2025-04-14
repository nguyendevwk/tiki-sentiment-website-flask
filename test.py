# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from services.tiki_service import TikiService
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_vector_database():
    """Tải vector database và kiểm tra tính hợp lệ"""
    logger.debug("--- Starting load_vector_database ---")
    try:
        vector_files = [
            'vector_db/product_index.faiss',
            'vector_db/product_data.pkl',
            'vector_db/product_ids.pkl'
        ]
        logger.debug("Checking vector database files")
        if not all(os.path.exists(f) for f in vector_files):
            logger.error("One or more vector database files missing")
            return None, None, None

        logger.debug("Loading FAISS index")
        index = faiss.read_index('vector_db/product_index.faiss')
        logger.debug("Loading product DataFrame")
        df = pd.read_pickle('vector_db/product_data.pkl')
        logger.debug("Loading product_ids")
        with open('vector_db/product_ids.pkl', 'rb') as f:
            product_ids = pickle.load(f)

        logger.debug(f"Vector database loaded. Total products: {len(product_ids)}")
        logger.debug(f"DataFrame shape: {df.shape}")
        logger.debug(f"FAISS index ntotal: {index.ntotal}")
        return index, df, product_ids
    except Exception as e:
        logger.error(f"Failed to load vector database: {str(e)}")
        return None, None, None

def test_similar_products_by_id(product_id, index, df, product_ids, model, tiki_service, top_k=10):
    """Kiểm tra tìm kiếm sản phẩm tương tự dựa trên product_id"""
    logger.debug(f"--- Starting test_similar_products_by_id for product_id: {product_id} ---")
    if index is None or df is None or product_ids is None:
        logger.error("Vector database not initialized")
        return []

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
        logger.debug(f"Final similar_products: {[p['product_id'] for p in similar_products]}")
        logger.debug(f"--- Completed test_similar_products_by_id for product_id: {product_id} ---")
        return similar_products
    except Exception as e:
        logger.error(f"Error in test_similar_products_by_id for ID {product_id}: {str(e)}")
        return []

def test_search_by_text(query_text, index, df, product_ids, model, top_k=10):
    """Kiểm tra tìm kiếm sản phẩm dựa trên text query"""
    logger.debug(f"--- Starting test_search_by_text for query: {query_text} ---")
    if index is None or df is None or product_ids is None:
        logger.error("Vector database not initialized")
        return []

    try:
        logger.debug("Encoding query text to embedding")
        query_embedding = model.encode([query_text])[0].astype('float32').reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        logger.debug(f"Query embedding shape: {query_embedding.shape}")

        logger.debug(f"Searching FAISS index with top_k: {top_k}")
        distances, indices = index.search(query_embedding, top_k)
        logger.debug(f"FAISS search results - distances: {distances.tolist()}")
        logger.debug(f"FAISS search results - indices: {indices.tolist()}")

        result_product_ids = [product_ids[idx] for idx in indices[0]]
        logger.debug(f"Result product_ids: {result_product_ids}")

        result_products = []
        for pid in result_product_ids:
            logger.debug(f"Checking product_id {pid} in DataFrame")
            if pid in df['product_id'].values:
                product = df[df['product_id'] == pid].iloc[0].to_dict()
                result_products.append(product)
                logger.debug(f"Added product {pid} to result_products")
            else:
                logger.warning(f"Product ID {pid} not found in DataFrame")

        logger.debug(f"Final result_products count: {len(result_products)}")
        logger.debug(f"Final result_products: {[p['product_id'] for p in result_products]}")
        logger.debug(f"--- Completed test_search_by_text for query: {query_text} ---")
        return result_products
    except Exception as e:
        logger.error(f"Error in test_search_by_text for query {query_text}: {str(e)}")
        return []

def main():
    """Chạy các bài kiểm tra truy vấn database"""
    logger.debug("--- Starting test_db_search ---")

    # Khởi tạo tài nguyên
    logger.debug("Loading SentenceTransformer model")
    try:
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        logger.error(f"Failed to load SentenceTransformer model: {str(e)}")
        return

    logger.debug("Initializing TikiService")
    try:
        tiki_service = TikiService()
    except Exception as e:
        logger.error(f"Failed to initialize TikiService: {str(e)}")
        return

    # Tải vector database
    index, df, product_ids = load_vector_database()
    if index is None or df is None or product_ids is None:
        logger.error("Cannot proceed with tests due to vector database failure")
        return

    # Test 1: Tìm kiếm sản phẩm tương tự với product_id
    test_product_ids = [187046435, 199104980]
    for product_id in test_product_ids:
        logger.debug(f"\n=== Running test for product_id: {product_id} ===")
        similar_products = test_similar_products_by_id(
            product_id, index, df, product_ids, model, tiki_service, top_k=10
        )
        if similar_products:
            logger.debug(f"Similar products found: {[p['name'] for p in similar_products]}")
        else:
            logger.warning(f"No similar products found for product_id: {product_id}")

    # Test 2: Tìm kiếm theo text query
    test_queries = ["laptop", "smartphone"]
    for query in test_queries:
        logger.debug(f"\n=== Running test for query: {query} ===")
        result_products = test_search_by_text(
            query, index, df, product_ids, model, top_k=10
        )
        if result_products:
            logger.debug(f"Products found: {[p['name'] for p in result_products]}")
        else:
            logger.warning(f"No products found for query: {query}")

    logger.debug("--- Completed test_db_search ---")

if __name__ == "__main__":
    main()
