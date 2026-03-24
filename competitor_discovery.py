# ...existing code...
from googleapiclient.discovery import build
import numpy as np
import re

class YouTubeClient:
    """Simple wrapper around youtube-data API using google-api-python-client."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_channel(self, channel_id):
        return self.youtube.channels().list(
            part='snippet,statistics,contentDetails',
            id=channel_id
        ).execute()

    def search_channels(self, query, max_results=10):
        return self.youtube.search().list(
            part='snippet',
            type='channel',
            q=query,
            maxResults=max_results
        ).execute()

    def get_playlist_items(self, playlist_id, max_results=50):
        return self.youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=min(max_results, 50)
        ).execute()

    def get_videos(self, video_ids):
        return self.youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()


class CompetitorDiscovery:
    def __init__(self, channel_id=None, api_key=None, youtube_client=None):
        self.channel_id = channel_id
        if youtube_client is not None:
            self.youtube = youtube_client.youtube
        else:
            self.youtube = build('youtube', 'v3', developerKey=api_key)

    def get_channel_id_by_name(self, channel_name):
        """Resolve a channel name to a channel ID using YouTube search."""
        if not channel_name:
            return None

        response = self.youtube.search().list(
            part='snippet',
            type='channel',
            q=channel_name,
            maxResults=3
        ).execute()

        items = response.get('items', [])
        if not items:
            return None

        # Use top-ranked result as the best approximate match
        return items[0]['snippet'].get('channelId')

    def extract_keywords(self, channel_data, videos_data):
        """Extract relevant keywords from channel description and video titles for competitor search."""
        keywords = set()
        
        # From channel description
        description = channel_data.get('snippet', {}).get('description', '').lower()
        # Remove common words and extract meaningful terms
        words = re.findall(r'\b\w+\b', description)
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'an', 'a', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'}
        keywords.update([word for word in words if len(word) > 3 and word not in stop_words])
        
        # From video titles
        for video in videos_data[:10]:  # Use first 10 videos
            title = video.get('title', '').lower()
            title_words = re.findall(r'\b\w+\b', title)
            keywords.update([word for word in title_words if len(word) > 3 and word not in stop_words])
        
        # Return top keywords (limit to 5-7 for search)
        return list(keywords)[:7]

    def discover(self, max_competitors=3, min_subscribers=1000):
        # Step 1: Get target channel info and videos to extract keywords
        channel_request = self.youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=self.channel_id
        )
        channel_response = channel_request.execute()

        if not channel_response['items']:
            return []

        channel_data = channel_response['items'][0]
        channel_title = channel_data['snippet']['title']
        uploads_playlist = channel_data['contentDetails']['relatedPlaylists']['uploads']
        
        # Get some videos to extract keywords
        videos_response = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=10
        ).execute()
        
        videos_data = [item['snippet'] for item in videos_response.get('items', [])]
        
        # Extract keywords from channel and videos
        keywords = self.extract_keywords(channel_data, videos_data)
        search_query = ' '.join(keywords) if keywords else channel_title
        
        print(f"🔍 Searching competitors using keywords: {search_query}")

        # Step 2: Search similar channels using extracted keywords
        search_request = self.youtube.search().list(
            part="snippet",
            type="channel",
            q=search_query,
            maxResults=max_competitors * 3  # Get more candidates, filter by metrics
        )

        response = search_request.execute()
        competitors = []
        
        for item in response['items']:
            comp_channel_id = item['snippet']['channelId']

            # Avoid adding the same channel
            if comp_channel_id == self.channel_id:
                continue

            # Fetch detailed metrics for filtering
            comp_info = self._get_channel_basic(comp_channel_id)
            if not comp_info:
                continue
            
            # Filter by minimum subscribers to ensure relevance
            if comp_info['subscribers'] < min_subscribers:
                continue

            comp_data = {
                "channel_id": comp_channel_id,
                "title": item['snippet']['title'],
                "description": item['snippet']['description'],
                "thumbnail": item['snippet']['thumbnails']['default']['url'],
                "subscribers": comp_info['subscribers'],
                "total_videos": comp_info['total_uploads'],
                "uploads_playlist": comp_info['uploads_playlist']
            }
            
            competitors.append(comp_data)
            
            if len(competitors) >= max_competitors:
                break

        return competitors
# ...existing code...

    def _get_channel_basic(self, channel_id):
        req = self.youtube.channels().list(part="snippet,statistics,contentDetails", id=channel_id)
        res = req.execute()
        if not res.get('items'):
            return None
        it = res['items'][0]
        stats = it.get('statistics', {})
        snippet = it.get('snippet', {})
        uploads_pl = it.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        return {
            'channel_id': channel_id,
            'title': snippet.get('title'),
            'uploads_playlist': uploads_pl,
            'subscribers': int(stats.get('subscriberCount') or 0),
            'total_uploads': int(stats.get('videoCount') or 0)
        }

    def _fetch_videos_stats(self, playlist_id, max_videos=50):
        if not playlist_id:
            return []
        vids = []
        nextPageToken = None
        while len(vids) < max_videos:
            resp = self.youtube.playlistItems().list(
                part="contentDetails,snippet",
                playlistId=playlist_id,
                maxResults=min(50, max_videos - len(vids)),
                pageToken=nextPageToken
            ).execute()
            for item in resp.get('items', []):
                vids.append(item['contentDetails']['videoId'])
            nextPageToken = resp.get('nextPageToken')
            if not nextPageToken:
                break
        if not vids:
            return []
        # fetch stats for video ids in batches
        details = []
        for i in range(0, len(vids), 50):
            batch = vids[i:i+50]
            vres = self.youtube.videos().list(part="statistics,snippet", id=",".join(batch)).execute()
            for v in vres.get('items', []):
                s = v.get('statistics', {})
                sn = v.get('snippet', {})
                details.append({
                    'videoId': v['id'],
                    'title': sn.get('title',''),
                    'description': sn.get('description',''),
                    'views': int(s.get('viewCount') or 0),
                    'likes': int(s.get('likeCount') or 0),
                    'comments': int(s.get('commentCount') or 0)
                })
        return details

    def find_competitors_by_metrics(self,
                                    selected_channel_id,
                                    candidate_channel_ids=None,
                                    top_n=5,
                                    video_sample=50,
                                    weights=None):
        # candidate_channel_ids: list of channel ids to compare; if None, search by selected title
        target_basic = self._get_channel_basic(selected_channel_id)
        if not target_basic:
            return []

        if candidate_channel_ids is None:
            # search similar channels by title
            title_q = target_basic.get('title') or ""
            search_resp = self.youtube.search().list(
                part="snippet",
                type="channel",
                q=title_q,
                maxResults=25
            ).execute()
            candidate_channel_ids = [
                it['snippet']['channelId'] for it in search_resp.get('items', [])
                if it['snippet'].get('channelId') and it['snippet']['channelId'] != selected_channel_id
            ]

        # ensure selected included
        ids = [selected_channel_id] + [cid for cid in candidate_channel_ids if cid != selected_channel_id]
        profiles = []
        for cid in ids:
            basic = self._get_channel_basic(cid)
            if not basic:
                continue
            videos = self._fetch_videos_stats(basic.get('uploads_playlist'), max_videos=video_sample)
            if videos:
                avg_views = float(sum(v['views'] for v in videos) / len(videos))
                avg_likes = float(sum(v['likes'] for v in videos) / len(videos))
                avg_comments = float(sum(v['comments'] for v in videos) / len(videos))
                # brand collaborations heuristic
                sponsor_kw = ['sponsor', 'sponsored', 'paid partnership', 'brand deal', '#ad', 'partnered']
                bc_count = 0
                for v in videos:
                    txt = (v['title'] + " " + v['description']).lower()
                    if any(k in txt for k in sponsor_kw):
                        bc_count += 1
                has_bc = int(bc_count > 0)
            else:
                avg_views = avg_likes = avg_comments = 0.0
                bc_count = 0
                has_bc = 0

            engagement_rate_pct = ( (avg_likes + avg_comments) / avg_views * 100.0 ) if avg_views > 0 else 0.0
            estimated_earnings_usd = (avg_views / 1000.0) * 2.0  # simple CPM=2 USD estimate

            profiles.append({
                'channel_id': cid,
                'title': basic.get('title'),
                'subscribers': float(basic.get('subscribers',0)),
                'avg_views': float(avg_views),
                'avg_likes': float(avg_likes),
                'avg_comments': float(avg_comments),
                'engagement_rate_pct': float(engagement_rate_pct),
                'total_uploads': float(basic.get('total_uploads',0)),
                'estimated_earnings_usd': float(estimated_earnings_usd),
                'brand_collaborations': float(bc_count),
                'has_brand_collaborations': float(has_bc)
            })

        if len(profiles) <= 1:
            return []

        feats = ['subscribers','avg_views','avg_likes','avg_comments',
                 'engagement_rate_pct','total_uploads','estimated_earnings_usd',
                 'brand_collaborations','has_brand_collaborations']

        M = np.array([[p[f] for f in feats] for p in profiles], dtype=float)

        # log transform for skewed fields: subscribers, avg_views, estimated_earnings_usd
        for idx, fname in enumerate(feats):
            if fname in ('subscribers','avg_views','estimated_earnings_usd'):
                M[:, idx] = np.log1p(M[:, idx])

        # z-score normalization
        mu = M.mean(axis=0)
        sigma = M.std(axis=0, ddof=0)
        sigma[sigma == 0] = 1.0
        Z = (M - mu) / sigma

        # apply weights if provided
        if weights:
            w = np.array([weights.get(f,1.0) for f in feats], dtype=float)
            Z = Z * w

        # cosine similarity
        target_vec = Z[0]
        norms = np.linalg.norm(Z, axis=1)
        norms[norms == 0] = 1.0
        sims = (Z @ target_vec) / (norms * np.linalg.norm(target_vec))
        # assemble results (skip index 0 which is target)
        results = []
        for i in range(1, len(profiles)):
            results.append({
                **profiles[i],
                'similarity': float(sims[i])
            })
        results = sorted(results, key=lambda x: x['similarity'], reverse=True)[:top_n]
        return results
    
    def discover_competitors_refined(self, max_competitors=5, min_subscribers=1000, video_sample=30):
        """
        Refined competitor discovery with full metrics integration
        Returns competitors with subscribers, views, engagement, etc.
        """
        # Step 1: Get target channel info and videos to extract keywords
        target_basic = self._get_channel_basic(self.channel_id)
        if not target_basic:
            return []

        # Get channel data for keyword extraction
        channel_request = self.youtube.channels().list(
            part="snippet,statistics,contentDetails",
            id=self.channel_id
        )
        channel_response = channel_request.execute()
        channel_data = channel_response['items'][0] if channel_response['items'] else {}
        uploads_playlist = channel_data.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        
        # Get videos for keyword extraction
        videos_response = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist,
            maxResults=10
        ).execute() if uploads_playlist else {'items': []}
        
        videos_data = [item['snippet'] for item in videos_response.get('items', [])]
        
        # Extract keywords
        keywords = self.extract_keywords(channel_data, videos_data)
        search_query = ' '.join(keywords) if keywords else target_basic.get('title', '')
        
        print(f"🔍 Searching refined competitors using keywords: {search_query}")

        # Step 2: Search similar channels by keywords
        search_resp = self.youtube.search().list(
            part="snippet",
            type="channel",
            q=search_query,
            maxResults=max_competitors * 4  # Get more candidates
        ).execute()
        
        candidate_channel_ids = [
            it['snippet']['channelId'] for it in search_resp.get('items', [])
            if it['snippet'].get('channelId') and it['snippet']['channelId'] != self.channel_id
        ]

        # Step 3: Fetch metrics for each candidate and filter
        competitors_with_metrics = []
        for cid in candidate_channel_ids:
            basic = self._get_channel_basic(cid)
            if not basic:
                continue
            
            # Filter by minimum subscribers
            if basic['subscribers'] < min_subscribers:
                continue
            
            # Fetch video statistics
            videos = self._fetch_videos_stats(basic.get('uploads_playlist'), max_videos=video_sample)
            
            if videos:
                avg_views = float(sum(v['views'] for v in videos) / len(videos))
                avg_likes = float(sum(v['likes'] for v in videos) / len(videos))
                avg_comments = float(sum(v['comments'] for v in videos) / len(videos))
                engagement_rate = ((avg_likes + avg_comments) / avg_views * 100) if avg_views > 0 else 0
            else:
                avg_views = avg_likes = avg_comments = 0.0
                engagement_rate = 0.0

            competitor_profile = {
                'channel_id': cid,
                'channel_name': basic.get('title'),
                'title': basic.get('title'),
                'subscribers': int(basic.get('subscribers', 0)),
                'avg_views': int(avg_views),
                'avg_likes': int(avg_likes),
                'avg_comments': int(avg_comments),
                'engagement_rate_pct': round(engagement_rate, 2),
                'total_uploads': int(basic.get('total_uploads', 0)),
                'videos': videos
            }
            
            competitors_with_metrics.append(competitor_profile)
            
            if len(competitors_with_metrics) >= max_competitors:
                break

        # Sort by subscribers and views
        competitors_with_metrics = sorted(
            competitors_with_metrics,
            key=lambda x: (x['subscribers'], x['avg_views']),
            reverse=True
        )

        return competitors_with_metrics
# ...existing code...