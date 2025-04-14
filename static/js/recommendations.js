// // // Function to load recommendations
// // function loadRecommendations(productId) {
// //     const recommendationsLoading = document.getElementById("recommendationsLoading");
// //     const recommendationsContainer = document.getElementById("recommendationsContainer");

// //     // Show loading indicator and hide previous results
// //     recommendationsLoading.classList.remove("d-none");
// //     recommendationsContainer.classList.add("d-none");
// //     recommendationsContainer.innerHTML = "";

// //     // Make API call to get recommendations
// //     fetch(`${apiBaseUrl}/api/recommendations/${productId}`)
// //         .then((response) => response.json())
// //         .then((data) => {
// //             // Hide loading indicator
// //             console.log("loadRecommendations", data);
// //             recommendationsLoading.classList.add("d-none");

// //             // Check for errors
// //             if (data.status === "error" || data.error) {
// //                 throw new Error(data.error || "Error loading recommendations");
// //             }

// //             // Display recommendations or no-data message
// //             if (data.data && data.data.length > 0) {
// //                 renderRecommendations(data.data);
// //             } else {
// //                 recommendationsContainer.innerHTML = '<p class="text-center">Không có gợi ý sản phẩm tương tự.</p>';
// //                 recommendationsContainer.classList.remove("d-none");
// //             }
// //         })
// //         .catch((error) => {
// //             // Handle errors
// //             recommendationsLoading.classList.add("d-none");
// //             recommendationsContainer.classList.remove("d-none");
// //             recommendationsContainer.innerHTML = `
// //                 <div class="alert alert-danger" role="alert">
// //                     Không thể tải gợi ý sản phẩm: ${error.message}
// //                 </div>
// //             `;
// //         });
// // }

// // // Function to render recommendations
// // function renderRecommendations(products) {
// //     const recommendationsContainer = document.getElementById("recommendationsContainer");

// //     // Create a row to hold products
// //     const row = document.createElement("div");
// //     row.classList.add("row", "recommendation-row");
// //     recommendationsContainer.appendChild(row);
// //     console.log("renderRecommendations", products);
// //     // Render each product
// //     products.forEach((product) => {
// //         // Create column for the product card
// //         const col = document.createElement("div");
// //         col.classList.add("col-md-4", "col-sm-6", "mb-3");

// //         // Create product card
// //         const card = document.createElement("div");
// //         card.classList.add("card", "product-card", "h-100");

// //         // Format price and discount information
// //         const priceStr = product.price ? formatPrice(product.price) : "Liên hệ";
// //         const discountStr = product.discount_rate && product.discount_rate > 0 ?
// //             `<span class="discount-badge">${product.discount_rate}%</span>` : '';

// //         // Generate product image HTML
// //         const imageUrl = product.image_url || 'assets/img/placeholder.jpg';

// //         // Populate card HTML
// //         card.innerHTML = `
// //             <div class="card-img-top position-relative">
// //                 <img src="${imageUrl}" alt="${product.name}" class="img-fluid product-thumbnail">
// //                 ${discountStr}
// //             </div>
// //             <div class="card-body d-flex flex-column">
// //                 <h6 class="card-title product-name text-truncate">${product.name}</h6>
// //                 <div class="mt-auto">
// //                     <div class="product-price">
// //                         <span class="current-price">${priceStr}</span>
// //                         ${product.original_price && product.original_price > product.price ?
// //                 `<span class="original-price">${formatPrice(product.original_price)}</span>` : ''}
// //                     </div>
// //                     ${product.rating_average ?
// //                 `<div class="small mt-1">${createRatingStars(product.rating_average)}
// //                        <span class="text-muted">(${product.review_count || 0})</span></div>` : ''}
// //                 </div>
// //             </div>
// //         `;

// //         // Add click event to open product modal
// //         card.addEventListener("click", function () {
// //             openProductModal(product.product_id);
// //         });

// //         // Add card to column and column to row
// //         col.appendChild(card);
// //         row.appendChild(col);
// //     });

// //     // Show recommendations container
// //     recommendationsContainer.classList.remove("d-none");
// // }

