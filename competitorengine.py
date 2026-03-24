# competitor_engine.py

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Local implementations for embeddings and metrics
def get_embeddings(texts):
    """Generate dummy embeddings for text similarity"""
    return [[0.1] * 384 for _ in texts]

def calculate_engagement(views, likes, comments):
    """Calculate engagement rate from metrics"""
    if views == 0:
        return 0
    return (likes + comments * 2) / views * 100


# ===============================
# 🔹 1. METRICS-BASED FILTERING
# ===============================
def filter_by_metrics(competitors, min_subscribers=1000, min_avg_views=100):
    """
    Filter competitors based on minimum performance metrics
    """
    filtered = []
    for comp in competitors:
        subscribers = comp.get('subscribers', 0)
        avg_views = comp.get('avg_views', 0)
        
        if subscribers >= min_subscribers and avg_views >= min_avg_views:
            filtered.append(comp)
    
    return filtered


# ===============================
# 🔹 2. METRICS SCORING FUNCTION
# ===============================
def compute_metrics_similarity(main_metrics, competitor_metrics, weights=None):
    """
    Compute similarity score based on key performance metrics
    """
    if weights is None:
        weights = {
            'subscribers': 0.30,
            'avg_views': 0.25,
            'avg_likes': 0.15,
            'avg_comments': 0.15,
            'engagement_rate_pct': 0.15
        }
    
    metrics_keys = ['subscribers', 'avg_views', 'avg_likes', 'avg_comments', 'engagement_rate_pct']
    main_vals = np.array([main_metrics.get(k, 0) for k in metrics_keys], dtype=float)
    comp_vals = np.array([competitor_metrics.get(k, 0) for k in metrics_keys], dtype=float)
    
    # Log transform for skewed metrics
    main_vals = np.log1p(main_vals)
    comp_vals = np.log1p(comp_vals)
    
    # Normalize
    main_max = np.max(main_vals)
    comp_max = np.max(comp_vals)
    
    if main_max > 0:
        main_vals = main_vals / main_max
    if comp_max > 0:
        comp_vals = comp_vals / comp_max
    
    # Apply weights
    weight_arr = np.array([weights.get(k, 1.0) for k in metrics_keys])
    weighted_main = main_vals * weight_arr
    weighted_comp = comp_vals * weight_arr
    
    # Cosine similarity
    similarity = np.dot(weighted_main, weighted_comp) / (np.linalg.norm(weighted_main) * np.linalg.norm(weighted_comp) + 1e-8)
    
    return float(similarity)


# ===============================
# 🔹 3. PREPARE TEXT DATA
# ===============================
def extract_titles(videos):
    """
    Extract titles from video list
    """
    return [v.get("title", "") for v in videos]


# ===============================
# 🔹 4. REFINED COMPETITOR SCORING
# ===============================
def score_competitors(main_channel, competitor_channels, use_metrics=True, weight_metrics=0.8):
    """
    Score competitors based on metrics similarity and content similarity
    Combines: subscribers, views, engagement rate, and content topic alignment
    """
    results = []
    
    # Extract main channel metrics
    main_metrics = {
        'subscribers': main_channel.get('subscribers', 0),
        'avg_views': main_channel.get('avg_views', 0),
        'avg_likes': main_channel.get('avg_likes', 0),
        'avg_comments': main_channel.get('avg_comments', 0),
        'engagement_rate_pct': main_channel.get('engagement_rate_pct', 0)
    }
    
    # Get embeddings for content similarity (if available)
    main_titles = extract_titles(main_channel.get("videos", []))
    main_embeddings = get_embeddings(main_titles) if main_titles else None
    
    for comp in competitor_channels:
        # Metrics-based similarity
        comp_metrics = {
            'subscribers': comp.get('subscribers', 0),
            'avg_views': comp.get('avg_views', 0),
            'avg_likes': comp.get('avg_likes', 0),
            'avg_comments': comp.get('avg_comments', 0),
            'engagement_rate_pct': comp.get('engagement_rate_pct', 0)
        }
        
        metrics_score = compute_metrics_similarity(main_metrics, comp_metrics)
        
        # Content-based similarity (secondary)
        content_score = 0.5  # default
        comp_titles = extract_titles(comp.get("videos", []))
        if main_embeddings and comp_titles:
            comp_embeddings = get_embeddings(comp_titles)
            similarity_matrix = cosine_similarity(main_embeddings, comp_embeddings)
            content_score = float(similarity_matrix.mean()) if len(similarity_matrix) > 0 else 0.5
        
        # Combine scores: prioritize metrics (80%) over content (20%)
        final_score = (metrics_score * weight_metrics) + (content_score * (1 - weight_metrics))
        
        results.append({
            "channel_id": comp.get('channel_id'),
            "channel_name": comp.get("channel_name") or comp.get("title"),
            "subscribers": comp_metrics['subscribers'],
            "avg_views": comp_metrics['avg_views'],
            "avg_engagement": comp_metrics['engagement_rate_pct'],
            "metrics_similarity": round(metrics_score, 3),
            "content_similarity": round(content_score, 3),
            "final_score": round(final_score, 3),
            "videos": comp.get("videos", [])
        })
    
    return sorted(results, key=lambda x: x["final_score"], reverse=True)


# ===============================
# 🔹 5. PERFORMANCE ANALYSIS
# ===============================
def analyze_performance(videos):
    """
    Analyze performance metrics of a channel
    """
    views = [v.get("views", 0) for v in videos]
    likes = [v.get("likes", 0) for v in videos]
    comments = [v.get("comments", 0) for v in videos]

    engagement_scores = [
        calculate_engagement(v, l, c)
        for v, l, c in zip(views, likes, comments)
    ]

    return {
        "avg_views": int(np.mean(views)) if views else 0,
        "avg_engagement": round(np.mean(engagement_scores), 3) if engagement_scores else 0
    }


