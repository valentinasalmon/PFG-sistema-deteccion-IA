# 2026-10-27 — Ajustes del informe (025) y versión en Hedera (029)

## Qué se hizo

- **Informe (025)**, a pedido de la autora después de probarlo en producción:
  - ningún bloque se corta entre páginas: si no entra, pasa entero a la hoja siguiente;
  - resultados por imagen más descriptivos: qué revisó cada técnica, qué encontró, hallazgos no repetidos, datos técnicos relevantes y mapa ELA;
  - se quitaron las secciones "Resultados deterministas y probabilísticos" y "Qué hacer ahora", y la línea de versiones;
  - las etiquetas de tipo se explican en una línea al empezar los resultados.
- **029**:
  - cada despliegue registra su commit y la huella del artefacto y la sella en Hedera;
  - cada análisis guarda el commit;
  - la verificación pública muestra con qué versión se analizó.
- **Calidad**:
  - backend: 484 pruebas y cobertura del 97,7 %;
  - frontend: 202 pruebas.

## Decisiones

- **La versión de la plataforma (RN29, RF56) se muestra en la página pública de verificación** y no en el PDF: la autora no quiere que el usuario la vea en el informe.
- **El registro de la versión ocurre después de que el despliegue pasa la verificación de salud.** Si falla, solo se avisa: nunca revierte el despliegue.
- **La versión de la aplicación pasa a 0.3.0.**

## Pendiente

- Comprobar la 029 en producción después del próximo despliegue.
- La lista completa de lo que falta está en `docs/guias/pendientes.md`, para ordenarla por prioridad y pasarla a Trello.
