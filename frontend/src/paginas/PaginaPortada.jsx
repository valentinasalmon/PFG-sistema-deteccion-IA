/**
 * Portada pública de evidentIA (funcionalidad 034, tercera tanda).
 *
 * Reemplaza el diseño de la 033 por la composición que aprobó la autora:
 * encabezado oscuro con la pregunta centrada y el sistema real debajo, las
 * cuatro miradas sobre cada foto, los tres pasos, los planes y el cierre.
 * En la quinta tanda (2026-11-02) la autora pidió una portada más limpia:
 * sin los beneficios ni los globos del encabezado, sin la sección «para
 * quién», sin el sello de Ctrl K ni las letras gigantes, sin el ojo del
 * cierre, las miradas en filas con el título a la izquierda y los planes
 * alineados. Habla de beneficios para el cliente: no nombra proveedores ni
 * detalles internos de la infraestructura.
 *
 * Los límites de los planes salen del sistema y el precio vacío se muestra
 * «A confirmar». Cada botón abre el registro con el camino y el plan ya
 * elegidos (``/registro?tipo=...&plan=...``, funcionalidad 032). Como toda
 * salida de la plataforma, aclara que ofrece indicios y no veredictos
 * (RN27, ADR-0017).
 *
 * Realiza: RF19, RF20; RN27; RNF10; CA1 a CA5 de la funcionalidad 033.
 */
import { useRef, useState } from 'react'
import { Link } from 'react-router'
import { listarPlanes } from '../api/pagos.js'
import { useAparecer } from '../hooks/useAparecer.js'
import { useDatos } from '../hooks/useDatos.js'
import { useSesion } from '../hooks/useSesion.js'
import { NOMBRES_DE_PLAN, textoDelPrecio } from '../utilidades/planes.js'
import '../estilos/portada.css'

/** Trazos de los íconos propios de la portada (24×24, línea). */
const TRAZOS = {
  documento: (
    <>
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M9 8h6M9 12h6M9 16h3" />
    </>
  ),
  firma: (
    <>
      <path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z" />
      <path d="M9 12l2 2 4-4" />
    </>
  ),
  retoque: (
    <>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="M3 15l5-5 4 4 3-3 6 6" />
    </>
  ),
  red: (
    <>
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4M5 5l3 3M16 16l3 3M19 5l-3 3M8 16l-3 3" />
    </>
  ),
}

function Trazo({ nombre }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
      {TRAZOS[nombre]}
    </svg>
  )
}

const MIRADAS = [
  {
    icono: 'documento',
    codigo: 'METADATOS',
    titulo: 'Datos ocultos',
    texto: 'Con qué se sacó la foto, cuándo y si pasó por un editor.',
  },
  {
    icono: 'firma',
    codigo: 'C2PA',
    titulo: 'Firma de origen',
    texto: 'Si la foto trae la credencial de quien la creó.',
  },
  {
    icono: 'retoque',
    codigo: 'ELA',
    titulo: 'Retoques',
    texto: 'Zonas que se guardaron distinto: posibles agregados.',
  },
  {
    icono: 'red',
    codigo: 'RED NEURONAL',
    titulo: 'Imagen con IA',
    texto: 'Qué tan probable es que la haya creado una IA.',
  },
]

const PASOS = [
  { titulo: 'Creá el caso o el siniestro', texto: 'Con la fecha y el lugar del hecho.' },
  { titulo: 'Subí o pedí las fotos', texto: 'Desde tu compu, tu celular o el de tu cliente o asegurado.' },
  { titulo: 'Descargá el informe', texto: 'Sellado y con un código para verificarlo.' },
]

/** Para quién es: una tarjeta por perfil (decisión de la autora, 037). */
const PERFILES = [
  {
    etiqueta: 'Abogados y estudios',
    titulo: 'Tus casos, con prueba revisada',
    texto: 'Antes de ofrecer una foto como prueba, sabé si conviene presentarla o pedir una pericia. Cuenta personal gratis; tu estudio, con un plan.',
    ruta: '/registro?tipo=independiente',
    accion: 'Crear cuenta de abogado',
  },
  {
    etiqueta: 'Aseguradoras',
    titulo: 'Tus siniestros, verificados antes de liquidar',
    texto: 'Revisá las fotos de cada denuncia y decidí si liquidar o derivar a verificación. Tu equipo entra por invitación.',
    ruta: '/registro?tipo=aseguradora',
    accion: 'Registrar mi aseguradora',
  },
]

const ORGANIZACIONES = [
  { valor: 'estudio', etiqueta: 'Estudio jurídico' },
  { valor: 'aseguradora', etiqueta: 'Aseguradora' },
]

/** Posición de los nodos que laten sobre la grilla del encabezado. */
const NODOS = [
  { left: '8%', top: '22%' },
  { left: '15%', top: '52%' },
  { right: '9%', top: '26%' },
  { right: '17%', top: '56%' },
  { left: '22%', top: '8%' },
  { right: '31%', top: '13%' },
]

