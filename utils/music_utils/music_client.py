
import os
import subprocess
import pygame
from pydub import AudioSegment
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.../.env')  
load_dotenv(dotenv_path)
from utils.music_utils.select_music import get_song

YOUTUBE_API_KEY=os.getenv('YOUTUBE_API_KEY')


def search_youtube(query):
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            part='snippet',
            maxResults=1,
            q=query
        )
        response = request.execute()
        return response['items'][0]['id']['videoId']
    except HttpError as e:
        print(f'An HTTP error occurred: {e}')
        return None
    except Exception as e:
        print(f'An error occurred: {e}')
        return None

def download_audio(video_url, output_path):
    try:
        command = [
            'yt-dlp',
            '-x', '--audio-format', 'mp3',
            '-o', output_path,
            video_url
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while downloading the audio: {e}")
        return False

def play_song_in_background(song_title):
    try:
        # Initialize pygame mixer
        pygame.mixer.init()

        # Search for the song on YouTube using YouTube Data API
        video_id = search_youtube(song_title)
        if not video_id:
            print("Failed to retrieve video ID.")
            return

        video_url = f'https://www.youtube.com/watch?v={video_id}'
        output_path = 'Infer_buffer/song.mp3'

        # Download the audio from YouTube
        if not download_audio(video_url, output_path):
            return

        # Convert the downloaded audio to .wav format for playback
        try:
            sound = AudioSegment.from_file(output_path)
            wav_path = "Infer_buffer/song.wav"
            sound.export(wav_path, format="wav")
        except Exception as e:
            print(f"An error occurred while converting the audio: {e}")
            return

        # Load and play the audio using pygame
        try:
            pygame.mixer.music.load(wav_path)
            pygame.mixer.music.play()
            print(f'Playing "{song_title}" in the background.')

            # Wait for the playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Stop the mixer and unload the music
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"An error occurred while playing the audio: {e}")
        finally:
            # Clean up the downloaded files after playback
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
                if os.path.exists(wav_path):
                    os.remove(wav_path)
            except Exception as e:
                print(f"An error occurred while deleting the files: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Root Function to play song given the user's emotion
def play_song(song=None,emotion=None):
    
    if song is not None:
        play_song_in_background(song)
    
    elif emotion is not None:
        play_song_in_background(get_song(emotion=emotion))
        
