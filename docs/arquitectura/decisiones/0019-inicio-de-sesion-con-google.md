# ADR-0019: Inicio de sesión con Google por OpenID Connect del lado del servidor

- **Estado**: Aceptada (pedido de la autora, 2026-10-28)
- **Fecha**: 2026-10-28
- **Requisitos relacionados**: RF52, RNF01, RNF02

## Contexto

La autora pidió que se pueda entrar con Google. Además, la primera vez la persona tiene que completar igualmente su rubro (Abogado o Aseguradora).

La sesión ya era una cookie de servidor en Redis con token CSRF (ADR-0003 y ADR-0010), y la cookie era `SameSite=Strict`.

## Alternativas evaluadas

| Alternativa | Ventajas | Desventajas |
|---|---|---|
| Google Identity Services en el navegador (botón con JavaScript de Google) | Botón oficial, sin redirecciones | Carga código de un tercero en todas las pantallas de acceso. Obliga a abrir la CSP (`script-src`, `frame-src`) y a verificar la firma del token con las claves públicas de Google |
| Biblioteca de OAuth (Authlib) | Resuelve todo el protocolo | Una dependencia más para tres pasos simples |
| **Código de autorización con PKCE, del lado del servidor, sin biblioteca** | No hay JavaScript de terceros y la CSP no cambia. El secreto nunca llega al navegador. El *ID token* llega por TLS directo desde Google | Hay que implementar y probar `state`, `nonce` y PKCE |

## Decisión

1. **Flujo de código de autorización con PKCE (S256), del lado del servidor.**
   - El backend genera `state`, `nonce` y el verificador PKCE y los guarda en la sesión.
   - Al volver de Google, compara el `state` en tiempo constante y canjea el código en el *token endpoint* con el secreto del cliente.
2. **Validación del *ID token* sin verificar su firma.** Se validan:
   - el emisor;
   - la audiencia;
   - el vencimiento;
   - el `nonce`;
   - `email_verified`.

   El token llega por una conexión TLS directa con Google y autenticada con el secreto del cliente. OpenID Connect Core 1.0, sección 3.1.3.7, punto 6, admite en ese caso validar el emisor por TLS.
3. **Se guarda solo el `sub` de Google** (columna `google_sub`): ni tokens ni datos de Google más allá del nombre y el correo.
4. **Vinculación por correo solo si Google lo informa como verificado.** Si la cuenta local no estaba verificada, se anula su contraseña y se cierran sus sesiones. Esto evita el "secuestro previo" de cuentas: alguien registra el correo de otra persona y espera a que esa persona entre con Google.
5. **La cookie de sesión pasa de `SameSite=Strict` a `Lax`.**
   - Con `Strict`, la vuelta desde Google (una navegación desde otro sitio) llega sin la cookie y se pierde el `state`.
   - `Lax` sigue sin enviar la cookie en los POST de otros sitios.
   - Toda solicitud que modifica datos exige el token CSRF.

## Consecuencias

- **Se gana:**
  - registro sin otra contraseña ni correo de verificación;
  - CSP intacta;
  - ninguna dependencia nueva.
- **Se pierde:**
  - el atributo `Strict` de la cookie. Se actualizan CA21 de la 002, RNF02 CA2 y las notas de ADR-0003 y ADR-0010;
  - las cuentas creadas con Google no tienen contraseña propia hasta que la definen con "¿Olvidaste tu contraseña?".
- **Queda condicionado a:**
  - que la autora cree el cliente OAuth en Google Cloud y cargue el secreto en SSM, nunca en el repositorio;
  - el dominio propio, para publicar la aplicación de Google para todo el público (CP-30). Hasta entonces funciona en modo de prueba con hasta 100 usuarios.
