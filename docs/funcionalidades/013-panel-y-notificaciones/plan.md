# Plan técnico: 013 — Panel principal y notificaciones

Referencias: [especificacion.md](especificacion.md)

## Resumen de la solución

### Panel (RF48)
- `GET /api/panel` devuelve todas las secciones en una sola consulta. Lo arman:
  - el servicio `ServicioPanel`, en `app/servicios/servicio_panel.py`;
  - el esquema `app/esquemas/panel.py`.
- Consultas nuevas, todas limitadas a los casos accesibles (RNF05):

  | Repositorio | Consultas |
  |---|---|
  | `RepositorioCasos` | `ids_accesibles`, `recientes`, `compartidos_desde` (accesos de los últimos 30 días, solo si sigue siendo miembro) y `con_retencion_a_cargo` |
  | `RepositorioAnalisis` | `en_curso_de_casos` |
  | `RepositorioAuditoria` | `recientes_de_recursos`: últimas entradas exitosas de los casos, con quien actuó. Es de solo lectura, como `de_usuario` |

- **Actividad**: cada acción de la auditoría sobre casos tiene un texto en lenguaje común (`TEXTOS_DE_ACTIVIDAD`), con variantes para:
  - los cambios de estado: cerró, archivó, desarchivó y reabrió;
  - la transferencia: la pidió, la canceló, la aceptó o la rechazó.

  Los eventos del sistema (análisis terminado o fallido, informe generado) se redactan sin sujeto. Las descargas no se muestran.
- **Casos próximos a destruirse**: los casos del Responsable cuyo vencimiento (RN30, 5 años) cae dentro de 30 días (RN31). Usa la misma función `vencimiento_de_retencion` que el detalle del caso.
- **Pantalla**: `PaginaInicio.jsx` muestra las secciones con contenido. Cada caso enlaza a su detalle; las invitaciones llevan a Organizaciones y las transferencias, a Casos.

### Correos (RF47)

```
servicio ──► EnviadorEnSegundoPlano ──► cola "correos" ──► trabajador ──► EnviadorSMTP.entregar ──► SES
                  (encola y vuelve)       (RQ, reintentos a los 30 s y 2 min)
```

- **`EnviadorSMTP.entregar`** deja pasar la excepción para que la cola reintente; `enviar` sigue registrando la falla sin propagarla.
- **`EnviadorEnSegundoPlano`** encola el correo con `encolar_con_reintentos`. Es la interfaz nueva de las tres colas:
  - `ColaRQ` usa el `Retry` de RQ, y por eso el trabajador corre con su planificador;
  - `ColaEnHilo` reintenta dentro del hilo;
  - `ColaSincronica` reintenta sin esperar.
- **Cola propia**: el trabajador atiende `correos` antes que `analisis`, así un correo de verificación no espera detrás de un análisis largo.
- En las pruebas (`PROVEEDOR_CORREO=memoria`) los correos siguen siendo sincrónicos, para poder inspeccionarlos.
- **Aviso de análisis**: lo reciben el solicitante y el Responsable, sin repetir si son la misma persona.

## Capas afectadas

| Capa | Cambio |
|---|---|
| `integraciones` | `correo.py` (`entregar`, `EnviadorEnSegundoPlano`); `cola.py` (`encolar_con_reintentos`, cola por nombre) |
| `tareas` | `correos.py`: el trabajo `entregar_correo` |
| Aplicación | `crear_app` arma el enviador en segundo plano; `trabajador.py` atiende dos colas con planificador |
| `repositorios`, `servicios`, `esquemas`, `rutas` | Panel |
| Frontend | `PaginaInicio.jsx`, `api/panel.js` y estilos |

## Estrategia de pruebas

- **Integración** (`test_panel.py`):
  - panel vacío y sesión obligatoria;
  - casos por estado, recientes y actividad, sin casos ajenos;
  - cierre y análisis en la actividad;
  - compartidos recientes y accesos viejos;
  - invitaciones, transferencias, próximos a destruirse y análisis en curso.
- **Unitarias**:
  - redacción de la transferencia y de la cuenta eliminada;
  - reintentos de las tres colas;
  - envío en segundo plano con reintentos y con falla final;
  - elección del enviador según el entorno.
- **Análisis**: el aviso llega al Responsable y al Colaborador que lo pidió, sin datos de las imágenes; el Responsable que lo pide recibe un solo aviso.
- **Frontend** (`panel.test.jsx`): las secciones, los enlaces, la actividad, el panel vacío y el error.
- **Navegador real**: registro con el correo en segundo plano, análisis y panel con la actividad redactada.
