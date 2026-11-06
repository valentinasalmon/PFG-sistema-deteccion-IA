# Guía de usuario de evidentIA

evidentIA analiza fotos que se usan como prueba —por ejemplo, de un siniestro— y busca **indicios** de que hayan sido modificadas o generadas. Entrega un informe PDF con la huella registrada en una red pública (Hedera), para que cualquiera compruebe que nadie lo alteró.

> **Importante.** evidentIA no dice si una foto es verdadera o falsa. Muestra indicios técnicos y recomienda consultar a un perito cuando corresponde. La decisión siempre es de una persona.

## 1. Crear la cuenta

1. Entrá a la plataforma y elegí **Crear cuenta**. También podés entrar con Google.
2. Elegí tu camino:
   - **Abogado o abogada**: trabajás solo/a o creás un estudio jurídico para tu equipo.
   - **Aseguradora**: elegís tu compañía del catálogo de la Superintendencia de Seguros. La aseguradora queda pendiente hasta que el Administrador de la plataforma la aprueba.
   - **Te invitaron**: usá el enlace del correo de invitación; el correo y la organización ya vienen completos.
3. Si creás una organización, pagás el plan con una transferencia. Los datos se copian con un botón y el pago se acredita solo.
4. Confirmá tu correo con el enlace que te llega.

**Aseguradoras:** el Referente puede tener que verificar su identidad con su DNI y una foto de su rostro antes de la aprobación. Se hace desde la pantalla de la organización con **Verificar mi identidad**. La plataforma guarda solo el resultado, nunca el DNI ni la foto.

## 2. Crear un caso

Un caso agrupa las fotos y los informes de un mismo hecho.

1. Tocá **Nuevo caso** (en el menú o con `Ctrl` + `K`).
2. Completá el título, la fecha y el lugar del hecho y, si querés, una descripción.
3. Elegí el **espacio de trabajo**: personal o el de tu organización, para que tu equipo también lo vea.

Desde la lista de **Casos** buscás por título o número y filtrás por estado.

## 3. Cargar las imágenes

En el caso, la etapa **Cargar imágenes** ofrece tres formas:

| Forma | Cuándo conviene |
|---|---|
| **Desde la computadora** | Tenés las fotos en la compu. Arrastralas o elegilas. |
| **Desde tu celular** | Las fotos están en el teléfono. Escaneás el código QR y las subís desde ahí (también fotos de iPhone, HEIC). |
| **Enlace para la persona afectada** | Las fotos las tiene otra persona, por ejemplo el asegurado. Le mandás un enlace y las sube sin crear una cuenta. |

Cada imagen guarda su huella digital al subirse, así se puede probar que no cambió después.

## 4. Analizar

1. Tocá **Analizar las imágenes**.
2. El análisis corre solo; podés seguir usando la plataforma mientras tanto.
3. Cada imagen muestra lo que encontró cada mirada:
   - **Metadatos**: cámara, fecha, ubicación y programas de edición registrados en el archivo.
   - **Credenciales de contenido (C2PA)**: si la foto trae una firma de origen y si es válida.
   - **Niveles de error (ELA)**: zonas con una compresión distinta del resto, que pueden indicar retoques. El mapa se compara con la foto deslizando el control.
   - **Red neuronal** (se suma con la funcionalidad 012): la probabilidad de que la imagen esté manipulada o generada por IA, según un modelo entrenado.

Los resultados se leen como **indicios**, con un nivel de atención. Los umbrales y los límites de cada mirada están publicados en el informe.

## 5. Obtener el informe

1. En la etapa **Informe**, tocá **Generar el informe**.
2. Cuando está listo, **Descargar el informe PDF**.

El informe trae:
- el resultado por imagen y su explicación según el rubro (legal o seguros);
- la huella de cada imagen y del propio informe, registradas en Hedera;
- un código QR y un código para verificarlo;
- el aviso de que es un análisis automático que debe revisar una persona.

## 6. Verificar un informe

Cualquiera puede comprobar que un informe no fue modificado, sin cuenta:

1. Entrá a **Verificar un informe** (`/verificar`) o escaneá el QR del PDF.
2. Subí el PDF o escribí su código.
3. La página confirma si coincide con el original y muestra el registro en Hedera, con un enlace a HashScan.

## 7. Trabajar en equipo

- En **Organizaciones**, el Referente invita por correo a su equipo y elige quién es Referente y quién miembro.
- Los casos del espacio de la organización los ven todos sus miembros. Un caso se puede compartir o transferir a otra persona.
- La pestaña **Plan** muestra los límites y el consumo, y permite cambiar de plan.

## 8. Tu cuenta y tus datos

En **Mi perfil**:
- cambiás tus datos, tu correo y tu contraseña;
- descargás una **copia de tus datos personales**;
- podés **eliminar tu cuenta**. Los casos que tienen que conservarse por ley se mantienen durante el plazo de retención (5 años) y después se destruyen.

## 9. Ayuda

- Si algo falla, el mensaje dice qué pasó y qué hacer.
- La página **Estado** (`/estado`) muestra si la plataforma, el análisis y el sello en Hedera funcionan.
- Los **Términos** y la **Política de privacidad** están al pie de cada página.
