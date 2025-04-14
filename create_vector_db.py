# create_vector_db.py
from product_recommendation import create_product_embeddings
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sử dụng: python create_vector_db.py <đường_dẫn_file_csv>")
        sys.exit(1)

    csv_file = sys.argv[1]
    create_product_embeddings(csv_file)