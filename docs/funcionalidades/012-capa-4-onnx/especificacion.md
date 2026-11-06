# Especificación: 012 — Capa 4 (red neuronal con ONNX)

- **Rama**: `funcionalidad/012-capa-4-onnx`
- **Estado**: Borrador
- **Requisitos que realiza**: RF42; RF43 (CA1 a CA4, para esta capa); RF44 (CA1 y CA2, para esta capa); RNF23 (CA1, CA3 a CA5); RNF24 (CA1 y CA4)
- **Reglas de negocio aplicadas**: RN21, RN26, RN27, RN29
- **Casos de uso**: la parte de CU28 que ejecuta la capa 4

## Problema

La red neuronal de la funcionalidad 010 ya está entrenada: la versión 1.0.0 tiene un AUC de 0,961 con generadores conocidos y de 0,938 con la familia de Google, que nunca vio. Pero el sistema todavía no la usa. Hoy el análisis de cada foto tiene tres capas (metadatos, C2PA y ELA), y las tres dependen de rastros que una foto pierde fácilmente: los metadatos y la credencial C2PA desaparecen con una captura de pantalla, y ELA es una señal débil.

La capa 4 mira la imagen misma y estima **qué tan probable es que la haya creado una IA**. Muchas veces es el único indicio disponible. Esta funcionalidad la conecta al análisis, al caso y al informe.

Lo que se sabe del modelo también marca sus límites. Con las imágenes de choques que la autora generó con ChatGPT, Gemini y Copilot, el modelo 1.0.0 detectó 5 de 49 con el umbral de 0,5 (capítulo 11 de `docs/red-neuronal/`). Por eso el resultado tiene que presentarse con mucha prudencia: es un indicio más, nunca una conclusión, y un valor bajo no significa que la foto sea real.

## Alcance

### Incluido

**Análisis (RF42)**
- La capa ejecuta el modelo ONNX publicado por la funcionalidad 010 sobre cada imagen y obtiene la **probabilidad calibrada** de que sea íntegramente sintética.
- Usa el mismo preprocesamiento que la evaluación del modelo (el contrato de ADR-0015), sin reimplementarlo: para la misma imagen, el backend y la evaluación dan exactamente la misma probabilidad.
- Corre en el servidor **sin GPU**.
- El modelo se carga **una sola vez por proceso de trabajo** (RF42 CA3) y se usa una **versión fija**, configurada, con la huella SHA-256 verificada antes de usarlo.

**Nivel de indicio y conclusión (RF43)**
- El nivel de indicio es la probabilidad expresada en porcentaje, con un máximo de 90 %: el 100 % se reserva para una declaración de IA con firma C2PA confiable (RN28).
- Los umbrales son públicos y se muestran en el resultado (ADR-0017): menos de 50 % no se informa como anomalía; de 50 % a 70 %, indicio débil; de 70 % a 90 %, indicio moderado; 90 % o más, indicio fuerte. Son una propuesta para validar con los tutores.
- La conclusión sale del catálogo de textos versionado (RNF23 CA3), habla de indicios y recomienda consultar a un profesional (RN27). Nunca usa términos de veredicto.
- La conclusión aclara siempre (RF42 CA2) que:
  - el modelo no detecta ediciones parciales (para eso están las capas 1 a 3);
  - su desempeño puede bajar con generadores que no vio durante el entrenamiento, como las herramientas comerciales más nuevas;
  - **una probabilidad baja no indica que la foto sea real**.

**Versiones (RN29, RNF24 CA4)**
- El resultado registra la versión del modelo, la huella del archivo del modelo, la huella del conjunto de datos con que se entrenó y la versión de ONNX Runtime. Esos datos salen del propio archivo del modelo.

**Pantalla del caso e informe PDF (RF43, RF44)**
- La capa 4 aparece junto a las otras tres, con su nivel, su conclusión y un recuadro «¿Qué significa?» en lenguaje no técnico (RF44 CA2, RNF23 CA1).
- La tabla de criterios (RNF23 CA5) muestra la probabilidad obtenida, los umbrales publicados y una referencia de desempeño del modelo (AUC con generadores conocidos y no vistos), sin describir el algoritmo interno.
- No hay ningún puntaje que combine las cuatro capas (RF43 CA4).

**Fallas (RN26, RF43 CA3)**
- Si el modelo no está configurado, no se puede descargar, su huella no coincide o la imagen no se puede leer, la capa queda «No disponible» con el motivo, y las demás capas siguen.

### Excluido

- **Entrenar, evaluar o publicar el modelo:** es la funcionalidad 010.
- **Señalar zonas de la imagen** (mapas de calor de la red): la capa 4 da una probabilidad para toda la imagen. Queda como trabajo futuro.
- **Elegir la versión del modelo desde la interfaz:** la versión se fija por configuración del servidor.
- **Ediciones parciales:** las cubren las capas 1 a 3.
- **Cambios en la ficha del modelo o en el registro de modelos:** se usan los de la 010 tal como están.

## Criterios de aceptación

- [ ] **CA1**: Dada una imagen, cuando se analiza, entonces la capa 4 informa la probabilidad de que sea sintética y la versión del modelo (RF42 CA1).
- [ ] **CA2**: Para la misma imagen, la probabilidad del backend es igual a la de la evaluación del modelo (mismo preprocesamiento, ADR-0015).
- [ ] **CA3**: El modelo se carga una sola vez por proceso de trabajo: analizar varias imágenes no lo vuelve a cargar (RF42 CA3).
- [ ] **CA4**: El nivel de indicio es la probabilidad en porcentaje con un máximo de 90 %, y las anomalías siguen los umbrales publicados (50, 70 y 90 %), que se muestran en el resultado.
- [ ] **CA5**: La conclusión es un indicio con la recomendación de consultar a un profesional, sin términos de veredicto (RN27). Aclara que el modelo no detecta ediciones parciales, que puede fallar con generadores que no vio y que una probabilidad baja no indica que la foto sea real (RF42 CA2).
- [ ] **CA6**: El resultado y el informe registran la versión del modelo, su huella, la huella del conjunto de entrenamiento y la versión de ONNX Runtime (RN29, RNF24 CA4).
- [ ] **CA7**: Si el modelo no está configurado, no se puede obtener o su huella no coincide, la capa queda «No disponible» con el motivo, y las otras tres capas se presentan normalmente (RN26, RF43 CA3).
- [ ] **CA8**: La capa 4 se ve en la pantalla del caso y en el informe PDF con su recuadro «¿Qué significa?» y su tabla de criterios (RF44 CA2, RNF23 CA1 y CA5).
- [ ] **CA9**: Ningún lugar del sistema calcula ni muestra un puntaje que combine las cuatro capas (RF43 CA4).
- [ ] **CA10**: El servidor ejecuta la capa sin GPU y sin instalar PyTorch (RNF24 CA1, ADR-0015).

## Preguntas abiertas

- **Umbrales del nivel de indicio (50, 70 y 90 %):** propuesta para validar con los tutores, igual que los de ELA. Se basan en la calibración del modelo (una probabilidad de 0,8 corresponde, en promedio, a un 80 % de imágenes sintéticas en la validación).
- **Dónde se aloja el modelo en producción:** ADR-0014 prevé un repositorio privado de Hugging Face (tarea E03 de la 010, a cargo de la autora). Mientras no exista, la capa queda «No disponible» con un motivo claro, sin detener el análisis (CA7). No bloquea esta funcionalidad.
