import time
import socket
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import numpy as np

class CompetitorDiscovery:
    def __init__(self, channel_id, api_key):
        self.channel_id = channel_id
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

    def discover(self, category_input, max_candidates=25):
        """Finds competitors based on category (string or list)"""
        # Step 1: Search channels by category to get a pool of candidates
        search_query = category_input
        if isinstance(category_input, list):
            search_query = " | ".join(category_input) # OR search for multiple categories

        # YouTube API limit for maxResults is 50
        limit = min(50, max_candidates)

        search_request = self.youtube.search().list(
            part="snippet",
            type="channel",
            q=search_query,
            maxResults=limit # Fetch a larger pool of candidates to calculate metrics for
        )
        response = self._retry_execute(search_request)

        if not response or not response.get('items'):
            return []

        candidate_ids = [item['snippet']['channelId'] for item in response['items'] if item['snippet']['channelId'] != self.channel_id]
        
        if not candidate_ids:
            return []

        # Step 2: Get detailed metrics for all candidates
        profiles = []
        for cid in candidate_ids:
            basic = self._get_channel_basic(cid)
            if not basic:
                continue
            
            videos = self._fetch_videos_stats(basic.get('uploads_playlist'), max_videos=20)
            
            if videos:
                avg_views = float(sum(v['views'] for v in videos) / len(videos))
                avg_likes = float(sum(v['likes'] for v in videos) / len(videos))
                avg_comments = float(sum(v['comments'] for v in videos) / len(videos))
                
                # Brand collaborations heuristic
                sponsor_kw = ['sponsor', 'sponsored', 'paid partnership', 'brand deal', '#ad', 'partnered']
                bc_count = 0
                for v in videos:
                    txt = (v['title'] + " " + v['description']).lower()
                    if any(k in txt for k in sponsor_kw):
                        bc_count += 1
            else:
                avg_views = avg_likes = avg_comments = 0.0
                bc_count = 0

            engagement_rate = ((avg_likes + avg_comments) / avg_views * 100.0) if avg_views > 0 else 0.0

            profiles.append({
                "title": basic.get('title'),
                "channel_id": cid,
                "description": basic.get('description', ''),
                "thumbnail": basic.get('thumbnail', ''),
                "category": basic.get('category', 'General'),
                "subscribers": int(basic.get('subscribers', 0)),
                "engagement_rate": engagement_rate,
                "brand_collaborations": bc_count,
                "avg_views": avg_views,
                "avg_likes": avg_likes
            })

        return profiles

    def _get_channel_basic(self, channel_id):
        req = self.youtube.channels().list(part="snippet,statistics,contentDetails,topicDetails", id=channel_id)
        res = self._retry_execute(req)
        if not res or not res.get('items'):
            return None
        it = res['items'][0]
        stats = it.get('statistics', {})
        snippet = it.get('snippet', {})
        uploads_pl = it.get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        
        # Extract category from topicDetails
        topics = it.get('topicDetails', {}).get('topicCategories', [])
        category = topics[0].split('/')[-1] if topics else "General"

        thumbnail = snippet.get('thumbnails', {}).get('high', {}).get('url') or \
                    snippet.get('thumbnails', {}).get('default', {}).get('url')
        
        if thumbnail and thumbnail.startswith('//'):
            thumbnail = 'https:' + thumbnail

        return {
            'channel_id': channel_id,
            'title': snippet.get('title'),
            'description': snippet.get('description'),
            'thumbnail': thumbnail,
            'category': category,
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
            resp_request = self.youtube.playlistItems().list(
                part="contentDetails,snippet",
                playlistId=playlist_id,
                maxResults=min(50, max_videos - len(vids)),
                pageToken=nextPageToken
            )
            resp = self._retry_execute(resp_request)
            if not resp:
                break
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
            vres_request = self.youtube.videos().list(part="statistics,snippet", id=",".join(batch))
            vres = self._retry_execute(vres_request)
            if not vres:
                continue
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
# ...existing code...