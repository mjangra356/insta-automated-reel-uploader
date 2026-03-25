import schedule
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import publish_from_queue, discover_and_process
from utils.logger import get_logger

logger = get_logger('scheduler')

def scheduled_publish():
    logger.info("Running scheduled publish task...")
    try:
        publish_from_queue()
    except Exception as e:
        logger.error(f"Error in scheduled publish: {str(e)}")

def scheduled_discover():
    logger.info("Running scheduled discovery task...")
    try:
        discover_and_process()
    except Exception as e:
        logger.error(f"Error in scheduled discover: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Reel Factory Scheduler...")
    
    # Schedule publishing at 10:00, 14:00, 18:00, 21:00
    publish_times = ["07:00","10:00", "14:00", "18:00", "21:00","23:59","03:00"]
    for t in publish_times:
        schedule.every().day.at(t).do(scheduled_publish)
        logger.info(f"Scheduled publish for {t} daily")
        
    # Schedule discovery once a day at 02:00
    # schedule.every().day.at("02:00").do(scheduled_discover)
    # logger.info("Scheduled discovery for 02:00 daily")
    
    # Run once on startup just to fill queue if empty
    # logger.info("Running initial discovery and processing...")
    # try:
    #     discover_and_process()
    # except Exception as e:
    #     logger.error(f"Initial discovery failed: {str(e)}")
    
    logger.info("Scheduler is now running. Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60) # check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")