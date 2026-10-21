/**
 * Textos que cambian según el rubro de la cuenta (funcionalidad 022).
 *
 * evidentIA ofrece el mismo motor con dos servicios: "Legal" para abogados y
 * estudios jurídicos, y "Seguros" para aseguradoras. Cada uno habla el idioma
 * de su rubro (caso y expediente; siniestro y número de siniestro), sin
 * cambiar los datos que guarda el backend.
 *
 * Realiza: RNF10 (lenguaje claro y apropiado para cada usuario).
 */
const TEXTOS = {
  abogado: {
    servicio: 'Legal',
    bajadaPanel: 'Prepará la prueba de tus casos: cargá las imágenes, analizalas y descargá el informe.',
    bajadaCasos: 'Los casos de tus clientes y los que compartieron con vos.',
    bajadaNuevoCaso: 'Los datos del hecho identifican el caso en el informe que vas a presentar.',
    etiquetaReferencia: 'Expediente',
    usoInforme: 'para acompañar una demanda, una mediación o un reclamo',
  },
  aseguradora: {
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
