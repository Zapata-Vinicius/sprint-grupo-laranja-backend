import asyncio
import logging
import os

import requests
from dotenv import load_dotenv

from app.integrations.olho_vivo.cliente_posicoes import ENV_PATH, buscar_posicoes


INTERVALO_SEGUNDOS = 30
logger = logging.getLogger(__name__)


async def coletar_periodicamente(estado):
    loop = asyncio.get_running_loop()
    proxima_coleta = loop.time()
    while True:
        await executar_coleta(estado)
        proxima_coleta += INTERVALO_SEGUNDOS
        agora = loop.time()
        if proxima_coleta <= agora:
            proxima_coleta += (int((agora - proxima_coleta) // INTERVALO_SEGUNDOS) + 1) * INTERVALO_SEGUNDOS
        await asyncio.sleep(proxima_coleta - agora)


async def executar_coleta(estado):
    load_dotenv(ENV_PATH)
    token = os.getenv("OLHO_VIVO_TOKEN")
    if not token:
        logger.error("Token do Olho Vivo não configurado.")
        return

    try:
        posicoes = await asyncio.to_thread(buscar_posicoes, token)
        estado.posicoes = posicoes
        logger.info("Posições coletadas com sucesso.")
    except (requests.RequestException, ValueError):
        logger.warning("Falha ao coletar posições do Olho Vivo; nova tentativa no próximo ciclo.")
