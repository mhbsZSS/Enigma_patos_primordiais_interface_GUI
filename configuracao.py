import json
from helpers_app import resource_path  

def carregar_config():   
    caminho_config = resource_path('config.json') 
    try:
        with open(caminho_config, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except FileNotFoundError:
        print(f"ERRO CRÍTICO: Arquivo 'config.json' não encontrado em {caminho_config}!")
        return None
    except json.JSONDecodeError:
        print("ERRO CRÍTICO: Arquivo 'config.json' está mal formatado!")
        return None

CONFIG = carregar_config()