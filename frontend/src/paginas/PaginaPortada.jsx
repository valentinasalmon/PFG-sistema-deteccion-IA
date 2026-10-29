/**
 * Portada pública de evidentIA (funcionalidad 033).
 *
 * Presenta el problema, la solución, para quién es y los planes, y lleva al
 * registro con el camino y el plan ya elegidos (``/registro?tipo=...&plan=...``,
 * que la funcionalidad 032 aplica al crear la cuenta). Combina las propuestas
 * que eligió la autora: encabezado, solución, «Para quién» y preguntas de la
 * B; problema y planes de la A.
 *
 * Los límites de los planes salen del sistema y el precio vacío se muestra
 * «A confirmar». Como toda salida de la plataforma, aclara que ofrece
 * indicios y no veredictos (RN27, ADR-0017).
 *
 * Realiza: RF19, RF20; RN27; RNF10; CA1 a CA5 de la funcionalidad 033.
 */
import { useRef, useState } from 'react'
import { Link } from 'react-router'
import { listarPlanes } from '../api/pagos.js'
import Icono from '../componentes/Icono.jsx'
import { useAparecer } from '../hooks/useAparecer.js'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { NOMBRES_DE_PLAN, textoDelPrecio } from '../utilidades/planes.js'
import '../estilos/portada.css'

const CAPAS = [
  { nombre: 'Metadatos', nivel: 'debil' },
  { nombre: 'Credenciales C2PA', nivel: 'sin' },
  { nombre: 'Niveles de error', nivel: 'moderado' },
  { nombre: 'Red neuronal', nivel: 'debil' },
]
const NIVELES = {
  sin: 'Sin indicios',
  debil: 'Indicios débiles',
  moderado: 'Indicios moderados',
}

const PROBLEMAS = [
  {
    titulo: 'Fotos que no resisten una pericia',
    texto:
      'Se presentan imágenes sin saber si fueron retocadas, recortadas o generadas, y el problema aparece cuando ya es tarde.',
  },
  {
    titulo: 'Revisión manual, lenta y cara',
    texto:
      'Cada caso dudoso termina en un perito, aunque muchas imágenes podrían ordenarse antes con indicios técnicos.',
  },
  {
    titulo: 'Sin cadena de custodia',
    texto:
      'Las fotos viajan por chats y correos: nadie puede demostrar después que la imagen analizada es la misma que se recibió.',
  },
]

const SOLUCIONES = [
  {
    icono: 'candado',
    titulo: 'Cadena de custodia en Hedera',
    texto:
      'La huella SHA-256 de cada imagen y de cada informe queda sellada en una red pública: nadie puede cambiarla sin que se note.',
    variante: 'azul',
  },
  {
    icono: 'documento',
    titulo: 'Informe PDF verificable',
    texto: 'Breve, adaptado al rubro, con un código para que cualquiera lo verifique sin cuenta.',
  },
  {
    icono: 'celular',
    titulo: 'Fotos desde el celular',
    texto: 'Un enlace para que la persona afectada suba sus propias fotos.',
  },
  {
    icono: 'organizaciones',
    titulo: 'Trabajo en equipo',
    texto: 'Casos compartidos con permisos y auditoría de cada acción.',
    variante: 'lima',
  },
  {
    icono: 'perfil',
    titulo: 'Persona en el circuito',
    texto: 'Indicios, nunca veredictos. Umbrales publicados y la decisión siempre humana.',
  },
]

const SEGMENTOS = [
  {
    icono: 'perfil',
    titulo: 'Abogados independientes',
    texto:
      'Revisás las fotos de tu cliente antes de presentarlas y adjuntás el informe verificable al escrito. Plan personal gratuito.',
    enlace: '/registro?tipo=independiente',
    accion: 'Crear cuenta gratis',
  },
  {
    icono: 'organizaciones',
    titulo: 'Estudios jurídicos',
    texto:
      'Registrás el estudio, sumás a tu equipo y comparten casos con permisos. Plan Básico o Profesional.',
    enlace: '/registro?tipo=estudio',
    accion: 'Registrar mi estudio',
  },
  {
    icono: 'escudo',
    titulo: 'Aseguradoras',
    texto:
      'Revisás las fotos de cada siniestro antes de derivarlo y detectás reclamos dudosos. Un Administrador aprueba la cuenta y el equipo entra por invitación.',
    enlace: '/registro?tipo=aseguradora',
    accion: 'Registrar mi aseguradora',
  },
]

