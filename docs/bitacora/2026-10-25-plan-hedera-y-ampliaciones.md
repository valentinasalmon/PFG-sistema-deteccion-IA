# 2026-10-25 — Cambio a Hedera y ampliaciones del alcance

## Qué se hizo

- Se investigó Hedera como reemplazo de Blockchain Federal Argentina: servicios, costos, SDK de Python, verificación pública y riesgos ([investigación](../investigacion/2026-10-25-hedera.md)).
- Se registró la decisión de la autora en el [ADR-0018](../arquitectura/decisiones/0018-sello-de-tiempo-en-hedera.md).
- Se actualizó la especificación general para que coincida con los cambios:
  - visión y glosario;
  - RF37 pasa a Hedera;
  - requisitos nuevos RF52 a RF55: Google, celular, informe por rubro e informe inalterable;
  - RNF07 y RNF20;
  - caso de uso de carga;
  - constitución y estructura del repositorio.
- Se resolvió CP-25 y se abrieron CP-26 a CP-31.
- Se agregaron las funcionalidades 023 a 029 y el calendario de la fase 10 en la hoja de ruta.
- La 016 (BFA) queda reemplazada por la 023. La rama `funcionalidad/016-sello-desde-navegador` se abandona y no se integra.

## Decisiones

- **Hedera Consensus Service**, no Token Service: alcanza con registrar huellas, y es lo más barato y simple de verificar.
- **Carga desde el celular por la web**, sin aplicación nativa: funciona en Android e iOS sin pasar por las tiendas de aplicaciones. Se agrega un QR para pasar de la computadora al celular, y soporte de HEIC para los iPhone.
- **Inalterabilidad del PDF**: huella en Hedera, más firma digital, más página pública de verificación. El NFT queda como opción (CP-27).

## Pendiente

- La autora define CP-26 (red y HBAR), CP-27 (alcance de "tokenizado"), CP-28 (secciones del informe), CP-29 ("host tokenizado") y CP-31 (a qué informe se refiere).
- La autora crea una cuenta en el portal de desarrolladores de Hedera y un cliente OAuth en Google Cloud (pasos en el mensaje de la sesión).
