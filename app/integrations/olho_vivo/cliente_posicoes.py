import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_URL = "https://api.olhovivo.sptrans.com.br/v2.1"
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


def buscar_posicoes(token):
    with requests.Session() as sessao:
        resposta = sessao.post(
            f"{BASE_URL}/Login/Autenticar", params={"token": token}, timeout=15
        )
        resposta.raise_for_status()
        if resposta.json() is not True:
            raise ValueError("Autenticação na API Olho Vivo recusada.")

        resposta = sessao.get(f"{BASE_URL}/Posicao", timeout=15)
        resposta.raise_for_status()
        return resposta.json()


def main():
    load_dotenv(ENV_PATH)
    token = os.getenv("OLHO_VIVO_TOKEN")
    if not token:
        print("Defina OLHO_VIVO_TOKEN no arquivo .env.", file=sys.stderr)
        return 1

    try:
        posicoes = buscar_posicoes(token)
    except requests.RequestException:
        print("Não foi possível acessar a API Olho Vivo.", file=sys.stderr)
        return 1
    except ValueError as erro:
        print(f"Falha ao processar a resposta da API Olho Vivo: {erro}", file=sys.stderr)
        return 1

    print(json.dumps(posicoes, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
