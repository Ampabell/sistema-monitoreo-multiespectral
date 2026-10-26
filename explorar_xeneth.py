
import ctypes
from pathlib import Path

# Ruta de la biblioteca de Xeneth
RUTA_DLL = Path(
    r"C:\Program Files\Common Files\XenICs\Runtime\xeneth64.dll"
)

def main():
    print("=== Prueba de Xeneth desde Python ===")

    if not RUTA_DLL.exists():
        print("ERROR: No se encontró la DLL.")
        return

    try:
        xeneth = ctypes.WinDLL(str(RUTA_DLL))
        print("OK: Biblioteca Xeneth cargada.")

    except OSError as error:
        print(f"ERROR al cargar Xeneth: {error}")
        return

    # Comprobar las funciones necesarias para la adquisición
    funciones = [
        "XC_OpenCamera",
        "XC_IsInitialised",
        "XC_CloseCamera",
        "XC_GetWidth",
        "XC_GetHeight",
        "XC_StartCapture",
        "XC_StopCapture",
        "XC_GetFrame",
        "XC_GetFrameSize",
    ]

    print("\nFunciones disponibles:")

    for nombre in funciones:
        if hasattr(xeneth, nombre):
            print(f"  OK: {nombre}")
        else:
            print(f"  NO DISPONIBLE: {nombre}")

    print(
        "\nLa biblioteca está lista para continuar. "
        "Todavía no se ha abierto ni iniciado la cámara."
    )

if __name__ == "__main__":
    main()
