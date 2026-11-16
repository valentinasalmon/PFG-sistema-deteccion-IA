# 2026-11-16 · 041: accesibilidad y materiales del cierre

## Contexto

La autora delegó `evidentiaa.com.ar` en DonWeb a los servidores de Route 53. El certificado falló con `SERVFAIL`: consultando el servidor de `.ar` (`f.dns.ar`), NIC Argentina todavía publica `ns1.donweb.com` y `ns2.donweb.com`, aunque el panel de DonWeb ya muestra los de AWS; Route 53 responde bien (devuelve la IP del servidor). Se esperan unas horas y, si sigue, la autora consulta a soporte de DonWeb. Mientras tanto, el agente avanzó con los pendientes del cierre.

## Hecho

- **Sensor de accesibilidad** con axe-core y su paso en la integración continua.
- **Dos problemas de contraste corregidos**: las iniciales del menú (1,9:1) y la etiqueta de la tarjeta «Aseguradoras» de la portada (2,4:1).
- **Protocolo de usabilidad** al día con la plataforma de la 037 a la 040.
- **QI**: segunda medición provisoria, 0,975.
- Se sumó a esta rama el commit de la guía de DonWeb (040) que había quedado fuera del PR #91.

## Decisiones

- El sensor falla solo con infracciones **serias o críticas** y corre **sin animaciones**: las tarjetas de la portada que aparecen al desplazarse, medidas a mitad de la animación, daban 30 falsos problemas de contraste.
- Se corrigió con los colores de la paleta (`--tinta`, `--p-lima`), sin colores nuevos (guía de identidad visual).

## Verificación

Sensor de accesibilidad sin infracciones graves (14 pantallas en pc y celular, un caso en cuatro etapas y Administración); sensor de diseño sin problemas; recorrido del abogado en pc y celular sin errores de la página; ESLint y 286 pruebas de Vitest; 612 pruebas del backend (cobertura 97,5 %).

## Pendiente

- Autora: seguir el dominio (propagación en NIC Argentina, certificado y correos).
- Autora: prueba de usabilidad con el protocolo actualizado.
