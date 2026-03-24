# analyzer.py
import numpy as np
from collections import Counter

# Try to import internal modules, fallback to dummies if not available
try:
    from backend.utils.preprocess import clean_text
except ImportError:
    def clean_text(texts):
        return [t.lower() for t in texts]

try:
    from backend.utils.metrics import calculate_engagement
except ImportError:
    def calculate_engagement(views, likes, comments):
        if views == 0:
            return 0
        return (likes + comments * 2) / views * 100

try:
    from backend.core.embeddings import get_embeddings
except ImportError:
    def get_embeddings(texts):
        # Dummy embeddings
        return [[0.1] * 10 for _ in texts]

try:
    from backend.models.sentiment import get_sentiment
except ImportError:
    def get_sentiment(texts):
        # Dummy sentiments
        return ["positive"] * len(texts)

try:
    from backend.models.topic_model import extract_topics
except ImportError:
    def extract_topics(texts):
        # Dummy topics
        return ["AI", "Tutorial", "Tech"]

# ===============================
# 🔹 1. BASIC STATS
# ===============================
def basic_stats(videos):
    """
    Calculate basic statistics
    """
    views = [v.get("views", 0) for v in videos]
    likes = [v.get("likes", 0) for v in videos]

    return {
        "total_videos": len(videos),
        "avg_views": int(np.mean(views)) if views else 0,
        "avg_likes": int(np.mean(likes)) if likes else 0,
        "max_views": int(np.max(views)) if views else 0
    }


# ===============================
# 🔹 2. ENGAGEMENT ANALYSIS
# ===============================
def engagement_analysis(videos):
    """
    Calculate engagement rates
    """
    engagement_scores = []

    for v in videos:
        views = v.get("views", 0)
        likes = v.get("likes", 0)
        comments = v.get("comments", 0)

        engagement = calculate_engagement(views, likes, comments)
        engagement_scores.append(engagement)

    return {
        "avg_engagement": round(np.mean(engagement_scores), 2) if engagement_scores else 0
    }


# ===============================
# 🔹 3. CONTENT ANALYSIS
# ===============================
def content_analysis(videos):
    """
    Analyze titles and content
    """
    titles = [v.get("title", "") for v in videos]
    cleaned_titles = clean_text(titles)

    # Embeddings
    embeddings = get_embeddings(cleaned_titles)

    # Topics
    topics = extract_topics(cleaned_titles)

    return {
        "titles": cleaned_titles,
        "embeddings": embeddings,
        "topics": topics
    }


# ===============================
# 🔹 4. SENTIMENT ANALYSIS
# ===============================
def sentiment_analysis(videos):
    """
    Analyze sentiment of titles/descriptions
    """
    texts = [v.get("title", "") for v in videos]

    sentiments = get_sentiment(texts)

    sentiment_counts = Counter(sentiments)

    return dict(sentiment_counts)


# ===============================
# 🔹 5. TOP PERFORMING CONTENT
# ===============================
def top_content(videos):
    """
    Find top performing videos
    """
    sorted_videos = sorted(videos, key=lambda x: x.get("views", 0), reverse=True)

    top = sorted_videos[:3]

    return [
        {
            "title": v.get("title"),
            "views": v.get("views")
        }
        for v in top
    ]


# ===============================
# 🔹 6. MAIN ANALYZER FUNCTION
# ===============================
def analyze_channel(channel_data):
    """
    Main function to analyze a channel

    channel_data = {
        "channel_name": "",
        "videos": [ {title, views, likes, comments}, ... ]
    }
    """

    videos = channel_data.get("videos", [])

    if not videos:
        return {"error": "No video data available"}

    # Step 1: Stats
    stats = basic_stats(videos)

    # Step 2: Engagement
    engagement = engagement_analysis(videos)

    # Step 3: Content
    content = content_analysis(videos)

    # Step 4: Sentiment
    sentiment = sentiment_analysis(videos)

    # Step 5: Top content
    top_videos = top_content(videos)

    return {
        "channel_name": channel_data.get("channel_name", "Unknown"),
        "stats": stats,
        "engagement": engagement,
        "content": {
            "topics": content["topics"]
        },
        "sentiment": sentiment,
        "top_videos": top_videos
    }


# ===============================
# 🔹 SAMPLE RUN
# ===============================
if __name__ == "__main__":
    # Sample data
    sample_channel = {
        "channel_name": "Tech Tutorials",
        "videos": [
            {"title": "Learn Python Basics", "views": 1500, "likes": 120, "comments": 25},
            {"title": "AI for Beginners", "views": 2200, "likes": 180, "comments": 40},
            {"title": "Machine Learning Tips", "views": 1800, "likes": 150, "comments": 30},
            {"title": "Data Science Guide", "views": 2500, "likes": 200, "comments": 50},
            {"title": "Coding Challenges", "views": 1200, "likes": 100, "comments": 20}
        ]
    }

    result = analyze_channel(sample_channel)

    print("=== ANALYZER RESULTS ===")
    print(f"Channel: {result['channel_name']}")

    print("\nStats:")
    for k, v in result['stats'].items():
        print(f"- {k}: {v}")

    print(f"\nEngagement: {result['engagement']['avg_engagement']}%")

    print(f"\nTopics: {', '.join(result['content']['topics'])}")

    print(f"\nSentiment: {result['sentiment']}")

    print("\nTop Videos:")
    for v in result['top_videos']:
        print(f"- {v['title']}: {v['views']} views")