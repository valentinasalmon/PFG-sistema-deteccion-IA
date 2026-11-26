# Configurar GitHub para el flujo de trabajo (ADR-0023)

Pasos que hace la autora una sola vez, con su cuenta de dueña del repositorio. Sin la protección de `main` el flujo pierde su red de seguridad: cada fusión se publica en producción.

## 1. Transición: un único Pull Request a `main`

La rama `infraestructura/flujo-github` ya contiene todo lo que había en `desarrollo` (accesibilidad, kit de usabilidad, teclado), más la portada nueva, la identidad simulada y este cambio de flujo. Por eso alcanza con **un solo Pull Request**:

1. **New pull request**: base **`main`** ← compare **`infraestructura/flujo-github`**.
2. Esperar el ✓ verde en todas las verificaciones.
3. Fusionarlo con **Create a merge commit** (es el último que entra así: conserva en `main` los commits de `desarrollo`). Se despliega solo.

`desarrollo` queda sin uso: se archiva en el paso 5.

## 2. Fusión con *squash* y borrado automático de ramas

En el repositorio: **Settings → General**, sección **Pull Requests**:

- Destildar **Allow merge commits** y **Allow rebase merging**.
- Dejar tildado solo **Allow squash merging**, con *Default commit message* en **Pull request title and description**.
- Tildar **Automatically delete head branches**: al integrar un Pull Request, GitHub borra la rama sola.

Cada Pull Request entra a `main` como un único commit con el título del Pull Request. GitHub suma las líneas `Co-authored-by` de los commits de la rama, así la asistencia de IA queda declarada.

## 3. Protección de `main`

**Settings → Rules → Rulesets → New ruleset → New branch ruleset**:

- **Ruleset name**: `main protegida`. **Enforcement status**: *Active*.
- **Target branches**: *Add target* → *Include default branch*.
- Tildar:
  - **Restrict deletions**.
  - **Require a pull request before merging** (aprobaciones requeridas: 0, porque la autora es la única persona del equipo).
  - **Require status checks to pass** → *Add checks* y agregar, uno por uno, los trabajos de la integración continua: *Backend (estilo, análisis, arquitectura y pruebas)*, *Frontend (análisis, pruebas y compilación)*, *Infraestructura (Terraform y scripts del servidor)*, *Seguridad (dependencias y configuración de Nginx)*, *Interfaz (sensor de diseño y recorrido de punta a punta)* y *Mensajes de commit (Conventional Commits en español)*. Tildar **Require branches to be up to date before merging**.
  - **Block force pushes**.
- **Create**.

Con esto el botón de fusionar queda gris hasta que todo esté en verde.

## 4. Dependabot

**Settings → Code security** (o *Advanced Security*): activar **Dependabot alerts** y **Dependabot security updates**. La configuración de las actualizaciones semanales ya está en `.github/dependabot.yml`.

## 5. Archivar las ramas viejas

Desde la computadora, en la carpeta del repositorio y con `main` al día (`git switch main && git pull`):

```bash
bash herramientas/archivar_ramas.sh            # muestra qué haría, sin cambiar nada
bash herramientas/archivar_ramas.sh --aplicar  # crea las etiquetas archivo/... y borra las ramas
```

Solo archiva ramas del modelo anterior cuyo trabajo ya está en `main` (incluida `desarrollo`). Conserva las que tienen trabajo sin integrar, como las de la red neuronal y las de otras sesiones del agente (`claude/…`). El [mapa de ramas](mapa-de-ramas.md) dice a qué área pertenece cada una.

## 6. Versiones

Al llegar a un hito (por ejemplo, la entrega): **Releases → Draft a new release → Choose a tag**, escribir `v1.0` → *Create new tag on publish*, destino `main` → **Generate release notes** → **Publish release**. Las notas se arman solas con los títulos de los Pull Requests desde la versión anterior.
