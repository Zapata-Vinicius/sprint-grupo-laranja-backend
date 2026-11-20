import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.api.rotas_gtfs import router as gtfs_router
from app.api.rotas_posicoes import router as posicoes_router
from app.services.coleta_posicoes import coletar_periodicamente
from app.services.verificacao_gtfs import verificar_periodicamente


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.posicoes = None
    app.state.gtfs = None
    app.state.gtfs_erro = None
    tarefas = [
        asyncio.create_task(coletar_periodicamente(app.state)),
        asyncio.create_task(verificar_periodicamente(app.state)),
    ]
    try:
        yield
    finally:
        for tarefa in tarefas:
            tarefa.cancel()
        for tarefa in tarefas:
            with suppress(asyncio.CancelledError):
                await tarefa


app = FastAPI(lifespan=lifespan)
app.include_router(posicoes_router)
app.include_router(gtfs_router)


@app.get("/")
def inicio():
    return {"mensagem": "Backend funcionando!"}
