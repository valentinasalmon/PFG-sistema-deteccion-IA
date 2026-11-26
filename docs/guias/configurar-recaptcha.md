# Configurar reCAPTCHA de Google (funcionalidad 051)

Pasos que hace la autora una sola vez. Mientras no estén hechos, reCAPTCHA queda desactivado y la plataforma funciona igual. Fuente: documentación de Google Cloud Fraud Defense, consultada el 2026-11-26.

## 1. Activar la API en el proyecto de Google Cloud

1. Entrar a [console.cloud.google.com](https://console.cloud.google.com) y elegir arriba **el mismo proyecto del inicio con Google**.
2. Buscar **reCAPTCHA Enterprise API** en la barra de búsqueda → **Habilitar** (*Enable*). Según Google, no hace falta activar la facturación para empezar (ver CP-44).
3. Anotar el **ID del proyecto**: aparece en el selector de proyectos (por ejemplo, `evidentia-123456`). No es el nombre del proyecto ni el número.

## 2. Crear la clave del sitio

1. Buscar **Fraud Defense** (o **reCAPTCHA**) → pestaña **Claves** (*Keys*) → **Crear clave** (*Create key*).
2. **Nombre visible**: `evidentIA producción`. **Tipo de aplicación**: **Web**.
3. Dejar **apagado** «Disable domain verification». En **Lista de dominios** → **Agregar un dominio** → `evidentiaa.com.ar`.
4. Dejar el tipo **por puntaje** (*score-based*), que es el que viene marcado. No tildar la opción de pruebas.
5. **Crear**. Copiar el **ID de la clave**: es la *clave del sitio*. Es pública, no es secreta.

## 3. Crear la clave de API (esta sí es secreta)

1. Ir a **APIs y servicios → Credenciales → Crear credenciales → Clave de API**.
2. En la clave nueva → **Editar** → **Restricciones de API** → **Restringir clave** → tildar solo **reCAPTCHA Enterprise API** → **Guardar**.
3. Copiar la clave. **No la pegues en ningún chat ni archivo.**

## 4. Cargar los valores en Parameter Store

Desde la terminal donde usás AWS, cargar los tres valores con estos comandos.

El proyecto y la clave del sitio son públicos:

```bash
aws ssm put-parameter --name /deteccion-imagenes/produccion/RECAPTCHA_PROYECTO --type String --value "ID-DEL-PROYECTO" --overwrite --region eu-west-1
aws ssm put-parameter --name /deteccion-imagenes/produccion/RECAPTCHA_CLAVE_SITIO --type String --value "ID-DE-LA-CLAVE" --overwrite --region eu-west-1
```

La clave de API es secreta. Pegala cuando la terminal la pida; no se ve mientras escribís:

```bash
read -rs SECRETO && aws ssm put-parameter --name /deteccion-imagenes/produccion/RECAPTCHA_CLAVE_API --type SecureString --value "$SECRETO" --overwrite --region eu-west-1 && unset SECRETO
```

El próximo despliegue (o un `generar_entorno.sh` en el servidor y reiniciar `plataforma-web`) los toma.

## 5. Probar (CA5 de la 051)

1. En `https://evidentiaa.com.ar/estado` tiene que decir **reCAPTCHA de Google · Activo**.
2. Cerrar sesión, iniciar sesión de nuevo y crear una cuenta de prueba: abajo a la derecha aparece el distintivo de reCAPTCHA y todo funciona sin tildar nada.
3. En Google Cloud → Fraud Defense → la clave: a los pocos minutos aparecen las evaluaciones.
4. Si algo falla, el formulario dice «No pudimos comprobar que seas una persona». Revisar que el dominio de la clave sea `evidentiaa.com.ar` y que la clave de API esté restringida a la API correcta.
