import os
import sys
import openai
import pyperclip
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Configuration
API_KEY = "your-qwen-api-key"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-plus"

def translate_and_optimize(prompt_text):
    client = openai.OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL
    )

    system_prompt = (
        "Translate the user's input into English. "
        "Use a direct, literal translation style. "
        "Do not paraphrase or explain. "
        "Output only the translation, nothing else."
    )

    try:
        print(f"{Fore.CYAN}Thinking...{Style.RESET_ALL}")
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            stream=True
        )

        full_response = ""
        print(f"{Fore.GREEN}Translated Prompt:{Style.RESET_ALL}")
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print("\n") # Newline at the end
        return full_response

    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        return None

def main():
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}Usage: qtrans <your prompt text>{Style.RESET_ALL}")
        return

    # Join all arguments to form the prompt (handling spaces in command line args)
    prompt_text = " ".join(sys.argv[1:])
    
    result = translate_and_optimize(prompt_text)
    
    if result:
        try:
            pyperclip.copy(result)
            print(f"{Fore.YELLOW}✓ Copied to clipboard!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to copy to clipboard: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