function Limites({ plan }) {
  if (!plan) return null
  return (
    <ul className="portada-plan__limites">
      {plan.miembros && <li>Hasta {plan.miembros} miembros</li>}
      <li>{plan.analisis_mes} análisis por mes</li>
      <li>{plan.imagenes_por_caso} imágenes por caso</li>
      {plan.almacenamiento_gb && <li>{plan.almacenamiento_gb} GB para tus casos</li>}
      <li>Informe sellado y verificable</li>
      {plan.miembros && <li>Casos compartidos con permisos</li>}
    </ul>
  )
}

function SeccionPlanes() {
  const { datos } = useDatos(listarPlanes)
  const [tipo, setTipo] = useState('estudio')
  const planes = Object.fromEntries((datos?.planes ?? []).map((plan) => [plan.codigo, plan]))
  const elegido = ORGANIZACIONES.find((opcion) => opcion.valor === tipo)
  const tarjetas = [
    { codigo: 'basico', para: tipo === 'estudio' ? 'Para estudios chicos.' : 'Para equipos chicos.' },
    {
      codigo: 'profesional',
      para: tipo === 'estudio' ? 'Para estudios con equipo.' : 'Para áreas de siniestros.',
      destacado: true,
    },
  ]

  return (
    <section id="planes" className="portada-planes" aria-labelledby="titulo-planes">
      <div className="portada-cab" data-aparecer>
        <span className="portada-etq">Planes</span>
        <h2 id="titulo-planes">Empezá gratis y sumá a tu equipo cuando lo necesites</h2>
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
          <h3 id="plan-personal">Personal</h3>
          <p className="portada-plan__para">Para abogados independientes.</p>
          <p className="portada-plan__precio">Gratis</p>
          <Limites plan={datos?.personal} />
          <Link to="/registro?tipo=independiente" className="portada-pill portada-pill--borde">
            Crear cuenta gratis
          </Link>
        </article>
        {tarjetas.map(({ codigo, para, destacado }, indice) => {
          const plan = planes[codigo]
          const nombre = NOMBRES_DE_PLAN[codigo]
          return (
            <article
              key={codigo}
              className={`portada-plan${destacado ? ' portada-plan--destacado' : ''}`}
              data-aparecer
              style={{ '--orden': indice + 1 }}
              aria-labelledby={`plan-${codigo}`}
            >
              {destacado && <span className="portada-plan__cinta">Más elegido</span>}
              <h3 id={`plan-${codigo}`}>{nombre}</h3>
              <p className="portada-plan__para">
                {elegido.etiqueta} · {para}
              </p>
              <p className="portada-plan__precio">
                {textoDelPrecio(plan?.precio)} <small>por mes</small>
              </p>
              <Limites plan={plan} />
              <Link
                to={`/registro?tipo=${tipo}&plan=${codigo}`}
                className={`portada-pill ${destacado ? 'portada-pill--lima' : 'portada-pill--borde'}`}
              >
                Elegir {nombre}
                <span className="portada-oculto"> para {elegido.etiqueta.toLowerCase()}</span>
              </Link>
            </article>
          )
        })}
      </div>
      <p className="portada-planes__nota">
        Cada botón abre el registro con el plan ya elegido. Pago por transferencia al final del registro;
        podés cambiar de plan cuando quieras.
      </p>
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
      <nav className="portada-nav" aria-label="Portada">
        <Link to="/presentacion" className="portada-nav__logo">
          <img src="/marca/logo-tipografia-blanca.png" alt="evidentIA" />
        </Link>
        <ul>
          <li>
            <a href="#como-funciona">Cómo funciona</a>
          </li>
          <li>
            <a href="#planes">Planes</a>
          </li>
          <li>
            <Link to="/privacidad">Seguridad</Link>
          </li>
        </ul>
        <div className="portada-nav__acciones">
          {usuario ? (
            <Link to="/" className="portada-pill portada-pill--lima portada-pill--chica">
              Ir a mi cuenta
            </Link>
          ) : (
            <>
              <Link to="/iniciar-sesion" className="portada-nav__entrar">
                Iniciar sesión
              </Link>
              <Link to="/registro" className="portada-pill portada-pill--lima portada-pill--chica">
                Crear cuenta
              </Link>
            </>
          )}
        </div>
      </nav>

      <main id="contenido">
        <header className="portada-heroe">
          {NODOS.map((posicion, indice) => (
            <i
              key={indice}
              className="portada-nodo"
              style={{ ...posicion, animationDelay: `${-indice * 0.6}s` }}
              aria-hidden="true"
            />
          ))}
          <span className="portada-etq portada-etq--doble">Para abogados y aseguradoras</span>
          <h1>
            ¿Esa foto es <span className="portada-resalte">real</span>? Sabelo en{' '}
            <span className="portada-recuadro">minutos</span>.
          </h1>
          <p className="portada-heroe__bajada">
            Subí las fotos de un caso o de un siniestro y evidentIA te muestra, capa por capa, si hay señales
            de edición o de imagen hecha con IA. Con un informe claro para presentar o para decidir.
          </p>
          <div className="portada-ctas">
            <Link to="/registro?tipo=independiente" className="portada-pill portada-pill--lima">
              Analizar gratis{' '}
              <span className="portada-pill__flecha" aria-hidden="true">
                →
              </span>
            </Link>
            <a href="#como-funciona" className="portada-pill portada-pill--borde-claro">
              Ver cómo funciona
            </a>
          </div>
          <div className="portada-escena">
            <div className="portada-pantalla">
              <div className="portada-pantalla__barra" aria-hidden="true">
                <i />
                <i />
                <i />
                <span>evidentia · Inicio</span>
              </div>
              <img
                src="/portada/inicio.jpg"
                width="1600"
                height="950"
                alt="Pantalla de inicio de evidentIA con el caso para retomar, los casos por estado y la actividad reciente (datos de ejemplo)"
              />
            </div>
          </div>
        </header>

        <section className="portada-perfiles" aria-labelledby="titulo-perfiles">
          <h2 id="titulo-perfiles" className="solo-lectores">Para quién es</h2>
          <ul className="portada-perfiles__grilla">
            {PERFILES.map((perfil) => (
              <li key={perfil.titulo} className="portada-perfil" data-aparecer>
                <span className="portada-etq">{perfil.etiqueta}</span>
                <h3>{perfil.titulo}</h3>
                <p>{perfil.texto}</p>
                <Link to={perfil.ruta} className="portada-perfil__enlace">
                  {perfil.accion} <span aria-hidden="true">→</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>

        <section id="como-funciona" className="portada-miradas" aria-labelledby="titulo-miradas">
          <div className="portada-cab portada-cab--izquierda" data-aparecer>
            <span className="portada-etq">Qué miramos</span>
            <h2 id="titulo-miradas">Cuatro miradas sobre cada foto</h2>
            <p>Cada una busca algo distinto. Juntas te dicen qué revisar antes de presentar la prueba.</p>
          </div>
          <ul className="portada-miradas__grilla">
            {MIRADAS.map((mirada, indice) => (
              <li key={mirada.codigo} className="portada-mirada" data-aparecer style={{ '--orden': indice }}>
                <span className="portada-mirada__icono">
                  <Trazo nombre={mirada.icono} />
                </span>
                <span className="portada-mirada__texto">
                  <code>{mirada.codigo}</code>
                  <h3>
                    {mirada.titulo}
                    {mirada.proximamente && <span className="portada-mirada__pronto">Próximamente</span>}
                  </h3>
                  <p>{mirada.texto}</p>
                </span>
              </li>
            ))}
          </ul>
        </section>

        <section className="portada-pasos" aria-labelledby="titulo-pasos">
          <div className="portada-pasos__texto" data-aparecer>
            <span className="portada-etq">Cómo funciona</span>
            <h2 id="titulo-pasos">Empezá en tres pasos</h2>
            <ol>
              {PASOS.map((paso, indice) => (
                <li key={paso.titulo}>
                  <i aria-hidden="true">{indice + 1}</i>
                  <span>
                    <b>{paso.titulo}</b>
                    {paso.texto}
                  </span>
                </li>
              ))}
            </ol>
          </div>
          <div className="portada-pasos__captura" data-aparecer>
            <img
              src="/portada/buscador.jpg"
              width="640"
              height="409"
              loading="lazy"
              alt="Buscador de evidentIA: escribiendo parte de una dirección aparecen los casos que coinciden"
            />
          </div>
        </section>

        <SeccionPlanes />

        <section className="portada-cierre" aria-labelledby="titulo-cierre">
          <div>
            <h2 id="titulo-cierre">Tu próxima prueba, revisada antes de presentarla.</h2>
            <p>Empezá gratis. Sin tarjeta.</p>
          </div>
          <Link to="/registro?tipo=independiente" className="portada-pill portada-pill--lima">
            Crear cuenta gratis{' '}
            <span className="portada-pill__flecha" aria-hidden="true">
              →
            </span>
          </Link>
        </section>
      </main>

      <footer className="portada-pie">
        <img src="/marca/logo-tipografia-blanca.png" alt="evidentIA" />
        <p className="portada-pie__descargo">
          La plataforma ofrece indicios técnicos para una evaluación preliminar y no emite veredictos. Ante
          cualquier duda, consultá con un perito especializado.
        </p>
        <nav aria-label="Enlaces del pie">
          <Link to="/terminos">Términos</Link>
          <Link to="/privacidad">Privacidad y seguridad</Link>
          <Link to="/verificar">Verificar un informe</Link>
          <Link to="/estado">Estado del sistema</Link>
        </nav>
      </footer>
    </div>
  )
}
