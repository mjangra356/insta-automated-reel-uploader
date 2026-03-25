import os
import time
import requests

from utils.logger import get_logger
from config import CAPTION, INSTAGRAM_ACCOUNT_ID, INSTAGRAM_ACCESS_TOKEN, BASE_VM_URL

logger = get_logger("instagram_publisher")


class InstagramPublisher:

    BASE_URL = BASE_VM_URL

    MAX_RETRIES = 3
    POLL_INTERVAL = 5   # seconds
    MAX_POLL_TIME = 120  # seconds

    def _get_public_url(self, video_path):
        filename = os.path.basename(video_path)
        return f"{self.BASE_URL}/{filename}"

    def _create_container(self, video_url, caption):

        url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"

        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        response = requests.post(url, data=payload)
        return response.json()

    def _check_status(self, creation_id):

        url = f"https://graph.facebook.com/v19.0/{creation_id}"

        params = {
            "fields": "status_code",
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        response = requests.get(url, params=params)
        return response.json()

    def _publish_container(self, creation_id):

        url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"

        payload = {
            "creation_id": creation_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        response = requests.post(url, data=payload)
        return response.json()
    
    def _is_url_accessible(self, url):

        try:
            response = requests.head(url, timeout=5)

            if response.status_code == 200:
                return True
            else:
                logger.error(f"URL not accessible: {url}, status: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"URL check failed: {url}, error: {e}")
            return False

    def publish(self, video_path, caption=CAPTION):
        video_url = self._get_public_url(video_path)
        logger.info(f"Video URL: {video_url}")

        if not self._is_url_accessible(video_url):
            logger.error("Video URL is not accessible. Aborting publish.")
            return False

        for attempt in range(1, self.MAX_RETRIES + 1):

            try:
                logger.info(f"Attempt {attempt}/{self.MAX_RETRIES}")

                # ------------------------------------------
                # Step 1: Create container
                # ------------------------------------------
                logger.info("Creating media container...")
                create_data = self._create_container(video_url, caption)

                if "id" not in create_data:
                    logger.error(f"Container creation failed: {create_data}")
                    continue

                creation_id = create_data["id"]
                logger.info(f"Container ID: {creation_id}")

                # ------------------------------------------
                # Step 2: Poll status
                # ------------------------------------------
                logger.info("Polling media status...")

                start_time = time.time()

                while True:

                    status_data = self._check_status(creation_id)

                    status = status_data.get("status_code")

                    logger.info(f"Status: {status}")

                    if status == "FINISHED":
                        break

                    if status == "ERROR":
                        logger.error(f"Processing failed: {status_data}")
                        raise Exception("Media processing failed")

                    if time.time() - start_time > self.MAX_POLL_TIME:
                        raise Exception("Polling timeout")

                    time.sleep(self.POLL_INTERVAL)

                # ------------------------------------------
                # Step 3: Publish
                # ------------------------------------------
                logger.info("Publishing reel...")
                publish_data = self._publish_container(creation_id)

                if "id" in publish_data:
                    logger.info("Reel published successfully!")
                    return True
                else:
                    logger.error(f"Publish failed: {publish_data}")

            except Exception as e:
                logger.error(f"Attempt {attempt} failed: {e}")

            # wait before retry
            time.sleep(5)

        logger.error("All attempts failed.")
        return False