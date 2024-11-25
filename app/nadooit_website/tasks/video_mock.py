"""Mock module for video processing during testing."""

class VideoFileClip:
    """Mock VideoFileClip class."""
    def __init__(self, filename):
        self.filename = filename
        self.duration = 10.0  # Mock duration
        
    def close(self):
        """Mock close method."""
        pass

def ffmpeg_tools():
    """Mock ffmpeg tools."""
    pass
