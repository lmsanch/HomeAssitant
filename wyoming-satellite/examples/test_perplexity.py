import asyncio
from openai import OpenAI
import logging

logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

PERPLEXITY_API_KEY = "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"

async def test_perplexity(question):
    try:
        client = OpenAI(
            api_key=PERPLEXITY_API_KEY,
            base_url="https://api.perplexity.ai"
        )
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides clear, concise answers with an academic tone while remaining approachable. Focus on providing accurate, well-structured responses. Do not include citations or references in your response."
            },
            {
                "role": "user",
                "content": question
            }
        ]
        
        _LOGGER.debug(f"Sending question to Perplexity: {question}")
        
        response = client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",
            messages=messages,
        )
        
        answer = response.choices[0].message.content
        print("\nPerplexity Response:")
        print("-" * 40)
        print(answer)
        print("-" * 40)
        
        return answer
        
    except Exception as e:
        _LOGGER.error(f"Error querying Perplexity: {e}")
        return None

async def main():
    # Test with a simple question
    question = "What is the capital of France and what is its population?"
    await test_perplexity(question)

if __name__ == "__main__":
    asyncio.run(main())
