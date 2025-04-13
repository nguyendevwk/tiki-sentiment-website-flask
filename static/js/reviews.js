// Function to load reviews
function loadReviews(productId, page, resetList) {
    document
        .getElementById("reviewsLoading")
        .classList.remove("d-none");

    if (resetList) {
        document.getElementById("reviewsList").innerHTML = "";
        document
            .getElementById("loadMoreReviews")
            .classList.add("d-none");
    }

    fetch(
        `${apiBaseUrl}/reviews/${productId}?page=${page}&limit=10`
    )
        .then((response) => response.json())
        .then((data) => {
            document
                .getElementById("reviewsLoading")
                .classList.add("d-none");

            if (data.error) {
                throw new Error(data.error);
            }
            console.log("Render Reviews loadReviews", data);
            renderReviews(data.reviews);

            // Update review count
            if (data.paging) {
                document.getElementById(
                    "reviewsCount"
                ).textContent = `${data.paging.total} đánh giá`;
            }

            // Update sentiment summary
            console.log(
                "Update sentiment summary",
                data.reviews.data
            );
            updateSentimentSummary(data.reviews);
        })
        .catch((error) => {
            document
                .getElementById("reviewsLoading")
                .classList.add("d-none");
            document.getElementById(
                "reviewsList"
            ).innerHTML += `
                            <div class="alert alert-danger">
                                Không thể tải đánh giá: ${error.message}
                            </div>
                        `;
        });
}

// Function to render reviews
function renderReviews(data) {
    const reviewsListElement =
        document.getElementById("reviewsList");
    const loadMoreButton =
        document.getElementById("loadMoreReviews");

    if (!data.data || data.data.length === 0) {
        if (currentReviewPage === 1) {
            reviewsListElement.innerHTML =
                '<div class="text-center py-4">Chưa có đánh giá nào cho sản phẩm này.</div>';
        }
        loadMoreButton.classList.add("d-none");
        return;
    }
    console.log("Render Reviews renderReviews ===", data.data);
    // Add reviews to the list
    data.data.forEach((review) => {
        // Save review data for sentiment analysis
        reviewsData[review.id] = review;
        console.log("Reviews renderReviews", review);
        console.log(review.id, reviewsData[review.id]);

        const reviewCard = document.createElement("div");
        reviewCard.classList.add("card", "mb-3");

        // Determine sentiment class
        let sentimentClass = "sentiment-neutral";
        let sentimentIcon = "fa-meh";
        let sentimentText = "Trung lập";
        console.log("review", review);
        console.log("sentiment_a", review.sentiment_analysis);
        if (review.sentiment_analysis) {
            const sentiment =
                review.sentiment_analysis.overall_sentiment;
            console.log("sentiment", sentiment);
            if (sentiment === "Tích cực") {
                sentimentClass = "sentiment-positive";
                sentimentIcon = "fa-smile-beam";
                sentimentText = "Tích cực";
            } else if (sentiment === "Tiêu cực") {
                sentimentClass = "sentiment-negative";
                sentimentIcon = "fa-frown";
                sentimentText = "Tiêu cực";
            }
        }

        // Format date
        const reviewDate = new Date(review.created_at);
        const formattedDate =
            reviewDate.toLocaleDateString("vi-VN");

        // Create model badges
        let modelBadges = "";
        if (
            review.sentiment_analysis &&
            review.sentiment_analysis.models
        ) {
            const models = review.sentiment_analysis.models;

            for (const [model, result] of Object.entries(
                models
            )) {
                let modelName = "";
                switch (model) {
                    case "naive_bayes":
                        modelName = "Naive Bayes";
                        break;
                    case "svm":
                        modelName = "Linear SVM";
                        break;
                    case "svc":
                        modelName = "SVC";
                        break;
                    case "deep_learning":
                        modelName = "Deep Learning";
                        break;
                    default:
                        modelName = model;
                }

                const confidence = result.confidence
                    ? `${result.confidence.toFixed(1)}%`
                    : "";
                modelBadges += `
                                <span class="badge bg-light text-dark model-badge">
                                    ${modelName}: ${result.label} ${confidence ? `(${confidence})` : ""
                    }
                                </span>
                            `;
            }
        }

        reviewCard.innerHTML = `
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <div>
                                    <strong>${review.created_by ||
            "Khách hàng ẩn danh"
            }</strong>
                                    <div class="text-muted small">${formattedDate}</div>
                                </div>
                                <span class="badge ${sentimentClass}">
                                    <i class="fas ${sentimentIcon} me-1"></i> ${sentimentText}
                                </span>
                            </div>
                            <div class="mb-2">
                                ${createRatingStars(review.rating)}
                            </div>
                            <p class="card-text">${review.content}</p>
                            ${modelBadges
                ? `<div class="d-flex flex-wrap mt-2">${modelBadges}</div>`
                : ""
            }
                        </div>
                    `;

        reviewsListElement.appendChild(reviewCard);
    });

    // Show/hide load more button
    if (
        data.paging &&
        currentReviewPage < data.paging.last_page
    ) {
        loadMoreButton.classList.remove("d-none");
    } else {
        loadMoreButton.classList.add("d-none");
    }
}

