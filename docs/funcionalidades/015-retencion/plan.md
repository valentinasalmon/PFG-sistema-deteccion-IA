# Plan técnico · 015

- **`TareasDeRetencion`** (en `servicios/servicio_casos.py`) reutiliza el repositorio, los permisos, los archivos, los correos y la auditoría de `ServicioCasos`.
  - `prorrogar(id_caso, usuario, motivo)`: corre un año el inicio del plazo (`retencion_desde`), así la destrucción se extiende 1 año sin columnas nuevas ni migración. Es renovable (RN32).
  - `procesar(ahora)`: recorre los casos con plazo en curso.
    - Si venció: audita con las huellas, quita el caso y borra los archivos después de confirmar.
    - Si faltan exactamente 30 días: manda el aviso y lo audita. Como la tarea corre una vez por día, el aviso sale una sola vez.
- **Comando** `flask --app wsgi retencion procesar`. En el servidor lo ejecuta `plataforma-retencion.timer` todos los días a las 04:00 de Argentina, media hora después del respaldo. El despliegue lo instala solo.
- **API**: `POST /api/casos/<id>/prorroga` con `{motivo}`, y la acción `prorrogar` en `acciones`.
- **Interfaz**: en «Estado» se ve la fecha de eliminación, destacada si faltan 30 días o menos, y el botón «Prorrogar 1 año» con motivo obligatorio.
- **Correo** `retencion_aviso` con el diseño de la marca.
- **Respaldos**: vencen a los 30 días (RNF13), así los datos destruidos no quedan para siempre en las copias (RF49 CA3).