const PREGUNTAS = [
  {
    pregunta: '¿evidentIA dice si una foto es falsa?',
    respuesta:
      'No. Muestra indicios técnicos con su nivel y su explicación, y recomienda consultar a un perito. La decisión es siempre de una persona.',
  },
  {
    pregunta: '¿Cómo se paga el plan?',
    respuesta:
      'Por transferencia a un CVU con la referencia del pago, al final del registro; se acredita sola y el plan queda aplicado. Por ahora el cobro es una simulación.',
  },
  {
    pregunta: '¿Puedo empezar solo y crear mi estudio después?',
    respuesta: 'Sí. Desde Mi perfil creás el estudio, elegís el plan y pagás.',
  },
  {
    pregunta: '¿Cómo se cuida la prueba?',
    respuesta:
      'Cada imagen guarda su huella desde la carga y queda sellada en Hedera; cada acceso queda en la auditoría y el informe se puede verificar con su código.',
  },
  {
    pregunta: '¿Qué pasa con las imágenes y los datos personales?',
    respuesta:
      'Se usan solo para el análisis del caso, con acceso por permisos, y se eliminan al vencer el plazo de conservación (Ley 25.326).',
  },
  {
    pregunta: '¿La aseguradora necesita aprobación?',
    respuesta:
      'Sí. Primero paga el plan y después un Administrador comprueba que figure en el catálogo de la SSN. Si no se aprueba, el pago se devuelve.',
  },
]

const ORGANIZACIONES = [
  { valor: 'estudio', etiqueta: 'Estudio jurídico' },
  { valor: 'aseguradora', etiqueta: 'Aseguradora' },
]

function Nivel({ nivel }) {
  return <span className={`portada-nivel portada-nivel--${nivel}`}>{NIVELES[nivel]}</span>
}

/** Ilustración de una foto de un siniestro (no es un caso real). */
function Foto({ calor = false, variante = '' }) {
  return (
    <div className={`portada-foto ${variante}`} aria-hidden="true">
      {calor && (
        <>
          <span className="portada-calor portada-calor--1" />
          <span className="portada-calor portada-calor--2" />
        </>
      )}
    </div>
  )
}

function VistaDeLaApp() {
  return (
    <div className="portada-app" aria-hidden="true">
      <div className="portada-app__barra">
        <i />
        <i />
        <i />
        <span>evidentia · Caso 2026-0147</span>
      </div>
      <div className="portada-app__cuerpo">
        <div className="portada-app__menu">
          <img src="/marca/logo-tipografia-blanca.png" alt="" />
          <b>Inicio</b>
          <span>Casos</span>
          <span>Organización</span>
          <span>Mi perfil</span>
        </div>
        <div className="portada-app__principal">
          <small>Caso 2026-0147 · Automovilístico</small>
          <strong>Choque en Av. Corrientes</strong>
          <div className="portada-app__miniaturas">
            <div className="visor portada-app__elegida">
              <Foto calor />
              <span className="portada-escaneo" />
            </div>
            <Foto variante="portada-foto--verde" />
            <Foto variante="portada-foto--gris" />
          </div>
        </div>
        <div className="portada-app__lateral">
          <strong>Indicios de la imagen 1</strong>
          {CAPAS.map((capa, indice) => (
            <div key={capa.nombre} className="portada-app__capa" style={{ '--orden': indice }}>
              {capa.nombre}
              <Nivel nivel={capa.nivel} />
            </div>
          ))}
          <div className="portada-app__huella">
            SHA-256 · 9f2c…41ab
            <br />
            Sellada en Hedera
          </div>
        </div>
      </div>
    </div>
  )
}

function Limites({ plan }) {
  if (!plan) return null
  return (
    <ul className="portada-plan__limites">
      {plan.miembros && <li>Hasta {plan.miembros} miembros</li>}
      <li>{plan.analisis_mes} análisis por mes</li>
      <li>{plan.imagenes_por_caso} imágenes por caso</li>
      {plan.almacenamiento_gb && <li>{plan.almacenamiento_gb} GB de almacenamiento</li>}
      <li>Sello en Hedera e informe verificable</li>
      {plan.miembros && <li>Casos compartidos con permisos</li>}
    </ul>
  )
}

