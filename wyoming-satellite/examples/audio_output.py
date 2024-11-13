\
# audio_output.py
import logging
import asyncio
import aiohttp
import tempfile
import os
import subprocess

_LOGGER = logging.getLogger(__name__)

class AudioOutput:
    def __init__(self, elevenlabs_api_key):
        self.api_key = elevenlabs_api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.voice_id = "2kIQVvX5soUslVRLDDum"  # Default voice ID - you can change this

    async def text_to_speech(self, text):
        """Convert text to speech using Eleven Labs API"""
        url = f"{self.base_url}/text-to-speech/{self.voice_id}/stream"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        # Create a temporary file for the audio
                        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                            temp_file.write(await response.read())
                            return temp_file.name
                    else:
                        _LOGGER.error(f"Error from Eleven Labs API: {response.status}")
                        return None
        except Exception as e:
            _LOGGER.error(f"Error in text_to_speech: {e}")
            return None

    async def play_audio(self, audio_file):
        """Play audio file through default audio output"""
        try:
            cmd = [
                'aplay',
                '-r', '22050',  # Match your service configuration
                '-c', '1',
                '-f', 'S16_LE',
                '-t', 'raw',
                audio_file
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                _LOGGER.error(f"Error playing audio: {stderr.decode()}")

            # Clean up the temporary file
            os.unlink(audio_file)

        except Exception as e:
            _LOGGER.error(f"Error in play_audio: {e}")




