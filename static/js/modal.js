function openProductModal(productId) {
    currentProductId = productId;
    document.getElementById("modalTitle").textContent = "Chi tiết sản phẩm";
    document.getElementById("modalLoading").classList.remove("d-none");
    document.getElementById("productDetail").classList.add("d-none");
    reviewsData = {};
    currentReviewPage = 1;
    productModal.show();
    loadProductDetails(productId);
    loadReviews(productId, 1, true);
    loadRecommendations(productId);
}

function loadProductDetails(productId) {
    fetch(`${apiBaseUrl}/product/${productId}`)
        .then((response) => response.json())
        .then((data) => {
            if (data.error) throw new Error(data.error);
            renderProductDetails(data);
        })
        .catch((error) => {
            document.getElementById("modalLoading").classList.add("d-none");
            document.getElementById("productDetail").classList.remove("d-none");
            document.getElementById("productDetail").innerHTML = `
                <div class="alert alert-danger">Không thể tải thông tin sản phẩm: ${error.message}</div>`;
        });
}

function renderProductDetails(product) {
    document.getElementById("modalLoading").classList.add("d-none");
    document.getElementById("productDetail").classList.remove("d-none");
    document.getElementById("modalTitle").textContent = product.name;
    document.getElementById("modalProductImage").src = product.images[0]?.base_url || product.thumbnail_url;
    document.getElementById("modalProductName").textContent = product.name;
    document.getElementById("modalRating").innerHTML = createRatingStars(product.rating_average);
    document.getElementById("modalRatingValue").textContent = product.rating_average ? `${product.rating_average}/5` : "Chưa có đánh giá";
    document.getElementById("modalSoldCount").textContent = product.all_time_quantity_sold ? `Đã bán ${product.all_time_quantity_sold}` : "";
    document.getElementById("modalProductPrice").textContent = formatPrice(product.price);
    let description = product.description || product.short_description || "Không có mô tả cho sản phẩm này.";
    document.getElementById("modalProductDescription").innerHTML = `<div class="overflow-auto" style="max-height: 200px;">${description}</div>`;
}