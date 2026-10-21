# Levantar evidentIA en la computadora local

Guía corta para ver y probar la plataforma desde Visual Studio Code. Supone el entorno ya instalado: WSL2 con Ubuntu, Docker Desktop, Node.js y VS Code con la extensión WSL. Si falta algo, primero seguí la [instalación del entorno en Windows](instalacion-entorno-windows.md).

> Todos los comandos se escriben en la **terminal de Ubuntu** o en la terminal integrada de VS Code (`` Ctrl+` ``) abierta dentro de WSL.

## 1. Traer la rama que querés ver

```bash
cd ~/PFG-sistema-deteccion-IA
git fetch origin
git switch funcionalidad/022-rediseno-interfaz   # o la rama que quieras revisar
git pull
code .
```

VS Code se abre conectado a WSL; abajo a la izquierda dice «WSL: Ubuntu». Si pregunta por las extensiones recomendadas, aceptá instalarlas.

## 2. Primera vez: preparar backend y frontend

Hacelo una sola vez, o cuando cambien `requirements*.txt` o `package.json`.

```bash
# Backend
cd ~/PFG-sistema-deteccion-IA/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp -n .env.ejemplo .env        # crea el .env si no existe; nunca se sube al repositorio
deactivate

# Frontend
cd ../frontend
npm install
```

### Cuenta de prueba (entra a todas las pantallas)

Con los servicios levantados (paso 3), en una terminal:

```bash
cd ~/PFG-sistema-deteccion-IA/backend && source .venv/bin/activate
flask --app wsgi db upgrade
flask --app wsgi administracion cuenta-de-prueba
```

Deja lista la cuenta:
- **Correo**: `prueba@evidentia.local`
- **Contraseña**: `Prueba12345`
- **Características**:
  - perfil Abogado, verificada y con rol de Administrador;
  - con el «Estudio de prueba evidentIA», así se ven Organizaciones y Administración.

Si la bloqueaste por intentos fallidos, volvé a ejecutar el comando: la restablece. El comando no funciona en producción.

Para que un correo propio tenga el rol de Administrador, completá `ADMINISTRADORES=` en `backend/.env`.

## 3. Levantar todo desde VS Code

1. `Ctrl+Shift+P` → **Tasks: Run Task** → **evidentIA: levantar todo**. Se abren dos terminales:
   - el backend (Flask en http://localhost:5000), que antes levanta PostgreSQL, Redis y Mailpit con Docker y aplica las migraciones;
   - el frontend (Vite en http://localhost:5173).
2. Abrí **http://localhost:5173** en el navegador.
3. Los correos (verificación, avisos de análisis) no salen a internet: se ven en **http://localhost:8025** (Mailpit).

Para ver el diseño completo:
1. Registrate.
2. Confirmá el correo desde Mailpit.
3. Creá un caso y cargá una imagen JPEG.
4. Tocá **Analizar** y descargá el informe PDF.

## 4. Sin las tareas (tres terminales)

```bash
# Terminal 1: servicios
cd ~/PFG-sistema-deteccion-IA && docker compose up -d

# Terminal 2: backend
cd ~/PFG-sistema-deteccion-IA/backend && source .venv/bin/activate
flask --app wsgi db upgrade && flask --app wsgi run --port 5000 --debug

# Terminal 3: frontend
cd ~/PFG-sistema-deteccion-IA/frontend && npm run dev
```

## 5. Depurar y probar

- **Depurar el backend**: pestaña «Ejecutar y depurar» (`Ctrl+Shift+D`) → **evidentIA: depurar backend (Flask)**. Detené antes la tarea del backend para liberar el puerto 5000.
- **Pruebas**: **Tasks: Run Task** →
  - **evidentIA: pruebas y calidad del backend**;
  - **evidentIA: pruebas y calidad del frontend**.

## 6. Apagar

- Cerrá las terminales de las tareas (ícono de tacho).
- Detené los servicios con `docker compose down`. Los datos se conservan.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `port is already allocated` al levantar Docker | Otro PostgreSQL o Redis usa el puerto: `sudo service postgresql stop` o cerrá el otro contenedor. |
| La pantalla dice «Error del servidor» | Mirá la terminal del backend. Si falta una tabla, ejecutá `flask db upgrade`. |
| «No me deja entrar» | Usá la cuenta de prueba de arriba, o confirmá el correo desde Mailpit (http://localhost:8025) antes de iniciar sesión. |
| No llega el correo de verificación | Abrí http://localhost:8025. En desarrollo los correos quedan en Mailpit. |
| La capa de metadatos sale «No disponible» | Falta ExifTool: `sudo apt install libimage-exiftool-perl`. |
| El PDF no se genera | Faltan las bibliotecas de WeasyPrint: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`. |
