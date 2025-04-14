# Tiki Sentiment Analysis Project

## Introduction

This is a Flask web application designed to analyze sentiments of product reviews on Tiki, a popular e-commerce platform, and provide personalized product recommendations. The project leverages machine learning models for sentiment classification and integrates with Tiki's API to fetch product details, reviews, and recommendations. It aims to help users understand customer sentiments through reviews and discover similar products effectively.

**Author:** Phạm Nguyễn
**GitHub:** [nguyendevwk](https://github.com/nguyendevwk/tiki-sentiment-website)

## Resources

-   **Dataset:** [Tiki Raw Sentiments Dataset](https://github.com/nguyendevwk/tiki-raw-sentiments-dataset.git) _(Update this link if available)_
-   **Trained Models:** [Kaggle Models](https://www.kaggle.com/code/phamnguyen03/sentiments-reviews-products) _(Update with specific Kaggle link)_

## Project Structure

```
tiki-sentiment-website/
│
├── api/
│   ├── product_routes.py       # API routes for product-related endpoints
│   ├── review_routes.py        # API routes for review-related endpoints
│   ├── sentiment_routes.py     # API routes for sentiment analysis
│   └── search_routes.py        # API routes for search and recommendation
├── models/
│   ├── loaders.py              # Model loading utilities
│   └── sentiment_models/       # Directory for pre-trained sentiment models
├── services/
│   ├── sentiment_service.py    # Sentiment analysis service
│   └── tiki_service.py         # Tiki API communication service
├── static/
│   ├── css/                    # CSS files (e.g., styles.css)
│   └── js/                     # JavaScript files (e.g., recommendations.js)
├── templates/
│   └── index.html              # Main HTML template
├── vector_db/
│   ├── product_index.faiss     # FAISS index for product recommendations
│   ├── product_data.pkl        # Product data DataFrame
│   └── product_ids.pkl         # Product IDs mapping
├── logs/
│   └── search.log              # Log file for search and recommendation activities
├── app.py                      # Main Flask application
├── requirements.txt            # Project dependencies
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # Project documentation
```

## Prerequisites

-   Python 3.8 or higher
-   Git
-   Virtual environment (recommended)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/nguyendevwk/tiki-sentiment-website.git
    cd tiki-sentiment-website
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    _Dependencies include Flask, pandas, numpy, faiss-cpu, sentence-transformers, requests, etc._

4. **Download the dataset:**

    - Obtain the [Tiki Raw Sentiments Dataset](https://example.com/tiki-raw-sentiments-dataset) and place it in the project directory (if required for preprocessing).

5. **Download pre-trained models:**
    - Visit [Kaggle Models](https://www.kaggle.com/models/your-model).
    - Download the sentiment classification models.
    - Place the models in the `models/sentiment_models/` directory.

## Configuration

1. **Environment Variables:**
   Create a `.env` file in the project root with the following variables:

    ```env
    FLASK_ENV=development
    TIKI_API_URL=https://api.tiki.vn/v2/
    MODEL_DIR=models/sentiment_models/
    MAX_LEN=100
    HEADERS = []
    DEBUG = True
    ```

    _Note:_ Update `TIKI_API_KEY` if Tiki API requires authentication.

2. **Vector Database:**
   Ensure the `vector_db/` directory contains:
    - `product_index.faiss`
    - `product_data.pkl`
    - `product_ids.pkl`
      These files are used for product recommendations.

## Running the Application

1. **Start the Flask server:**

    ```bash
    python main.py
    ```

    The server will run on `http://localhost:5000`.

2. **Access the application:**
   Open your browser and navigate to: [http://localhost:5000](http://localhost:5000).

## Core Components

### 1. API Endpoints

-   `/api/products`: Fetch product listings with pagination and keyword search.
-   `/api/product/<product_id>`: Retrieve details of a specific product.
-   `/api/reviews/<product_id>`: Fetch reviews for a product with sentiment analysis.
-   `/api/sentiment`: Perform sentiment analysis on custom text input.
-   `/api/search`: Search products by text query using vector similarity.
-   `/api/recommendations/<product_id>`: Get product recommendations based on a product ID using vector embeddings.

### 2. Services

-   **SentimentService:** Handles sentiment analysis using pre-trained ML models to classify reviews as Positive, Neutral, or Negative.
-   **TikiService:** Manages communication with Tiki's API to fetch products, reviews, and product details.

### 3. Models

-   **Sentiment Classification Models:** Pre-trained models for classifying review sentiments.
-   **Product Recommendation Models:** Uses SentenceTransformer (`all-MiniLM-L6-v2`) and FAISS for vector-based product recommendations.

## Development Features

-   **Logging:** Comprehensive logging to `logs/search.log` for search and recommendation activities, with rotation to manage file size.
-   **Error Handling:** Graceful error management with meaningful error messages in API responses.
-   **API Security:** Implements rate limiting and input validation for API endpoints.
-   **Static File Serving:** Efficiently serves CSS and JavaScript files from the `static/` directory.

## Troubleshooting

### Common Issues

1. **Model Loading Errors:**
    - **Issue:** "Failed to load sentiment models."
    - **Solution:** Verify the `MODEL_PATH` in `.env` and ensure models are placed in `models/sentiment_models/`.
2. **API Connection Issues:**
    - **Issue:** "Failed to fetch product details from Tiki API" in `logs/search.log`.
    - **Solution:**
        - Check `TIKI_API_URL` in `.env`.
        - Verify internet connection and Tiki API status.
        - Inspect `logs/search.log` for rate limit errors and adjust request frequency if needed.
3. **Recommendations Returning Empty Data:**
    - **Issue:** `/api/recommendations/<product_id>` returns `{"data": [], "status": "success"}`.
    - **Solution:** Check `logs/search.log` for:
        - `Tiki API response: ...` (ensure it returns valid product details).
        - `Combined text: ...` (ensure it's not empty).
        - If Tiki API fails, verify `product_id` or add retry logic in `TikiService`.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## License

This project is licensed under the MIT License.

## Support

For support, please open an issue on the [GitHub repository](https://github.com/nguyendevwk/tiki-sentiment-website).

## Acknowledgments

-   Tiki for providing the API.
-   Contributors to the Tiki Raw Sentiments Dataset.
-   The open-source machine learning community for tools and libraries.

For more information, contact Phạm Nguyễn via GitHub: [@nguyendevwk](https://github.com/nguyendevwk).
