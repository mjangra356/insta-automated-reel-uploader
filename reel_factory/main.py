import os
import sys

# Ensure config can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import CHANNEL_URL, QUEUE_FILE, USED_FILE
from agents.discovery_agent import DiscoveryAgent
from agents.downloader_agent import DownloaderAgent
from agents.processor_agent import ProcessorAgent
from agents.publisher_agent import PublisherAgent
from utils.logger import get_logger
from utils.file_manager import load_json, save_json, remove_file

logger = get_logger('main_pipeline')

def discover_and_process():
    """
    Pipeline to discover new shorts, download, process them, and add to queue.
    """
    logger.info("Starting discover and process pipeline.")
    
    discovery = DiscoveryAgent()
    downloader = DownloaderAgent()
    processor = ProcessorAgent()
    
    # 1. Discover
    videos = discovery.discover(CHANNEL_URL)
    if not videos:
        logger.info("No new videos found to process.")
        return
        
    queue = load_json(QUEUE_FILE, default_value=[])
    used = load_json(USED_FILE, default_value=[])
    
    for video in videos:
        video_id = video['video_id']
        logger.info(f"Processing video {video_id} - {video['title']}")
        
        # 2. Download
        downloaded_path = downloader.download(video_id, video['video_url'])
        if not downloaded_path:
            logger.error(f"Failed to download {video_id}, skipping.")
            continue
            
        # 3. Process
        processed_path = processor.process_video(downloaded_path)
        if not processed_path:
            logger.error(f"Failed to process {video_id}, skipping.")
            # Clean up raw download if not the same path
            if downloaded_path != processed_path:
                 remove_file(downloaded_path)
            continue
            
        # Add to queue
        queue.append({
            "video_id": video_id,
            "video_path": processed_path,
            "status": "pending",
            "title": video['title']
        })
        save_json(QUEUE_FILE, queue)
        
        # Add to used videos
        used.append({"video_id": video_id})
        save_json(USED_FILE, used)
        
        # Clean up raw if we have a processed version that is different
        if downloaded_path != processed_path:
            remove_file(downloaded_path)
            
        logger.info(f"Video {video_id} added to queue and marked as used.")
        
    logger.info("Pipeline execution completed.")


def publish_from_queue():
    """
    Takes one video from the queue and publishes it.
    """
    logger.info("Starting publish from queue pipeline.")
    
    queue = load_json(QUEUE_FILE, default_value=[])
    if not queue:
        logger.info("Queue is empty. Nothing to publish.")
        return False
        
    # Get first pending video
    video_to_publish = None
    video_index = -1
    for idx, item in enumerate(queue):
        if item.get("status") == "pending":
            video_to_publish = item
            video_index = idx
            break
            
    if not video_to_publish:
        logger.info("No pending videos in queue.")
        return False
        
    publisher = PublisherAgent()
    video_path = video_to_publish['video_path']
    title = video_to_publish.get('title', 'Unknown Title')
    
    logger.info(f"Attempting to publish: {video_path} - {title}")
    
    try:
        from config import CAPTION
        # Optionally append title to caption:
        # full_caption = f"{title}\n\n{CAPTION}"
        full_caption = CAPTION
        success = publisher.publish(video_path, caption=full_caption)
    except Exception as e:
        logger.error(f"Publish agent threw exception: {str(e)}")
        success = False
    
    if success:
        logger.info(f"Publishing successful. Removing {video_path} from queue and cleaning up.")
        queue.pop(video_index)
        save_json(QUEUE_FILE, queue)
        remove_file(video_path)
        return True
    else:
        logger.error("Publishing failed.")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reel Factory Main CLI")
    parser.add_argument('--discover', action='store_true', help='Run discovery and processing pipeline')
    parser.add_argument('--publish', action='store_true', help='Run single publish from queue')
    
    args = parser.parse_args()
    
    if args.discover:
        discover_and_process()
    elif args.publish:
        publish_from_queue()
    else:
        logger.info("Please specify --discover or --publish. Run with -h for help.")
