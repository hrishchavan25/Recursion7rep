import os
from dotenv import load_dotenv

load_dotenv()

class StrategyGenerator:
    def __init__(self, insights: list, target_channel_id: str):
        self.insights = insights
        self.target_channel_id = target_channel_id
        
        # AI libraries are currently unavailable in this environment
        self.model = None

    def generate_strategy(self):
        """Produce actionable recommendations based on analysis."""
        return self._fallback_strategy()

    def _fallback_strategy(self):
        """Generate a basic strategy using rule-based logic in HTML format."""
        strategy = f"<h3>Data-Backed Growth Strategy for {self.target_channel_id}</h3>"
        
        # Aggregate top themes across all competitors
        all_themes = {}
        for insight in self.insights:
            for theme, count in insight['high_performing_themes'].items():
                all_themes[theme] = all_themes.get(theme, 0) + count
        
        sorted_themes = sorted(all_themes.items(), key=lambda x: x[1], reverse=True)[:5]
        
        strategy += "<h4>1. High Potential Content Themes</h4>"
        strategy += "<p>Based on competitor analysis, these themes are currently generating the most views and engagement:</p><ul>"
        for theme, _ in sorted_themes:
            strategy += f"<li><strong>{theme.capitalize()}</strong>: This theme is consistently appearing in high-performing competitor videos.</li>"
        strategy += "</ul>"
            
        strategy += "<h4>2. Engagement Strategy</h4>"
        strategy += "<p>To improve engagement rates, focus on content that mimics the following successful patterns:</p><ul>"
        
        total_anomalies = sum([i['anomaly_count'] for i in self.insights])
        if total_anomalies > 0:
            strategy += f"<li><strong>Topic Deep Dives</strong>: We identified {total_anomalies} videos with unusually high engagement. These topics should be prioritized.</li>"
        strategy += "<li><strong>Call to Action Optimization</strong>: Competitors with high engagement often use specific prompts for likes and comments.</li></ul>"
        
        strategy += "<h4>3. Performance Benchmarking</h4>"
        avg_views_competitors = sum([i['avg_views'] for i in self.insights]) / len(self.insights) if self.insights else 0
        strategy += f"<p>Target for next video: <strong>{avg_views_competitors:,.0f} views</strong>. This is the current average performance of your top competitors.</p>"
        
        return strategy


# ===============================
# 🔹 SAMPLE RUN
# ===============================
if __name__ == "__main__":
    # Sample insights data
    sample_insights = [
        {
            "high_performing_themes": {"ai": 5, "tutorial": 3, "python": 4},
            "anomaly_count": 2,
            "avg_views": 15000
        },
        {
            "high_performing_themes": {"machine learning": 4, "data science": 6, "tips": 2},
            "anomaly_count": 1,
            "avg_views": 12000
        },
        {
            "high_performing_themes": {"coding": 3, "beginners": 5, "projects": 4},
            "anomaly_count": 3,
            "avg_views": 18000
        }
    ]

    target_channel = "MyTechChannel"

    generator = StrategyGenerator(sample_insights, target_channel)
    strategy_html = generator.generate_strategy()

    print("=== STRATEGY GENERATOR RESULTS ===")
    print(f"Target Channel: {target_channel}")
    print("\nGenerated Strategy (HTML):")
    print(strategy_html)