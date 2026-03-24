# simulator.py

import numpy as np
import pandas as pd

from xgboost import XGBRegressor
from prophet import Prophet


# ===============================
# 🔹 1. XGBOOST PREDICTION
# ===============================
def run_xgboost_prediction(data):
    """
    Predict next value using XGBoost
    data: list of views
    """

    if len(data) < 3:
        return None

    X = np.array([[i] for i in range(len(data))])
    y = np.array(data)

    model = XGBRegressor()
    model.fit(X, y)

    prediction = model.predict([[len(data)]])

    return float(prediction[0])


# ===============================
# 🔹 2. PROPHET FORECAST
# ===============================
def run_prophet_forecast(data):
    """
    Forecast next value using Prophet
    """

    if len(data) < 3:
        return None

    dates = pd.date_range(start="2023-01-01", periods=len(data))

    df = pd.DataFrame({
        "ds": dates,
        "y": data
    })

    model = Prophet()
    model.fit(df)

    future = model.make_future_dataframe(periods=1)
    forecast = model.predict(future)

    return float(forecast['yhat'].iloc[-1])


# ===============================
# 🔹 3. SIMULATE STRATEGY
# ===============================
def simulate_strategy(videos, strategy_type="increase_frequency"):
    """
    Simulate different strategies and predict impact

    strategy_type:
    - increase_frequency
    - improve_engagement
    - trend_focus
    """

    views = [v.get("views", 0) for v in videos]

    if not views:
        return None

    modified_views = views.copy()

    # 🔥 STRATEGY SIMULATIONS

    if strategy_type == "increase_frequency":
        # Assume slight growth boost
        modified_views = [v * 1.1 for v in views]

    elif strategy_type == "improve_engagement":
        # Higher engagement → better performance
        modified_views = [v * 1.2 for v in views]

    elif strategy_type == "trend_focus":
        # Trend-based content boost
        modified_views = [v * 1.3 for v in views]

    # Predict outcomes
    xgb_result = run_xgboost_prediction(modified_views)
    prophet_result = run_prophet_forecast(modified_views)

    return {
        "strategy": strategy_type,
        "xgboost_prediction": xgb_result,
        "prophet_prediction": prophet_result
    }


# ===============================
# 🔹 4. MULTI-STRATEGY COMPARISON
# ===============================
def compare_strategies(videos):
    """
    Compare multiple strategies and return best one
    """

    strategies = [
        "increase_frequency",
        "improve_engagement",
        "trend_focus"
    ]

    results = []

    for s in strategies:
        result = simulate_strategy(videos, s)
        if result:
            results.append(result)

    # Select best based on highest prediction
    best = max(results, key=lambda x: x["xgboost_prediction"])

    return {
        "all_results": results,
        "best_strategy": best
    }


# ===============================
# 🔹 5. MAIN SIMULATOR FUNCTION
# ===============================
def simulator_engine(channel_data):
    """
    Full simulation pipeline
    """

    videos = channel_data.get("videos", [])

    if not videos:
        return {"error": "No video data"}

    base_views = [v.get("views", 0) for v in videos]

    base_prediction = run_xgboost_prediction(base_views)

    comparison = compare_strategies(videos)

    return {
        "current_prediction": base_prediction,
        "strategy_simulation": comparison
    }


# ===============================  
# 🔹 SAMPLE RUN
# ===============================
if __name__ == "__main__":
    # Sample data
    sample_channel = {
        "videos": [
            {"title": "Video 1", "views": 100},
            {"title": "Video 2", "views": 120},
            {"title": "Video 3", "views": 150},
            {"title": "Video 4", "views": 170},
            {"title": "Video 5", "views": 200}
        ]
    }

    result = simulator_engine(sample_channel)
    
    print("=== SIMULATOR RESULTS ===")
    print(f"Current Prediction: {result['current_prediction']}")
    
    print("\nStrategy Simulations:")
    for strat in result['strategy_simulation']['all_results']:
        print(f"- {strat['strategy']}: XGBoost={strat['xgboost_prediction']:.2f}, Prophet={strat['prophet_prediction']:.2f}")
    
    best = result['strategy_simulation']['best_strategy']
    print(f"\nBest Strategy: {best['strategy']} (XGBoost: {best['xgboost_prediction']:.2f})")
