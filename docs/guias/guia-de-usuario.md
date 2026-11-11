# Guía de usuario de evidentIA

evidentIA analiza fotos que se usan como prueba —por ejemplo, de un siniestro— y busca **indicios** de que hayan sido modificadas o generadas. Entrega un informe PDF con la huella registrada en una red pública (Hedera), para que cualquiera compruebe que nadie lo alteró.

> **Importante.** evidentIA no dice si una foto es verdadera o falsa. Muestra indicios técnicos y recomienda consultar a un perito cuando corresponde. La decisión siempre es de una persona.

> **Abogados y aseguradoras.** La plataforma es la misma; cambia el vocabulario. Para un abogado, cada hecho es un **caso**; para una aseguradora, un **siniestro**, en las pantallas, en el informe y en los correos. En esta guía se dice «caso» para los dos.

## 1. Crear la cuenta

1. Entrá a la plataforma y elegí **Crear cuenta**. También podés entrar con Google.
2. Elegí tu camino:
   - **Abogado o abogada**: trabajás solo/a o creás un estudio jurídico para tu equipo.
   - **Aseguradora**: escribís parte del nombre o el CUIT de tu compañía y la elegís de la lista del catálogo de la Superintendencia de Seguros.
   - **Te invitaron**: usá el enlace del correo de invitación; el correo y la organización ya vienen completos y, al confirmar tu correo, **quedás dentro de la organización** sin otro paso. Si ya tenés cuenta, iniciá sesión desde el enlace y aceptá la invitación con un clic.
3. Si creás una organización (un estudio o una aseguradora), pagás el plan con una transferencia. Los datos se copian con un botón y el pago se acredita solo.
4. Confirmá tu correo con el enlace que te llega.
5. **La organización queda pendiente** hasta que el Administrador de la plataforma la revisa y la aprueba; te avisamos por correo. Mientras tanto no podés invitar a tu equipo. Si no se aprueba, el pago se devuelve y te avisamos el motivo; si era un estudio, tu cuenta de abogado sigue activa.

También podés crear tu estudio más adelante, desde **Organizaciones** o **Mi perfil**.

**Aseguradoras:** el Referente puede tener que verificar su identidad con su DNI y una foto de su rostro antes de la aprobación. Se hace desde la pantalla de la organización con **Verificar mi identidad**. La plataforma guarda solo el resultado, nunca el DNI ni la foto.

## 2. Crear un caso

Un caso agrupa las fotos y los informes de un mismo hecho.

1. Tocá **Nuevo caso** (en el menú o con `Ctrl` + `K`).
2. Elegí el **espacio de trabajo**: personal o el de tu organización, para que tu equipo también lo vea. No se puede cambiar después.
3. Elegí el tipo (automovilístico o laboral) y completá la fecha y el lugar del hecho. El expediente y la descripción son opcionales.
4. **Crear y cargar las fotos** te lleva directo a la primera etapa.

Desde la lista de **Casos** buscás por número, expediente o lugar y filtrás por estado. Los datos del caso, quién tiene acceso, compartirlo o transferirlo están en **Datos y gestión**, arriba a la derecha de la pantalla del caso.

## 3. Cargar las imágenes

En el caso, la etapa **Cargar imágenes** ofrece tres formas:

| Forma | Cuándo conviene |
|---|---|
| **Desde la computadora** | Tenés las fotos en la compu. Arrastralas o elegilas. |
| **Desde tu celular** | Las fotos están en el teléfono. Tocás **Mostrar el QR**, lo escaneás y las subís desde ahí (también fotos de iPhone, HEIC). Cuando terminás, tocá **Terminar** en el celular: la computadora se entera y cierra el QR. Cada QR sirve para un solo celular; para subir más, mostrá uno nuevo. |
| **Enlace para la persona afectada** | Las fotos las tiene otra persona, por ejemplo el asegurado. Le mandás un enlace y las sube sin crear una cuenta. |

Cada imagen guarda su huella digital al subirse, así se puede probar que no cambió después. Al terminar de cargar, la barra **Analizar las imágenes** se destaca como siguiente paso.