// Function to update sentiment summary
function updateSentimentSummary(reviews) {
    console.log("updateSentimentSummary", reviews.data);
    if (!reviews.data || reviews.data.length === 0) {
        // Reset UI if there are no reviews
        document.getElementById(
            "positiveProgress"
        ).style.width = "0%";
        document.getElementById("neutralProgress").style.width =
            "0%";
        document.getElementById(
            "negativeProgress"
        ).style.width = "0%";
        document.getElementById(
            "positivePercentage"
        ).textContent = "0%";
        document.getElementById(
            "neutralPercentage"
        ).textContent = "0%";
        document.getElementById(
            "negativePercentage"
        ).textContent = "0%";
        updateSentimentChart(0, 0, 0);
        return;
    }

    // Calculate average percentages from sentiment_percentages
    let positiveSum = 0;
    let neutralSum = 0;
    let negativeSum = 0;
    let validReviewCount = 0;
    // console.log("Reviews", reviews);
    reviews.data.forEach((review) => {
        console.log("Reviews ", review);
        if (
            review.sentiment_analysis &&
            review.sentiment_analysis.sentiment_percentages
        ) {
            console.log(
                "sentiment_percentages",
                review.sentiment_analysis.sentiment_percentages
            );
            const percentages =
                review.sentiment_analysis.sentiment_percentages;
            positiveSum +=
                percentages.positive !== undefined
                    ? percentages.positive
                    : 0;
            neutralSum +=
                percentages.neutral !== undefined
                    ? percentages.neutral
                    : 0;
            negativeSum +=
                percentages.negative !== undefined
                    ? percentages.negative
                    : 0;
            validReviewCount++;
        }
    });

    if (validReviewCount === 0) {
        // Reset if no valid reviews
        document.getElementById(
            "positiveProgress"
        ).style.width = "0%";
        document.getElementById("neutralProgress").style.width =
            "0%";
        document.getElementById(
            "negativeProgress"
        ).style.width = "0%";
        document.getElementById(
            "positivePercentage"
        ).textContent = "0%";
        document.getElementById(
            "neutralPercentage"
        ).textContent = "0%";
        document.getElementById(
            "negativePercentage"
        ).textContent = "0%";
        updateSentimentChart(0, 0, 0);
        return;
    }

    // Calculate average percentages
    const positivePercentage = positiveSum / validReviewCount;
    const neutralPercentage = neutralSum / validReviewCount;
    const negativePercentage = negativeSum / validReviewCount;
    console.log(
        "Sentiment Percentages",
        positivePercentage,
        neutralPercentage,
        negativePercentage
    );

    // Update UI
    document.getElementById(
        "positiveProgress"
    ).style.width = `${positivePercentage}%`;
    document.getElementById(
        "neutralProgress"
    ).style.width = `${neutralPercentage}%`;
    document.getElementById(
        "negativeProgress"
    ).style.width = `${negativePercentage}%`;

    document.getElementById(
        "positivePercentage"
    ).textContent = `${positivePercentage.toFixed(1)}%`;
    document.getElementById(
        "neutralPercentage"
    ).textContent = `${neutralPercentage.toFixed(1)}%`;
    document.getElementById(
        "negativePercentage"
    ).textContent = `${negativePercentage.toFixed(1)}%`;

    // Update chart
    updateSentimentChart(
        positivePercentage,
        neutralPercentage,
        negativePercentage
    );
}

// Function to update sentiment chart
function updateSentimentChart(positive, neutral, negative) {
    const ctx = document
        .getElementById("sentimentPieChart")
        .getContext("2d");

    // Destroy previous chart if exists
    if (sentimentChart) {
        sentimentChart.destroy();
    }

    // Create new chart
    sentimentChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: ["Tích cực", "Trung lập", "Tiêu cực"],
            datasets: [
                {
                    data: [positive, neutral, negative],
                    backgroundColor: [
                        "rgba(0, 171, 86, 0.8)",
                        "rgba(255, 196, 0, 0.8)",
                        "rgba(255, 66, 78, 0.8)",
                    ],
                    borderColor: [
                        "rgba(0, 171, 86, 1)",
                        "rgba(255, 196, 0, 1)",
                        "rgba(255, 66, 78, 1)",
                    ],
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 12,
                    },
                },
            },
        },
    });
}
