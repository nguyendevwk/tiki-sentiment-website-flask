function loadRecommendations(productId) {
    const recommendationsLoading = document.getElementById("recommendationsLoading");
    const recommendationsContainer = document.getElementById("recommendationsContainer");

    recommendationsLoading.classList.remove("d-none");
    recommendationsContainer.classList.add("d-none");
    recommendationsContainer.innerHTML = "";

    fetch(`${apiBaseUrl}/recommendations/${productId}`)
        .then((response) => response.json())
        .then((data) => {
            recommendationsLoading.classList.add("d-none");
            if (data.error) throw new Error(data.error);
            if (data.data && data.data.length > 0) {
                renderRecommendations(data.data);
            } else {
                recommendationsContainer.innerHTML = '<div class="text-center py-3">Không có gợi ý sản phẩm tương tự.</div>';
                recommendationsContainer.classList.remove("d-none");
            }
        })
        .catch((error) => {
            recommendationsLoading.classList.add("d-none");
            recommendationsContainer.classList.remove("d-none");
            recommendationsContainer.innerHTML = `<div class="alert alert-danger">Không thể tải gợi ý sản phẩm: ${error.message}</div>`;
        });
}

function renderRecommendations(products) {
    const recommendationsContainer = document.getElementById("recommendationsContainer");
    products.slice(0, 10).forEach((product) => {
        const card = document.createElement("div");
        card.classList.add("card");
        const priceStr = product.price ? formatPrice(product.price) : "Liên hệ";
        card.innerHTML = `
            <div class="product-image">
                <img src="${product.thumbnail_url}" alt="${product.name}" class="img-fluid">
            </div>
            <div class="card-body p-2">
                <h6 class="card-title product-title small">${product.name}</h6>
                <div class="product-price small">${priceStr}</div>
            </div>
        `;
        recommendationsContainer.appendChild(card);
        card.addEventListener("click", () => openProductModal(product.id));
    });
    recommendationsContainer.classList.remove("d-none");
}