## 4. Analizar

1. Elegí qué imágenes incluir (todas vienen marcadas; las que quedan afuera se ven atenuadas) y tocá **Analizar las imágenes**.
2. El análisis corre solo; podés seguir usando la plataforma mientras tanto y te avisamos por correo cuando termina.
3. Cada imagen muestra lo que encontró cada mirada:
   - **Metadatos**: cámara, fecha, ubicación y programas de edición registrados en el archivo.
   - **Credenciales de contenido (C2PA)**: si la foto trae una firma de origen y si es válida.
   - **Niveles de error (ELA)**: zonas con una compresión distinta del resto, que pueden indicar retoques. El mapa se compara con la foto deslizando el control.
   - **Red neuronal**: la probabilidad de que la imagen completa haya sido generada con inteligencia artificial, según un modelo entrenado. Por debajo de 50 % no aporta indicios, lo que no significa que la foto sea real; no detecta ediciones parciales (para eso están las otras capas).

Los resultados se leen como **indicios**, con un nivel de atención. Los umbrales y los límites de cada mirada están publicados en el informe. Cada técnica tiene plegado **Qué significa y datos técnicos**.

Al terminar, al pie de los resultados aparecen **Descargar el informe PDF** y **Seguir al informe**.

## 5. Obtener el informe

El informe PDF se genera solo al terminar el análisis. Lo descargás desde el pie del análisis o desde la etapa **Informe**. Si alguna vez no se pudo generar, el botón **Generar el informe** lo vuelve a intentar.

El informe es **breve** y trae:
- arriba, el aviso de que es una herramienta de apoyo que debe revisar una persona;
- el resultado por imagen y su explicación según el rubro (legal o seguros);
- la huella de cada imagen y del propio informe, registradas en Hedera;
- al final, dos códigos QR uno debajo del otro, cada uno con su título:
  1. **Análisis detallado**: abre en la plataforma el análisis con todo el detalle desplegado. Pide iniciar sesión con una cuenta que tenga acceso al caso.
  2. **Verificar este PDF**: comprueba, sin cuenta, que el informe no fue modificado.

## 6. Verificar un informe

Cualquiera puede comprobar que un informe no fue modificado, sin cuenta:

1. Entrá a **Verificar un informe** (`/verificar`) o escaneá el QR del PDF.
2. Subí el PDF o escribí su código.
3. La página confirma si coincide con el original y muestra el registro en Hedera, con un enlace a HashScan.

## 7. Trabajar en equipo

- En **Organizaciones**, el Referente invita por correo a su equipo (con el cargo, si quiere) y elige quién es Referente y quién miembro. La invitación vence a los 7 días y ocupa un lugar del plan mientras está pendiente.
- Los casos del espacio de la organización los ven todos sus miembros. Un caso se puede compartir o transferir a otra persona.
- La pestaña **Plan** muestra los límites y el consumo, y permite cambiar de plan.

## 8. Tu cuenta y tus datos

En **Mi perfil**:
- cambiás tus datos, tu correo y tu contraseña;
- descargás una **copia de tus datos personales**;
- podés **eliminar tu cuenta**. Los casos que tienen que conservarse por ley se mantienen durante el plazo de retención (5 años) y después se destruyen.

## 9. Administración de la plataforma

La cuenta de **Administrador** se reconoce por la marca «Admin» en el menú. En **Administración** ve el tablero de la plataforma con métricas agregadas (nunca casos, imágenes ni informes) y, debajo, las **organizaciones pendientes de aprobación**: cada una en dos líneas, con **Ver detalle** para el CUIT, el Referente y el plan. Recibe un correo cada vez que una organización paga y queda pendiente. A una aseguradora la puede aprobar solo cuando su Referente verificó la identidad.

## 10. Ayuda

- Si algo falla, el mensaje dice qué pasó y qué hacer.
- La página **Estado** (`/estado`) muestra si la plataforma, el análisis y el sello en Hedera funcionan.
- Los **Términos** y la **Política de privacidad** están al pie de cada página.
