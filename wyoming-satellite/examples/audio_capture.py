import asyncio
import aiohttp
import logging
import subprocess
import tempfile
import os
from perplexity_client import PerplexityClient
from audio_output import AudioOutput
import config

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

class AudioCaptureHandler:
    def __init__(self, whisper_url=config.WHISPER_URL):
        self.whisper_url = whisper_url
        self.perplexity_client = PerplexityClient()
        self.audio_output = AudioOutput(config.ELEVENLABS_API_KEY)

    async def capture_audio(self, duration=5):
        """Capture audio for specified duration"""
        _LOGGER.debug("Starting audio capture")
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            cmd = [
                'arecord',
                '-D', 'plughw:CARD=seeed2micvoicec,DEV=0',
                '-r', '16000',
                '-c', '1',
                '-f', 'S16_LE',
                '-d', str(duration),
                '-t', 'wav',
                temp_wav.name
            ]
            try:
                _LOGGER.debug(f"Running command: {' '.join(cmd)}")
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    _LOGGER.error(f"Error capturing audio: {stderr.decode()}")
                    return None
                _LOGGER.debug(f"Audio captured successfully to {temp_wav.name}")
                return temp_wav.name
            except Exception as e:
                _LOGGER.error(f"Exception during audio capture: {e}")
                return None

    async def send_to_whisper(self, audio_file_path):
        """Send audio file to Whisper service"""
        if not audio_file_path or not os.path.exists(audio_file_path):
            _LOGGER.error("No audio file to send")
            return None

        _LOGGER.debug(f"Sending audio file {audio_file_path} to Whisper")
        try:
            async with aiohttp.ClientSession() as session:
                with open(audio_file_path, 'rb') as audio_file:
                    files = {'file': audio_file}
                    async with session.post(self.whisper_url, data=files) as response:
                        result = await response.json()
                        _LOGGER.debug(f"Whisper response: {result}")
                        return result
        except Exception as e:
            _LOGGER.error(f"Error sending to Whisper: {e}")
            return None
        finally:
            # Clean up temp file
            try:
                os.unlink(audio_file_path)
            except Exception as e:
                _LOGGER.error(f"Error deleting temporary file: {e}")

    async def process_wake_word_detected(self):
        """Main processing function"""
        try:
            # 1. Capture audio
            _LOGGER.debug("Starting wake word processing")
            audio_file = await self.capture_audio(duration=5)
            if not audio_file:
                _LOGGER.error("Failed to capture audio")
                return None

            # 2. Send to Whisper
            whisper_result = await self.send_to_whisper(audio_file)
            if not whisper_result or 'transcription' not in whisper_result:
                _LOGGER.error("Failed to get transcription from Whisper")
                return None

            transcription = whisper_result['transcription']
            _LOGGER.info(f"Transcription: {transcription}")

            # 3. Query Perplexity
            perplexity_response = await self.perplexity_client.query(transcription)
            if not perplexity_response:
                _LOGGER.error("Failed to get response from Perplexity")
                return None

            # 4. Convert response to speech and play
            _LOGGER.debug("Converting response to speech")
            audio_file = await self.audio_output.text_to_speech(perplexity_response)
            if audio_file:
                _LOGGER.debug("Playing audio response")
                await self.audio_output.play_audio(audio_file)
            else:
                _LOGGER.error("Failed to generate speech from response")

            return {
                "transcription": transcription,
                "response": perplexity_response
            }

        except Exception as e:
            _LOGGER.error(f"Error in process_wake_word_detected: {e}")
            return None

    async def cleanup(self):
        """Cleanup any resources"""
        try:
            # Add any cleanup code here if needed
            pass
        except Exception as e:
            _LOGGER.error(f"Error during cleanup: {e}")

async def main():
    """Test function"""
    handler = AudioCaptureHandler()
    try:
        result = await handler.process_wake_word_detected()
        print(f"Final result: {result}")
    finally:
        await handler.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
