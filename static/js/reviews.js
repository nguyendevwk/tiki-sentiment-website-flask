function loadReviews(productId, page, resetList) {
    document.getElementById("reviewsLoading").classList.remove("d-none");
    if (resetList) {
        document.getElementById("reviewsList").innerHTML = "";
        document.getElementById("loadMoreReviews").classList.add("d-none");
    }

    fetch(`${apiBaseUrl}/reviews/${productId}?page=${page}&limit=5`)
        .then((response) => response.json())
        .then((data) => {
            console.log("Reviews data", data);
            document.getElementById("reviewsLoading").classList.add("d-none");
            if (data.error) throw new Error(data.error);
            renderReviews(data.reviews);
            if (data.paging) document.getElementById("reviewsCount").textContent = `${data.paging.total} đánh giá`;
            updateSentimentSummary(data);
        })
        .catch((error) => {
            document.getElementById("reviewsLoading").classList.add("d-none");
            document.getElementById("reviewsList").innerHTML += `
                <div class="alert alert-danger">Không thể tải đánh giá: ${error.message}</div>`;
        });
}

function renderReviews(reviews) {
    const reviewsListElement = document.getElementById("reviewsList");
    const loadMoreButton = document.getElementById("loadMoreReviews");

    if (!reviews || reviews.length === 0) {
        if (currentReviewPage === 1) {
            reviewsListElement.innerHTML = '<div class="text-center py-4">Chưa có đánh giá nào cho sản phẩm này.</div>';
        }
        loadMoreButton.classList.add("d-none");
        return;
    }

    reviews.forEach((review) => {
        reviewsData[review.id] = review;
        const reviewCard = document.createElement("div");
        reviewCard.classList.add("card", "mb-3");

        let sentimentClass = "sentiment-neutral";
        let sentimentIcon = "fa-meh";
        let sentimentText = "Trung lập";

        if (review.sentiment_analysis) {
            const sentiment = review.sentiment_analysis.overall_sentiment;
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

        const reviewDate = new Date(review.created_at * 1000);
        const formattedDate = reviewDate.toLocaleDateString("vi-VN");

        let modelBadges = "";
        if (review.sentiment_analysis && review.sentiment_analysis.models) {
            for (const [model, result] of Object.entries(review.sentiment_analysis.models)) {
                let modelName = {
                    naive_bayes: "Naive Bayes",
                    svm: "Linear SVM",
                    svc: "SVC",
                    deep_learning: "Deep Learning",
                }[model] || model;
                const confidence = result.confidence ? `${result.confidence.toFixed(1)}%` : "";
                modelBadges += `<span class="badge bg-light text-dark model-badge">${modelName}: ${result.label} ${confidence ? `(${confidence})` : ""}</span>`;
            }
        }

        reviewCard.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div>
                        <strong>${review.created_by?.full_name || "Khách hàng ẩn danh"}</strong>
                        <div class="text-muted small">${formattedDate}</div>
                    </div>
                    <span class="badge ${sentimentClass}"><i class="fas ${sentimentIcon} me-1"></i> ${sentimentText}</span>
                </div>
                <div class="mb-2">${createRatingStars(review.rating)}</div>
                <p class="card-text">${review.content}</p>
                ${modelBadges ? `<div class="d-flex flex-wrap mt-2">${modelBadges}</div>` : ""}
            </div>
        `;
        reviewsListElement.appendChild(reviewCard);
    });

    if (data.paging && currentReviewPage < data.paging.last_page) {
        loadMoreButton.classList.remove("d-none");
    } else {
        loadMoreButton.classList.add("d-none");
    }
}

function updateSentimentSummary(data) {
    const summary = data.sentiment_summary || { positive: 0, neutral: 0, negative: 0 };
    const positivePercentage = summary.positive;
    const neutralPercentage = summary.neutral;
    const negativePercentage = summary.negative;

    document.getElementById("positiveProgress").style.width = `${positivePercentage}%`;
    document.getElementById("neutralProgress").style.width = `${neutralPercentage}%`;
    document.getElementById("negativeProgress").style.width = `${negativePercentage}%`;
    document.getElementById("positivePercentage").textContent = `${positivePercentage.toFixed(1)}%`;
    document.getElementById("neutralPercentage").textContent = `${neutralPercentage.toFixed(1)}%`;
    document.getElementById("negativePercentage").textContent = `${negativePercentage.toFixed(1)}%`;

    updateSentimentChart(positivePercentage, neutralPercentage, negativePercentage);
}

function updateSentimentChart(positive, neutral, negative) {
    const ctx = document.getElementById("sentimentPieChart").getContext("2d");
    if (sentimentChart) sentimentChart.destroy();

    sentimentChart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: ["Tích cực", "Trung lập", "Tiêu cực"],
            datasets: [{
                data: [positive, neutral, negative],
                backgroundColor: ["rgba(0, 171, 86, 0.8)", "rgba(255, 196, 0, 0.8)", "rgba(255, 66, 78, 0.8)"],
                borderColor: ["rgba(0, 171, 86, 1)", "rgba(255, 196, 0, 1)", "rgba(255, 66, 78, 1)"],
                borderWidth: 1,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { boxWidth: 12 },
                },
            },
        },
    });
}