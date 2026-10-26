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
  - enlace de un solo uso (15 minutos, 30 fotos, solo carga en ese caso);
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

## Informe PDF breve, por rubro y verificable (funcionalidades 025 y 026)

- **Por qué:** quien analiza imágenes todos los días no puede leer un PDF de 8 o 9 páginas. Se redujo a unas 4 páginas, sin numeración ni saltos de página, y con más espacio.
- **Orden aprobado por la autora:** caso; custodia con cronología; escala; resultados deterministas y probabilísticos; resultados por imagen; qué hacer ahora; verificación; y el aviso final.
- **Lenguaje por rubro:**
  - Abogado: expediente, prueba, pericia.
  - Aseguradora: siniestro, liquidación, verificación o inspección.
- **Deterministas y probabilísticos:**
  - deterministas: integridad, metadatos y C2PA (hechos verificables, reproducibles y comprobables por terceros);
  - probabilísticos: ELA y la red neuronal (estimaciones que pueden fallar en los dos sentidos).
  
  Un indicio determinista pesa más.
- **PDF verificable:**
  - la huella del PDF se sella en Hedera;
  - QR y código de 12 caracteres;
  - página pública donde el navegador calcula la huella (el PDF nunca se sube);
  - nunca se muestran datos del caso.

- **Ajustes después de probarlo (2026-10-27):**
  - ningún bloque se corta entre páginas;
  - resultados más descriptivos (qué revisó, qué encontró, hallazgos y datos relevantes);
  - se quitaron la sección de tipos, "qué hacer" y las versiones.
  
  Criterio: la plataforma muestra la versión breve y el PDF, el detalle legible.
- **"Host tokenizado" (029):** cada despliegue sella en Hedera la huella de su artefacto, y cada análisis guarda su commit. La verificación pública muestra con qué versión se analizó: refuerza la cadena de custodia sobre el propio software.

- **Inicio con Google (027, 2026-10-28):**
  - OpenID Connect con código de autorización y PKCE del lado del servidor, sin JavaScript de terceros ni biblioteca de JWT (ADR-0019, con la justificación de OpenID Connect Core 3.1.3.7);
  - el rubro se pide igual la primera vez, porque define el lenguaje y los permisos;
  - se evita el "secuestro previo" de cuentas: un correo registrado por otra persona y sin verificar pierde su contraseña al vincularse;
  - para la sección de seguridad: la cookie de sesión pasó de `SameSite=Strict` a `Lax`, porque con `Strict` se perdía la sesión al volver desde Google, y la protección CSRF compensa el cambio.
- **Integración continua (2026-10-28):** la validación de commits se limitó a los Pull Requests de funcionalidades, porque fallaba en los de integración por commits ya validados. Es un ejemplo de ajuste del arnés a la práctica real.

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
