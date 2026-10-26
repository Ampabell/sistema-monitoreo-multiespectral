
import ctypes
import os
import time
from pathlib import Path

import numpy as np


# DLL para ejecutar sin camara

RUTA_DLL = Path(
    r"C:\Program Files\Common Files\XenICs\Runtime\xeneth64.dll")


# se utiliza esta bandera para saber si esta la camara virtual
CAMARA_URL = os.getenv("CAMARA_URL", "soft://0")

CARPETA_SALIDA = Path("capturas")
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)


# ==========================================================
# CAPTURA XENICS
# ==========================================================

class CamaraXenics:

    def __init__(self, ruta_dll=RUTA_DLL, url=CAMARA_URL):
        self.ruta_dll = Path(ruta_dll)
        self.url = url
        self.xeneth = None
        self.camara = None
        self.captura_iniciada = False
        self.ancho = 0
        self.alto = 0
        self.tamano = 0

    def conectar(self):
        """Carga Xeneth y abre la cámara configurada."""

        if not self.ruta_dll.is_file():
            raise FileNotFoundError(
                f"No se encontró la DLL: {self.ruta_dll}"
            )

        self.xeneth = ctypes.WinDLL(str(self.ruta_dll))

        x = self.xeneth

        # Declaraciones de la API Xeneth
        x.XC_OpenCamera.argtypes = [
            ctypes.c_char_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
        x.XC_OpenCamera.restype = ctypes.c_void_p

        x.XC_IsInitialised.argtypes = [ctypes.c_void_p]
        x.XC_IsInitialised.restype = ctypes.c_int

        x.XC_GetWidth.argtypes = [ctypes.c_void_p]
        x.XC_GetWidth.restype = ctypes.c_int

        x.XC_GetHeight.argtypes = [ctypes.c_void_p]
        x.XC_GetHeight.restype = ctypes.c_int

        x.XC_GetFrameSize.argtypes = [ctypes.c_void_p]
        x.XC_GetFrameSize.restype = ctypes.c_uint32

        x.XC_StartCapture.argtypes = [ctypes.c_void_p]
        x.XC_StartCapture.restype = ctypes.c_uint32

        x.XC_StopCapture.argtypes = [ctypes.c_void_p]
        x.XC_StopCapture.restype = ctypes.c_uint32

        x.XC_GetFrame.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        x.XC_GetFrame.restype = ctypes.c_uint32

        x.XC_CloseCamera.argtypes = [ctypes.c_void_p]

        print(f"Conectando con {self.url}...")

        self.camara = x.XC_OpenCamera(
            self.url.encode("ascii"), None, None
        )

        if not self.camara:
            self.camara = None
            raise RuntimeError(
                "Xeneth no pudo abrir la cámara. "
                "Verifica el dispositivo, la red y el protocolo."
            )

        if not x.XC_IsInitialised(self.camara):
            self.cerrar()
            raise RuntimeError(
                "La cámara se abrió, pero no se inicializó."
            )

        self.ancho = x.XC_GetWidth(self.camara)
        self.alto = x.XC_GetHeight(self.camara)
        self.tamano = x.XC_GetFrameSize(self.camara)

        if min(self.ancho, self.alto, self.tamano) <= 0:
            self.cerrar()
            raise RuntimeError(
                "La cámara devolvió dimensiones inválidas."
            )

        print(f"Resolución: {self.ancho} x {self.alto}")
        print(f"Tamaño del fotograma: {self.tamano} bytes")

        return {
            "conectada": True,
            "url": self.url,
            "ancho": self.ancho,
            "alto": self.alto,
            "tamano_fotograma": self.tamano,
        }

    def iniciar_captura(self):
        """Inicia la adquisición de imágenes."""

        if self.camara is None:
            raise RuntimeError("La cámara no está conectada.")

        if self.captura_iniciada:
            return

        error = self.xeneth.XC_StartCapture(self.camara)

        if error != 0:
            raise RuntimeError(
                f"Error al iniciar la captura: {error}"
            )

        self.captura_iniciada = True
        time.sleep(0.5)

    def capturar(self):
        """Obtiene un fotograma y lo devuelve como matriz NumPy."""

        if self.camara is None:
            raise RuntimeError("La cámara no está conectada.")

        if not self.captura_iniciada:
            self.iniciar_captura()

        buffer = (ctypes.c_ubyte * self.tamano)()

        # FT_NATIVE = 0; XGF_Blocking = 1
        error = self.xeneth.XC_GetFrame(
            self.camara, 0, 1, buffer, self.tamano
        )

        if error != 0:
            raise RuntimeError(
                f"Error al obtener el fotograma: {error}"
            )

        datos = bytes(buffer)

        # No asumir uint16 si el tamaño no coincide.
        if self.tamano != self.ancho * self.alto * 2:
            ruta_raw = CARPETA_SALIDA / "fotograma.raw"
            ruta_raw.write_bytes(datos)

            raise RuntimeError(
                "El tamaño del fotograma no corresponde a una "
                "imagen uint16. Se guardaron los datos originales "
                f"en {ruta_raw.resolve()}. Hay que verificar "
                "el formato de píxel."
            )

        imagen = np.frombuffer(
            datos, dtype=np.uint16
        ).reshape(self.alto, self.ancho).copy()

        return imagen

    def cerrar(self):
        """Detiene la adquisición y libera la cámara."""

        if self.camara is not None:
            try:
                if self.captura_iniciada:
                    self.xeneth.XC_StopCapture(self.camara)
            finally:
                self.captura_iniciada = False
                self.xeneth.XC_CloseCamera(self.camara)
                self.camara = None

        print("Cámara cerrada.")


# prueba

def main():
    camara = CamaraXenics()

    try:
        informacion = camara.conectar()
        print("Estado:", informacion)

        imagen = camara.capturar()

        ruta = CARPETA_SALIDA / "fotograma.npy"
        np.save(ruta, imagen)

        print("Fotograma adquirido correctamente.")
        print("Forma:", imagen.shape)
        print("Tipo:", imagen.dtype)
        print("Mínimo:", int(imagen.min()))
        print("Máximo:", int(imagen.max()))
        print("Píxeles distintos de cero:",
              int(np.count_nonzero(imagen)))
        print("Archivo:", ruta.resolve())

        if not np.any(imagen):
            print(
                "ADVERTENCIA: todos los píxeles son cero. "
                "Hay que comprobar la señal, la exposición "
                "y la configuración de adquisición."
            )

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        camara.cerrar()


if __name__ == "__main__":
    main()
