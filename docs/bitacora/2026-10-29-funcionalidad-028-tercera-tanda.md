# 2026-10-29 — Interfaz (028), tercera tanda, y propuesta del pago en el registro (032)

## Qué se hizo

- **Inicio de sesión (frames 9a y 9c, aprobados):**
  - el panel de marca suma tres ventajas reales (análisis por capas, cadena de custodia en Hedera, informe verificable) y para quién es;
  - «Creá una» debajo del título, «¿La olvidaste?» junto a la contraseña y el botón «Mostrar» (componente nuevo `CampoContrasenia`);
  - en el celular, el panel se reduce a una banda corta con el logo.
- **Celular:** se recorrieron las pantallas a 390 px de ancho y se corrigió:
  - el logo cortado en el acceso;
  - la huella del PDF que se mostraba en vertical en la etapa del informe;
  - las tarjetas de imagen, que ahora pliegan la huella, el sello y los datos técnicos y entran de a dos;
  - la cabecera y la zona de riesgo de la organización, que se apilan.
- **Rama 010 limpia:** se quitaron de toda su historia 53 archivos de `backend/almacenamiento_local/` subidos por error (imágenes, miniaturas y PDF) y se integró `desarrollo`.
- **Diagramas del informe:** la autora no los aprobó; se quitaron de la rama del informe y se rehacen más adelante.
- **Propuesta del pago en el registro (032):** frames 10a a 10g en el lienzo de diseño, a validar por la autora antes de implementar.

## Decisiones de la autora (2026-10-29)

- **El pago va en el registro**, no en una sección aparte, para estudios jurídicos y aseguradoras, con plan Básico o Profesional.
- **El abogado elige en el registro** entre independiente (plan personal, sin pago) o con estudio jurídico (con el nombre del estudio y el pago).
- **El independiente puede crear su estudio después**, desde Mi perfil, con el plan y el pago.
- **Aseguradoras: primero el pago y después la aprobación** del Administrador.
- **Precios: a confirmar.**
- **El pago se simula con Cresium** hasta averiguar su API y sus costos.

## Investigación de Cresium

- Fintech argentina con cuenta empresa; la apertura y el mantenimiento son gratuitos.
- Cobra por transferencia a un CVU, concilia los pagos de forma automática y avisa por *webhook* cuando entran.
- La comisión de cobranza figura desde el 0,4 % por pago en su página para clubes.
- No se encontró documentación pública de la API ni un entorno de pruebas: hay que pedirlos al equipo comercial.
- Por eso el diseño simula un cobro por transferencia: CVU, alias y una referencia, con un botón «Simular la transferencia» que hace de aviso de Cresium. Se integra detrás de una interfaz intercambiable, como el sello de tiempo.

## Pendiente

- La autora valida los frames 10a a 10g; después se implementan el registro (9b) y el pago (032).
- La autora borra a mano la rama `claude/intelligent-franklin-yl0b03` desde GitHub: el proxy de la sesión no permite borrar ramas.
