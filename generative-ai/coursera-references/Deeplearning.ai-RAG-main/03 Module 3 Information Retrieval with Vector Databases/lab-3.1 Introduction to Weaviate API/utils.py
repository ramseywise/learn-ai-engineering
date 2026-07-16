from flask import Flask, request, jsonify
import threading
from sentence_transformers import SentenceTransformer
import json
import requests
from typing import Union
import os
from contextlib import redirect_stdout, redirect_stderr
import logging
from typing import Dict, List
import together
import torch
import os
import subprocess
import signal
import sys
import logging
import httpx
from openai import OpenAI, DefaultHttpxClient


# Custom transport to bypass SSL verification
transport = httpx.HTTPTransport(local_address="0.0.0.0", verify=False)

# Create a DefaultHttpxClient instance with the custom transport
http_client = DefaultHttpxClient(transport=transport)

# Define utility functions and classes
def generate_embedding(prompt: str, model: str = "BAAI/bge-base-en-v1.5", together_api_key = None, **kwargs):
    payload = {
        "model": model,
        "input": prompt,
        **kwargs
    }
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        client = OpenAI(
    api_key = '', # Set any as dlai proxy does not use it. Set the together api key if using the together endpoint
    base_url="http://proxy.dlai.link/coursera_proxy/together/", # If using together endpoint, add it here https://api.together.xyz/
   http_client=http_client, # ssl bypass to make it work via proxy calls, remove it if running with together.ai endpoint 
)
        try:
            json_dict = client.embeddings.create(**payload).model_dump()
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


def generate_with_single_input(prompt: str, 
                               role: str = 'user', 
                               top_p: float = None, 
                               temperature: float = None,
                               max_tokens: int = 500,
                               model: str ="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                               together_api_key = None,
                              **kwargs):
    
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
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: f{response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}\nResponse: {response.text}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"Failed to get correct output dict. Please try again. Error: {e}")
    return output_dict


def generate_with_multiple_input(messages: List[Dict], 
                               top_p: float = 1, 
                               temperature: float = 1,
                               max_tokens: int = 500,
                               model: str ="meta-llama/Llama-3.2-3B-Instruct-Turbo", 
                                together_api_key = None,
                                **kwargs):
    payload = {
        "model": model,
        "messages": messages,
        "top_p": top_p,
        "temperature": temperature,
        "max_tokens": max_tokens,
        **kwargs
              }
    if (not together_api_key) and ('TOGETHER_API_KEY' not in os.environ):
        url = os.path.join('https://proxy.dlai.link/coursera_proxy/together', 'v1/chat/completions')   
        response = requests.post(url, json = payload, verify=False)
        if not response.ok:
            raise Exception(f"Error while calling LLM: f{response.text}")
        try:
            json_dict = json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to get correct output from LLM call.\nException: {e}\nResponse: {response.text}")
    else:
        if together_api_key is None:
            together_api_key = os.environ['TOGETHER_API_KEY']
        client = Together(api_key =  together_api_key)
        json_dict = client.chat.completions.create(**payload).model_dump()
        json_dict['choices'][-1]['message']['role'] = json_dict['choices'][-1]['message']['role'].name.lower()
    try:
        output_dict = {'role': json_dict['choices'][-1]['message']['role'], 'content': json_dict['choices'][-1]['message']['content']}
    except Exception as e:
        raise Exception(f"Failed to get correct output dict. Please try again. Error: {e}")
    return output_dict




def print_object_properties(obj: Union[dict, list]) -> None:
    t = ''
    if isinstance(obj, dict):
        for x,y in obj.items():
            if x == 'article_content':
                t += f'{x}: {y[:100]}...(truncated)\n'
            elif x == 'main_vector':
                t+= f'{x}: {y[:30]}...(truncated)\n'
            elif x == 'chunk':
                t+= f'{x}: {y[:100]}...(truncated)\n'

            else:
                t+= f'{x}: {y}\n'
    else:
        for l in obj:
            for x,y in l.items():
                if x == 'article_content':
                    t += f'{x}: {y[:100]}...(truncated)\n'
                elif x == 'main_vector':
                    t+= f'{x}: {y[:30]}...(truncated)\n'
                elif x == 'chunk':
                    t+= f'{x}: {y[:100]}...(truncated)\n'

                else:
                    t+= f'{x}: {y}\n'
            t += "\n\n"
        
    print(t)


def print_properties(item):
    print(
        json.dumps(
            item.properties,
            indent=2, sort_keys=True, default=str
        )
    )

import subprocess
from contextlib import contextmanager

@contextmanager
def suppress_subprocess_output():
    """
    Context manager that suppresses the standard output and error 
    of any subprocess.Popen calls within this context.
    """
    # Store the original Popen
    original_popen = subprocess.Popen

    def patched_popen(*args, **kwargs):
        # Redirect the stdout and stderr to subprocess.DEVNULL
        kwargs['stdout'] = subprocess.DEVNULL
        kwargs['stderr'] = subprocess.DEVNULL
        return original_popen(*args, **kwargs)

    try:
        # Apply the patch by replacing subprocess.Popen with patched_popen
        subprocess.Popen = patched_popen
        # Yield control back to the context
        yield
    finally:
        # Ensure that the original Popen method is restored
        subprocess.Popen = original_popen
