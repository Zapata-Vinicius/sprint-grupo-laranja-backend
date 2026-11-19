from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/posicoes", tags=["posições"])


@router.get("")
def consultar_posicoes(request: Request):
    posicoes = request.app.state.posicoes
    if posicoes is None:
        raise HTTPException(status_code=503, detail="Nenhuma coleta de posições disponível ainda.")
    return posicoes
