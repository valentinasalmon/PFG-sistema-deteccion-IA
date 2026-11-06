# Tareas: 012 — Capa 4 (red neuronal con ONNX)

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

Orden: dependencias y configuración → integración del modelo → capa → registro → informe → frontend → despliegue → verificación manual → documentación.

- [x] **T01** — Dependencias: `onnxruntime` y `huggingface_hub` fijadas en `requirements.txt`, `onnx` en `requirements-dev.txt`, y el paquete `clasificador` instalado sin dependencias en la integración continua y en el despliegue (con `red_neuronal` dentro del artefacto).
  - Archivos: `backend/requirements.txt`, `backend/requirements-dev.txt`, `.github/workflows/integracion-continua.yml`, `infraestructura/scripts/desplegar.sh`, `infraestructura/scripts/generar_entorno.sh` (agregado al implementar: sin él, las variables del Parameter Store no llegaban al `.env`)
  - Verificación: `pip install --no-deps ../red_neuronal` y `python -c "from clasificador.inferencia import PredictorOnnx"` sin PyTorch.
  - Commit: `construccion(012): instalar el clasificador y ONNX Runtime en el backend`
- [x] **T02** — Configuración: `MODELO_RED_NEURONAL_REGISTRO`, `MODELO_RED_NEURONAL_VERSION` y `CARPETA_MODELOS_ONNX`, sin valores por defecto en producción.
  - Archivos: `backend/app/configuracion/entornos.py`, `infraestructura/terraform/principal/parametros.tf` (comentario sobre `HF_TOKEN`)
  - Verificación: prueba de configuración.
  - Commit: `funcionalidad(012): configuracion del modelo de la capa 4`
- [x] **T03** — Integración del modelo: `obtener_predictor` con registro local o de Hugging Face, versión fija, huella verificada, caché por proceso y `ModeloNoDisponible` con el motivo.
  - Archivos: `backend/app/integraciones/modelo_red_neuronal.py`, `backend/pruebas/unitarias/test_modelo_red_neuronal.py`
  - Verificación: carga una sola vez; huella alterada, versión inexistente o sin configuración dan el motivo (CA3, CA7).
  - Commit: `funcionalidad(012): obtener el modelo verificado una vez por proceso`
- [x] **T04** — Capa 4: nivel, anomalía, conclusión con las tres aclaraciones, tabla de criterios y versiones.
  - Archivos: `backend/app/analisis/red_neuronal.py`, `backend/pruebas/unitarias/test_capa_red_neuronal.py`
  - Verificación: CA1, CA2, CA4, CA5, CA6; imagen ilegible da `CapaNoDisponible`.
  - Commit: `funcionalidad(012): capa 4 con la probabilidad del clasificador`
- [x] **T05** — Registrar la capa y verificar que, sin modelo configurado, el análisis sigue con las otras tres (RN26).
  - Archivos: `backend/app/analisis/registro.py`, pruebas del servicio y de las rutas de análisis
  - Verificación: CA7, CA9.
  - Commit: `funcionalidad(012): registrar la capa 4 en el analisis`
- [x] **T06** — Informe PDF: títulos de la capa 4.
  - Archivos: `backend/app/informes/informe_analisis.py`, `backend/pruebas/unitarias/test_informe_analisis.py`
  - Verificación: el PDF muestra la capa 4 con su tabla (CA8).
  - Commit: `funcionalidad(012): capa 4 en el informe`
- [x] **T07** — Pantalla del caso: la capa 4 con su título y su «¿Qué significa?».
  - Archivos: `frontend/src/componentes/SeccionAnalisis.jsx` y su prueba
  - Verificación: `npm run lint && npm run test`; captura de la sección.
  - Commit: `funcionalidad(012): capa 4 en la pantalla del analisis`
- [ ] **T08 (manual, autora)** — Publicar el modelo 1.0.0 en el repositorio privado de Hugging Face (E03 de la 010), cargar `HF_TOKEN` de lectura y `MODELO_RED_NEURONAL_*` en Parameter Store, y analizar un caso en producción.
  - Verificación: la capa 4 aparece con su probabilidad y la versión 1.0.0 en la pantalla y en el PDF.
- [x] **T09** — Documentación: capítulo 7 de `docs/red-neuronal/` (cómo lo usa el backend), guía de la autora para T08, bitácora, insumos, Trello.
  - Commit: `documentacion(012): ...`

## Cierre

- [x] Pruebas, flake8, pylint y cobertura en verde (backend: 602 pruebas, 97 %; frontend: 274).
- [x] Criterios de aceptación de la especificación verificados con pruebas automáticas; la verificación contra el servicio real queda en T08.
- [x] Entrada en la bitácora; sin ADR nuevo (aplica ADR-0006, ADR-0014 y ADR-0015).
