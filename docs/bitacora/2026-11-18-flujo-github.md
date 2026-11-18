# 2026-11-18 · Cambio a GitHub Flow (ADR-0023)

## Contexto

El 2026-11-16 la autora pidió dejar de abrir una rama y un Pull Request por cada arreglo chico, agrupar el trabajo en ramas que representen algo para la defensa y aplicar el mismo criterio a los commits. Pidió una propuesta de ingeniería «sin importar nada más que un código limpio, mantenible y que refleje la ingeniería», y la aprobó como **decisión de mejora del proceso**.

## Hecho

- **ADR-0023**: GitHub Flow con despliegue continuo. `main` única rama permanente; ramas cortas por objetivo con el área adelante; un Pull Request directo a `main`; protección de `main` (nada se integra sin todas las verificaciones en verde); fusión con *squash*; versiones con GitHub Releases.
- **Integración continua**: corre en los Pull Requests y en `main`; se quitó `desarrollo`. Dependabot (`.github/dependabot.yml`) y notas de versión (`.github/release.yml`).
- **Guía para la autora** (`docs/guias/configurar-github.md`): transición, *squash*, protección de `main`, Dependabot, archivo de ramas y versiones.
- **`herramientas/archivar_ramas.sh`**: archiva como etiqueta `archivo/<área>/<nombre>` cada rama del modelo anterior ya integrada en `main` y la borra; muestra primero qué haría. La corre la autora: desde el entorno del agente no se pueden subir etiquetas ni borrar ramas en bloque.
- `CLAUDE.md`, `/especificar`, flujo de trabajo, hoja de ruta, despliegue, tablero, mapa de ramas, versiones y README al día.
- Ya del 2026-11-16: gancho `revisar_commit.py` (formato, 72 caracteres, `Co-Authored-By`). Commitlint en la integración continua queda en 100: con 72 rechazaba commits ya subidos (uno de la 044 tiene 79) y habría bloqueado el Pull Request de transición.

## Decisiones

- **Se descartaron las ramas permanentes por área**: una rama que vive meses se aleja de la principal y arrastra conflictos.
- **Se retira `desarrollo`**: el segundo Pull Request repetía las mismas verificaciones sin sumar control; la protección automática de `main` lo reemplaza con más fuerza.
- **Las ramas viejas no se borran sin dejar rastro**: quedan como etiquetas y el mapa las agrupa por área, como pidió la autora.
- **Lo ya subido no se reescribe**: el *squash* ordena la historia de ahora en adelante.

## Pendiente

- Autora: los dos Pull Requests de transición, la configuración de GitHub y el archivo de ramas (guía `configurar-github.md`).
- Agente: `interfaz/calidad-visual` (sensor de composición, galería, comparación visual y auditoría completa) desde `main` cuando termine la transición.