function SeccionPlanes() {
  const { datos } = useDatos(listarPlanes)
  const [tipo, setTipo] = useState('estudio')
  const planes = Object.fromEntries((datos?.planes ?? []).map((plan) => [plan.codigo, plan]))
  const tarjetas = [
    {
      codigo: 'basico',
      para: tipo === 'estudio' ? 'Estudios chicos' : 'Equipos chicos',
    },
    {
      codigo: 'profesional',
      para: tipo === 'estudio' ? 'Estudios con equipo' : 'Áreas de siniestros',
      destacado: true,
    },
  ]
  const elegido = ORGANIZACIONES.find((opcion) => opcion.valor === tipo)

  return (
    <section id="planes" className="portada-planes" aria-labelledby="titulo-planes">
      <div className="portada-contenedor">
        <div className="portada-cabeza portada-cabeza--centrada" data-aparecer>
          <small>Planes</small>
          <h2 id="titulo-planes">Elegí tu plan y creá la cuenta con él.</h2>
          <p>
            El estudio y la aseguradora pagan por transferencia al final del registro; el plan queda aplicado
            apenas se acredita.
          </p>
        </div>
        <fieldset className="portada-selector" data-aparecer>
          <legend>¿Para qué tipo de organización?</legend>
          {ORGANIZACIONES.map((opcion) => (
            <label key={opcion.valor} className={tipo === opcion.valor ? 'elegido' : undefined}>
              <input
                type="radio"
                name="tipo-organizacion"
                value={opcion.valor}
                checked={tipo === opcion.valor}
                onChange={() => setTipo(opcion.valor)}
              />
              {opcion.etiqueta}
            </label>
          ))}
        </fieldset>
        <div className="portada-planes__grilla">
          <article className="portada-plan" data-aparecer aria-labelledby="plan-personal">
            <span className="portada-plan__para">Abogado o abogada independiente</span>
            <h3 id="plan-personal">Personal</h3>
            <p className="portada-plan__precio">Gratis</p>
            <Limites plan={datos?.personal} />
            <Link to="/registro?tipo=independiente" className="portada-boton portada-boton--borde-claro">
              Crear cuenta gratis
            </Link>
          </article>
          {tarjetas.map(({ codigo, para, destacado }) => {
            const plan = planes[codigo]
            const nombre = NOMBRES_DE_PLAN[codigo]
            return (
              <article
                key={codigo}
                className={`portada-plan${destacado ? ' portada-plan--destacado' : ''}`}
                data-aparecer
                aria-labelledby={`plan-${codigo}`}
              >
                {destacado && <span className="portada-plan__cinta">Para equipos grandes</span>}
                <span className="portada-plan__para">
                  {elegido.etiqueta} · {para}
                </span>
                <h3 id={`plan-${codigo}`}>{nombre}</h3>
                <p className="portada-plan__precio">
                  {textoDelPrecio(plan?.precio)} <small>por mes</small>
                </p>
                <Limites plan={plan} />
                <Link
                  to={`/registro?tipo=${tipo}&plan=${codigo}`}
                  className={`portada-boton ${destacado ? 'portada-boton--azul' : 'portada-boton--lima'}`}
                >
                  Elegir {nombre}
                  <span className="portada-oculto"> para {elegido.etiqueta.toLowerCase()}</span>
                </Link>
              </article>
            )
          })}
        </div>
        <p className="portada-planes__aclaracion">
          Cada botón abre el registro con el plan ya elegido · Pago por transferencia con Cresium (por ahora,
          simulado) · Precios a confirmar
        </p>
      </div>
    </section>
  )
}

