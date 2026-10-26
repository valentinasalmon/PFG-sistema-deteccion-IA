# 029 · Plan técnico

- **Modelo `VersionSistema`**: `version`, `commit` (único), `huella`, `desplegada_en` y las columnas `sello_*`. `TIPO_SELLO = "version"`. Migración `c9e5a2f3d029`.
- **`ServicioVersiones.registrar`**: valida un commit de 40 y una huella de 64 caracteres hexadecimales, crea la versión si no existe, audita y pide el sello. `por_commit` busca la versión.
- **`ServicioSellos`**: además de imágenes e informes, procesa las versiones (`RepositorioVersiones.con_sello_en_curso`). La auditoría usa el recurso `version` cuando el objeto no pertenece a un caso.
- **Commit en ejecución**: `desplegar.sh` escribe el archivo `COMMIT` en la raíz de la versión; `configuracion.COMMIT` lo lee (o toma la variable `COMMIT`). `ServicioAnalisis` lo guarda en `analisis.versiones["commit"]`. La versión de la aplicación pasa a 0.3.0.
- **Verificación pública**: `GET /api/verificacion` agrega `version` (número, commit corto, huella del artefacto y sello), y la página la muestra.
- **Pruebas**: registro y sello por comando, sin duplicar; datos inválidos; el análisis guarda el commit y la verificación muestra la versión sellada.
