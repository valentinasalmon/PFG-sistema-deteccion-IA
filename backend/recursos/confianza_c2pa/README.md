# Lista de confianza de C2PA

Certificados raíz e intermedios públicos con los que la capa 2 verifica la firma de las credenciales de contenido (funcionalidad 009, RF40). No son secretos: el consorcio C2PA los publica para que cualquier validador los use.

| Archivo | Contenido | SHA-256 |
|---|---|---|
| `C2PA-TRUST-LIST.pem` | Autoridades que emiten certificados de firma de credenciales (32 certificados: Google, Trufo, que emite el de OpenAI, DigiCert, SSL.com, Adobe, Xiaomi, Huawei y otras). | `b3949271a07b007e92ef1d18050b55388f5e0d2686a16fd864176c48421af8ae` |
| `C2PA-TSA-TRUST-LIST.pem` | Autoridades de sello de tiempo de las firmas (23 certificados). | `7182cb227c02701be0eebd67ab635fca7f85431c32796fb53b267c657cd2c675` |

- **Fuente**: repositorio público `c2pa-org/conformance-public`, carpeta `trust-list/`, rama `main`. Descargada el 2026-10-19.
- **Licencia**: pendiente de confirmar. Es un listado publicado por el consorcio para los validadores.
- **Versión en los resultados**: la capa registra los primeros 12 caracteres de la huella SHA-256 de cada lista (RN29). Así se sabe con qué lista se verificó cada análisis.

## Cómo actualizarla

```bash
cd backend/recursos/confianza_c2pa
curl -sSO https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem
curl -sSO https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem
sha256sum *.pem   # actualizar la tabla de arriba
```

Hay que reiniciar el proceso trabajador para que tome la lista nueva. Los análisis anteriores conservan la versión con la que se hicieron.
