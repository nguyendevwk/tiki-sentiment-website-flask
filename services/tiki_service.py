import requests
from utils.http_utils import get_with_retry
from config import TIKI_API_BASE, HEADERS

# Create a singleton session for Tiki API
class TikiService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TikiService, cls).__new__(cls)
            cls._instance.session = requests.Session()
            cls._instance.session.headers.update(HEADERS)
        return cls._instance

    def get_products(self, keyword=None, page=1, limit=30):
        """Get products from Tiki API"""
        url = f"{TIKI_API_BASE}/products"
        params = {
            'limit': limit,
            'page': page
        }

        if keyword and keyword != 'all':
            params['q'] = keyword
        else:
            params['sort'] = 'top_seller'

        return get_with_retry(self.session, url, params)

    def get_product_details(self, product_id):
        """Get product details from Tiki API"""
        url = f"{TIKI_API_BASE}/products/{product_id}"
        return get_with_retry(self.session, url)

    def get_reviews(self, product_id, page=1, limit=20):
        """Get product reviews from Tiki API"""
        url = f"{TIKI_API_BASE}/reviews"
        params = {
            'product_id': product_id,
            'page': page,
            'limit': limit,
            'include': 'comments,contribute_info,attribute_vote_summary'
        }
        return get_with_retry(self.session, url, params)

    def test_api_connectivity(self):
        """Test API connectivity"""
        test_results = {}

        # Test products API
        try:
            url = f"{TIKI_API_BASE}/products"
            params = {'limit': 5, 'sort': 'top_seller'}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            test_results['products_api'] = {
                'status': 'success',
                'status_code': response.status_code,
                'items_count': len(response.json().get('data', []))
            }
        except Exception as e:
            test_results['products_api'] = {
                'status': 'error',
                'error': str(e)
            }

        # Test reviews API
        try:
            # Use a common product ID for testing
            test_product_id = 187046435  # You may need to update this with a valid product ID
            url = f"{TIKI_API_BASE}/reviews"
            params = {'product_id': test_product_id, 'limit': 5}
            response = self.session.get(url, params=params)
            response.raise_for_status()
            test_results['reviews_api'] = {
                'status': 'success',
                'status_code': response.status_code,
                'items_count': len(response.json().get('data', [])),
                'product_id': test_product_id
            }
        except Exception as e:
            test_results['reviews_api'] = {
                'status': 'error',
                'error': str(e)
            }

        return test_results