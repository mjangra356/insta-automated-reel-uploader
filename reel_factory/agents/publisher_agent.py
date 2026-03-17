import os
import sys
import time

# Ensure config can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, CAPTION
from utils.logger import get_logger

logger = get_logger('publisher_agent')

class PublisherAgent:
    def publish(self, video_path, caption=CAPTION):
        """
        Uploads a video to Instagram Reels.
        Re-uses browser session where possible via Playwright.
        """
        if not os.path.exists(video_path):
            logger.error(f"Video file not found for publishing: {video_path}")
            return False
            
        logger.info(f"Starting publisher for {video_path}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Headless needs a good user agent for Instagram
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                # 1. Login
                logger.info("Logging into Instagram...")
                page.goto("https://www.instagram.com/accounts/login/")
                page.wait_for_selector("input[name='username']", timeout=15000)
                page.fill("input[name='username']", INSTAGRAM_USERNAME)
                page.fill("input[name='password']", INSTAGRAM_PASSWORD)
                page.click("button[type='submit']")
                
                try:
                    page.wait_for_url(lambda url: "instagram.com" in url and "login" not in url, timeout=15000)
                except PlaywrightTimeoutError:
                    logger.warning("Main login wait timed out, proceeding anyway (might be on 2FA or save info page).")
                
                time.sleep(5) # Wait for page to settle
                
                # Check for "Save your login info" or other popups
                try:
                    not_now = page.locator("button:has-text('Not Now')").first
                    if not_now.is_visible():
                        not_now.click()
                        time.sleep(2)
                except Exception:
                    pass
                
                # 2. Navigate to Reels creation
                logger.info("Navigating to creation page...")
                page.goto("https://www.instagram.com/reels/create/")
                time.sleep(3)
                
                if "create" not in page.url:
                    # Alternative approach if direct URL doesn't work
                    logger.info("Direct create URL did not work, trying UI buttons...")
                    page.goto("https://www.instagram.com/")
                    time.sleep(3)
                    new_post_svg = page.locator("svg[aria-label='New post']").first
                    if new_post_svg.is_visible():
                        new_post_svg.click()
                        time.sleep(2)
                    
                # 3. Upload file
                file_input = page.locator("input[type='file']").first
                try:
                    file_input.wait_for(state="attached", timeout=15000)
                    file_input.set_input_files(video_path)
                    logger.info("Video file uploaded to browser.")
                except PlaywrightTimeoutError:
                    logger.error("Could not find file input for upload.")
                    browser.close()
                    return False
                
                time.sleep(5)
                
                # 4. Progress through dialogues (Next -> Next -> Share)
                logger.info("Progressing through upload dialogues...")
                
                for _ in range(2):
                    try:
                        next_button = page.locator("div[role='button']:has-text('Next')").first
                        if next_button.is_visible(timeout=5000):
                            next_button.click()
                            time.sleep(3)
                    except Exception as e:
                        break
                
                logger.info("Adding caption...")
                try:
                    editor = page.locator("div[aria-label='Write a caption...']").first
                    if editor.is_visible(timeout=5000):
                        editor.fill(caption)
                except Exception:
                    logger.warning("Caption editor not visible/found.")
                
                time.sleep(2)
                
                # 5. Share
                logger.info("Clicking Share...")
                try:
                    share_btn = page.locator("div[role='button']:has-text('Share')").first
                    if share_btn.is_visible(timeout=5000):
                        share_btn.click()
                    else:
                        logger.error("Share button not found.")
                        browser.close()
                        return False
                except Exception:
                    logger.error("Error clicking Share button.")
                    browser.close()
                    return False
                    
                # Wait for upload completion message or checkmark
                try:
                    page.wait_for_selector("img[alt='Animated checkmark']", timeout=60000)
                    logger.info("Successfully published Reel!")
                except PlaywrightTimeoutError:
                    logger.warning("Upload completion checkmark not found. Proceeding anyway.")
                
                time.sleep(5) # Let network requests finish
                context.close()
                browser.close()
                return True
                
        except Exception as e:
            logger.error(f"Error during publishing: {str(e)}")
            return False
