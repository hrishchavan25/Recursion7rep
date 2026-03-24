class PatternRecognitionEngine:
    def __init__(self, data):
        self.data = data

    def recognize_patterns(self):
        insights = {}

        for item in self.data:
            cid = item['channel_id']

            if cid not in insights:
                insights[cid] = {
                    "channel_id": cid,
                    "videos": []
                }

            engagement = (item['likes'] + item['comments']) / (item['views'] + 1)

            insights[cid]["videos"].append({
                "title": item['title'],
                "engagement_rate": engagement
            })

        result = []

        for cid, val in insights.items():
            top_videos = sorted(
                val["videos"],
                key=lambda x: x["engagement_rate"],
                reverse=True
            )[:3]

            result.append({
                "channel_id": cid,
                "high_performing_themes": {"Short videos": 5, "Trending topics": 3},
                "top_engagement_videos": top_videos,
                "anomaly_count": len([v for v in top_videos if v['engagement_rate'] > 0.05]) # Simple anomaly threshold
            })

        return result