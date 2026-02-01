import os
import sys
import json
import openai
import requests
import pyperclip
from abc import ABC, abstractmethod
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"{Fore.RED}Error: Config file not found at {CONFIG_FILE}{Style.RESET_ALL}")
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

class Translator(ABC):
    @abstractmethod
    def translate(self, prompt_text):
        pass

class QwenTranslator(Translator):
    def __init__(self, config):
        self.api_key = config['api_key']
        self.base_url = config['base_url']
        self.model = config['model']
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        # Using the "literal" system prompt from previous iteration
        self.system_prompt = (
            "Translate the user's input into English. "
            "Use a direct, literal translation style. "
            "Do not paraphrase or explain. "
            "Output only the translation, nothing else."
        )

    def translate(self, prompt_text):
        try:
            print(f"{Fore.CYAN}Thinking (Qwen)...{Style.RESET_ALL}")
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
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
            
            print("\n")
            return full_response

        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None

class BaiduTranslator(Translator):
    def __init__(self, config):
        self.appid = config['appid']
        self.api_key = config['api_key']
        self.model_type = config.get('model_type', 'llm')
        self.url = "https://fanyi-api.baidu.com/ait/api/aiTextTranslate"

    def translate(self, prompt_text):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "appid": self.appid,
            "from": "zh",
            "to": "en",
            "q": prompt_text,
            "model_type": self.model_type
        }

        try:
            print(f"{Fore.CYAN}Thinking (Baidu)...{Style.RESET_ALL}")
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Expected response: {"from":"zh","to":"en","trans_result":[{"src":"你好","dst":"Hello"}]}
            data = response.json()
            
            if "trans_result" in data and len(data["trans_result"]) > 0:
                result = data["trans_result"][0]["dst"]
                print(f"{Fore.GREEN}Translated Prompt:{Style.RESET_ALL}")
                print(result)
                print("\n")
                return result
            else:
                print(f"{Fore.RED}Error: Unexpected response format: {data}{Style.RESET_ALL}")
                return None

        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None

def get_translator(config):
    provider_name = config.get('current_provider', 'qwen')
    providers_config = config.get('providers', {})
    
    if provider_name not in providers_config:
        print(f"{Fore.RED}Error: Provider '{provider_name}' not found in config.{Style.RESET_ALL}")
        sys.exit(1)
        
    provider_config = providers_config[provider_name]
    
    if provider_name == 'qwen':
        return QwenTranslator(provider_config)
    elif provider_name == 'baidu':
        return BaiduTranslator(provider_config)
    else:
        print(f"{Fore.RED}Error: Unknown provider '{provider_name}'{Style.RESET_ALL}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print(f"{Fore.YELLOW}Usage: atrans <your prompt text>{Style.RESET_ALL}")
        return

    # Join all arguments to form the prompt
    prompt_text = " ".join(sys.argv[1:])
    
    config = load_config()
    translator = get_translator(config)
    
    result = translator.translate(prompt_text)
    
    if result:
        try:
            pyperclip.copy(result)
            print(f"{Fore.YELLOW}✓ Copied to clipboard!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Failed to copy to clipboard: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