// // Function to load recommendations
// function loadRecommendations(productId) {
//     const recommendationsLoading = document.getElementById("recommendationsLoading");
//     const recommendationsContainer = document.getElementById("recommendationsContainer");

//     // Show loading indicator and hide previous results
//     recommendationsLoading.classList.remove("d-none");
//     recommendationsContainer.classList.add("d-none");
//     recommendationsContainer.innerHTML = "";

//     // Ensure apiBaseUrl is defined
//     if (!apiBaseUrl) {
//         console.error("apiBaseUrl is not defined");
//         recommendationsLoading.classList.add("d-none");
//         recommendationsContainer.classList.remove("d-none");
//         recommendationsContainer.innerHTML = `
//             <div class="alert alert-danger" role="alert">
//                 Lỗi cấu hình: apiBaseUrl chưa được định nghĩa
//             </div>
//         `;
//         return;
//     }

//     // Make API call to get recommendations
//     fetch(`${apiBaseUrl}/recommendations/${productId}`)
//         .then((response) => {
//             // Check if response is OK
//             if (!response.ok) {
//                 throw new Error(`HTTP error! status: ${response.status}`);
//             }
//             // Check content type
//             const contentType = response.headers.get("content-type");
//             if (!contentType || !contentType.includes("application/json")) {
//                 throw new Error("Received non-JSON response from server");
//             }
//             return response.json();
//         })
//         .then((data) => {
//             recommendationsLoading.classList.add("d-none");

//             // Check for errors in response
//             if (data.status === "error" || data.error) {
//                 throw new Error(data.error || "Error loading recommendations");
//             }

//             // Display recommendations or no-data message
//             if (data.data && data.data.length > 0) {
//                 renderRecommendations(data.data);
//             } else {
//                 recommendationsContainer.innerHTML = '<p class="text-center">Không có gợi ý sản phẩm tương tự.</p>';
//                 recommendationsContainer.classList.remove("d-none");
//             }
//         })
//         .catch((error) => {
//             console.error("Error loading recommendations:", error);
//             recommendationsLoading.classList.add("d-none");
//             recommendationsContainer.classList.remove("d-none");
//             recommendationsContainer.innerHTML = `
//                 <div class="alert alert-danger" role="alert">
//                     Không thể tải gợi ý sản phẩm: ${error.message}
//                 </div>
//             `;
//         });
// }

// // Function to render recommendations
// function renderRecommendations(products) {
//     const recommendationsContainer = document.getElementById("recommendationsContainer");
//     console.log("Rendering recommendations:", products);

//     // Create a row to hold products
//     const row = document.createElement("div");
//     row.classList.add("row", "recommendation-row");
//     recommendationsContainer.appendChild(row);

//     // Render each product
//     products.forEach((product) => {
//         // Validate product data
//         if (!product.product_id || !product.name) {
//             console.warn("Invalid product data:", product);
//             return;
//         }

//         const col = document.createElement("div");
//         col.classList.add("col-md-4", "col-sm-6", "mb-3");

//         const card = document.createElement("div");
//         card.classList.add("card", "product-card", "h-100");

//         const priceStr = product.price ? formatPrice(product.price) : "Liên hệ";
//         const discountStr = product.discount_rate && product.discount_rate > 0 ?
//             `<span class="discount-badge">${product.discount_rate}%</span>` : '';
//         const imageUrl = product.image_url || 'assets/img/placeholder.jpg';

//         card.innerHTML = `
//             <div class="card-img-top position-relative">
//                 <img src="${imageUrl}" alt="${product.name}" class="img-fluid product-thumbnail">
//                 ${discountStr}
//             </div>
//             <div class="card-body d-flex flex-column">
//                 <h6 class="card-title product-name text-truncate">${product.name}</h6>
//                 <div class="mt-auto">
//                     <div class="product-price">
//                         <span class="current-price">${priceStr}</span>
//                         ${product.original_price && product.original_price > product.price ?
//                 `<span class="original-price">${formatPrice(product.original_price)}</span>` : ''}
//                     </div>
//                     ${product.rating_average ?
//                 `<div class="small mt-1">${createRatingStars(product.rating_average)}
//                        <span class="text-muted">(${product.review_count || 0})</span></div>` : ''}
//                 </div>
//             </div>
//         `;

