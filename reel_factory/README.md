# Reel Factory

An automated Python system to discover, download, process, and publish YouTube Shorts as Instagram Reels. It uses `yt-dlp` to fetch videos, `ffmpeg` to process them to Instagram specifications (1080x1920, 30fps), and `Playwright` to handle the Instagram uploading.

## Requirements

- Python 3.10+
- `ffmpeg` installed and added to your system PATH
- Supported OS: Windows, macOS, Linux

## Installation

1. **Clone/Download the repository**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install Playwright Browsers:**
   ```bash
   playwright install chromium
   ```
4. **Install FFmpeg:**
   - **Windows:** Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or use `winget install ffmpeg`.
   - Ensure the `ffmpeg` executable is in your system PATH.

## Configuration

Edit `config.py` with your custom settings (or set them as environment variables):
- `INSTAGRAM_USERNAME`: Your Instagram login
- `INSTAGRAM_PASSWORD`: Your Instagram password
- `CHANNEL_URL`: The URL of the YouTube Shorts channel
- `CAPTION`: Caption to use when posting (includes hashtags)

## Usage

### 1. Manual Execution

To fetch new videos, process them, and add to the queue:
```bash
python main.py --discover
```

To publish one video from the queue manually:
```bash
python main.py --publish
```

### 2. Scheduled Automated Execution

To run the system in the background and publish at scheduled times (10:00, 14:00, 18:00, 21:00) and discover dynamically at 02:00:
```bash
python scheduler.py
```

## Logs

All actions, discoveries, downloads, processing, and publishing attempts are logged securely in `logs/app.log`.
