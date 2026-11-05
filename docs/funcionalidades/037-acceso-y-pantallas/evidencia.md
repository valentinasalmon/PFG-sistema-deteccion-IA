# Evidencia: recorridos de punta a punta (2026-11-05)

Corrida con los scripts de `frontend/e2e/` contra el entorno local (PostgreSQL, Redis, SMTP de prueba, Flask y Vite), en Chromium.

## Aseguradora (computadora)

| Paso | Resultado |
|---|---|
| Elegir «Aseguradora», datos y aseguradora del catálogo | Correcto |
| Plan y cuenta → «Crear la cuenta e ir al pago» | Correcto |
| Pago simulado | Acreditado |
| Correo de verificación (SMTP de prueba) | Recibido y usado |
| Ingreso con la aseguradora pendiente | «Hola, Rita»; aviso de pendiente de aprobación |
| Administrador con la identidad sin verificar | «Aprobar» deshabilitado (RN41) — **correcto** |
| Verificar mi identidad → simular aprobada | «Identidad verificada» |
| Administrador aprueba | «… fue aprobada.» |
| Menú de la aseguradora | Inicio · **Siniestros** · Organizaciones · Mi perfil |
| Alta | «**Nuevo siniestro**» |

Hallazgo durante la prueba: elegir una aseguradora que ya tiene organización da 409 (RN37, correcto); el mensaje se muestra en el paso de la cuenta.

## Abogado (computadora y celular emulado, iPhone 13)

| Paso | Computadora | Celular |
|---|---|---|
| Ingreso | Correcto | Correcto |
| Caso nuevo (automovilístico, fecha, lugar) | CASO-2026-000028 | CASO-2026-000029 |
| Subir dos fotos | 2 | 2 |
| Análisis | Terminado | Terminado |
| Informe PDF | Descargado, formato breve con «Herramienta de apoyo» arriba | Descargado |
| Verificación pública por código | Muestra código, fecha, huella y sello | — |

Errores de JavaScript en la página: ninguno. Los 401 de la consola son la consulta de sesión antes de ingresar (esperados).

## Limitaciones de esta evidencia

- Solo Chromium: en el entorno del agente no están instalados Firefox ni WebKit (Safari). **Pendiente:** probarlo en Safari (iPhone) y en Firefox; lo hace la autora con la guía de usuario.
- El sello en Hedera local es simulado; en producción ya se probó contra testnet (2026-11-02).

## Capturas

![Identidad aprobada](evidencia/chromium-09-identidad-aprobada.jpg)
![Aseguradora aprobada por el Administrador](evidencia/chromium-admin-aprobada.jpg)
![Inicio de la aseguradora activa](evidencia/chromium-12-inicio-activa.jpg)
![Análisis terminado (computadora)](evidencia/abogado-pc-05-analisis.jpg)
![Análisis terminado (celular)](evidencia/abogado-cel-05-analisis.jpg)
![Verificación pública](evidencia/abogado-pc-verificar.jpg)
![Pendientes con la identidad sin verificar](evidencia/chromium-admin-pendientes.jpg)
![Alta de un siniestro](evidencia/chromium-13-nuevo-siniestro.jpg)

## Segunda corrida (2026-11-05, noche)

- Informe PDF real descargado por la interfaz: incluye «Más detalle y verificación» con los dos QR (análisis detallado y verificación pública); 4 páginas con dos imágenes.
- Hallazgo y corrección: en la portada, el título de la tarjeta «Aseguradoras» no se veía (texto oscuro sobre fondo oscuro).

## Tercera corrida (2026-11-05, noche): pagos, administración y sensor de diseño

- **Recorrido de la aseguradora** (Chromium, computadora y celular de 390 px): registro con la lista desplegable → plan → pago → acreditación → correo → identidad → aprobación → «Siniestros». Pasa, con el sensor de diseño en cada captura: **«Sin problemas de diseño»**.
- **Recorrido del abogado** (computadora e iPhone 13 emulado): caso → 2 fotos → análisis → PDF → verificación pública. Pasa, **«Sin problemas de diseño»**.
- **Correo al Administrador**: al acreditarse el pago de una aseguradora llegó «… espera tu aprobación» a las dos cuentas con rol de Administrador del entorno local (servidor SMTP de prueba).
- **Pagos revisados uno por uno** (pc y celular): pago y resultado de una aseguradora y de un estudio en el registro, cambio de plan desde la organización y página del enlace de pago. El sensor no marca problemas.
- **El sensor detecta el error que vio la autora**: volviendo a poner la tarjeta de alto fijo sobre el pago, informa «contenido escondido: … muestra 672px de 1308px»; con la corrección, nada.

| Antes | Después |
|---|---|
| ![Pago cortado dentro de la tarjeta](capturas/pago-antes.jpg) | ![Pago completo](capturas/pago-despues.jpg) |
| ![Resultado cortado y pasos desparejos](capturas/pago-resultado-antes.jpg) | ![Resultado con línea de avance](capturas/pago-resultado-despues.jpg) |
| ![Lista larga de aseguradoras](capturas/aseguradora-lista-antes.jpg) | ![Lista desplegable](capturas/aseguradora-lista-despues.jpg) |

![Pago en el celular](capturas/pago-celular-despues.jpg)
![Administración: tablero arriba y pendientes compactas](capturas/administracion-despues.jpg)
![Cierre del análisis con el informe](capturas/analisis-cierre-despues.jpg)
![Fotos cargadas: siguiente paso](capturas/carga-siguiente-paso-despues.jpg)
![Cambio de plan](capturas/plan-cambio-despues.jpg)

