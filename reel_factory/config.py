import os

# Instagram Credentials
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME', 'your_username')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD', 'your_password')

# Content Source
CHANNEL_URL = os.getenv('CHANNEL_URL', 'https://www.youtube.com/@Daily_Funnies1/shorts')

# Publishing Settings
VIDEOS_PER_DAY = int(os.getenv('VIDEOS_PER_DAY', '4'))
CAPTION = os.getenv('CAPTION', 'Credits to the owner. #shorts #reels #viral #trending')

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, 'videos')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')

QUEUE_FILE = os.path.join(STORAGE_DIR, 'queue.json')
USED_FILE = os.path.join(STORAGE_DIR, 'used_videos.json')
LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Discovery Config
QUEUE_TARGET_SIZE = 100
BROWSER_FOR_COOKIES = os.getenv('BROWSER_FOR_COOKIES', 'chrome') # Common options: 'chrome', 'edge', 'firefox', 'brave'
COOKIES_FILE = os.path.join(BASE_DIR, 'cookies.txt')
