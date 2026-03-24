class StrategyGenerator:
    def __init__(self, insights, target_id):
        self.insights = insights
        self.target_id = target_id

    def generate_strategy(self):
        strategy = "## 🚀 Growth Strategy\n\n"

        strategy += "### 🔥 Key Recommendations:\n"
        strategy += "- Focus on high-engagement content\n"
        strategy += "- Post consistently\n"
        strategy += "- Use trending topics\n"
        strategy += "- Create short-form videos\n\n"

        strategy += "### 📊 Competitor Insights:\n"

        for insight in self.insights:
            strategy += f"\n**Channel {insight['channel_id']}**\n"
            for video in insight['top_engagement_videos']:
                strategy += f"- {video['title']} (Engagement: {video['engagement_rate']:.2%})\n"

        return strategy