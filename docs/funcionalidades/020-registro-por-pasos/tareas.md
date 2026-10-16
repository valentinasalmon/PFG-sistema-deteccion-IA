# Tareas: 020 — Registro guiado por pasos

Referencias: [especificacion.md](especificacion.md) · [plan.md](plan.md)

**Responsable** indica quién escribe y sube cada parte, según el reparto de [CLAUDE.md](../../../CLAUDE.md). Los comandos se ejecutan en `frontend/`.

- [x] **T01** — Componentes de presentación y estilos de los formularios por pasos, con sus pruebas.
  - Responsable: Asistente
  - Archivos: `src/componentes/IndicadorPasos.jsx`, `src/componentes/OpcionTarjeta.jsx`, `src/estilos/global.css`, `src/componentes/presentacion.test.jsx`
  - Verificación: `npx vitest run src/componentes` pasa.
  - Commit: `funcionalidad(registro): agregar indicador de pasos y opciones en tarjeta`
- [ ] **T02** — Marcar varios errores a la vez en el hook de formularios.
  - Responsable: Autora
  - Archivos: `src/hooks/useFormulario.js`
  - Verificación: `npm run lint` sin errores; las pantallas de perfil y restablecimiento siguen pasando sus pruebas.
  - Commit: `funcionalidad(formularios): permitir marcar varios errores a la vez`
- [ ] **T03** — Pantalla de registro en cuatro pasos.
  - Responsable: Autora
  - Archivos: `src/paginas/PaginaRegistro.jsx`
  - Verificación: en `npm run dev`, el registro muestra "Paso 1 de 4" y se completa hasta "Revisá tu correo".
  - Commit: `funcionalidad(registro): dividir el registro en cuatro pasos`
- [ ] **T04** — Pruebas del registro por pasos (CA1 a CA8).
  - Responsable: Asistente
  - Archivos: `src/paginas/acceso.test.jsx`
  - Verificación: `npm run lint && npm run test:cobertura` en verde.
  - Commit: `pruebas(registro): probar el registro por pasos`
- [ ] **T05** — Recorrido manual con Docker y Mailpit: registrar una cuenta de cada perfil, volver atrás, dejar un paso vacío y usar solo el teclado.
  - Responsable: Autora

## Cierre

- [ ] Lint, pruebas y cobertura en verde; integración continua del Pull Request en verde.
- [ ] Criterios de aceptación de la especificación verificados.
- [ ] Entrada en la bitácora.
