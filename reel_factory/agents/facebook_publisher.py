import os
import requests

from utils.logger import get_logger
from config import PAGE_ID, INSTAGRAM_ACCESS_TOKEN

logger = get_logger("facebook_publisher")


class FacebookPublisher:

    def publish(self, video_path, caption):

        if not os.path.exists(video_path):
            logger.error(f"Video not found: {video_path}")
            return False

        try:

            url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"

            logger.info("Uploading video to Facebook...")

            with open(video_path, "rb") as video_file:

                files = {
                    "source": video_file
                }

                data = {
                    "description": caption,
                    "access_token": INSTAGRAM_ACCESS_TOKEN
                }

                response = requests.post(url, files=files, data=data)
                result = response.json()

            if "id" in result:
                logger.info("Facebook video published successfully!")
                return True
            else:
                logger.error(f"Facebook publish failed: {result}")
                return False

        except Exception as e:
            logger.error(f"Facebook publish error: {e}")
            return False