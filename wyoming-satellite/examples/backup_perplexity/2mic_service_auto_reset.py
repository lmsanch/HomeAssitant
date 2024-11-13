import asyncio
import argparse
from wyoming.info import Info
from wyoming.server import AsyncServer
import logging
from functools import partial
from audio_capture import AudioCaptureHandler
import config

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

class LEDHandler:
    def __init__(self):
        self.reset_timer = None
        self.led_state = "idle"
        self.audio_handler = AudioCaptureHandler(whisper_url=config.WHISPER_URL)
        
    async def set_leds(self, state):
        self.led_state = state
        _LOGGER.debug(f"LED State: {state}")
        
    async def schedule_reset(self):
        if self.reset_timer:
            self.reset_timer.cancel()
        self.reset_timer = asyncio.create_task(self._reset_after_delay())
        
    async def _reset_after_delay(self):
        await asyncio.sleep(5)  # 5 second timeout
        await self.set_leds("idle")
        _LOGGER.debug("Auto-reset to idle state")

    async def handle_wake_word(self):
        """Handle wake word detection with enhanced processing"""
        try:
            # Set LED state
            await self.set_leds("active")
            _LOGGER.debug("Wake word detected - Starting processing")
            
            # Process audio and get response
            result = await self.audio_handler.process_wake_word_detected()
            if result:
                _LOGGER.info(f"Processed result: {result}")
            
            # Schedule LED reset
            await self.schedule_reset()
            
        except Exception as e:
            _LOGGER.error(f"Error in wake word handling: {e}")
            await self.set_leds("idle")

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", required=True, help="URI to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    led_handler = LEDHandler()
    
    async def handle_client(client):
        try:
            async for event in client:
                if event.type == "run-pipeline":
                    _LOGGER.debug("Wake word detected - Starting pipeline")
                    await led_handler.handle_wake_word()
        except Exception as e:
            _LOGGER.error(f"Error in client handler: {e}")
    
    _LOGGER.debug("Starting LED service with enhanced processing")
    
    # Run server
    async with AsyncServer.from_uri(args.uri) as server:
        await server.run(partial(handle_client))

if __name__ == "__main__":
    asyncio.run(main())
