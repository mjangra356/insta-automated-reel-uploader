import os
import sys

# Ensure config can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yt_dlp
from config import VIDEO_DIR, BROWSER_FOR_COOKIES, COOKIES_FILE, DOG_VIDEO_DIR, DISCOVER_CONTENT
from utils.logger import get_logger
from utils.file_manager import ensure_dir

logger = get_logger('downloader_agent')

class DownloaderAgent:
    def __init__(self):

        content_map = {
            "DOG": DOG_VIDEO_DIR,
            "CAT": VIDEO_DIR
        }

        content_type = DISCOVER_CONTENT.upper()

        self.output_dir = content_map.get(content_type, VIDEO_DIR)
        ensure_dir(self.output_dir)

    def download(self, video_id, video_url):
        
        output_template = os.path.join(self.output_dir, f"{video_id}.%(ext)s")
        
        ydl_opts = {
            "outtmpl": output_template,
            "cookies": "cookies.txt",
            "js_runtimes": {"node": {}},
            "remote_components": ["ejs:github"],
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "retries": 5
        }
        if os.path.exists(COOKIES_FILE):
            ydl_opts['cookiefile'] = COOKIES_FILE
        elif BROWSER_FOR_COOKIES:
            ydl_opts['cookiesfrombrowser'] = (BROWSER_FOR_COOKIES,)
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
            # Locate the exact downloaded file since extension might vary
            expected_path = None
            for file in os.listdir(self.output_dir):
                if file.startswith(video_id):
                    expected_path = os.path.join(self.output_dir, file)
                    break
                    
            if expected_path and os.path.exists(expected_path):
                logger.info(f"Successfully downloaded to {expected_path}")
                return expected_path
            else:
                logger.error(f"Download seemingly succeeded but file not found for {video_id} on path {expected_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading {video_id}: {str(e)}")
            return None
