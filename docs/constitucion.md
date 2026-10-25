# Constitución del proyecto

Principios que rigen toda decisión de arquitectura, de código y de proceso. Una especificación o un plan que contradiga alguno de ellos debe justificarlo en su sección **Excepciones a la constitución**, y la excepción se registra al final de este documento.

> Adaptada de la constitución del repositorio anterior (TIF), ampliada con los requisitos del proyecto final.

## 1. Arquitectura en capas (backend)

El código de `backend/app/` se organiza en capas con una única responsabilidad cada una. Las dependencias solo apuntan hacia abajo:

```
rutas/         Controladores delgados: validan la entrada con un esquema, invocan un servicio
               y devuelven JSON. No contienen reglas de negocio.
servicios/     Lógica de negocio y reglas de acceso. No conocen Flask (ni request ni response).
repositorios/  Único punto de acceso a datos (consultas de SQLAlchemy).
modelos/       Entidades de dominio (modelos de SQLAlchemy).
```

Componentes transversales:

```
esquemas/      Validación y serialización de entradas y salidas de la API.
seguridad/     Decoradores de control de acceso y utilidades de autenticación.
analisis/      Capas de análisis (Strategy). No acceden a la base de datos.
integraciones/ Adaptadores a servicios externos: S3, SES, Hedera (sello de tiempo).
tareas/        Trabajos en segundo plano (RQ): análisis, correos, retención.
informes/      Generación del informe PDF.
```

Reglas:

- Una ruta **nunca** consulta la base de datos ni contiene reglas de negocio.
- Un servicio **nunca** importa `flask.request` ni arma respuestas HTTP.
- Todo acceso a datos pasa por un repositorio.
- Las capas de análisis y las integraciones se acceden **siempre** a través de su interfaz, nunca de su implementación concreta.

## 2. Patrones de diseño obligatorios

| Patrón | Dónde | Para qué |
|---|---|---|
| **Application Factory** | `app/__init__.py::crear_app` | La aplicación se construye en una función, nunca como instancia global. |
| **Factory + Strategy de configuración** | `app/configuracion/` | Cada entorno (desarrollo, pruebas, producción) es una clase; un entorno nuevo es una clase nueva. |
| **Repository** | `app/repositorios/` | Acceso a datos encapsulado por entidad. |
| **Service Layer** | `app/servicios/` | Lógica de negocio encapsulada por dominio. |
| **Decorator** | `app/seguridad/` | Control de acceso por rol y por permiso sobre el caso. |
| **Strategy** | `app/analisis/`, `app/integraciones/` | Capas de análisis intercambiables; proveedores externos reemplazables por simulaciones. |

## 3. Análisis y resultados

- Cada capa es independiente; la falla de una no detiene a las demás.
- Ninguna capa ni el informe emiten veredictos ni combinan las capas en un puntaje global.
- La ausencia de manifiesto C2PA nunca se interpreta como evidencia de autenticidad.
- Los archivos originales nunca se modifican; su huella SHA-256 se verifica antes de cada análisis.

## 4. Seguridad y privacidad

- Ningún secreto en el repositorio. Configuración por variables de entorno.
- El acceso se decide siempre en el servidor; el frontend solo oculta opciones.
- Un recurso sin permiso responde 404.
- El Administrador nunca accede a casos, imágenes ni informes.
- Se cumple la Ley N.° 25.326 según la especificación (RNF08).

## 5. Pruebas

- Todo servicio, repositorio, capa de análisis e integración nueva tiene pruebas con `pytest`, usando la configuración de pruebas y nunca la base de datos de desarrollo o producción.
- Los servicios externos se reemplazan por simulaciones en las pruebas.
- Cobertura mínima: 80 %. Un cambio que la reduzca no se integra.

## 6. Proceso

- Desarrollo guiado por especificaciones: `/especificar` → `/planificar` → `/tareas` → implementación.
- Conventional Commits con tipos en español.
- Toda integración pasa por la integración continua (flake8, pylint, pytest, ESLint, Vitest, commitlint).

## 7. Idioma y documentación

- Todo en español (código, comentarios, commits, ramas y documentación).
- Todo módulo, clase y función pública tiene docstring con su propósito y los requisitos que realiza.
- Cada etapa cerrada deja una entrada en la bitácora; cada decisión de arquitectura, un ADR.

## Excepciones

Ninguna registrada. Formato: fecha, principio afectado, motivo y especificación que la origina.
