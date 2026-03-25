#!/usr/bin/env python3

import argparse
import requests
import subprocess
import time
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

# ---------- OLLAMA ----------

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

# ---------- CLEAN OUTPUT ----------

def clean_output(text):
    text = text.replace("```", "")

    unwanted = [
        "Here is",
        "Explanation:",
        "Output:",
        "[Response]",
        "Sure,",
        "Here’s",
        "Here is the code:",
        "This code",
    ]

    for word in unwanted:
        text = text.replace(word, "")

    return text.strip()

# ---------- ASK OLLAMA (FIXED STREAMING) ----------

def ask_ollama(prompt, model, stream=True):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": 200,
                "temperature": 0.3
            }
        },
        stream=stream
    )

    full = ""

    if stream:
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))

                    chunk = data.get("response", "")
                    if chunk:
                        print(chunk, end="", flush=True)
                        full += chunk

                except:
                    continue
        print()

    else:
        full = response.json().get("response", "")

    return full

# ---------- PROMPT BUILDER ----------

def build_prompt(args, user_input):
    base_rules = (
        "STRICT RULES:\n"
        "- Do NOT explain anything\n"
        "- Do NOT use markdown or ```\n"
        "- Output ONLY final result\n"
    )

    if args.shell:
        return base_rules + f"\nReturn ONLY a shell command:\n{user_input}"

    if args.code:
        return base_rules + f"\nReturn ONLY raw code. NO text:\n{user_input}"

    if args.preprompt:
        return base_rules + f"\n{args.preprompt}\n{user_input}"

    return base_rules + "\n" + user_input

# ---------- SHELL ----------

def run_shell(command, auto=False):
    print("\n" + command)

    if auto:
        subprocess.run(command, shell=True)
    else:
        confirm = input("\nExecute? (y/n): ")
        if confirm.lower() == "y":
            subprocess.run(command, shell=True)

# ---------- INTERACTIVE ----------

def interactive_mode(model):
    print("Interactive mode (type 'exit' to quit)\n")

    while True:
        user = input(">>> ")
        if user.lower() in ["exit", "quit"]:
            break

        response = ask_ollama(user, model, stream=True)
        print()

# ---------- MAIN ----------

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("prompt", nargs="*", help="Your prompt")

    parser.add_argument("-s", "--shell", action="store_true")
    parser.add_argument("-c", "--code", action="store_true")
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-w", "--whole", action="store_true")
    parser.add_argument("-i", "--interactive", action="store_true")

    parser.add_argument("-y", action="store_true")
    parser.add_argument("--model", default="qwen:0.5b")
    parser.add_argument("--preprompt")

    args = parser.parse_args()

    # ensure ollama running
    if not check_ollama():
        start_ollama()

    # interactive
    if args.interactive:
        interactive_mode(args.model)
        return

    if not args.prompt:
        print("Usage: tgpt 'your prompt'")
        return

    user_input = " ".join(args.prompt)
    final_prompt = build_prompt(args, user_input)

    stream = not args.whole

    response = ask_ollama(final_prompt, args.model, stream=stream)

    # clean only in whole mode (important fix)
    if args.whole:
        response = clean_output(response)
        print(response)

    # shell execution
    if args.shell:
        run_shell(response, args.y)

# ---------- RUN ----------

if __name__ == "__main__":
    main()
