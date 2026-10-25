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

## Respuestas de la autora (mismo día)

- **Host tokenizado:** opción (a), la huella de cada versión desplegada en Hedera. Se agrega RF56 y la funcionalidad 029.
- **PDF:** alcanza con la huella en Hedera, sin NFT. La firma digital queda como opcional.
- **Hedera para imágenes:** se aplica a lo mismo que antes se hacía con BFA.
- **"Informe":** se refiere al **informe final del proyecto**. Se creó `docs/informe-final/insumos.md` para juntar todo lo que tiene que quedar en ese documento.
- **Red:** se recomendó *testnet* para desarrollar y *mainnet* para la defensa (CP-26).
- **Carga desde el celular:** se investigó y se propusieron diez ideas con pros y contras (`docs/investigacion/2026-10-25-carga-desde-el-celular.md`). La autora las revisa.

## Pendiente

- La autora confirma CP-26 (compra de HBAR para *mainnet*), detalla CP-28 (secciones del PDF de resultados) y las secciones nuevas del informe final, y elige las ideas de carga desde el celular.
- La autora crea una cuenta en el portal de desarrolladores de Hedera y un cliente OAuth en Google Cloud (pasos en el mensaje de la sesión).
