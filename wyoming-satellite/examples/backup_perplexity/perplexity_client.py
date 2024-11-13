# perplexity_client.py
import logging
import re
from openai import OpenAI
import config

_LOGGER = logging.getLogger(__name__)

class PerplexityClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )

    def clean_response(self, text):
        """Clean up response text by removing citations and other unwanted formatting"""
        # Remove citations like [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        # Remove trailing periods if there are multiple
        text = re.sub(r'\.+$', '.', text.strip())
        # Remove any extra whitespace
        text = ' '.join(text.split())
        return text

    async def query(self, text):
        """Query Perplexity API with the given text"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides clear, concise answers with an academic tone while remaining approachable. Focus on providing accurate, well-structured responses. Do not include citations or references in your response."
                },
                {
                    "role": "user",
                    "content": text
                }
            ]

            response = self.client.chat.completions.create(
                model=config.PERPLEXITY_MODEL,
                messages=messages,
            )

            answer = response.choices[0].message.content
            cleaned_answer = self.clean_response(answer)

            _LOGGER.info(f"Perplexity response: {cleaned_answer}")
            print("\nPerplexity Response:")
            print("-" * 40)
            print(cleaned_answer)
            print("-" * 40)

            return cleaned_answer

        except Exception as e:
            _LOGGER.error(f"Error querying Perplexity: {e}")
            return None
