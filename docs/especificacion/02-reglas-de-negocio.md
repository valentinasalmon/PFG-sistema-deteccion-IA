# 2. Reglas de negocio

Las reglas de negocio son restricciones del dominio que el sistema debe respetar en todo momento, con independencia de la pantalla o la operación desde la que se apliquen. Se implementan en la capa de servicios.

## Cuentas y perfiles

| ID | Regla |
|---|---|
| **RN01** | Todo usuario tiene exactamente un perfil: **Abogado** o **Aseguradora**. Ambos perfiles tienen las mismas capacidades; el perfil se utiliza para la identificación del solicitante en los informes y para las estadísticas. **El perfil se elige al registrarse y no puede modificarse después** (decisión CP-12). |
| **RN02** | El perfil Abogado puede declarar opcionalmente el colegio de abogados al que pertenece. El perfil Aseguradora puede declarar opcionalmente la empresa a la que pertenece. Estos datos son declarativos y el sistema no los valida. No se solicitan matrículas ni otros datos de carácter legal. |
| **RN03** | El correo electrónico es único en el sistema y constituye el identificador de inicio de sesión. |
| **RN04** | Los datos personales de un usuario solo pueden ser modificados por su titular (derecho de rectificación, Ley N.° 25.326, art. 16). Ningún otro usuario, incluidos el Referente y el Administrador, puede modificarlos. |
| **RN05** | Un usuario no puede eliminar su cuenta mientras sea Responsable de casos activos: para cada uno debe elegir transferirlo o eliminarlo. Tampoco puede eliminarla mientras sea el único Referente de una organización con otros miembros. |

## Organizaciones

| ID | Regla |
|---|---|
| **RN06** | Un usuario puede crear varias organizaciones y pertenecer a varias organizaciones a la vez. |
| **RN07** | Toda organización tiene en todo momento **exactamente un Referente**. El creador es el Referente inicial. |
| **RN08** | El Referente solo puede abandonar la organización o eliminar su cuenta después de designar a otro miembro como Referente. Si es el único miembro, la organización se elimina junto con su salida, aplicando RN09. |
| **RN09** | Al eliminar una organización se eliminan definitivamente todos los casos de su espacio de trabajo **[PROPUESTA]**. La operación requiere doble confirmación y notifica por correo a todos los miembros. |
| **RN10** | Las invitaciones se envían a una dirección de correo, esté registrada o no, y vencen a los 7 días **[PROPUESTA]**. Una invitación solo puede aceptarla quien inicie sesión con el correo invitado. |
| **RN11** | El Referente puede editar los datos de la membresía (cargo o área dentro de la organización) pero no los datos personales del miembro (RN04). |

## Espacios de trabajo y planes

| ID | Regla |
|---|---|
| **RN12** | Todo caso pertenece a un único espacio de trabajo: el espacio personal de su creador o el de una organización de la que el creador es miembro. El espacio se elige al crear el caso y no puede cambiarse. **[PROPUESTA]** |
| **RN13** | Los casos del espacio personal **no pueden compartirse**. Solo los casos de una organización pueden compartirse, y únicamente con miembros de esa misma organización. |
| **RN14** | Los casos de una organización pertenecen a la organización. Si el Responsable abandona la organización o es desvinculado, debe transferir sus casos a otro miembro; si fue desvinculado sin hacerlo, la responsabilidad pasa al Referente. **[PROPUESTA]** |
| **RN15** | Cada espacio de trabajo está sujeto a los límites de su plan (cantidad de miembros, análisis por mes, imágenes por caso y almacenamiento). Al alcanzar un límite, la operación se rechaza con un mensaje que indica el límite y cómo ampliarlo. Los valores concretos están **[A DEFINIR]**. |

## Casos

