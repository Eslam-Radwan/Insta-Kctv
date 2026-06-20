import os
import argparse
import json
from pprint import pprint
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_response(model_name, prompt, temperature=0.0, time_wait=5):
    prompt[0]['content'] = ' '.join(prompt[0]['content'].split(' '))

    response = client.chat.completions.create(
        messages=prompt,
        model=model_name,
        temperature=temperature,
    )
    time.sleep(time_wait)
    

    return {"choices": [{"message": {"content": response.choices[0].message.content}}]}


if __name__=="__main__":
    messages = [{"role": "user", "content": "Hello"}]
    response = get_response("gpt35", messages)
    pprint(response)
