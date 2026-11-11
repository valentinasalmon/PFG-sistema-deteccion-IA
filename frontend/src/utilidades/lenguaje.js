/**
 * Textos que cambian según el rubro de la cuenta (funcionalidad 022).
 *
 * evidentIA ofrece el mismo motor con dos servicios: "Legal" para abogados y
 * estudios jurídicos, y "Seguros" para aseguradoras. Cada uno habla el idioma
 * de su rubro (caso y expediente; siniestro y número de siniestro), sin
 * cambiar los datos que guarda el backend.
 *
 * Desde la funcionalidad 037 también cambia el nombre del objeto de trabajo:
 * «caso» para abogados y «siniestro» para aseguradoras, en el menú, los
 * títulos, los botones y el informe. Las direcciones (``/casos``) no cambian.
 *
 * Realiza: RNF10 (lenguaje claro y apropiado para cada usuario).
 */
/**
 * Frases que nombran el objeto de trabajo, armadas a partir de una sola
 * palabra en singular y en plural (037). Así cada rubro define una palabra y
 * todas las pantallas dicen lo mismo, sin una lista de frases que mantener.
 * «Caso» y «siniestro» son masculinos, por eso los artículos son fijos.
 */
export function vocabulario(singular, plural) {
  const mayuscula = (texto) => texto[0].toUpperCase() + texto.slice(1)
  return {
    caso: singular,
    casos: plural,
    Caso: mayuscula(singular),
    Casos: mayuscula(plural),
    nuevo: `Nuevo ${singular}`,
    recientes: `${mayuscula(plural)} recientes`,
    verTodos: `Ver todos los ${plural}`,
    buscar: `Buscar un ${singular}`,
    tipo: `Tipo de ${singular}`,
    vacio: `Todavía no tenés ${plural}.`,
  }
}

const TEXTOS = {
  abogado: {
    ...vocabulario('caso', 'casos'),
    servicio: 'Legal',
    bajadaPanel: 'Prepará la prueba de tus casos: cargá las imágenes, analizalas y descargá el informe.',
    bajadaCasos: 'Los casos de tus clientes y los que compartieron con vos.',
    bajadaNuevoCaso: 'Los datos del hecho identifican el caso en el informe que vas a presentar.',
    etiquetaReferencia: 'Expediente',
    usoInforme: 'para acompañar una demanda, una mediación o un reclamo',
  },
  aseguradora: {
    ...vocabulario('siniestro', 'siniestros'),
    servicio: 'Seguros',
    bajadaPanel: 'Verificá las fotos de cada siniestro antes de liquidarlo: subilas, analizalas y descargá el informe.',
    bajadaCasos: 'Los siniestros que revisa tu equipo, con su estado y sus fotos.',
    bajadaNuevoCaso: 'Cargá los datos del siniestro tal como figuran en la denuncia.',
    etiquetaReferencia: 'N.° de siniestro',
    usoInforme: 'para respaldar la decisión sobre un siniestro',
  },
}

/** Textos del rubro de la cuenta; por defecto, los del servicio Legal. */
export function textosDelRubro(perfil) {
  return TEXTOS[perfil] ?? TEXTOS.abogado
}
