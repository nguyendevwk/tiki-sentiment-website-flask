import pandas as pd
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
from services.tiki_service import TikiService
from flask import jsonify, request
import logging

# Thiết lập logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        logger.debug("--- Initializing SearchService ---")
        self.model = None
        self.tiki_service = None
        self.index = None
        self.df = None
        self.product_ids = None
        self._load_resources()

    def _load_resources(self):
        """Tải model, TikiService và vector database"""
        try:
            logger.debug("Loading SentenceTransformer model")
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.debug("Initializing TikiService")
            self.tiki_service = TikiService()

            vector_files = [
                'vector_db/product_index.faiss',
                'vector_db/product_data.pkl',
                'vector_db/product_ids.pkl'
            ]
            logger.debug("Checking vector database files")
            if not all(os.path.exists(f) for f in vector_files):
                logger.error("One or more vector database files missing")
                return

            logger.debug("Loading FAISS index")
            self.index = faiss.read_index('vector_db/product_index.faiss')
            logger.debug("Loading product DataFrame")
            self.df = pd.read_pickle('vector_db/product_data.pkl')
            logger.debug("Loading product_ids")
            with open('vector_db/product_ids.pkl', 'rb') as f:
                self.product_ids = pickle.load(f)
            logger.debug(f"Vector database loaded. Total products: {len(self.product_ids)}")
            logger.debug(f"DataFrame shape: {self.df.shape}")
            logger.debug(f"FAISS index ntotal: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Failed to initialize SearchService: {str(e)}")
            self.index = None
            self.df = None
            self.product_ids = None

    def get_similar_products_by_id(self, product_id, top_k=10):
        """Tìm sản phẩm tương tự dựa trên product_id"""
        logger.debug(f"--- Starting get_similar_products_by_id for product_id: {product_id} ---")
        if self.index is None or self.df is None or self.product_ids is None:
            logger.error("Vector database not initialized")
            return []

        try:
            # Bước 1: Kiểm tra product_id
            logger.debug(f"Checking if product_id {product_id} exists in product_ids")
            product_id_exists = product_id in self.product_ids
            logger.debug(f"Product_id exists in vector database: {product_id_exists}")

            # Bước 2: Gọi API Tiki
            logger.debug(f"Fetching product details from Tiki API for product_id: {product_id}")
            product_details = self.tiki_service.get_product_details(product_id)
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
            query_embedding = self.model.encode([combined_text])[0].astype('float32').reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            logger.debug(f"Query embedding shape: {query_embedding.shape}")

            # Bước 6: Tìm kiếm FAISS
            logger.debug(f"Searching FAISS index with top_k: {top_k + 1}")
            distances, indices = self.index.search(query_embedding, top_k + 1)
            logger.debug(f"FAISS search results - distances: {distances.tolist()}")
            logger.debug(f"FAISS search results - indices: {indices.tolist()}")

            # Bước 7: Lọc product_id gốc và lấy danh sách
            result_product_ids = [self.product_ids[idx] for idx in indices[0] if self.product_ids[idx] != product_id][:top_k]
            logger.debug(f"Filtered result_product_ids: {result_product_ids}")

            # Bước 8: Lấy thông tin sản phẩm từ DataFrame
            similar_products = []
            for pid in result_product_ids:
                logger.debug(f"Checking product_id {pid} in DataFrame")
                if pid in self.df['product_id'].values:
                    product = self.df[self.df['product_id'] == pid].iloc[0].to_dict()
                    similar_products.append(product)
                    logger.debug(f"Added product {pid} to similar_products")
                else:
                    logger.warning(f"Product ID {pid} not found in DataFrame")

            logger.debug(f"Final similar_products count: {len(similar_products)}")
            logger.debug(f"Final similar_products: {[p['product_id'] for p in similar_products]}")
            logger.debug(f"--- Completed get_similar_products_by_id for product_id: {product_id} ---")
            return similar_products
        except Exception as e:
            logger.error(f"Error in get_similar_products_by_id for ID {product_id}: {str(e)}")
            return []

    def search_products_by_text(self, query_text, top_k=10):
        """Tìm kiếm sản phẩm dựa trên text query"""
        logger.debug(f"--- Starting search_products_by_text for query: {query_text} ---")
        if self.index is None or self.df is None or self.product_ids is None:
            logger.error("Vector database not initialized")
            return []

        try:
            logger.debug("Encoding query text to embedding")
            query_embedding = self.model.encode([query_text])[0].astype('float32').reshape(1, -1)
            faiss.normalize_L2(query_embedding)
            logger.debug(f"Query embedding shape: {query_embedding.shape}")

            logger.debug(f"Searching FAISS index with top_k: {top_k}")
            distances, indices = self.index.search(query_embedding, top_k)
            logger.debug(f"FAISS search results - distances: {distances.tolist()}")
            logger.debug(f"FAISS search results - indices: {indices.tolist()}")

            result_product_ids = [self.product_ids[idx] for idx in indices[0]]
            logger.debug(f"Result product_ids: {result_product_ids}")

            result_products = []
            for pid in result_product_ids:
                logger.debug(f"Checking product_id {pid} in DataFrame")
                if pid in self.df['product_id'].values:
                    product = self.df[self.df['product_id'] == pid].iloc[0].to_dict()
                    result_products.append(product)
                    logger.debug(f"Added product {pid} to result_products")
                else:
                    logger.warning(f"Product ID {pid} not found in DataFrame")

            logger.debug(f"Final result_products count: {len(result_products)}")
            logger.debug(f"Final result_products: {[p['product_id'] for p in result_products]}")
            logger.debug(f"--- Completed search_products_by_text for query: {query_text} ---")
            return result_products
        except Exception as e:
            logger.error(f"Error in search_products_by_text for query {query_text}: {str(e)}")
            return []
