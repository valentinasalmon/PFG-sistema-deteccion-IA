# Hechos del sistema para el informe

Fuente única de datos verificados para redactar el informe. Si un dato del informe no coincide con esta página, se corrige el informe o se actualiza esta página con su evidencia. **Las cifras del proceso no se copian a mano: se recalculan** con `python backend/herramientas/cifras_del_proyecto.py`.

Última revisión: 2026-11-05.

## 1. Identidad

- **Nombre:** evidentIA, con minúscula inicial. No es registrable como marca: «EVIDENTIA» está concedida a terceros en las clases 9 y 42 (CP-36), así que se mantiene como nombre académico.
- **Eslogan:** «Tu primera línea de defensa contra el fraude visual».
- **Título del informe:** *evidentIA: plataforma de apoyo a la decisión para la detección de indicios de generación o manipulación por inteligencia artificial en la prueba fotográfica de siniestros de tránsito y laborales en Argentina*.
- **Autora:** Valentina Salmón. **Docentes:** Sergio Lapertosa, Augusto Portillo y Martín Jones (revisor técnico).
- **Repositorios:**
  - actual: https://github.com/valentinasalmon/PFG-sistema-deteccion-IA;
  - anterior: https://github.com/valentinasalmon/TIF.

## 2. Relevamiento (Capítulo II)

- **Encuesta a profesionales del derecho:** n = 11, del 24 de agosto al 1 de septiembre de 2026, con un formulario de 16 preguntas aplicado por muestreo de conveniencia.
  - El 72,7 % dudó o tal vez dudó de la autenticidad de una imagen.
  - El 100 % nunca pidió una pericia.
  - El 81,8 % prioriza un método validado judicialmente y el 63,6 %, un reporte comprensible sin perito.
- **Entrevistas:**
  - Flavia Veron, de la UFIE (20 de agosto);
  - la perito Gisela Insaurralde (2 de septiembre);
  - Jorge Silva, de Ariel Silva Asesores de Seguros SRL (7 de septiembre);
  - Federico Miskinich, de LegalTech (2 de octubre).
- **Pruebas de canales:** ChatGPT y Gemini, con 5 canales. El manifiesto C2PA se pierde por WhatsApp como foto y por captura de pantalla.

## 3. Lo que hace el sistema (estado al 2026-11-05)

| Función | Estado | Evidencia |
|---|---|---|
| Registro con perfil Abogado o Aseguradora, con Google (OpenID Connect con PKCE) | Implementado; Google en modo de prueba hasta tener el dominio | Funcionalidades 002, 020 y 027; ADR-0019 |
| Organizaciones (estudio jurídico y aseguradora del catálogo de la SSN), invitaciones y permisos por caso | Implementado | Funcionalidades 004, 005 y 021 |
| Carga de JPEG, PNG y HEIC desde la computadora, desde el celular (QR) y por la persona afectada (enlace con declaración) | Implementado | Funcionalidades 006, 024 y 028 |
| Huella SHA-256 y sello de tiempo en Hedera (imágenes, informes y versiones) | Implementado; **probado en producción contra la *testnet*** el 2026-11-02 | Funcionalidades 023, 026 y 029; ADR-0018; `/estado` |
| Capa 1: metadatos EXIF/XMP | Implementado | Funcionalidad 007 |
| Capa 2: C2PA con verificación de firma | Implementado | Funcionalidad 009 |
| Capa 3: ELA por bloques, con mapa | Implementado | Funcionalidad 011 |
| Capa 4: clasificador de redes neuronales (ONNX) | Integrada en el código (012); se activa cuando se publique el modelo 1.0.0, que depende del entrenamiento (010) | `docs/red-neuronal/` |
| Informe PDF por rubro, unas 4 páginas, verificable con QR | Implementado | Funcionalidades 008, 025 y 026 |
| Notificaciones, panel y tablero de administración | Implementado | Funcionalidades 013 y 014 |
| Planes y cobro con Cresium | Implementado con **proveedor simulado**; precios a confirmar (CP-38) | Funcionalidad 032; ADR-0020 |
| Portada pública con los planes | Implementado | Funcionalidad 033 |
| Verificación de identidad del Referente de una aseguradora (DNI y rostro con prueba de vida) | Implementado con **proveedor simulado**; Identik pendiente (CP-41) | Funcionalidad 035; RN41 |
| Microsoft Clarity | Instalado solo en producción y enmascarado; **se quita antes de la versión final** (CP-37) | Funcionalidad 031 |
| Retención de 5 años y destrucción | Implementado | Funcionalidad 015 |
| Seguridad (OWASP Top 10, límites por IP, cabeceras, auditoría de dependencias) | Implementado | Funcionalidad 030; `docs/arquitectura/seguridad.md` |
| Índice de calidad y usabilidad | QI provisorio de 0,977 sin SUS; protocolo SUS listo, **resultados pendientes** | Funcionalidad 018 |

