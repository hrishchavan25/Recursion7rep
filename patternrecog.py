import re
import collections

class PatternRecognizer:
    def __init__(self, data=None):
        self.data = data or []
        self.user_patterns = {}
        self.pattern_threshold = 0.7
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

    def analyze_channel_style(self, channel_data):
        """Surf the channel data to understand the creator's persona"""
        titles = [v['title'] for v in channel_data]
        all_keywords = []
        for title in titles:
            all_keywords.extend(self._extract_keywords(title))
        
        top_themes = collections.Counter(all_keywords).most_common(5)
        primary_intent = self._get_intent(titles)
        dominant_style = self._get_title_style(titles)
        
        return {
            "intent": primary_intent,
            "style": dominant_style,
            "themes": [t[0] for t in top_themes],
            "niche": top_themes[0][0] if top_themes else "General"
        }

    def personalize_app_for_user(self, target_channel_data):
        """Automatically personalize the application based on the user's channel style"""
        persona = self.analyze_channel_style(target_channel_data)
        
        # Personalize UI and strategy focus based on persona
        personalization = {
            "dashboard_theme": "dark" if persona["style"] == "High Intensity (All Caps)" else "light",
            "primary_focus": "Competitive Edge" if persona["intent"] == "Reviews/Comparisons" else "Content Quality",
            "suggested_layout": "Detailed Grid" if persona["style"] == "Descriptive" else "Minimalist Feed",
            "auto_selected_niche": persona["niche"],
            "creator_persona": f"{persona['style']} {persona['intent']}"
        }
        
        return personalization

    def record_user_action(self, user_id, action, timestamp=None):
        """Record user actions to identify patterns"""
        if user_id not in self.user_patterns:
            self.user_patterns[user_id] = []
        
        self.user_patterns[user_id].append({
            'action': action,
            'timestamp': timestamp
        })
    
    def get_frequent_patterns(self, user_id, min_frequency=2):
        """Identify frequently occurring patterns for a user"""
        if user_id not in self.user_patterns:
            return []
        
        actions = self.user_patterns[user_id]
        pattern_count = {}
        
        for item in actions:
            action = item['action']
            pattern_count[action] = pattern_count.get(action, 0) + 1
        
        frequent = {k: v for k, v in pattern_count.items() if v >= min_frequency}
        return sorted(frequent.items(), key=lambda x: x[1], reverse=True)
    
    def personalize_experience(self, user_id):
        """Generate personalization settings based on recognized patterns"""
        patterns = self.get_frequent_patterns(user_id)
        
        if not patterns:
            return {'theme': 'default', 'features': []}
        
        top_action = patterns[0][0]
        
        personalization = {
            'preferred_action': top_action,
            'frequent_patterns': patterns,
            'quick_access': [p[0] for p in patterns[:3]]
        }
        
        return personalization