export default function PaginaPortada() {
  const { usuario } = useSesion()
  const refPortada = useRef(null)
  useAparecer(refPortada)

  return (
    <div className="portada" ref={refPortada}>
      <a href="#contenido" className="saltar-al-contenido">
        Saltar al contenido
      </a>
      <header className="portada-heroe">
        <div className="portada-contenedor">
          <nav className="portada-nav" aria-label="Portada">
            <Link to="/presentacion" className="portada-nav__logo">
              <img src="/marca/logo-tipografia-negra.png" alt="evidentIA" />
            </Link>
            <ul>
              <li>
                <a href="#problema">El problema</a>
              </li>
              <li>
                <a href="#solucion">La solución</a>
              </li>
              <li>
                <a href="#para-quien">Para quién</a>
              </li>
              <li>
                <a href="#planes">Planes</a>
              </li>
              <li>
                <a href="#preguntas">Preguntas</a>
              </li>
            </ul>
            <div className="portada-nav__acciones">
              {usuario ? (
                <Link to="/" className="portada-boton portada-boton--azul">
                  Ir a mi cuenta
                </Link>
              ) : (
                <>
                  <Link to="/iniciar-sesion" className="portada-nav__entrar">
                    Iniciar sesión
                  </Link>
                  <Link to="/registro" className="portada-boton portada-boton--azul">
                    Crear cuenta
                  </Link>
                </>
              )}
            </div>
          </nav>
          <main id="contenido" className="portada-heroe__texto">
            <span className="portada-sello">
              <span aria-hidden="true">◆</span> Tu primera línea de defensa contra el fraude visual
            </span>
            <h1>
              Revisá cada foto del caso <span className="visor portada-marco">antes</span> de que la revise
              otro.
            </h1>
            <p>
              Análisis por capas, cadena de custodia sellada en Hedera e informe verificable, para abogados,
              estudios jurídicos y aseguradoras.
            </p>
            <div className="portada-ctas">
              <a href="#planes" className="portada-boton portada-boton--azul portada-boton--grande">
                Elegir un plan
              </a>
              <Link
                to="/registro?tipo=independiente"
                className="portada-boton portada-boton--borde portada-boton--grande"
              >
                Probar gratis como abogado
              </Link>
            </div>
            <p className="portada-heroe__nota">
              Ofrece indicios, no veredictos: la decisión siempre es de una persona.
            </p>
          </main>
          <VistaDeLaApp />
        </div>
      </header>

      <div className="portada-cinta" aria-hidden="true">
        <div className="portada-cinta__pista">
          {[0, 1].map((copia) => (
            <span key={copia}>
              {[
                'Metadatos',
                'Credenciales C2PA',
                'Niveles de error',
                'Red neuronal',
                'Sello en Hedera',
                'Informe verificable',
                'Cadena de custodia',
              ].map((texto) => (
                <span key={texto}>{texto}</span>
              ))}
            </span>
          ))}
        </div>
      </div>

      <section
        id="problema"
        className="portada-seccion portada-seccion--fondo"
        aria-labelledby="titulo-problema"
      >
        <div className="portada-contenedor">
          <div className="portada-cabeza" data-aparecer>
            <small>El problema</small>
            <h2 id="titulo-problema">Hoy editar una foto lleva segundos. Probar que no se editó, semanas.</h2>
            <p>
              Las imágenes son prueba central en siniestros, reclamos y juicios, y la inteligencia artificial
              generativa hace que cualquier persona pueda alterarlas sin dejar rastros visibles.
            </p>
          </div>
          <ol className="portada-problemas">
            {PROBLEMAS.map((problema, indice) => (
              <li
                key={problema.titulo}
                className="portada-problema"
                data-aparecer
                style={{ '--orden': indice }}
              >
                <span className="portada-problema__numero" aria-hidden="true">
                  0{indice + 1}
                </span>
                <h3>{problema.titulo}</h3>
                <p>{problema.texto}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="solucion" className="portada-seccion" aria-labelledby="titulo-solucion">
        <div className="portada-contenedor">
          <div className="portada-titulo-doble" data-aparecer>
            <div className="portada-cabeza">
              <small>La solución</small>
              <h2 id="titulo-solucion">Todo lo que hace falta para confiar en una imagen.</h2>
            </div>
            <p>
              evidentIA no reemplaza al perito: le llega mejor preparado el caso que vale la pena revisar.
            </p>
          </div>
          <div className="portada-bento">
            <article className="portada-celda portada-celda--principal" data-aparecer>
              <span className="portada-celda__icono">
                <Icono nombre="analisis" tamanio={28} />
              </span>
              <h3>Análisis por capas</h3>
              <p>
                Metadatos, credenciales de contenido C2PA, niveles de error y una red neuronal entrenada para
                reconocer manipulación y generación por IA.
              </p>
              <ul className="portada-celda__capas">
                {CAPAS.map((capa) => (
                  <li key={capa.nombre}>
                    {capa.nombre}
                    <Nivel nivel={capa.nivel} />
                  </li>
                ))}
              </ul>
              <div className="visor portada-celda__foto">
                <Foto calor />
                <span className="portada-escaneo" />
              </div>
            </article>
            {SOLUCIONES.map((solucion, indice) => (
              <article
                key={solucion.titulo}
                className={`portada-celda${solucion.variante ? ` portada-celda--${solucion.variante}` : ''}`}
                data-aparecer
                style={{ '--orden': indice }}
              >
                <span className="portada-celda__icono">
                  <Icono nombre={solucion.icono} tamanio={28} />
                </span>
                <h3>{solucion.titulo}</h3>
                <p>{solucion.texto}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section
        id="para-quien"
        className="portada-seccion portada-seccion--sin-arriba"
        aria-labelledby="titulo-para-quien"
      >
        <div className="portada-contenedor">
          <div className="portada-titulo-doble" data-aparecer>
            <div className="portada-cabeza">
              <small>Para quién</small>
              <h2 id="titulo-para-quien">Pensado para quienes trabajan con imágenes como prueba.</h2>
            </div>
            <p>Tres formas de usarla, con el plan que corresponde a cada una.</p>
          </div>
          <div className="portada-segmentos">
            {SEGMENTOS.map((segmento, indice) => (
              <article
                key={segmento.titulo}
                className="portada-segmento"
                data-aparecer
                style={{ '--orden': indice }}
              >
                <span className="portada-segmento__icono">
                  <Icono nombre={segmento.icono} tamanio={26} />
                </span>
                <h3>{segmento.titulo}</h3>
                <p>{segmento.texto}</p>
                <Link to={segmento.enlace}>
                  {segmento.accion} <span aria-hidden="true">→</span>
                </Link>
              </article>
            ))}
          </div>
        </div>
      </section>

      <SeccionPlanes />

      <section id="preguntas" className="portada-seccion" aria-labelledby="titulo-preguntas">
        <div className="portada-contenedor portada-preguntas">
          <div className="portada-cabeza" data-aparecer>
            <small>Preguntas frecuentes</small>
            <h2 id="titulo-preguntas">Lo que suelen preguntarnos.</h2>
            <p>
              Si recibiste un informe, podés comprobar que no cambió en{' '}
              <Link to="/verificar">la página de verificación</Link>, sin cuenta.
            </p>
          </div>
          <div className="portada-preguntas__lista">
            {PREGUNTAS.map((item) => (
              <details key={item.pregunta} data-aparecer>
                <summary>{item.pregunta}</summary>
                <p>{item.respuesta}</p>
              </details>
            ))}
          </div>
        </div>
      </section>

      <section className="portada-cierre" aria-labelledby="titulo-cierre" data-aparecer>
        <div>
          <h2 id="titulo-cierre">Antes de presentar una foto, mirala con evidentIA.</h2>
          <p>
            Elegí tu plan y creá la cuenta en minutos. Si llegás desde un plan, el registro ya lo trae
            elegido.
          </p>
        </div>
        <div className="portada-ctas">
          <a href="#planes" className="portada-boton portada-boton--lima portada-boton--grande">
            Ver los planes
          </a>
          <Link to="/registro" className="portada-boton portada-boton--borde-claro portada-boton--grande">
            Crear cuenta
          </Link>
        </div>
      </section>

      <footer className="portada-pie">
        <div className="portada-contenedor">
          <img src="/marca/logo-tipografia-negra.png" alt="evidentIA" />
          <p className="portada-pie__descargo">
            La plataforma ofrece indicios para una evaluación preliminar y no emite veredictos. Ante cualquier
            duda, consultá con un perito especializado.
          </p>
          <nav aria-label="Enlaces del pie">
            <Link to="/terminos">Términos de Uso</Link>
            <Link to="/privacidad">Política de Privacidad</Link>
            <Link to="/verificar">Verificar un informe</Link>
            <Link to="/estado">Estado del sistema</Link>
          </nav>
        </div>
      </footer>
    </div>
  )
}
