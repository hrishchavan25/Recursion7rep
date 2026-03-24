import re
import collections
import pandas as pd

class PatternRecognitionEngine:
    def __init__(self, data):
        self.data = data
        self.stopwords = {
            'the', 'and', 'how', 'to', 'for', 'in', 'on', 'with', 'a', 'is', 'it', 'of', 'that', 'this', 'you', 'your',
            'i', 'me', 'my', 'we', 'us', 'our', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'at', 'by', 'from', 'up', 'down', 'out',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'vlog', 'video', 'youtube'
        }

    def _extract_keywords(self, text):
        words = re.findall(r'\w+', text.lower())
        return [w for w in words if w not in self.stopwords and len(w) > 2]

    def _get_intent(self, titles):
        intents = {
            "Educational/How-to": ["how", "tutorial", "guide", "learn", "explained", "basics", "masterclass"],
            "Reviews/Comparisons": ["review", "vs", "versus", "comparison", "unboxing", "worth", "best", "top"],
            "News/Updates": ["news", "update", "new", "released", "happened", "leaks", "rumors"],
            "Vlog/Storytelling": ["vlog", "day", "life", "story", "went", "travel", "journey", "meet"]
        }
        scores = collections.Counter()
        for title in titles:
            title_lower = title.lower()
            for intent, keywords in intents.items():
                if any(k in title_lower for k in keywords):
                    scores[intent] += 1
        
        return scores.most_common(1)[0][0] if scores else "General Entertainment"

    def _get_title_style(self, titles):
        styles = collections.Counter()
        for title in titles:
            if title.isupper():
                styles["High Intensity (All Caps)"] += 1
            elif "!" in title:
                styles["Clicky (Exclamatory)"] += 1
            elif len(title.split()) < 5:
                styles["Minimalist"] += 1
            else:
                styles["Descriptive"] += 1
        return styles.most_common(1)[0][0] if styles else "Standard"

    def _analyze_upload_timing(self, videos):
        """Analyze the best upload times based on engagement density"""
        hour_engagement = collections.defaultdict(list)
        for v in videos:
            if 'published_at' in v:
                try:
                    # Parse ISO format timestamp
                    dt = pd.to_datetime(v['published_at'])
                    hour = dt.hour
                    hour_engagement[hour].append(v['engagement_rate'])
                except Exception:
                    continue
        
        if not hour_engagement:
            return None
            
        hour_stats = {}
        for hour, rates in hour_engagement.items():
            hour_stats[hour] = sum(rates) / len(rates)
            
        best_hour = max(hour_stats, key=hour_stats.get)
        avg_rate = sum(hour_stats.values()) / len(hour_stats)
        boost = ((hour_stats[best_hour] - avg_rate) / (avg_rate + 0.001)) * 100
        
        return {
            "best_hour": best_hour,
            "projected_boost": max(5.0, min(boost, 35.0)), # Realistic range
            "hour_map": hour_stats
        }

    def recognize_patterns(self):
        insights = {}
        all_videos = []

        for item in self.data:
            cid = item['channel_id']
            if cid not in insights:
                insights[cid] = {
                    "channel_id": cid,
                    "videos": [],
                    "total_views": 0,
                    "total_engagement": 0,
                    "titles": [],
                    "descriptions": []
                }

            engagement_count = item.get('likes', 0) + item.get('comments', 0)
            engagement_rate = engagement_count / (item.get('views', 0) + 1)
            
            video_data = {
                "video_id": item.get('video_id'),
                "title": item['title'],
                "description": item.get('description', ''),
                "views": item.get('views', 0),
                "engagement_rate": engagement_rate,
                "keywords": self._extract_keywords(item['title']),
                "published_at": item.get('published_at')
            }
            
            insights[cid]["videos"].append(video_data)
            insights[cid]["titles"].append(item['title'])
            insights[cid]["descriptions"].append(item.get('description', ''))
            insights[cid]["total_views"] += item.get('views', 0)
            insights[cid]["total_engagement"] += engagement_count
            all_videos.append(video_data)

        result = []
        for cid, val in insights.items():
            # Identify high performing themes for this channel
            all_keywords = []
            for v in val["videos"]:
                all_keywords.extend(v["keywords"])
            
            top_themes = collections.Counter(all_keywords).most_common(5)
            
            # Find viral anomalies
            channel_avg_engagement = val["total_engagement"] / (val["total_views"] + 1)
            anomalies = [v for v in val["videos"] if v['engagement_rate'] > (channel_avg_engagement * 2)]

            # Refined category
            from backend.ytclassify import classify_video
            refined_cat = classify_video(" ".join(val["titles"]), " ".join(val["descriptions"]))

            # Timing analysis
            timing = self._analyze_upload_timing(val["videos"])

            # Personalization Metrics
            primary_intent = self._get_intent(val["titles"])
            dominant_style = self._get_title_style(val["titles"])
            keyword_consistency = (top_themes[0][1] / len(val["videos"])) if top_themes and val["videos"] else 0
            
            # Sentiment Proxy (Likes per 1000 views)
            sentiment_score = (val["total_engagement"] / (val["total_views"] + 1)) * 1000

            result.append({
                "channel_id": cid,
                "high_performing_themes": dict(top_themes),
                "top_engagement_videos": sorted(val["videos"], key=lambda x: x["engagement_rate"], reverse=True)[:3],
                "anomaly_count": len(anomalies),
                "avg_channel_engagement": channel_avg_engagement,
                "refined_category": refined_cat,
                "timing_insights": timing,
                "personalization": {
                    "intent": primary_intent,
                    "style": dominant_style,
                    "consistency_score": keyword_consistency,
                    "niche_focus": top_themes[0][0] if top_themes else "General",
                    "sentiment_proxy": sentiment_score
                }
            })

        return result