function loadProducts() {
    const loadingElement = document.getElementById("loading");
    const productsListElement = document.getElementById("productsList");
    const paginationElement = document.getElementById("pagination");

    loadingElement.style.display = "flex";
    productsListElement.innerHTML = "";
    paginationElement.innerHTML = "";

    const sectionTitle = document.getElementById("productSectionTitle");
    sectionTitle.textContent = currentKeyword ? `Kết quả tìm kiếm cho: "${currentKeyword}"` : "Sản phẩm nổi bật";

    let url = `${apiBaseUrl}/products?page=${currentPage}&limit=12`;
    if (currentKeyword) url += `&keyword=${encodeURIComponent(currentKeyword)}`;

    fetch(url)
        .then((response) => response.json())
        .then((data) => {
            loadingElement.style.display = "none";
            if (data.data && data.data.length > 0) {
                renderProducts(data.data);
                renderPagination(data.paging);
            } else {
                productsListElement.innerHTML = '<div class="col-12 text-center py-5">Không tìm thấy sản phẩm nào.</div>';
            }
        })
        .catch((error) => {
            loadingElement.style.display = "none";
            productsListElement.innerHTML = `<div class="col-12 text-center py-5">Đã xảy ra lỗi: ${error.message}</div>`;
        });
}

function renderProducts(products) {
    const productsListElement = document.getElementById("productsList");
    products.forEach((product) => {
        const productCard = document.createElement("div");
        productCard.classList.add("col");
        const priceStr = product.price ? formatPrice(product.price) : "Liên hệ";
        const ratingStars = createRatingStars(product.rating_average || 0);

        productCard.innerHTML = `
            <div class="card h-100 product-card" data-product-id="${product.id}">
                <div class="product-image">
                    <img src="${product.thumbnail_url}" alt="${product.name}" class="img-fluid">
                </div>
                <div class="card-body">
                    <h6 class="card-title product-title">${product.name}</h6>
                    <div class="d-flex align-items-center mb-2">
                        <div class="rating-stars me-2">${ratingStars}</div>
                        <small class="text-muted">${product.review_count || 0} đánh giá</small>
                    </div>
                    <div class="product-price">${priceStr}</div>
                </div>
            </div>
        `;
        productsListElement.appendChild(productCard);
        productCard.querySelector(".product-card").addEventListener("click", function () {
            openProductModal(this.getAttribute("data-product-id"));
        });
    });
}

function renderPagination(paging) {
    if (!paging || paging.last_page <= 1) return;
    const paginationElement = document.getElementById("pagination");
    const totalPages = paging.last_page;

    const prevLi = document.createElement("li");
    prevLi.classList.add("page-item");
    if (currentPage === 1) prevLi.classList.add("disabled");
    prevLi.innerHTML = `<a class="page-link" href="#" aria-label="Previous"><span aria-hidden="true">«</span></a>`;
    paginationElement.appendChild(prevLi);
    prevLi.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentPage > 1) {
            currentPage--;
            loadProducts();
        }
    });

    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);
    if (endPage - startPage < 4) startPage = Math.max(1, endPage - 4);

    for (let i = startPage; i <= endPage; i++) {
        const pageLi = document.createElement("li");
        pageLi.classList.add("page-item");
        if (i === currentPage) pageLi.classList.add("active");
        pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        paginationElement.appendChild(pageLi);
        pageLi.addEventListener("click", (e) => {
            e.preventDefault();
            currentPage = i;
            loadProducts();
        });
    }

    const nextLi = document.createElement("li");
    nextLi.classList.add("page-item");
    if (currentPage === totalPages) nextLi.classList.add("disabled");
    nextLi.innerHTML = `<a class="page-link" href="#" aria-label="Next"><span aria-hidden="true">»</span></a>`;
    paginationElement.appendChild(nextLi);
    nextLi.addEventListener("click", (e) => {
        e.preventDefault();
        if (currentPage < totalPages) {
            currentPage++;
            loadProducts();
        }
    });
}