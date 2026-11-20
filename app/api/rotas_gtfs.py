from fastapi import APIRouter, HTTPException, Request


router = APIRouter(prefix="/gtfs", tags=["GTFS"])


@router.get("/verificacao")
def consultar_verificacao(request: Request):
    estado = request.app.state
    if estado.gtfs is None:
        raise HTTPException(status_code=503, detail=estado.gtfs_erro or "Nenhuma verificação de GTFS disponível ainda.")
    return {**estado.gtfs, "erro": estado.gtfs_erro}
