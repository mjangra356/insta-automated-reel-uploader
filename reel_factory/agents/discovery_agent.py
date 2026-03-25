import os
import sys

# Ensure config can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yt_dlp
from config import QUEUE_TARGET_SIZE, USED_FILE, BROWSER_FOR_COOKIES, COOKIES_FILE, DOG_USED_FILE, DISCOVER_CONTENT
from utils.logger import get_logger
from utils.file_manager import load_json

logger = get_logger('discovery_agent')

class DiscoveryAgent:
    def __init__(self, target_size=QUEUE_TARGET_SIZE):
        self.target_size = target_size

        content_map = {
            "DOG": DOG_USED_FILE,
            "CAT": USED_FILE
        }

        content_type = DISCOVER_CONTENT.upper()

        self.used_file = content_map.get(content_type, USED_FILE)

    def discover(self, channel_url):
        logger.info(f"Starting discovery for channel: {channel_url}")
        
        # Load used videos to filter out
        used_videos = load_json(self.used_file, default_value=[])
        used_ids = set()
        
        for v in used_videos:
            if isinstance(v, dict) and 'video_id' in v:
                used_ids.add(v['video_id'])
            elif isinstance(v, str):
                used_ids.add(v)
                
        ydl_opts = {
            'extract_flat': True,
            'quiet': True,
            'playlistend': 300, # Fetch up to 300 latest shorts
        }
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
        elif BROWSER_FOR_COOKIES:
            ydl_opts['cookiesfrombrowser'] = (BROWSER_FOR_COOKIES,)

        videos = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                if 'entries' in info:
                    entries = list(info['entries'])
                    logger.info(f"Fetched {len(entries)} videos from channel.")
                    
                    # Reverse entries so oldest (from the last 300) are processed first
                    entries.reverse()
                    
                    for entry in entries:
                        video_id = entry.get('id')
                        if not video_id:
                            continue
                            
                        if video_id in used_ids:
                            logger.debug(f"Skipping already used video: {video_id}")
                            continue
                            
                        title = entry.get('title', 'Unknown Title')
                        
                        videos.append({
                            "video_id": video_id,
                            "video_url": f"https://www.youtube.com/shorts/{video_id}",
                            "title": title
                        })
                        
                        if len(videos) >= self.target_size:
                            logger.info(f"Reached target queue size of {self.target_size}")
                            break
                            
        except Exception as e:
            logger.error(f"Error discovering videos: {str(e)}")
            
        logger.info(f"Discovery completed. Selected {len(videos)} new videos.")
        return videos
