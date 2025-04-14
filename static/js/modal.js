
// Function to open product modal
function openProductModal(productId) {
    currentProductId = productId;

    // Reset modal content
    document.getElementById("modalTitle").textContent =
        "Chi tiết sản phẩm";
    document
        .getElementById("modalLoading")
        .classList.remove("d-none");
    document
        .getElementById("productDetail")
        .classList.add("d-none");

    // Reset reviews data
    reviewsData = {};
    currentReviewPage = 1;

    // Show modal
    productModal.show();

    // Load product details
    loadProductDetails(productId);

    // Load reviews
    loadReviews(productId, 1, true);

    // Load recommendations
    loadRecommendations(productId);
}

// Function to load product details
function loadProductDetails(productId) {
    fetch(`${apiBaseUrl}/product/${productId}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                throw new Error(data.error);
            }

            renderProductDetails(data);
        })
        .catch((error) => {

            document
                .getElementById("modalLoading")
                .classList.add("d-none");
            document
                .getElementById("productDetail")
                .classList.remove("d-none");
            document.getElementById(
                "productDetail"
            ).innerHTML = `
                            <div class="alert alert-danger">
                                Không thể tải thông tin sản phẩm: ${error.message}
                            </div>
                        `;
        });
}

// Function to render product details
function renderProductDetails(product) {
    document
        .getElementById("modalLoading")
        .classList.add("d-none");
    document
        .getElementById("productDetail")
        .classList.remove("d-none");

    // Update modal title
    document.getElementById("modalTitle").textContent =
        product.name;

    // Update product details
    document.getElementById("modalProductImage").src =
        product.images[0]?.base_url || product.thumbnail_url;
    document.getElementById("modalProductName").textContent =
        product.name;
    document.getElementById("modalRating").innerHTML =
        createRatingStars(product.rating_average);
    document.getElementById("modalRatingValue").textContent =
        product.rating_average
            ? `${product.rating_average}/5`
            : "Chưa có đánh giá";
    document.getElementById("modalSoldCount").textContent =
        product.all_time_quantity_sold
            ? `Đã bán ${product.all_time_quantity_sold}`
            : "";
    document.getElementById("modalProductPrice").textContent =
        formatPrice(product.price);

    // Render description
    let description = product.description;
    if (!description) {
        description =
            product.short_description ||
            "Không có mô tả cho sản phẩm này.";
    }
    document.getElementById(
        "modalProductDescription"
    ).innerHTML = `
                    <div class="overflow-auto" style="max-height: 200px;">
                        ${description}
                    </div>
                `;
}
