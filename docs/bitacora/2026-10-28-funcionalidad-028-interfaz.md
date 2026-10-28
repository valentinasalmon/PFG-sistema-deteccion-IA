# 2026-10-28 — Mejoras de interfaz (028): auditoría, frames y primera tanda

## Qué se hizo

- **Auditoría** de las 19 pantallas en computadora y celular, con la plataforma levantada en local con datos de ejemplo. Se encontraron unos 30 problemas:
  - duplicados;
  - etiquetas del mismo color;
  - datos repetidos;
  - formularios y listas mal armados;
  - una pantalla del caso de unos 8.800 px.
- **Frames de la propuesta** en un lienzo de diseño, en dos rondas.
  - Ronda 1: la autora aprobó Inicio, Lista de casos, Mi perfil, Organización y Administración.
  - Ronda 2: pidió estados de azul a verde, el menú según el rol, la pantalla del caso por etapas con un enlace para la persona afectada, y mejoras en el inicio de sesión y el registro.
- **Primera tanda implementada:** Inicio, Lista de casos (con buscador único en el backend), Mi perfil en pestañas, Organización y Administración, y los estados de azul a verde.
- **Calidad:**
  - backend: 525 pruebas, cobertura del 97,5 %, pylint 10/10;
  - frontend: 221 pruebas.

## Decisiones

- **La actividad propia se redacta en segunda persona** («Cargaste…»). Se convierte el verbo y no se repite el nombre de quien mira.
- **Un solo buscador** que busca a la vez en el número, el expediente (sin tildes) y el lugar. Se conservan los filtros `numero` y `expediente` de la API por compatibilidad.
- **Las pestañas del perfil siguen el patrón de WAI-ARIA** (flechas del teclado) y quedan en la dirección (`?seccion=`).
- **El rol «Responsable» deja de mostrarse como etiqueta**: es lo habitual. Solo se aclara cuando el caso es compartido.
- **Corrección de la auditoría inicial:** dos cosas que se habían marcado como errores eran efectos de la captura de página completa.
  - El menú lateral es fijo y acompaña al desplazarse.
  - El mapa ELA se carga recién al llegar a él.
  
  Igual se le reservó el lugar al mapa para que la pantalla no salte.

## Pendiente

- Segunda tanda, a validar por la autora:
  - menú según el rol;
  - caso por etapas;
  - enlace para la persona afectada (CP-32);
  - celular;
  - inicio de sesión y registro.
