// Global variables
let apiBaseUrl = "/api";
let currentPage = 1;
let currentKeyword = "";
let currentProductId = null;
let currentReviewPage = 1;
let reviewsData = {};
let productModal = null;
let sentimentChart = null;

document.addEventListener("DOMContentLoaded", function () {
    // Initialize Bootstrap Modal
    productModal = new bootstrap.Modal(document.getElementById("productModal"));

    // Load initial products
    loadProducts();

    // Event Listeners
    document
        .getElementById("searchButton")
        .addEventListener("click", function () {
            currentKeyword = document
                .getElementById("searchInput")
                .value.trim();
            currentPage = 1;
            loadProducts();
        });

    document
        .getElementById("searchInput")
        .addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                currentKeyword = document
                    .getElementById("searchInput")
                    .value.trim();
                currentPage = 1;
                loadProducts();
            }
        });

    document
        .getElementById("loadMoreReviews")
        .addEventListener("click", function () {
            currentReviewPage++;
            loadReviews(currentProductId, currentReviewPage, false);
        });
});
