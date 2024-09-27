import os
import argparse
import json
import urllib
import openai
from pprint import pprint
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

model_mapping = {
    "gpt35": {
        "azure": "GPT35-Turbo",
        "openai": "gpt-3.5-turbo"
    },
    "gpt35-16k": {
        "azure": "GPT35-Turbo-16k",
        "openai": "gpt-3.5-turbo-16k"
    },
    "gpt4": {
        "azure": "GPT4",
        "openai": "gpt-4"
    },
    "gpt4-32k": {
        "azure": "GPT4-32k",
        "openai": "gpt-4-32k"
    }
}

max_tokens_model_mapping = {
    "gpt3": 4000,
    "gpt35": 4000,
    "gpt35-16k": 16000,
    "gpt4": 8000,
    "gpt4-32k": 32000,
    "mistral": 8000,
    "mixtral": 8000
}

@retry(wait=wait_exponential(min=1, max=60), stop=stop_after_attempt(6))
def get_response(model_name, service, prompt, temperature=0.0, time_wait=5):
    # Check len of prompt
    max_tokens = int(max_tokens_model_mapping[model_name]*.35)
    max_tokens_req = int(max_tokens_model_mapping[model_name]*.2)

    prompt[0]['content'] = ' '.join(prompt[0]['content'].split(' ')[:max_tokens])
   
    if service == 'azure':
        openai.api_type = "azure"
        openai.api_key = os.getenv("AZURE_OPENAI_KEY")
        openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT") 
        openai.api_version = "2023-05-15"  # subject to change
        if model_name == 'gpt3':
            response = openai.Completion.create(
                                                prompt=prompt,
                                                deployment_id=model_mapping[model_name][service],
                                                temperature=temperature,
                                                max_tokens=max_tokens_req
                                                )
        else:
            response = openai.ChatCompletion.create(
                                                    messages=prompt,
                                                    deployment_id=model_mapping[model_name][service],
                                                    temperature=temperature,
                                                    max_tokens=max_tokens_req
                                                    )
        
    elif service == 'openai':
        openai.api_key = os.getenv("OPENAI_KEY")
        openai.organization = os.getenv("OPENAI_ORG")
        openai.api_version = "2020-11-07"
        if model_name == 'gpt3':
            response = openai.Completion.create(
                                                prompt=prompt,
                                                model=model_mapping[model_name][service],
                                                temperature=temperature,
                                                max_tokens=max_tokens_req
                                                )
        else:
            response = openai.ChatCompletion.create(
                                                    messages=prompt,
                                                    model=model_mapping[model_name][service],
                                                    temperature=temperature,
                                                    max_tokens=max_tokens_req
                                                    )
    elif service == 'aml':
        
        if model_name == 'mistral':
            url = os.getenv("AZURE_ML_MISTRAL_ENDPOINT")
            api_key = os.getenv("AZURE_ML_MISTRAL_KEY")
            az_model_deployment = 'mistralai-mistral-7b-instruct-5'
            

        elif model_name == 'mixtral':
            url = os.getenv("AZURE_ML_MIXTRAL_ENDPOINT")
            api_key = os.getenv("AZURE_ML_MIXTRAL_KEY")
            az_model_deployment = 'mistralai-mixtral-8x7b-instru-4'
        
        data = {
            "input_data": {
                "input_string": [
                    {
                        "role": "user",
                        "content": prompt[0]['content']
                    }
                ],
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens_req
                }
            }
        }

        body = str.encode(json.dumps(data))
        headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key), 'azureml-model-deployment': az_model_deployment}
        res = urllib.request.urlopen(urllib.request.Request(url, body, headers))
        response = {'choices':[{'message':{'content':json.loads(res.read())['output']}}]}
    
    time.sleep(time_wait)
    return response


def test_apis():
    messages = [{"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Who won the world series in 2020?"},
                {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
                {"role": "user", "content": "Where was it played?"}]
    completion_prompt = "Where was the world series in 2020 played?"
    for service in ['openai', 'azure']:
        for model_name in model_mapping.keys():
            try:
                prompt = completion_prompt if model_name == 'gpt3' else messages
                response = get_response(model_name, service, prompt)
                pprint(response)
            except Exception as e:
                print(f'Error {e} with model {service}-{model_name}')


def test_mistral():
    messages = [{"role": "user", "content": "Who won the world series in 2020?"}]

    for model_name in ['mistral', 'mixtral']:
        response = get_response(model_name, 'aml', messages)
        pprint(response)


if __name__=="__main__":
    test_apis()
