#!/usr/bin/env python3

import argparse
import requests
import subprocess
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

def check_ollama():
    try:
        requests.get("http://localhost:11434")
        return True
    except:
        return False

def start_ollama():
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

# ---------- STRONG CLEANER ----------

def clean_output(text):
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        # remove markdown / junk
        if line.startswith("```"):
            continue
        if line.lower().startswith("here is"):
            continue
        if line.lower().startswith("a simple"):
            continue
        if line.lower() == "c":
            continue
        if line.lower().startswith("explanation"):
            continue

        cleaned.append(line)

    return "\n".join(cleaned).strip()

# ---------- ASK OLLAMA ----------

def ask(prompt, model):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 400,
                "temperature": 0.05
            }
        }
    )
    return response.json().get("response", "")

# ---------- MAIN ----------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("prompt", nargs="*")
    parser.add_argument("-c", "--code", action="store_true")
    parser.add_argument("-f", "--fast", action="store_true")

    args = parser.parse_args()

    if not check_ollama():
        start_ollama()

    if not args.prompt:
        print("Usage: tgpt \"your prompt\"")
        return

    user_input = " ".join(args.prompt)

    # ---------- MODEL ----------
    if args.fast:
        model = "qwen2:0.5b"
    elif args.code:
        model = "qwen2:1.5b"
    else:
        model = "qwen2:0.5b"

    # ---------- ULTRA STRICT PROMPT ----------
    if args.code:
        prompt = (
            "ONLY output valid C code.\n"
            "NO explanation.\n"
            "NO extra text.\n"
            "NO labels.\n"
            "Complete program with main().\n"
            + user_input
        )
    else:
        prompt = user_input

    result = ask(prompt, model)
    result = clean_output(result)

    print(result)

# ---------- RUN ----------

if __name__ == "__main__":
    main()
