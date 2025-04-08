import requests, subprocess, os, logging
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp4 import MP4, MP4Cover
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('rapidapi_token')

# Configure logging
os.makedirs("log", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log/spotify_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SpotifySong:
    def __init__(self, song_ID: str): 
        logger.info(f"Initializing SpotifySong with ID: {song_ID}")
        url = "https://spotify-scraper.p.rapidapi.com/v1/track/download/soundcloud"
        querystring = {"track":song_ID, "quality":"hq"}
        headers = {
            "x-rapidapi-key": token,
            "x-rapidapi-host": "spotify-scraper.p.rapidapi.com"
        }

        self.response = requests.get(url, headers=headers, params=querystring)
        logger.debug(f"API Response status code: {self.response.status_code}")

        self.song_ID = song_ID
        self.song_url = self.get_song_url(song_ID)
        self.song_name = self.get_song_name(song_ID)
        self.song_artist = self.get_song_artist(song_ID)
        self.song_thumbnail_url = self.get_song_thumbnail(song_ID)
        self.format = self.get_format(song_ID)
        logger.info(f"Song initialized: {self.song_name} by {self.song_artist}")

    def get_song_url(self, song_ID: str) -> str:
        """
        Returns the URL of the song from the given spotify song ID.
        """
        try:
            return self.response.json()['soundcloudTrack']['audio'][0]['url']
        except KeyError:
            return None

    def get_song_name(self, song_ID: str) -> str:
        """
        Returns the name of the song from the given spotify song ID.
        """
        try:
            return self.response.json()['soundcloudTrack']['title']
        except KeyError:
            return None

    def get_song_artist(self, song_ID: str) -> str:
        """
        Returns the artist of the song from the given spotify song ID.
        """
        try:
            return ', '.join([artist['name'] for artist in self.response.json()['spotifyTrack']['artists']])
        except KeyError:
            return None

    def get_song_thumbnail(self, song_ID: str) -> str:
        """
        Returns the thumbnail of the song from the given spotify song ID.
        """
        try:
            return self.response.json()['spotifyTrack']['album']['cover'][-1]['url']
        except KeyError:
            return None

    def get_format(self, song_ID: str) -> str:
        """
        Returns the format of the song from the given spotify song ID.
        """
        try:
            return self.response.json()['soundcloudTrack']['audio'][0]['format']
        except KeyError:
            return None


    def download_song(self) -> str:
        logger.info(f"Starting download for: {self.song_name}")
        try:
            if not all([self.song_url, self.song_name, self.song_artist, self.format]):
                logger.error("Missing required metadata for download")
                return None

            filename = f"{self.song_name}.{self.format}"
            filepath = os.path.join(os.getcwd(), filename)
            logger.debug(f"Download path: {filepath}")

            curl_command = ['curl', '-L', '-o', filepath, self.song_url]
            logger.debug(f"Executing curl command: {' '.join(curl_command)}")
            process = subprocess.run(curl_command, capture_output=True, text=True)
            
            if process.returncode != 0:
                logger.error(f"Download failed: {process.stderr}")
                return None

            logger.info(f"Download completed: {filename}")

            if self.format.lower() == 'mp3':
                logger.debug("Setting MP3 metadata")
                self._set_mp3_metadata(filepath)
            elif self.format.lower() == 'm4a':
                logger.debug("Setting M4A metadata")
                self._set_m4a_metadata(filepath)

            logger.info(f"Successfully processed: {filename}")
            return filepath

        except Exception as e:
            logger.exception(f"Error during download: {str(e)}")
            return None

    def _set_mp3_metadata(self, filepath: str) -> None:
        logger.info(f"Setting MP3 metadata for: {filepath}")
        try:
            try:
                audio = EasyID3(filepath)
                logger.debug("Loaded existing ID3 tags")
            except:
                logger.debug("Creating new ID3 tags")
                audio = ID3()
                audio.save(filepath)
                audio = EasyID3(filepath)

            audio['title'] = self.song_name
            audio['artist'] = self.song_artist
            audio.save()
            logger.debug("Basic metadata set")

            if self.song_thumbnail_url:
                logger.debug("Adding thumbnail")
                thumbnail_data = requests.get(self.song_thumbnail_url).content
                audio = ID3(filepath)
                audio['APIC'] = APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=thumbnail_data
                )
                audio.save()
                logger.debug("Thumbnail added successfully")

        except Exception as e:
            logger.error(f"Failed to set MP3 metadata: {str(e)}")

    def _set_m4a_metadata(self, filepath: str) -> None:
        logger.info(f"Setting M4A metadata for: {filepath}")
        try:
            audio = MP4(filepath)
            
            audio['\xa9nam'] = [self.song_name]
            audio['\xa9ART'] = [self.song_artist]
            logger.debug("Basic metadata set")

            if self.song_thumbnail_url:
                logger.debug("Adding thumbnail")
                thumbnail_data = requests.get(self.song_thumbnail_url).content
                audio['covr'] = [MP4Cover(thumbnail_data)]
                logger.debug("Thumbnail added successfully")
            
            audio.save()
            logger.debug("M4A metadata saved")

        except Exception as e:
            logger.error(f"Failed to set M4A metadata: {str(e)}")
