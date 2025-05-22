# utils/file_manager.py
import json
import os

CONFIG_FILE = "app_settings.json" # Poderia estar em um local de dados do app

def _load_settings() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                # Verifica se o arquivo não está vazio antes de tentar carregar o JSON
                content = f.read()
                if not content:
                    print(f"Aviso: O arquivo de configurações '{CONFIG_FILE}' está vazio.")
                    return {}
                return json.loads(content) # Usa json.loads para ler de uma string
        except json.JSONDecodeError:
            print(f"Aviso: Erro ao decodificar JSON de '{CONFIG_FILE}'. O arquivo pode estar corrompido ou mal formatado.")
            return {} # Retorna dict vazio em caso de erro de JSON
        except Exception as e:
            print(f"Aviso: Erro inesperado ao ler '{CONFIG_FILE}': {e}")
            return {}
    return {}

def _save_settings(settings: dict):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar configurações em '{CONFIG_FILE}': {e}")


def get_last_input_directory() -> str | None:
    settings = _load_settings()
    return settings.get("last_input_directory")

def set_last_input_directory(path: str):
    settings = _load_settings()
    settings["last_input_directory"] = path
    _save_settings(settings)

# --- Funções para diretório de SAÍDA ---
def get_last_output_directory() -> str | None:
    """
    Obtém o último diretório usado para salvar arquivos SVG.
    """
    settings = _load_settings()
    return settings.get("last_output_directory")

def set_last_output_directory(path: str):
    """
    Define o último diretório usado para salvar arquivos SVG.
    """
    settings = _load_settings()
    settings["last_output_directory"] = path
    _save_settings(settings)

# Você pode adicionar outras funções aqui no futuro, se necessário,
# como para lembrar o último valor do slider de epsilon, por exemplo:
#
# def get_last_epsilon_factor() -> float | None:
#     settings = _load_settings()
#     epsilon = settings.get("last_epsilon_factor")
#     if isinstance(epsilon, (float, int)): # Garante que é um número
#         return float(epsilon)
#     return None

# def set_last_epsilon_factor(factor: float):
#     settings = _load_settings()
#     settings["last_epsilon_factor"] = factor
#     _save_settings(settings)

if __name__ == '__main__':
    # Pequeno teste (opcional)
    print("Testando file_manager...")
    set_last_input_directory("caminho/para/entrada")
    print(f"Último dir de entrada: {get_last_input_directory()}")

    set_last_output_directory("caminho/para/saida")
    print(f"Último dir de saída: {get_last_output_directory()}")

    # set_last_epsilon_factor(0.007)
    # print(f"Último fator epsilon: {get_last_epsilon_factor()}")

    # Limpa o arquivo de teste (ou comente as linhas abaixo para mantê-lo)
    # if os.path.exists(CONFIG_FILE):
    #     os.remove(CONFIG_FILE)
    #     print(f"Arquivo de teste '{CONFIG_FILE}' removido.")