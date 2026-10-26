
const estado = document.getElementById('estado');
const btnConectar = document.getElementById('btnConectar');
const resultadoPython = document.getElementById('resultadoPython');

const banda = document.getElementById('banda');
const bandaSeleccionada = document.getElementById('bandaSeleccionada');

function mostrarResultado(mensaje, salida = '') {
  if (estado) {
    estado.textContent = mensaje;
  }

  if (resultadoPython) {
    resultadoPython.textContent = salida;
  }
}

// Actualizar el texto al seleccionar una longitud de onda.
function actualizarBanda() {
  if (banda && bandaSeleccionada) {
    bandaSeleccionada.textContent =
      `Banda seleccionada: ${banda.value} nm`;
  }
}

if (banda) {
  banda.addEventListener('change', actualizarBanda);
  actualizarBanda();
}

// Probar la conexión con el servicio Python.
if (btnConectar) {
  btnConectar.addEventListener('click', async () => {
    btnConectar.disabled = true;

    mostrarResultado(
      'Conectando con el servicio de cámara...',
      'Esperando respuesta de FastAPI.'
    );

    try {
      if (!window.cameraAPI ||
          typeof window.cameraAPI.probarConexion !== 'function') {
        throw new Error(
          'La API de Electron no está disponible. Revisa preload.js y main.js.'
        );
      }

      const respuesta = await window.cameraAPI.probarConexion();

      mostrarResultado(
        respuesta.mensaje || 'Respuesta recibida.',
        respuesta.salida || JSON.stringify(respuesta, null, 2)
      );
    } catch (error) {
      mostrarResultado(
        'No se pudo realizar la conexión.',
        error.message
      );
    } finally {
      btnConectar.disabled = false;
    }
  });
}

const btnCapturaIndividual =
  document.getElementById('btnCapturaIndividual');

const btnCapturaRueda =
  document.getElementById('btnCapturaRueda');

const panelIndividual =
  document.getElementById('panelIndividual');

const panelRueda =
  document.getElementById('panelRueda');

const resumenBandas =
  document.getElementById('resumenBandas');

if (btnCapturaIndividual && btnCapturaRueda) {
  btnCapturaIndividual.addEventListener('click', () => {
    panelIndividual.hidden = false;
    panelRueda.hidden = true;

    resumenBandas.textContent =
      'Modo individual seleccionado.';

    btnCapturaIndividual.classList.remove('secondary');
    btnCapturaRueda.classList.add('secondary');
  });

  btnCapturaRueda.addEventListener('click', () => {
    panelIndividual.hidden = true;
    panelRueda.hidden = false;

    const seleccionadas = [
      ...document.querySelectorAll(
        'input[name="bandas"]:checked'
      )
    ].map(input => input.value);

    resumenBandas.textContent =
      `Modo rueda de filtros: ${seleccionadas.length} bandas seleccionadas (${seleccionadas.join(', ')} nm).`;

    btnCapturaRueda.classList.remove('secondary');
    btnCapturaIndividual.classList.add('secondary');
  });

  document.querySelectorAll('input[name="bandas"]')
    .forEach(input => {
      input.addEventListener('change', () => {
        const seleccionadas = [
          ...document.querySelectorAll(
            'input[name="bandas"]:checked'
          )
        ].map(item => item.value);

        resumenBandas.textContent =
          `Modo rueda de filtros: ${seleccionadas.length} bandas seleccionadas (${seleccionadas.join(', ')} nm).`;
      });
    });
}

const btnCapturar = document.getElementById("btnCapturar");

btnCapturar.addEventListener("click", async () => {
    try {
        btnCapturar.disabled = true;
        btnCapturar.textContent = "Capturando...";

        const respuesta = await fetch(
            "http://127.0.0.1:8001/camara/capturar",
            {
                method: "POST"
            }
        );

        const resultado = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                resultado.detail || "Error al capturar la banda."
            );
        }

        console.log("Captura realizada:", resultado);

        alert(
            `Captura realizada correctamente.\n` +
            `Dimensiones: ${resultado.ancho} × ${resultado.alto}\n` +
            `Tipo: ${resultado.tipo}\n` +
            `Píxeles no cero: ${resultado.pixeles_no_cero}`
        );

    } catch (error) {
        console.error("Error de captura:", error);
        alert(error.message);
    } finally {
        btnCapturar.disabled = false;
        btnCapturar.textContent = "Capturar banda";
    }
});