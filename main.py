
import os
from backend.channel_analyzer import ChannelAnalyzer
from backend.competitor_discovery import CompetitorDiscovery
from backend.data_extractor import DataExtractor
from backend.pattern_recognition import PatternRecognitionEngine
from backend.strategy_generator import StrategyGenerator

try:
    from config import YOUTUBE_API_KEY
except ImportError:
    YOUTUBE_API_KEY = None

def main():
    """Main function to run the competitor analysis pipeline."""
    
    # 1. Check for API Key in config.py
    if not YOUTUBE_API_KEY or YOUTUBE_API_KEY == "PASTE_YOUR_API_KEY_HERE":
        print("="*50)
        print("ERROR: API Key not found or not set.")
        print("Please open the 'config.py' file and paste your YouTube API key.")
        print("="*50)
        return

    # 2. Get Target Channel ID from user
    target_channel_id = input("Enter the Target Channel ID: ")
    if not target_channel_id:
        print("Channel ID cannot be empty. Exiting.")
        return

    api_key = YOUTUBE_API_KEY
    
    # --- Start Analysis Pipeline ---
    try:
        print(f"\n--- Step 1: Analyzing Target Channel ({target_channel_id}) ---")
        analyzer = ChannelAnalyzer(target_channel_id, api_key=api_key)
        target_analysis = analyzer.analyze()
        if not target_analysis:
             print(f"Could not analyze channel {target_channel_id}. It may be invalid or have no videos.")
             return
        print(f"Target Average Views: {target_analysis['avg_views']:.0f}")
        print(f"Top Themes: {', '.join(target_analysis['top_themes'].keys())}\n")

        print("--- Step 2: Discovering Competitors ---")
        discovery = CompetitorDiscovery(target_channel_id, api_key=api_key)
        competitors = discovery.discover(max_competitors=3)
        if not competitors:
            print("Could not discover any competitors. The target channel might have insufficient metadata.")
            return
        print(f"Discovered {len(competitors)} competitors:")
        for comp in competitors:
            print(f"- {comp['title']} ({comp['channel_id']})")
        print()

        print("--- Step 3: Extracting Competitor Data ---")
        competitor_ids = [c['channel_id'] for c in competitors]
        extractor = DataExtractor(competitor_ids, api_key=api_key)
        competitor_data = extractor.extract()
        print(f"Extracted data for {len(competitor_data)} competitors.\n")

        print("--- Step 4: Recognizing Patterns ---")
        pattern_engine = PatternRecognitionEngine(competitor_data)
        insights = pattern_engine.recognize_patterns()
        print("Identified high-performing themes and anomalies across competitors.\n")

        print("--- Step 5: Generating Strategy ---")
        strategy_gen = StrategyGenerator(insights, target_channel_id)
        strategy = strategy_gen.generate_strategy()
        
        # --- Assemble and Save HTML Report ---
        html_report = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Spyra Report</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 20px auto; padding: 0 20px; }
                h1, h2, h3, h4 { color: #2c3e50; }
                h1 { text-align: center; }
                .section { border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 20px; }
                .competitor { border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; }
                .competitor img { max-width: 100px; float: left; margin-right: 15px; border-radius: 5px; }
                .competitor-info { overflow: hidden; }
                strong { color: #2980b9; }
            </style>
        </head>
        <body>
            <h1>🕵️ Spyra Report</h1>
        """

        # Target Channel Section
        html_report += f"""
            <div class="section">
                <h2>Target Channel: {target_channel_id}</h2>
                <p><strong>Average Views:</strong> {target_analysis['avg_views']:,.0f}</p>
                <p><strong>Top Themes:</strong> {', '.join(target_analysis['top_themes'].keys())}</p>
            </div>
        """

        # Competitors Section
        html_report += "<div class=\"section\"><h2>Discovered Competitors</h2>"
        for comp in competitors:
            html_report += f"""
                <div class="competitor">
                    <img src="{comp['thumbnail']}" alt="Thumbnail for {comp['title']}">
                    <div class="competitor-info">
                        <h4>{comp['title']}</h4>
                        <p><strong>Channel ID:</strong> {comp['channel_id']}</p>
                        <p>{comp['description']}</p>
                    </div>
                </div>
            """
        html_report += "</div>"

        # Strategy Section
        html_report += f"""
            <div class="section">
                <h2>Growth Strategy</h2>
                {strategy}
            </div>
        </body>
        </html>
        """

        report_filename = "report.html"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(html_report)
            
        print("="*50)
        print("ANALYSIS COMPLETE")
        print(f"Your HTML report has been saved to: {report_filename}")
        print("="*50)

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please check your API key and the Channel ID and try again.")


if __name__ == "__main__":
    main()
