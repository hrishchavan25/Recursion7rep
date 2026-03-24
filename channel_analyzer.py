from googleapiclient.discovery import build

class ChannelAnalyzer:
    def __init__(self, channel_id, api_key):
        self.channel_id = channel_id
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def analyze(self):
        request = self.youtube.search().list(
            part="snippet",
            channelId=self.channel_id,
            maxResults=10,
            order="date"
        )

        response = request.execute()

        data = []
        total_views = 0
        total_likes = 0

        for item in response['items']:
            video_id = item['id'].get('videoId')
            if not video_id:
                continue

            stats = self.youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            stat = stats['items'][0]['statistics']

            views = int(stat.get('viewCount', 0))
            likes = int(stat.get('likeCount', 0))

            total_views += views
            total_likes += likes

            data.append({
                "title": item['snippet']['title'],
                "view_count": views
            })

        return {
            "avg_views": total_views // len(data) if data else 0,
            "avg_likes": total_likes // len(data) if data else 0,
            "total_videos_analyzed": len(data),
            "data": data
        }