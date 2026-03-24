# models/topicmodel.py
import logging
import sys

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def safe_imports():
    try:
        from sentence_transformers import SentenceTransformer
        from bertopic import BERTopic
        from xgboost import XGBRegressor
        from prophet import Prophet
    except ImportError as exc:
        print(f"Warning: Some ML libraries not available: {exc}")
        # Provide dummy classes
        class DummySentenceTransformer:
            def __init__(self, model_name):
                self.model_name = model_name
            def encode(self, texts, **kwargs):
                return [[0.1] * 384 for _ in texts]  # Dummy 384-dim embeddings
        
        class DummyBERTopic:
            def __init__(self, **kwargs):
                self.texts = []
            def fit_transform(self, texts):
                self.texts = texts
                return [0] * len(texts), None
            def get_topic_info(self):
                return pd.DataFrame({"Topic": [-1], "Count": [len(self.texts)], "Name": ["General Content"]})
            def get_topic(self, topic_id):
                return [("keyword", 0.9)]
        
        class DummyXGBRegressor:
            def __init__(self, **kwargs):
                pass
            def fit(self, X, y):
                pass
            def predict(self, X):
                return [100.0] * len(X)
        
        class DummyProphet:
            def __init__(self):
                pass
            def fit(self, df):
                pass
            def make_future_dataframe(self, periods=1):
                last_date = pd.Timestamp("2023-01-05") + pd.Timedelta(days=periods)
                return pd.DataFrame({"ds": [last_date]})
            def predict(self, future):
                return pd.DataFrame({"yhat": [150.0]})
        
        return DummySentenceTransformer, DummyBERTopic, DummyXGBRegressor, DummyProphet
    return SentenceTransformer, BERTopic, XGBRegressor, Prophet


def find_competitors(main_emb, comp_emb_list, names):
    scores = []

    for i, emb in enumerate(comp_emb_list):
        if emb is None or main_emb is None:
            continue
        score = cosine_similarity(main_emb, emb).mean()
        scores.append((names[i] if i < len(names) else f"comp_{i}", float(score)))

    return sorted(scores, key=lambda x: x[1], reverse=True)


def generate_strategy(top_competitors, xgb_pred):
    strategy = []

    if top_competitors and top_competitors[0][1] > 0.7:
        strategy.append("Focus on similar content as top competitor")

    if xgb_pred > 180:
        strategy.append("High growth potential — increase posting frequency")
    else:
        strategy.append("Improve content quality and thumbnails")

    strategy.append("Post consistently and follow trends")

    return strategy


def main():
    SentenceTransformer, BERTopic, XGBRegressor, Prophet = safe_imports()

    main_channel = [
        "Learn AI in 10 minutes",
        "Python machine learning tutorial",
        "Deep learning basics",
    ]

    competitor_channels = [
        ["AI tutorial for beginners", "Machine learning crash course"],
        ["Travel vlog in Paris", "Best places to visit"],
    ]
    competitor_names = ["AI Channel", "Travel Channel"]

    logger.info("Loading embeddings and models. This may take some time...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    main_embeddings = model.encode(main_channel)
    competitor_embeddings = [model.encode(c) for c in competitor_channels]

    top_competitors = find_competitors(main_embeddings, competitor_embeddings, competitor_names)

    topic_model = BERTopic(verbose=False)
    topics, _ = topic_model.fit_transform(main_channel)
    topic_info = topic_model.get_topic_info()

    views_data = [100, 120, 150, 170, 200]
    X = np.array([[i] for i in range(len(views_data))])
    y = np.array(views_data)
    xgb_model = XGBRegressor(objective="reg:squarederror", random_state=0)
    xgb_model.fit(X, y)
    xgb_prediction = float(xgb_model.predict([[len(views_data)]])[0])

    dates = pd.date_range(start="2023-01-01", periods=len(views_data))
    df = pd.DataFrame({"ds": dates, "y": views_data})
    prophet_model = Prophet()
    prophet_model.fit(df)
    future = prophet_model.make_future_dataframe(periods=1)
    forecast = prophet_model.predict(future)
    prophet_prediction = float(forecast["yhat"].iloc[-1])

    strategy = generate_strategy(top_competitors, xgb_prediction)

    print("\n=== COMPETITORS ===")
    print(top_competitors)
    print("\n=== TOPICS ===")
    print(topic_info)

    print("\n=== PREDICTIONS ===")
    print("XGBoost:", xgb_prediction)
    print("Prophet:", prophet_prediction)

    print("\n=== STRATEGY ===")
    for s in strategy:
        print("-", s)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Error while running topicmodel pipeline")
        sys.exit(1)
