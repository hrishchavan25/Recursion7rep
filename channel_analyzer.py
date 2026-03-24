import time
import collections
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import socket

class ChannelAnalyzer:
    def __init__(self, channel_name, api_key):
        self.channel_name = channel_name
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def _retry_execute(self, request, retries=3, delay=2):
        """Helper to retry API calls on connection/DNS issues"""
        for i in range(retries):
            try:
                return request.execute()
            except (socket.timeout, ConnectionError, socket.error, socket.gaierror) as e:
                if i == retries - 1:
                    raise e
                time.sleep(delay * (i + 1))
            except HttpError as e:
                if e.resp.status == 404:
                    return None
                raise e
        return None

    def resolve_channel_id(self):
        """Resolves channel ID from channel name/handle using YouTube API"""
        # First check if it's already an ID
        if self.channel_name.startswith('UC') and len(self.channel_name) == 24:
            return self.channel_name

        # Handle @ handles
        if self.channel_name.startswith('@'):
            try:
                request = self.youtube.channels().list(
                    part="id",
                    forHandle=self.channel_name
                )
                response = self._retry_execute(request)
                if response.get('items'):
                    return response['items'][0]['id']
            except Exception:
                pass # Fallback to search if handle resolution fails

        # Use Search API as fallback for names or handles
        request = self.youtube.search().list(
            part="snippet",
            q=self.channel_name,
            type="channel",
            maxResults=1
        )
        response = self._retry_execute(request)
        
        if response.get('items'):
            return response['items'][0]['id']['channelId']
        
        raise ValueError(f"Could not find a YouTube channel matching '{self.channel_name}'. Please check the name or use the exact Channel ID.")

    def analyze(self):
        channel_id = self.resolve_channel_id()
        
        # Get channel details (subscribers, category/topic)
        channel_req = self.youtube.channels().list(
            part="snippet,statistics,topicDetails",
            id=channel_id
        )
        channel_res = self._retry_execute(channel_req)
        
        if not channel_res or not channel_res.get('items'):
            raise ValueError(f"Could not retrieve details for channel ID '{channel_id}'.")
            
        channel_item = channel_res['items'][0]
        subscribers = int(channel_item['statistics'].get('subscriberCount', 0))
        
        # Get category/topics
        topics = channel_item.get('topicDetails', {}).get('topicCategories', [])
        # Extract last part of the URL as the category name
        category_names = [t.split('/')[-1] for t in topics]
        primary_category = category_names[0] if category_names else "General"

        request = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=25,
            order="date",
            type="video"
        )

        response = self._retry_execute(request)

        data = []
        total_views = 0
        total_likes = 0

        for item in response['items']:
            video_id = item['id'].get('videoId')
            if not video_id:
                continue

            stats_request = self.youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            )
            
            stats = self._retry_execute(stats_request)

            if stats and stats.get('items'):
                v_item = stats['items'][0]
                stat = v_item['statistics']
                snippet = v_item['snippet']

                views = int(stat.get('viewCount', 0))
                likes = int(stat.get('likeCount', 0))
                comments = int(stat.get('commentCount', 0))

                total_views += views
                total_likes += likes

                data.append({
                    "video_id": video_id,
                    "title": snippet.get('title', 'Unknown'),
                    "description": snippet.get('description', ''),
                    "published_at": snippet.get('publishedAt'),
                    "views": views,
                    "likes": likes,
                    "comments": comments
                })

        # Advanced Theme Extraction using stopword filtering
        from backend.pattern_recognition import PatternRecognitionEngine
        engine = PatternRecognitionEngine([]) # Just for the keyword extraction
        all_keywords = []
        for d in data:
            all_keywords.extend(engine._extract_keywords(d['title']))
        
        # Sort and take top 5
        top_themes = dict(collections.Counter(all_keywords).most_common(5))

        thumbnail = channel_item['snippet']['thumbnails'].get('high', {}).get('url') or \
                    channel_item['snippet']['thumbnails'].get('default', {}).get('url')
        
        if thumbnail and thumbnail.startswith('//'):
            thumbnail = 'https:' + thumbnail

        total_comments = sum(d['comments'] for d in data)

        return {
            "channel_id": channel_id,
            "title": channel_item['snippet']['title'],
            "thumbnail": thumbnail,
            "subscribers": subscribers,
            "category": primary_category,
            "avg_views": total_views // len(data) if data else 0,
            "avg_likes": total_likes // len(data) if data else 0,
            "avg_comments": total_comments // len(data) if data else 0,
            "total_videos_analyzed": len(data),
            "top_themes": top_themes,
            "data": data
        }