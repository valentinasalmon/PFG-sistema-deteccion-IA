# 2026-11-16 · 041: accesibilidad y materiales del cierre

## Contexto

La autora delegó `evidentiaa.com.ar` en DonWeb a los servidores de Route 53. El certificado falló con `SERVFAIL`: consultando el servidor de `.ar` (`f.dns.ar`), NIC Argentina todavía publica `ns1.donweb.com` y `ns2.donweb.com`, aunque el panel de DonWeb ya muestra los de AWS; Route 53 responde bien (devuelve la IP del servidor). Se esperan unas horas y, si sigue, la autora consulta a soporte de DonWeb. Mientras tanto, el agente avanzó con los pendientes del cierre.

## Hecho

- **Sensor de accesibilidad** con axe-core y su paso en la integración continua.
- **Dos problemas de contraste corregidos**: las iniciales del menú (1,9:1) y la etiqueta de la tarjeta «Aseguradoras» de la portada (2,4:1).
- **Protocolo de usabilidad** al día con la plataforma de la 037 a la 040.
- **QI**: segunda medición provisoria, 0,975.
- **Versión 1.0 preparada**: README nuevo (producción, qué hace, cómo ejecutarlo y verificar la calidad, insignia de la integración continua, uso de IA) y `docs/versiones.md` con el contenido de la v1.0 y la lista de lo que falta antes de etiquetarla. Solo existe la etiqueta `v0.1`; la v0.2 y la v0.3 quedan como hitos alcanzados sin etiqueta.
- Se sumó a esta rama el commit de la guía de DonWeb (040) que había quedado fuera del PR #91.

## Decisiones

- El sensor falla solo con infracciones **serias o críticas** y corre **sin animaciones**: las tarjetas de la portada que aparecen al desplazarse, medidas a mitad de la animación, daban 30 falsos problemas de contraste.
- Se corrigió con los colores de la paleta (`--tinta`, `--p-lima`), sin colores nuevos (guía de identidad visual).

## Verificación

Sensor de accesibilidad sin infracciones graves (14 pantallas en pc y celular, un caso en cuatro etapas y Administración); sensor de diseño sin problemas; recorrido del abogado en pc y celular sin errores de la página; ESLint y 286 pruebas de Vitest; 612 pruebas del backend (cobertura 97,5 %).

## Pendiente

- Autora: seguir el dominio (propagación en NIC Argentina, certificado y correos).
- Autora: prueba de usabilidad con el protocolo actualizado.

## Más tarde: 042, kit imprimible de la prueba de usabilidad

- PDF A4 de cuatro hojas (`docs/calidad/usabilidad/kit-impresion.pdf`): consentimiento, guion con las consignas, planilla de registro y cuestionario SUS con las preguntas finales, con su fuente HTML para regenerarlo. Se renderizó cada página para comprobar que nada se pase de hoja (la planilla y el cuestionario desbordaban en la primera versión; las preguntas finales pasaron al cuestionario).
- El PR #93 de la 041 falló en la verificación de mensajes de commit (un título de 109 caracteres; el máximo es 100). Como reescribir la rama de un Pull Request abierto no corresponde, los mismos cambios con el título corregido se subieron a `funcionalidad/041-accesibilidad-wcag` (PR #94, integrado). Lección: medir el largo del título antes de cada commit.
## Más tarde: 043, uso con teclado y plan B del DNS

- **Sensor de uso con teclado**: 9 pantallas recorridas con Tab, foco siempre visible, sin trampas, e inicio de sesión solo con el teclado. Primera corrida con un falso positivo: el campo de fecha nativo usa Tab entre día, mes y año, y parecía una trampa; se toleran hasta cinco Tab en el mismo control. Se comprobó que el sensor falla al quitar el contorno de foco.
- **Plan B del DNS**: salida `registros_dns` de Terraform y sección en la guía, por si NIC Argentina no toma la delegación de DonWeb.
