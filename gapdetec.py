import re
from typing import List, Dict, Any

class GapDetector:
    """Detects gaps in user strategy and YouTube video content."""
    
    def __init__(self):
        self.strategy_gaps = []
        self.video_gaps = []
    
    def detect_strategy_gaps(self, strategy: str) -> List[Dict[str, Any]]:
        """
        Detect gaps in user strategy.
        
        Args:
            strategy: Strategy text to analyze
            
        Returns:
            List of detected gaps with descriptions
        """
        gaps = []
        
        # Check for missing objectives
        if not re.search(r'(goal|objective|target)', strategy, re.IGNORECASE):
            gaps.append({"type": "Missing Objectives", "severity": "high"})
        
        # Check for missing timeline
        if not re.search(r'(timeline|deadline|schedule|duration)', strategy, re.IGNORECASE):
            gaps.append({"type": "Missing Timeline", "severity": "medium"})
        
        # Check for missing resources
        if not re.search(r'(budget|resource|tool|personnel)', strategy, re.IGNORECASE):
            gaps.append({"type": "Missing Resources", "severity": "high"})
        
        # Check for missing metrics
        if not re.search(r'(metric|kpi|measure|track)', strategy, re.IGNORECASE):
            gaps.append({"type": "Missing Metrics", "severity": "medium"})
        
        self.strategy_gaps = gaps
        return gaps
    
    def detect_video_gaps(self, video_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Detect gaps in YouTube video content.
        
        Args:
            video_data: List of video info (title, description, tags)
            
        Returns:
            List of detected gaps
        """
        gaps = []
        
        for video in video_data:
            title = video.get('title', '')
            description = video.get('description', '')
            
            # Check for missing description
            if len(description) < 50:
                gaps.append({"video": title, "issue": "Insufficient Description"})
            
            # Check for missing keywords
            if len(title.split()) < 3:
                gaps.append({"video": title, "issue": "Title Too Short"})
            
            # Check for missing call-to-action
            if not re.search(r'(subscribe|like|comment|click)', description, re.IGNORECASE):
                gaps.append({"video": title, "issue": "Missing Call-to-Action"})
        
        self.video_gaps = gaps
        return gaps
    
    def generate_report(self) -> Dict[str, List]:
        """Generate a comprehensive gap report."""
        return {
            "strategy_gaps": self.strategy_gaps,
            "video_gaps": self.video_gaps
        }


# Example usage
if __name__ == "__main__":
    detector = GapDetector()
    
    # Test strategy analysis
    strategy = "Launch campaign with budget allocation and monthly KPIs"
    print("Strategy Gaps:", detector.detect_strategy_gaps(strategy))
    
    # Test video analysis
    videos = [
        {"title": "Python Tips", "description": "Learn Python", "tags": "python"}
    ]
    print("Video Gaps:", detector.detect_video_gaps(videos))