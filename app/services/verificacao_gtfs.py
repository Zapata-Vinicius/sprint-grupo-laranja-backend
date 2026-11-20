import asyncio
from datetime import datetime, timezone
import logging
import os

import requests
from dotenv import load_dotenv

from app.integrations.gtfs.cliente_gtfs import GTFS_URL_PADRAO, calcular_hash_gtfs
from app.integrations.olho_vivo.cliente_posicoes import ENV_PATH


INTERVALO_SEGUNDOS = 60 * 60
logger = logging.getLogger(__name__)


async def verificar_gtfs(estado):
    load_dotenv(ENV_PATH)
    url = os.getenv("GTFS_URL") or GTFS_URL_PADRAO
    try:
        novo_hash = await asyncio.to_thread(calcular_hash_gtfs, url)
    except (requests.RequestException, ValueError):
        estado.gtfs_erro = "Falha ao consultar um arquivo ZIP GTFS válido."
        logger.warning("Falha ao consultar o GTFS; nova tentativa no próximo ciclo.")
        return

    anterior = estado.gtfs
    estado.gtfs = {
        "verificado_em": datetime.now(timezone.utc).isoformat(),
        "alterado": None if anterior is None else anterior["sha256"] != novo_hash,
        "sha256": novo_hash,
    }
    estado.gtfs_erro = None
    logger.info("Verificação do GTFS concluída; alterado=%s", estado.gtfs["alterado"])


async def verificar_periodicamente(estado):
    while True:
        await verificar_gtfs(estado)
        await asyncio.sleep(INTERVALO_SEGUNDOS)
