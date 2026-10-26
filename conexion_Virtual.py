
import ctypes
from pathlib import Path

RUTA_DLL = Path(
    r"C:\Program Files\Common Files\XenICs\Runtime\xeneth64.dll"
)

def main():
    xeneth = ctypes.WinDLL(str(RUTA_DLL))

    # Declarar los tipos para evitar errores con punteros de 64 bits.
    xeneth.XC_OpenCamera.argtypes = [
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    xeneth.XC_OpenCamera.restype = ctypes.c_void_p

    xeneth.XC_IsInitialised.argtypes = [ctypes.c_void_p]
    xeneth.XC_IsInitialised.restype = ctypes.c_int

    for nombre in ("XC_GetWidth", "XC_GetHeight"):
        funcion = getattr(xeneth, nombre)
        funcion.argtypes = [ctypes.c_void_p]
        funcion.restype = ctypes.c_int

    xeneth.XC_CloseCamera.argtypes = [ctypes.c_void_p]
    xeneth.XC_CloseCamera.restype = None

    camara = None

    try:
        print("Conectando a la cámara virtual...")

        camara = xeneth.XC_OpenCamera(
            b"soft://0", None, None
        )

        if not camara:
            print("No se pudo abrir la cámara virtual.")
            print("Revisaremos la configuración y la API.")
            return

        print("Se obtuvo un identificador de cámara.")

        inicializada = xeneth.XC_IsInitialised(camara)

        if not inicializada:
            print("La cámara no quedó inicializada.")
            return

        ancho = xeneth.XC_GetWidth(camara)
        alto = xeneth.XC_GetHeight(camara)

        print("¡Cámara virtual inicializada!")
        print(f"Ancho: {ancho} píxeles")
        print(f"Alto: {alto} píxeles")
        print("Aún no hemos capturado fotogramas.")

    finally:
        if camara:
            xeneth.XC_CloseCamera(camara)
            print("Conexión cerrada.")

if __name__ == "__main__":
    main()
