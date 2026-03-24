# pattern_engine.py
import numpy as np
import pandas as pd
from collections import Counter
# Prediction models
from competitor_spy.backend.simulator import run_xgboost_prediction, run_prophet_forecast
# ===============================
# 🔹 1. EXTRACT TIME FEATURES
# ===============================
def extract_time_features(videos):
    """
    Extract hour/day from upload time
    """
    hours = []
    days = []

    for v in videos:
        timestamp = v.get("published_at")

        if timestamp:
            dt = pd.to_datetime(timestamp)
            hours.append(dt.hour)
            days.append(dt.day_name())

    return hours, days


# ===============================
# 🔹 2. BEST POSTING TIME
# ===============================
def best_posting_time(videos):
    """
    Find best posting hour
    """
    hour_views = {}

    for v in videos:
        timestamp = v.get("published_at")
        views = v.get("views", 0)

        if timestamp:
            hour = pd.to_datetime(timestamp).hour
            hour_views.setdefault(hour, []).append(views)

    avg_hour_views = {
        h: np.mean(v) for h, v in hour_views.items()
    }

    if not avg_hour_views:
        return None

    best_hour = max(avg_hour_views, key=avg_hour_views.get)

    return best_hour


# ===============================
# 🔹 3. POSTING FREQUENCY
# ===============================
def posting_frequency(videos):
    """
    Calculate videos per week
    """
    dates = [
        pd.to_datetime(v.get("published_at"))
        for v in videos if v.get("published_at")
    ]

    if len(dates) < 2:
        return 0

    dates.sort()
    days_diff = (dates[-1] - dates[0]).days

    weeks = max(days_diff / 7, 1)

    return round(len(videos) / weeks, 2)


# ===============================
# 🔹 4. TREND ANALYSIS
# ===============================
def trend_analysis(videos):
    """
    Analyze view trend
    """
    views = [v.get("views", 0) for v in videos]

    if len(views) < 2:
        return "stable"

    trend = np.polyfit(range(len(views)), views, 1)[0]

    if trend > 0:
        return "increasing"
    elif trend < 0:
        return "decreasing"
    else:
        return "stable"


# ===============================
# 🔹 5. CONTENT TYPE PATTERN
# ===============================
def content_patterns(videos):
    """
    Detect common keywords in titles
    """
    words = []

    for v in videos:
        title = v.get("title", "").lower()
        words.extend(title.split())

    common_words = Counter(words).most_common(5)

    return [w[0] for w in common_words]


# ===============================
# 🔹 6. VIEW PREDICTION (XGBoost)
# ===============================
def predict_views(videos):
    """
    Predict future views using XGBoost
    """
    views = [v.get("views", 0) for v in videos]

    if len(views) < 3:
        return None

    return run_xgboost_prediction(views)


# ===============================
# 🔹 7. TIME-SERIES FORECAST (PROPHET)
# ===============================
def forecast_views(videos):
    """
    Forecast future trend using Prophet
    """
    views = [v.get("views", 0) for v in videos]

    if len(views) < 3:
        return None

    return run_prophet_forecast(views)


# ===============================
# 🔹 8. MAIN PATTERN ENGINE
# ===============================
def pattern_engine(channel_data):
    """
    Full pattern detection pipeline
    """

    videos = channel_data.get("videos", [])

    if not videos:
        return {"error": "No video data"}

    # Step 1: Time features
    hours, days = extract_time_features(videos)

    # Step 2: Best posting time
    best_time = best_posting_time(videos)

    # Step 3: Frequency
    freq = posting_frequency(videos)

    # Step 4: Trend
    trend = trend_analysis(videos)

    # Step 5: Content pattern
    patterns = content_patterns(videos)

    # Step 6: Predictions
    xgb_pred = predict_views(videos)
    prophet_pred = forecast_views(videos)

    return {
        "best_posting_hour": best_time,
        "posting_frequency_per_week": freq,
        "trend": trend,
        "top_keywords": patterns,
        "predictions": {
            "xgboost": xgb_pred,
            "prophet": prophet_pred
        }
    }


# ===============================
# 🔹 SAMPLE RUN
# ===============================
if __name__ == "__main__":
    # Sample data
    sample_channel = {
        "videos": [
            {"title": "Learn Python Basics", "views": 1500, "published_at": "2023-01-01 10:00:00"},
            {"title": "AI Tutorial for Beginners", "views": 2200, "published_at": "2023-01-03 14:00:00"},
            {"title": "Machine Learning Tips", "views": 1800, "published_at": "2023-01-05 16:00:00"},
            {"title": "Data Science Guide", "views": 2500, "published_at": "2023-01-07 12:00:00"},
            {"title": "Coding Challenges", "views": 1200, "published_at": "2023-01-09 18:00:00"}
        ]
    }

    result = pattern_engine(sample_channel)

    print("=== PATTERN ENGINE RESULTS ===")
    import pprint
    pprint.pprint(result)