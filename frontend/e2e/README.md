# Recorridos de punta a punta por la interfaz

Scripts de Playwright que usan el sistema como una persona: hacen clic, completan formularios, leen los correos del servidor SMTP de prueba y descargan el PDF. Se corren contra el entorno local levantado (backend, cola, SMTP de prueba y Vite) con la cuenta de prueba (`flask administracion cuenta-de-prueba`).

| Script | Qué recorre |
|---|---|
| `recorrido-aseguradora.cjs <capturas> <buzón SMTP>` | Registro de una aseguradora → pago simulado → verificación del correo → ingreso pendiente → verificación de identidad → aprobación del Administrador → menú con «Siniestros» → alta de un siniestro |
| `recorrido-abogado.cjs <capturas> <imágenes> [pc\|cel]` | Ingreso → caso nuevo → dos fotos → análisis → informe PDF descargado → verificación pública por código; `cel` emula un iPhone 13 |

Resultado de la última corrida y capturas: `docs/funcionalidades/037-acceso-y-pantallas/evidencia.md`.
