# Insumos para el informe final del proyecto

Lista viva de temas, decisiones y hallazgos que tienen que quedar en el **informe final del proyecto** (el documento para la facultad). La actualiza el agente cada vez que aparece algo relevante. Cada punto indica dónde está el detalle.

## Sello de tiempo: de BFA a Hedera

- **Plan original:** Blockchain Federal Argentina, por su valor probatorio local (especificación 016).
- **Problemas encontrados (2026-10-21 y 22):**
  - la dirección supuesta no existía;
  - el servicio 2.0 estaba caído (404);
  - el 1.0 funciona pero bloquea conexiones desde fuera de Argentina;
  - el diagnóstico se hizo con curl, comparando la PC de la autora con el servidor de AWS.
  
  Ver las bitácoras del 2026-10-22.
- **Alternativa intermedia descartada:** sello pedido desde el navegador del usuario.
- **Decisión:** Hedera Consensus Service, ADR-0018. Incluir:
  - comparación de alternativas;
  - costos (unos US$ 0,0008 por registro);
  - verificación pública con HashScan y el *mirror node*;
  - riesgos (custodia de la clave, reinicios de *testnet*).
  
  Ver `docs/investigacion/2026-10-25-hedera.md`.
- **Usos de Hedera en el sistema:**
  1. huella de cada imagen al cargarla (lo que antes hacía BFA);
  2. huella de cada informe PDF, con página de verificación;
  3. huella de cada versión desplegada del sistema ("host tokenizado", CP-29).
- **Implementación (funcionalidad 023):**
  - mensaje mínimo `{"v":1,"tipo":"imagen","sha256":...}`;
  - recibo `<red>:<tema>/<secuencia>`;
  - verificación en el *mirror node* comparando la huella;
  - enlace público a HashScan;
  - clave privada solo en SSM (nunca en el repositorio ni en el estado de Terraform), pedida sin mostrarla al crear el tema;
  - SDK oficial `hiero-sdk-python`, importado solo cuando el modo es Hedera.
- **Lección para el informe:** depender de un servicio externo sin documentación pública. El patrón Strategy permitió cambiar de proveedor sin tocar el resto del sistema.

## Carga desde el celular

- Hallazgos sobre la web móvil, HEIC, pérdida de ubicación en iOS, fotos sin EXIF y compresión de WhatsApp.
- Diez ideas con pros y contras, y la propuesta elegida.
- **Evolución de la propuesta:**
  - primero, web en el celular más QR;
  - la autora descartó la plataforma móvil;
  - propuesta final: código de carga (QR y 6 dígitos) más "compartir desde la galería", con Web Share Target (PWA) en Android y Atajo de Apple en iPhone.
  
  Las alternativas evaluadas y descartadas (cable, AirDrop, Quick Share, iCloud, LocalSend, correo, WhatsApp, app nativa) están en la investigación.
- **Etapa 1 implementada** (funcionalidad 024): soporte de HEIC sin convertir el original, detectado por la caja `ftyp`, y ELA con validez limitada en HEIC.
- **El tutor aprobó el QR hacia la galería (2026-10-26). Etapa 2 implementada:**
  - enlace de un solo uso (15 minutos, sin tope de fotos más allá del límite del plan, solo carga en ese caso);
  - token de 192 bits, del que solo se guarda la huella;
  - QR en SVG generado en el servidor;
  - página del celular sin sesión, con galería y cámara;
  - auditoría con origen `celular`;
  - actualización automática en la computadora.
  
  Queda como trabajo futuro el "compartir desde la galería" (Web Share Target y Atajo de Apple).
- **Importar desde Drive o Dropbox: descartado** por doble trabajo, por sumar un custodio intermedio sin trazabilidad (que puede comprimir o convertir la foto) y por la privacidad. Como ampliación futura, importar desde un enlace enviado por un tercero requeriría:
  - descargar sin acceder a cuentas;
  - no guardar el enlace;
  - marcar el origen como "sin garantía";
  - una declaración de autorización (Ley 25.326).
- Ver `docs/investigacion/2026-10-25-carga-desde-el-celular.md`.

## Otros temas ya registrados

- Metodología: desarrollo guiado por especificaciones, arnés para agentes de IA (CLAUDE.md, constitución) y trazabilidad con `Co-Authored-By`.
- Arquitectura en capas verificada con import-linter; patrón Strategy en análisis, almacenamiento, cola y sello.
- Marco normativo y supervisión humana (ADR-0017): sin veredictos, persona en el circuito y umbrales publicados.
- Entrevista con Federico Miskinich (2026-10-02) y su impacto en el informe PDF.
- Infraestructura en AWS con Terraform, despliegue continuo con OIDC, y SES en modo de prueba (solo destinatarios verificados).
- Rediseño de la interfaz (022): identidad "Visor" y lenguaje por rubro.
- Calidad: cobertura del 98 %, pylint 10/10, cantidad de pruebas.

## Secciones nuevas pedidas por la autora

- Pendiente: la autora indica qué secciones agregar y qué modificar (CP-31).
