import asyncio
import logging
import subprocess
import tempfile
import os

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

async def test_audio_capture(duration=5):
    """Test audio capture"""
    _LOGGER.debug("Starting audio capture test")
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
            print("\nRecording for 5 seconds... Please speak something.")
            
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
            
            # Test playback
            print("\nPlaying back the recording...")
            playback_cmd = [
                'aplay',
                temp_wav.name
            ]
            
            play_process = await asyncio.create_subprocess_exec(
                *playback_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await play_process.communicate()
            
            return temp_wav.name
            
        except Exception as e:
            _LOGGER.error(f"Exception during audio capture: {e}")
            return None
        finally:
            # Clean up temp file after playback
            if os.path.exists(temp_wav.name):
                os.unlink(temp_wav.name)

async def main():
    print("Testing audio capture and playback...")
    await test_audio_capture()
    print("\nTest completed!")

if __name__ == "__main__":
    asyncio.run(main())
