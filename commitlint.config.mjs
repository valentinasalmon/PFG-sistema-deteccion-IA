/**
 * Configuración de commitlint (RNF20, ADR-0007).
 *
 * Exige Conventional Commits con tipos en español. Es la única fuente de la
 * lista de tipos: la usan el gancho local (.pre-commit-config.yaml) y la
 * integración continua (.github/workflows).
 */
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'funcionalidad',
        'correccion',
        'documentacion',
        'estilo',
        'refactorizacion',
        'rendimiento',
        'pruebas',
        'construccion',
        'integracion',
        'tarea',
        'revertir',
      ],
    ],
    // Las descripciones en español pueden empezar con mayúscula en nombres propios.
    'subject-case': [0],
    // El largo máximo queda en 100 (el de config-conventional) para los commits ya
    // subidos y los de Dependabot; los del agente los limita a 72 el gancho del arnés
    // revisar_commit.py antes de crearlos (ADR-0023).
  },
}
