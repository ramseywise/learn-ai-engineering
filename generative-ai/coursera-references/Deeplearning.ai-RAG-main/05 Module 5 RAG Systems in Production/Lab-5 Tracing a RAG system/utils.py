# Importing necessary modules and libraries
from flask import Flask, request, jsonify
import json
import os
import requests
from contextlib import contextmanager
import subprocess
import joblib
import time
from together import Together

def make_url():
    lab_id = os.environ['WORKSPACE_ID']
    url = f"http://{lab_id}.labs.coursera.org"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    
    print(f"{BOLD}FOLLOW THIS URL TO OPEN THE UI: {url}{RESET}")

def restart_kernel():
    # This forces the kernel to restart by exiting Python
    import os
    os._exit(00)  # Exiting the Python process itself

# Define utility functions and classes
def generate_with_single_input(prompt: str, role: str = 'user', top_p: float = None, temperature: float = None,
                               max_tokens: int = 500, model: str = "meta-llama/Llama-3.2-3B-Instruct-Turbo",
                               together_api_key=None, **kwargs):
    if top_p is None:
        top_p = 'none'
    if temperature is None:
        temperature = 'none'
    payload = {
        "model": model,
        "messages": [{'role': role, 'content': prompt}],
        "top_p": top_p,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
    }
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/chat/completions')
        response = requests.post(url, json=payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: f{response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key=together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'],
                       'content': json_dict['choices'][-1]['message']['content'],
                      'total_tokens':json_dict['usage']['total_tokens']}
    except Exception as e:
        raise Exception(f"Failed to get correct output dict. Please try again. Error: {e}")
    return output_dict


# Define utility functions and classes
def generate_embedding(prompt: str, model: str = "BAAI/bge-base-en-v1.5", together_api_key = None, **kwargs):
    payload = {
        "model": model,
        "input": prompt,
        **kwargs
    }
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/embeddings')
        response = requests.post(url, json=payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: f{response.text}")
        try:
            json_dict = json.loads(response.text)
            return json_dict['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key=together_api_key)
        try:
            json_dict = client.embeddings.create(**payload).model_dump()
            return json_dict['data'][0]['embedding']
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}")