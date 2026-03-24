import re
from collections import defaultdict

# Expanded and more granular genre keywords mapping for YouTube
GENRE_KEYWORDS = {
    "Finance & Investing": ["finance", "money", "investing", "stock", "market", "trading", "crypto", "bitcoin", "bank", "credit", "budget", "saving", "tax", "wealth", "portfolio", "dividend", "passive income", "real estate", "equity", "nifty", "sensex"],
    "Tech & Gadgets": ["tech", "technology", "gadget", "smartphone", "iphone", "android", "laptop", "review", "unboxing", "tutorial", "coding", "programming", "software", "ai", "hardware", "processor", "camera", "console", "specs"],
    "Gaming": ["game", "gaming", "play", "gamer", "console", "pc", "xbox", "playstation", "nintendo", "esports", "walkthrough", "gameplay", "stream", "minecraft", "roblox", "pubg", "fortnite", "valorant", "bgmi", "free fire"],
    "Education & Science": ["education", "learn", "study", "tutorial", "lesson", "course", "university", "school", "exam", "teach", "how to", "explained", "science", "history", "facts", "space", "physics", "biology", "upsc", "jee", "neet"],
    "Food & Cooking": ["cook", "recipe", "kitchen", "food", "chef", "bake", "meal", "ingredient", "tasty", "delicious", "street food", "restaurant", "eating", "mukbang", "lunch", "dinner", "breakfast", "spicy"],
    "Vlog & Lifestyle": ["vlog", "day in the life", "lifestyle", "routine", "daily", "story", "personal", "home", "family", "parenting", "morning routine", "night routine", "my house", "meet my", "shopping"],
    "Comedy & Entertainment": ["funny", "comedy", "sketch", "parody", "joke", "prank", "reaction", "meme", "roast", "stand up", "humor", "hilarious", "challenge", "entertainment", "bollywood", "movies", "actor"],
    "Music & Art": ["music", "song", "album", "artist", "band", "concert", "guitar", "piano", "cover", "remix", "lyrics", "official video", "instrumental", "singer", "dance", "drawing", "painting", "art"],
    "Health & Fitness": ["gym", "fitness", "workout", "health", "exercise", "weight loss", "muscle", "bodybuilding", "yoga", "diet", "nutrition", "training", "athlete", "running", "meditation"],
    "Business & Entrepreneurship": ["business", "startup", "entrepreneur", "marketing", "sales", "growth", "strategy", "hustle", "company", "ceo", "founder", "ecommerce", "dropshipping", "agency"],
    "Travel & Adventure": ["travel", "trip", "vacation", "tour", "destination", "hotel", "flight", "adventure", "explore", "backpack", "wanderlust", "tourism", "itinerary", "mountains", "beach", "road trip"],
    "News & Current Affairs": ["news", "breaking", "headline", "report", "journalism", "politics", "world", "update", "live", "media", "current affairs", "debate", "government", "election", "scam", "exposed"]
}

def classify_video(title: str, description: str = "", tags: list = None) -> str:
    """
    Classify a YouTube video into a genre using high-precision keyword scoring.
    Weights Term Frequency (TF) to prioritize specific over generic matches.
    """
    text = f"{title} {description}".lower()
    if tags:
        if isinstance(tags, list):
            text += " " + " ".join(tags).lower()
        elif isinstance(tags, str):
            text += " " + tags.lower()
    
    # Use weights: Title keywords count for 3x, Description for 1x
    title_text = title.lower()
    desc_text = description.lower()
    
    scores = defaultdict(float)
    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            # Title matches are weighted higher for better accuracy
            if kw in title_text:
                scores[genre] += 3.0
            # Description matches
            if kw in desc_text:
                scores[genre] += 1.0
            # Tag matches
            if tags and any(kw in str(t).lower() for t in (tags if isinstance(tags, list) else [tags])):
                scores[genre] += 1.5
    
    if not scores:
        return "Entertainment"
    
    # Select the genre with the highest weighted score
    best_genre = max(scores, key=scores.get)
    return best_genre if scores[best_genre] > 0 else "Entertainment"

def categorize_youtubers(videos_data):
    """
    Given a list of video dictionaries, return a mapping of channel_id to its dominant genre.
    """
    channel_genres = defaultdict(lambda: defaultdict(int))
    
    for video in videos_data:
        genre = classify_video(video.get("title", ""), video.get("description", ""), video.get("tags"))
        channel_genres[video.get("channel_id", "unknown")][genre] += 1
    
    channel_dominant_genre = {}
    for channel, genre_counts in channel_genres.items():
        main_genre = max(genre_counts, key=genre_counts.get)
        channel_dominant_genre[channel] = main_genre
    
    return channel_dominant_genre

# Example usage:
if __name__ == "__main__":
    sample_videos = [
        {"channel_id": "UC123", "title": "Easy Pasta Recipe", "description": "Learn to cook delicious pasta at home", "tags": ["cooking", "recipe"]},
        {"channel_id": "UC456", "title": "Gaming Live Stream", "description": "Playing Fortnite with friends", "tags": ["gaming", "fortnite"]},
        {"channel_id": "UC123", "title": "Best Chocolate Cake", "description": "Step by step chocolate cake recipe", "tags": ["baking", "dessert"]},
    ]
    
    categories = categorize_youtubers(sample_videos)
    print("Youtubers categorized by genre:")
    for genre, channels in categories.items():
        print(f"{genre}: {channels}")