## 4. Arquitectura e infraestructura

- **Monorepositorio:** interfaz React (Vite) y API REST en Flask 3.1 bajo `/api`; sesión con cookies en Redis y protección CSRF.
- **Capas del backend:** rutas → servicios → repositorios → modelos, verificadas con import-linter (3 contratos).
- **Patrones:**
  - Strategy: capas de análisis, almacenamiento, cola, sello, pagos e identidad;
  - Repository;
  - Service Layer;
  - Factory: configuración por entorno;
  - Decorator: control de acceso.
- **Procesamiento:** cola en Redis con un trabajador RQ. Hay tareas programadas de systemd para los sellos (cada 15 minutos), la retención y el respaldo.
- **AWS, eu-west-1 (Irlanda), definido en Terraform:**
  - una EC2 t3.small con Ubuntu Server 24.04 y disco cifrado;
  - Nginx con TLS en el puerto 443;
  - Gunicorn en 127.0.0.1:8000;
  - PostgreSQL y Redis locales;
  - S3 privado, cifrado y versionado (datos, y respaldos con artefactos);
  - SES por SMTP con STARTTLS;
  - Parameter Store para los secretos;
  - un presupuesto con alertas.
- **Despliegue continuo** desde `main` con OIDC y Systems Manager: migra la base, verifica la salud, vuelve a la versión anterior si falla y sella la huella de la versión.
- **Pendiente de infraestructura:** el dominio propio, la salida de SES del modo de prueba y Hedera en la red principal (*mainnet*) antes de la defensa.

## 5. Diagramas (todos generados o verificados contra el código)

Están en `docs/arquitectura/diagramas/`; ver su `README.md`. Se regeneran con `/generar-diagramas`. La herramienta `diagramas_del_sistema.py verificar` falla si un diagrama no coincide con el código o con la infraestructura.

## 6. Cifras del proceso

Se recalculan antes de cada entrega. Valores al 2026-11-11 (commit d3f5b7d):

| Indicador | Valor |
|---|---|
| Commits (sin integraciones) | 395 |
| Commits con coautoría de IA | 364 (92,2 %) |
| Pull requests integrados | 77 |
| Pruebas automatizadas | 810 (534 del backend y 276 de la interfaz) |
| Funcionalidades en el plan | 39 (las 39 con especificación) |
| ADR | 21 |
| Entradas de bitácora | 62 |
| Requisitos | 56 RF, 24 RNF, 41 RN, 38 casos de uso |
| Cuestiones abiertas registradas | 43 |
| Cobertura del backend / frontend | 97,5 % / 92,4 % (índice de calidad, 018) |

## 7. Cuestiones que el informe no puede dar por cerradas

| Cuestión | Qué falta |
|---|---|
| CP-07 | Criterio del clasificador: F1-score ≥ 0,85 (informe) o AUC ≥ 0,90 (especificación). Lo deciden los tutores |
| CP-04 | Fórmula del índice de calidad |
| CP-38 | Precios de los planes (ver `plan-de-negocios.md`) |
| CP-37 | Texto de Clarity en la política de privacidad, y su retiro |
| CP-41 y CP-42 | Identik: verificación aparte o dentro de la firma; firmar el PDF o dejarlo como trabajo futuro |
| CP-32 | Texto de la declaración de la persona afectada (Ley 25.326) |
| CP-26 | Hedera en *mainnet* |
