"""
Services package initialization
"""
from .youtube_service import YouTubeService, YouTubeOAuth2Strategy, YouTubeAPIKeyStrategy
from .music_service import MusicService, Song, MusicPlayer

__all__ = [
    'YouTubeService',
    'YouTubeOAuth2Strategy',
    'YouTubeAPIKeyStrategy',
    'MusicService',
    'Song',
    'MusicPlayer'
]
