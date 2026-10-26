
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from Captura_image import CamaraXenics


camara = CamaraXenics()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # la camara se conectara cuando se solicite
    yield

    # liberando el servicio
    camara.cerrar()


app = FastAPI(
    title="Sistema de Monitoreo Multiespectral",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def inicio():
    return {
        "servicio": "Sistema Multiespectral",
        "funcionando": True,
    }


@app.get("/estado")
def estado():
    return {
        "ok": True,
        "servicio": "Python",
        "camara": (
            "conectada"
            if camara.camara is not None
            else "no_conectada"
        ),
        "script_captura_existe": True,
    }


@app.post("/camara/conectar")
def conectar_camara():
    if camara.camara is not None:
        return {
            "ok": True,
            "mensaje": "La cámara ya está conectada.",
            "informacion": {
                "url": camara.url,
                "ancho": camara.ancho,
                "alto": camara.alto,
                "tamano_fotograma": camara.tamano,
            },
        }

    try:
        informacion = camara.conectar()

        return {
            "ok": True,
            "mensaje": "Cámara conectada correctamente.",
            "informacion": informacion,
        }

    except Exception as error:
        camara.cerrar()

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


    
@app.post("/camara/capturar")
def capturar_imagen():
    if camara.camara is None:
        raise HTTPException(
            status_code=409,
            detail="Primero debes conectar la cámara.",
        )

    try:
        imagen = camara.capturar()

        return {
            "ok": True,
            "mensaje": "Fotograma capturado correctamente.",
            "ancho": int(imagen.shape[1]),
            "alto": int(imagen.shape[0]),
            "tipo": str(imagen.dtype),
            "minimo": int(imagen.min()),
            "maximo": int(imagen.max()),
            "pixeles_no_cero": int((imagen != 0).sum()),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

