from openai import OpenAI
import os
import pandas as pd
from datetime import datetime
from ..prompts.prompt_assembly import *
from ..prompts.starting_prompt import create_starting_prompt

def prompt_deepseek(text: str, model: str = "deepseek-chat") -> str:

    deepseek_client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",)
    
    response = deepseek_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        temperature=0.0,
    )

    if not response.choices:
        raise RuntimeError("No choices returned from DeepSeek.")

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Output from DeepSeek was None.")

    return content


def prompt_chatgpt(text: str, model: str = "gpt-4.1-mini") -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        temperature=0.0,
    )

    if not response.choices:
        raise RuntimeError("No choices returned from ChatGPT.")

    content = response.choices[0].message.content
    if content is None:
        raise RuntimeError("Output from ChatGPT was None.")

    return content

def prompt_grok(text: str, model: str) -> str:

    client = OpenAI(
    api_key=os.environ["XAI_API_KEY"],
    base_url="https://api.x.ai/v1",
)
    response = client.responses.create(
        model=model,
        input=[
            {"role": "user", "content": text},
        ],
    )
    if response is None:
        raise RuntimeError("Response from Grok was None.")
    if not response.output_text:
        raise RuntimeError("Output text from Grok was None.")
    return response.output_text

def prompt_deep_research(skeleton, libb) -> tuple[str, str]:

    model = libb._model_path.replace("multi_model_ipo/artifacts/", "")
    text = create_deep_research_prompt(skeleton, libb)
        
    if model == "deepseek":
        return prompt_deepseek(text), text
    elif model == "gpt-4.1":
        return prompt_chatgpt(text), text
    else:
        raise RuntimeError(f"Unidentified model: {model}")

def prompt_daily_report(skeleton, libb) -> tuple[str, str]:

    model = libb._model_path.replace("multi_model_ipo/artifacts/", "")
    text = create_daily_prompt(skeleton, libb)
    if model == "deepseek":
        return prompt_deepseek(text), text
    elif model == "gpt-4.1":
        return prompt_chatgpt(text), text
    else:
        raise RuntimeError(f"Unidentified model: {model}")
    
def prompt_starting_report(prompt: str, libb: LIBBmodel):

    model = libb._model_path.replace("multi_model_ipo/artifacts/", "")

    if model == "deepseek":
        return prompt_deepseek(prompt)
    elif model == "gpt-4.1":
        return prompt_chatgpt(prompt)
    else:
        raise RuntimeError(f"Unidentified model: {model}")