import hashlib

import requests


GTFS_URL_PADRAO = "https://www.sptrans.com.br/umbraco/Surface/PerfilDesenvolvedor/BaixarGTFS?memberName=sptrans"


def calcular_hash_gtfs(url):
    """Calcula o SHA-256 do ZIP sem armazenar o arquivo."""
    digest = hashlib.sha256()
    inicio = b""
    with requests.get(url, stream=True, timeout=(15, 60)) as resposta:
        resposta.raise_for_status()
        for trecho in resposta.iter_content(chunk_size=65536):
            if trecho:
                if len(inicio) < 4:
                    inicio = (inicio + trecho)[:4]
                digest.update(trecho)
    if inicio != b"PK\x03\x04":
        raise ValueError("A resposta não parece ser um arquivo ZIP GTFS.")
    return digest.hexdigest()