| ID | Regla |
|---|---|
| **RN16** | El número de caso lo asigna el sistema con el formato `CASO-AAAA-NNNNNN` (año de creación y secuencia global), es único y no puede modificarse. El expediente es un dato externo opcional y no es único. |
| **RN17** | El tipo de caso es **Automovilístico** o **Laboral**. |
| **RN18** | Estados del caso y transiciones permitidas: `Borrador → En análisis` (al solicitar un análisis); `En análisis → Analizado` (al finalizar); `Analizado → En análisis` (nuevo análisis); `Borrador / Analizado → Cerrado`; `Cerrado → Archivado`; `Archivado → Cerrado` (desarchivar); `Cerrado / Archivado → Analizado o Borrador` (reabrir, según tenga o no informes). |
| **RN19** | Un caso en estado Cerrado o Archivado es de solo lectura: no admite edición de datos, carga o eliminación de imágenes ni nuevos análisis hasta que se reabra. |
| **RN20** | Solo el Responsable puede cerrar, archivar, desarchivar, reabrir, eliminar, compartir y transferir un caso. El Colaborador puede editar datos, cargar y eliminar imágenes y solicitar análisis. El Lector solo puede consultar y descargar informes. |
| **RN21** | La eliminación de un caso es inmediata y definitiva: elimina datos, imágenes e informes, incluidas todas las versiones almacenadas en S3. En el registro de auditoría se conserva únicamente la constancia de la operación y las huellas digitales de los archivos eliminados. |

## Imágenes y análisis

| ID | Regla |
|---|---|
| **RN22** | Solo se aceptan imágenes JPEG y PNG, cuyo formato se determina por la firma binaria del contenido y no por la extensión ni por el tipo declarado por el navegador. El tamaño máximo por imagen es de 20 MB **[PROPUESTA]**. |
| **RN23** | La huella digital SHA-256 se calcula al recibir el archivo, antes de cualquier procesamiento, y se almacena junto con la imagen. El archivo original nunca se modifica. |
| **RN24** | Una imagen incluida en un informe ya generado no puede eliminarse, salvo mediante la eliminación del caso completo o la destrucción por retención. |
| **RN25** | Un análisis se ejecuta únicamente por solicitud expresa del usuario y sobre al menos una imagen del caso. Un caso puede tener varios análisis; cada uno genera un informe nuevo y los anteriores se conservan. |
| **RN26** | Cada capa de análisis es independiente: la falla de una capa no impide que las demás se ejecuten. La capa fallida se informa como "No disponible" con el motivo. |
| **RN27** | Ninguna capa ni el informe emiten un veredicto. Las conclusiones se redactan en términos de indicios y siempre incluyen la recomendación de consultar a un profesional especializado. **No se calcula un puntaje global** que combine las cuatro capas. |
| **RN28** | La ausencia de manifiesto C2PA no se interpreta como evidencia de autenticidad. Un manifiesto válido que declara generación por IA es el indicio más fuerte del sistema. |
| **RN29** | El informe registra la versión del modelo de red neuronal y de cada componente de análisis utilizado, para garantizar la reproducibilidad. |

## Retención y privacidad

| ID | Regla |
|---|---|
| **RN30** | Los datos de un caso se conservan durante **2 años contados desde que el caso pasa a Cerrado o Archivado**. Reabrir el caso detiene el cómputo; al volver a cerrarse o archivarse, el plazo comienza nuevamente. |
| **RN31** | Treinta días antes del vencimiento del plazo de retención se notifica al Responsable por correo y en el panel. |
| **RN32** | El Responsable puede prorrogar el plazo de retención por 1 año, indicando un motivo (por ejemplo, juicio en trámite). La prórroga es renovable y queda registrada en la auditoría. **[PROPUESTA]** |
| **RN33** | Vencido el plazo sin prórroga, el sistema destruye el caso aplicando RN21. |
| **RN34** | Al eliminarse una cuenta, sus datos personales se suprimen y las entradas del registro de auditoría que la referencian se conservan con el usuario anonimizado. |
| **RN35** | El Administrador no accede a casos, imágenes ni informes. Solo consulta estadísticas agregadas y listados de usuarios y organizaciones. |
