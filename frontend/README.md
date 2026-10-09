# Frontend

Interfaz web en React (Vite) que consume la API REST del backend ([ADR-0002](../docs/arquitectura/decisiones/0002-react-y-api-rest.md)). Todo el texto visible está en español y está pensada para usuarios no técnicos (RNF10).

## Requisitos previos

- Node.js 24 (LTS) instalado con nvm en Ubuntu (ver [guía de instalación](../docs/guias/instalacion-entorno-windows.md)).
- El backend en ejecución en el puerto 5000 (ver [backend/README.md](../backend/README.md)).

## Instalación (una sola vez)

```bash
cd frontend
npm install
```

## Ejecución

```bash
cd frontend
npm run dev
```

La interfaz queda disponible en `http://localhost:5173`. En desarrollo, Vite redirige las solicitudes a `/api` hacia el backend (`http://localhost:5000`), de modo que el navegador ve un único origen.

## Comandos

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con recarga automática |
| `npm run lint` | Análisis estático con ESLint |
| `npm test` | Pruebas con Vitest |
| `npm run test:cobertura` | Pruebas con informe de cobertura |
| `npm run build` | Compilación para producción en `dist/` |

## Estructura de `src/`

| Carpeta | Contenido |
|---|---|
| `api/` | Funciones de acceso a la API. Único lugar que conoce las URL del backend |
| `paginas/` | Una pantalla por archivo, con sus pruebas (`*.test.jsx`) |
| `componentes/` | Componentes reutilizables (a partir de la funcionalidad 002) |
| `estilos/` | Estilos globales |
| `pruebas/` | Configuración común de las pruebas |
