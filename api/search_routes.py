from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import faiss
import pickle
import os
from sentence_transformers import SentenceTransformer
import logging
from logging.handlers import RotatingFileHandler

# Thiết lập logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Tạo file handler với giới hạn kích thước
os.makedirs('logs', exist_ok=True)
file_handler = RotatingFileHandler('logs/search.log', maxBytes=10*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Giữ console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Tạo Blueprint
def create_search_blueprint(tiki_service):
    search_bp = Blueprint('search_bp', __name__)

    class SearchService:
        def __init__(self, tiki_service):
            logger.debug("--- Initializing SearchService ---")
            self.model = None
            self.tiki_service = tiki_service
            self.index = None
            self.df = None
            self.product_ids = None
            self._load_resources()

        def _load_resources(self):
            """Tải model và vector database"""
            try:
                logger.debug(f"Current working directory: {os.getcwd()}")
                logger.debug("Loading SentenceTransformer model")
                self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

                base_dir = os.path.dirname(os.path.abspath(__file__))
                vector_dir = os.path.join(base_dir, '..', 'vector_db')
                logger.debug(f"Vector database directory: {vector_dir}")
                vector_files = [
                    os.path.join(vector_dir, 'product_index.faiss'),
                    os.path.join(vector_dir, 'product_data.pkl'),
                    os.path.join(vector_dir, 'product_ids.pkl')
                ]
                logger.debug(f"Checking vector database files: {vector_files}")
                for f in vector_files:
                    if not os.path.exists(f):
                        logger.error(f"File not found: {f}")
                        raise FileNotFoundError(f"Vector database file missing: {f}")

                logger.debug("Loading FAISS index")
                self.index = faiss.read_index(vector_files[0])
                logger.debug("Loading product DataFrame")
                self.df = pd.read_pickle(vector_files[1])
                logger.debug("Loading product_ids")
                with open(vector_files[2], 'rb') as f:
                    self.product_ids = pickle.load(f)
                logger.debug(f"Vector database loaded. Total products: {len(self.product_ids)}")
                logger.debug(f"DataFrame shape: {self.df.shape}")
                logger.debug(f"FAISS index ntotal: {self.index.ntotal}")
            except Exception as e:
                logger.error(f"Failed to initialize SearchService: {str(e)}", exc_info=True)
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
                logger.debug(f"Checking if product_id {product_id} exists in product_ids")
                product_id_exists = product_id in self.product_ids
                logger.debug(f"Product_id exists in vector database: {product_id_exists}")

                logger.debug(f"Fetching product details from Tiki API for product_id: {product_id}")
                product_details = self.tiki_service.get_product_details(product_id)
                logger.debug(f"Tiki API response: {product_details}")

                if not product_details or 'error' in product_details:
                    logger.warning(f"Failed to fetch product details for ID {product_id} from Tiki API")
                    return []

                logger.debug("Extracting product details")
                name = product_details.get('name', '')
                short_description = product_details.get('short_description', '')
                category_name = product_details.get('categories', {}).get('name', '')
                brand_name = product_details.get('brand', {}).get('name', '')
                logger.debug(f"Name: {name}")
                logger.debug(f"Short_description: {short_description}")
                logger.debug(f"Category_name: {category_name}")
                logger.debug(f"Brand_name: {brand_name}")

                combined_text = f"{name} {short_description} {category_name} {brand_name}"
                logger.debug(f"Combined text: {combined_text}")
                if not combined_text.strip():
                    logger.warning(f"No valid text data for product_id: {product_id}")
                    return []

                logger.debug("Encoding combined text to embedding")
                query_embedding = self.model.encode([combined_text])[0].astype('float32').reshape(1, -1)
                faiss.normalize_L2(query_embedding)
                logger.debug(f"Query embedding shape: {query_embedding.shape}")

                logger.debug(f"Searching FAISS index with top_k: {top_k + 1}")
                distances, indices = self.index.search(query_embedding, top_k + 1)
                logger.debug(f"FAISS search results - distances: {distances.tolist()}")
                logger.debug(f"FAISS search results - indices: {indices.tolist()}")
                result_product_ids = [self.product_ids[idx] for idx in indices[0] if self.product_ids[idx] != product_id][:top_k]
                logger.debug(f"Filtered result_product_ids: {result_product_ids}")

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
                logger.error(f"Error in get_similar_products_by_id for ID {product_id}: {str(e)}", exc_info=True)
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
                logger.error(f"Error in search_products_by_text for query {query_text}: {str(e)}", exc_info=True)
                return []

    # Khởi tạo SearchService
    search_service = SearchService(tiki_service)

    @search_bp.route('/recommendations/<int:product_id>', methods=['GET'])
    def get_recommendations(product_id):
        logger.debug(f"--- Processing request for /api/recommendations/{product_id} ---")
        if search_service.index is None or search_service.df is None or search_service.product_ids is None:
            logger.error("Vector database not initialized")
            return jsonify({
                "error": "Vector database not initialized",
                "status": "error"
            }), 500

        try:
            limit = int(request.args.get('limit', 10))
            if limit < 1 or limit > 50:
                logger.warning(f"Invalid limit value: {limit}. Using default limit of 10.")
                limit = 10
            logger.debug(f"Limit set to: {limit}")

            similar_products = search_service.get_similar_products_by_id(product_id, top_k=limit)
            logger.debug(f"get_similar_products_by_id returned {len(similar_products)} products")

            if not similar_products:
                logger.warning(f"No similar products found for product_id: {product_id}")
                if search_service.df is not None and len(search_service.df) > 0:
                    logger.debug("Falling back to random products")
                    random_products = search_service.df.sample(n=min(limit, len(search_service.df)), replace=False).to_dict('records')
                    logger.debug(f"Selected {len(random_products)} random products")
                    return jsonify({
                        "data": random_products,
                        "status": "success",
                        "note": "random_fallback"
                    }), 200
                else:
                    logger.debug("No products available for fallback")
                    return jsonify({
                        "data": [],
                        "status": "success",
                        "note": "no_data_available"
                    }), 200

            logger.debug("Preparing response with similar products")
            response = {
                "data": similar_products,
                "status": "success"
            }
            logger.debug(f"Response data: {response}")
            logger.debug(f"--- Completed request for /api/recommendations/{product_id} ---")
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Error in /api/recommendations/{product_id}: {str(e)}", exc_info=True)
            return jsonify({
                "error": f"Failed to fetch recommendations: {str(e)}",
                "status": "error"
            }), 500

    @search_bp.route('/search', methods=['GET'])
    def search_products():
        logger.debug("--- Processing request for /api/search ---")
        try:
            query = request.args.get('q', '')
            limit = int(request.args.get('limit', 10))
            if limit < 1 or limit > 50:
                logger.warning(f"Invalid limit value: {limit}. Using default limit of 10.")
                limit = 10
            logger.debug(f"Query: {query}, Limit: {limit}")

            if not query:
                logger.warning("Empty search query received")
                return jsonify({
                    "error": "No search query provided",
                    "status": "error"
                }), 400

            if search_service.index is None or search_service.df is None or search_service.product_ids is None:
                logger.error("Vector database not initialized")
                return jsonify({
                    "error": "Vector database not initialized",
                    "status": "error"
                }), 500

            result_products = search_service.search_products_by_text(query, top_k=limit)
            logger.debug(f"search_products_by_text returned {len(result_products)} products")

            response = {
                "data": result_products,
                "status": "success"
            }
            logger.debug(f"Response data: {response}")
            logger.debug("--- Completed request for /api/search ---")
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Error in /api/search: {str(e)}", exc_info=True)
            return jsonify({
                "error": f"Failed to fetch search results: {str(e)}",
                "status": "error"
            }), 500

    return search_bp