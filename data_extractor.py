import time
import socket
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class DataExtractor:
    def __init__(self, channel_ids, api_key):
        self.channel_ids = channel_ids
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
                # If it's a 404, we want to return None so the caller can handle it
                if e.resp.status == 404:
                    return None
                raise e
        return None

    def extract(self):
        all_data = []

        for channel_id in self.channel_ids:
            # Get uploads playlist ID for the channel
            channel_req = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            channel_res = self._retry_execute(channel_req)
            
            playlist_id = None
            if channel_res and channel_res.get('items'):
                playlist_id = channel_res['items'][0]['contentDetails']['relatedPlaylists'].get('uploads')

            # Fallback to search if playlist ID is missing or if the playlist call fails
            response = None
            if playlist_id:
                try:
                    playlist_request = self.youtube.playlistItems().list(
                        part="snippet,contentDetails",
                        playlistId=playlist_id,
                        maxResults=25
                    )
                    response = self._retry_execute(playlist_request)
                except HttpError:
                    response = None

            # If playlist failed or was missing, use search fallback
            if not response:
                search_request = self.youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=25,
                    type="video",
                    order="date"
                )
                response = self._retry_execute(search_request)

            if response and response.get('items'):
                for item in response['items']:
                    if 'videoId' in item.get('id', {}): # Search result
                        video_id = item['id']['videoId']
                    elif 'contentDetails' in item: # Playlist item
                        video_id = item['contentDetails'].get('videoId')
                    else:
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

                        all_data.append({
                            "channel_id": channel_id,
                            "video_id": video_id,
                            "title": snippet.get('title', 'Unknown'),
                            "description": snippet.get('description', ''),
                            "published_at": snippet.get('publishedAt'),
                            "views": views,
                            "likes": likes,
                            "comments": comments
                        })

        return all_data