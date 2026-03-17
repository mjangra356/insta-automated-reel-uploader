import os
import sys
import subprocess

# Ensure config can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import VIDEO_DIR
from utils.logger import get_logger

logger = get_logger('processor_agent')

class ProcessorAgent:
    def process_video(self, input_path):
        """
        Uses ffmpeg to ensure video meets Instagram Reels standards:
        - Aspect Ratio: 9:16
        - Resolution: 1080x1920
        - Frame rate: 30 fps
        - Format: MP4
        Also adds a tiny scaling/crop to help avoid repost detection.
        """
        if not input_path or not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return None
            
        logger.info(f"Processing video: {input_path}")
        
        filename = os.path.basename(input_path)
        name, _ = os.path.splitext(filename)
        output_filename = f"{name}_processed.mp4"
        output_path = os.path.join(VIDEO_DIR, output_filename)
        
        if os.path.exists(output_path):
            logger.info(f"Processed file already exists: {output_path}")
            return output_path
            
        # ffmpeg command
        # crop: 1080:1920:0:0 (ensure 9:16)
        # scale: slightly larger and crop to bypass hash-based duplication checks
        # -r 30: 30 fps
        # -c:v libx264, -c:a aac
        
        # Adding a slight scaling to 1084x1924, then cropping to 1080x1920 
        # to slightly alter the video.
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-vf', 'scale=1084:-1,crop=1080:1920,fps=30',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            output_path
        ]
        
        try:
            # Run ffmpeg
            process = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.returncode != 0:
                logger.error(f"ffmpeg processing failed:\n{process.stderr}")
                return None
                
            if os.path.exists(output_path):
                logger.info(f"Successfully processed to {output_path}")
                return output_path
            else:
                logger.error(f"ffmpeg completed but output file not found: {output_path}")
                return None
        except Exception as e:
            logger.error(f"Error executing ffmpeg: {str(e)}")
            return None
