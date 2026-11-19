import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.api.rotas_posicoes import router as posicoes_router
from app.services.coleta_posicoes import coletar_periodicamente


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.posicoes = None
    tarefa = asyncio.create_task(coletar_periodicamente(app.state))
    try:
        yield
    finally:
        tarefa.cancel()
        with suppress(asyncio.CancelledError):
            await tarefa


app = FastAPI(lifespan=lifespan)
app.include_router(posicoes_router)


@app.get("/")
def inicio():
    return {"mensagem": "Backend funcionando!"}
