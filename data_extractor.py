from googleapiclient.discovery import build

class DataExtractor:
    def __init__(self, channel_ids, api_key):
        self.channel_ids = channel_ids
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def extract(self):
        all_data = []

        for channel_id in self.channel_ids:
            request = self.youtube.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=5
            )

            response = request.execute()

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
                comments = int(stat.get('commentCount', 0))

                all_data.append({
                    "channel_id": channel_id,
                    "title": item['snippet']['title'],
                    "views": views,
                    "likes": likes,
                    "comments": comments
                })

        return all_data