# ===============================
# 🔹 6. COMPETITOR INSIGHTS
# ===============================
def competitor_insights(main_channel, top_competitors):
    """
    Compare main channel with competitors based on metrics
    """
    main_perf = analyze_performance(main_channel.get("videos", []))
    main_subs = main_channel.get('subscribers', 0)
    main_avg_views = main_channel.get('avg_views', 0)

    insights = []

    for comp in top_competitors:
        comp_perf = analyze_performance(comp.get("videos", []))
        
        # Calculate deltas
        subs_diff = comp['subscribers'] - main_subs
        views_diff = comp['avg_views'] - main_avg_views
        engagement_diff = comp['avg_engagement'] - main_perf["avg_engagement"]

        insight = {
            "channel_id": comp.get('channel_id'),
            "channel_name": comp["channel_name"],
            "metrics_score": comp["metrics_similarity"],
            "content_alignment": comp["content_similarity"],
            "performance_comparison": {
                "subscriber_diff": int(subs_diff),
                "avg_views_diff": int(views_diff),
                "engagement_diff": round(engagement_diff, 3),
                "is_stronger": (subs_diff > 0 and views_diff > 0)
            }
        }

        insights.append(insight)

    return insights


# ===============================
# 🔹 7. SELECT TOP COMPETITORS
# ===============================
def get_top_competitors(scored_list, top_n=3):
    """
    Return top N competitors by final score
    """
    return scored_list[:top_n]


# ===============================
# 🔹 8. MAIN ENGINE FUNCTION
# ===============================
def competitor_engine(main_channel, competitor_channels, top_n=3, min_subscribers=1000, min_avg_views=100):
    """
    Full metrics-driven competitor analysis pipeline
    
    Args:
        main_channel: dict with channel metrics and videos
        competitor_channels: list of competitor dicts
        top_n: number of top competitors to return
        min_subscribers: minimum subscriber filter
        min_avg_views: minimum average views filter
    
    Returns:
        dict with scored competitors and insights
    """
    
    # Step 1: Filter competitors by metrics thresholds
    filtered = filter_by_metrics(
        competitor_channels, 
        min_subscribers=min_subscribers, 
        min_avg_views=min_avg_views
    )
    
    if not filtered:
        filtered = competitor_channels  # fallback if no competitors meet threshold
    
    # Step 2: Score competitors based on metrics similarity
    scored = score_competitors(main_channel, filtered, use_metrics=True, weight_metrics=0.8)

    # Step 3: Select top competitors
    top = get_top_competitors(scored, top_n=top_n)

    # Step 4: Generate insights
    insights = competitor_insights(main_channel, top)

    return {
        "total_competitors_analyzed": len(filtered),
        "top_competitors": [
            {
                "channel_id": c.get("channel_id"),
                "name": c["channel_name"],
                "subscribers": int(c['subscribers']),
                "avg_views_per_video": int(c['avg_views']),
                "engagement_rate": round(c['avg_engagement'], 2),
                "metrics_score": c["metrics_similarity"],
                "content_alignment": c["content_similarity"],
                "final_similarity": c["final_score"]
            }
            for c in top
        ],
        "competitor_insights": insights
    }


# ===============================
# 🔹 SAMPLE RUN
# ===============================
if __name__ == "__main__":
    # Sample data with metrics
    main_channel = {
        "channel_name": "MyTechChannel",
        "subscribers": 15000,
        "avg_views": 1850,
        "avg_likes": 150,
        "avg_comments": 32.5,
        "engagement_rate_pct": 9.7,
        "videos": [
            {"title": "Learn Python Basics", "views": 1500, "likes": 120, "comments": 25},
            {"title": "AI Tutorial", "views": 2200, "likes": 180, "comments": 40}
        ]
    }

    competitor_channels = [
        {
            "channel_id": "comp1",
            "channel_name": "TechGuru",
            "subscribers": 12000,
            "avg_views": 1800,
            "avg_likes": 140,
            "avg_comments": 30,
            "engagement_rate_pct": 9.4,
            "videos": [
                {"title": "Python for Beginners", "views": 2000, "likes": 150, "comments": 30},
                {"title": "AI Explained", "views": 1600, "likes": 130, "comments": 30}
            ]
        },
        {
            "channel_id": "comp2",
            "channel_name": "CodeMaster",
            "subscribers": 8000,
            "avg_views": 950,
            "avg_likes": 85,
            "avg_comments": 18,
            "engagement_rate_pct": 10.8,
            "videos": [
                {"title": "Web Development 101", "views": 900, "likes": 80, "comments": 15},
                {"title": "JavaScript Tips", "views": 1000, "likes": 90, "comments": 21}
            ]
        },
        {
            "channel_id": "comp3",
            "channel_name": "DataScience Pro",
            "subscribers": 22000,
            "avg_views": 3200,
            "avg_likes": 280,
            "avg_comments": 65,
            "engagement_rate_pct": 10.8,
            "videos": [
                {"title": "Data Science with Python", "views": 3500, "likes": 300, "comments": 75},
                {"title": "ML Pipeline Tutorial", "views": 2900, "likes": 260, "comments": 55}
            ]
        }
    ]

    result = competitor_engine(main_channel, competitor_channels, top_n=3)

    print("=== REFINED COMPETITOR ENGINE RESULTS ===\n")
    import json
    print(json.dumps(result, indent=2))