//         card.addEventListener("click", function () {
//             openProductModal(product.product_id);
//         });

//         col.appendChild(card);
//         row.appendChild(col);
//     });

//     recommendationsContainer.classList.remove("d-none");
// }


function loadRecommendations(productId) {
    const recommendationsLoading = document.getElementById("recommendationsLoading");
    const recommendationsContainer = document.getElementById("recommendationsContainer");

    // Show loading indicator and hide previous results
    recommendationsLoading.classList.remove("d-none");
    recommendationsContainer.classList.add("d-none");
    recommendationsContainer.innerHTML = "";

    // Ensure apiBaseUrl is defined
    if (!apiBaseUrl) {
        console.error("apiBaseUrl is not defined");
        recommendationsLoading.classList.add("d-none");
        recommendationsContainer.classList.remove("d-none");
        recommendationsContainer.innerHTML = `
            <div class="alert alert-danger" role="alert">
                Lỗi cấu hình: apiBaseUrl chưa được định nghĩa
            </div>
        `;
        return;
    }

    // Make API call to get recommendations
    fetch(`${apiBaseUrl}/recommendations/${productId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error("Received non-JSON response from server");
            }
            return response.json();
        })
        .then((data) => {
            recommendationsLoading.classList.add("d-none");

            if (data.status === "error" || data.error) {
                throw new Error(data.error || "Error loading recommendations");
            }

            if (data.data && data.data.length > 0) {
                renderRecommendations(data.data);
            } else {
                recommendationsContainer.innerHTML = `
                    <p class="text-center text-muted">
                        Không có gợi ý sản phẩm tương tự.
                    </p>`;
                recommendationsContainer.classList.remove("d-none");
            }
        })
        .catch((error) => {
            console.error("Error loading recommendations:", error);
            recommendationsLoading.classList.add("d-none");
            recommendationsContainer.classList.remove("d-none");
            recommendationsContainer.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    Không thể tải gợi ý sản phẩm: ${error.message}
                </div>
            `;
        });
}

// Function to render recommendations
function renderRecommendations(products) {
    const recommendationsContainer = document.getElementById("recommendationsContainer");
    console.log("Rendering recommendations:", products);

    // Limit to 6 recommendations for better UI
    const maxRecommendations = 6;
    const limitedProducts = products.slice(0, maxRecommendations);

    // Create scroll container
    const scrollContainer = document.createElement("div");
    scrollContainer.classList.add("recommendation-scroll");

    // Render each product
    limitedProducts.forEach((product) => {
        // Validate product data
        if (!product.product_id || !product.name) {
            console.warn("Invalid product data:", product);
            return;
        }

        const card = document.createElement("div");
        card.classList.add("card", "recommendation-card", "h-100");

        const priceStr = product.price ? formatPrice(product.price) : "Liên hệ";
        const discountStr = product.discount_rate && product.discount_rate > 0 ?
            `<span class="discount-badge">${product.discount_rate}%</span>` : '';
        const imageUrl = product.image_url || 'assets/img/placeholder.jpg';

        card.innerHTML = `
            <div class="card-img-top position-relative">
                <img src="${imageUrl}" alt="${product.name}" class="img-fluid product-thumbnail">
                ${discountStr}
            </div>
            <div class="card-body d-flex flex-column">
                <h6 class="card-title product-name text-truncate">${product.name}</h6>
                <div class="mt-auto">
                    <div class="product-price">
                        <span class="current-price">${priceStr}</span>
                        ${product.original_price && product.original_price > product.price ?
                `<span class="original-price">${formatPrice(product.original_price)}</span>` : ''}
                    </div>
                    ${product.rating_average ?
                `<div class="small mt-1">${createRatingStars(product.rating_average)}
                       <span class="text-muted">(${product.review_count || 0})</span></div>` : ''}
                </div>
            </div>
        `;

        card.addEventListener("click", function () {
            openProductModal(product.product_id);
        });

        scrollContainer.appendChild(card);
    });

    recommendationsContainer.appendChild(scrollContainer);
    recommendationsContainer.classList.remove("d-none");
}