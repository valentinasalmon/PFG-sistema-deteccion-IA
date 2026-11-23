/**
 * Guía pública «Verificar sin evidentIA» (funcionalidad 048).
 *
 * La huella de cada informe y de cada imagen se publica en Hedera, una red
 * pública que no depende de evidentIA. Esta guía explica cómo comprobarlo con
 * herramientas propias: calcular la huella SHA-256 del PDF en la computadora y
 * buscarla entre los mensajes del tema en HashScan, el explorador público de
 * Hedera. Así un juzgado o un perito no necesita confiar en la plataforma.
 *
 * Realiza: CA2 de la funcionalidad 048; RF37, RF55.
 */
import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { obtenerRedPublica } from '../api/informes.js'

const COMANDOS = [
  { sistema: 'Windows', comando: 'certutil -hashfile informe.pdf SHA256', donde: 'en «Símbolo del sistema» o PowerShell' },
  { sistema: 'Mac', comando: 'shasum -a 256 informe.pdf', donde: 'en la app Terminal' },
  { sistema: 'Linux', comando: 'sha256sum informe.pdf', donde: 'en una terminal' },
]

export default function PaginaVerificarSinEvidentia() {
  const [red, setRed] = useState(undefined)

  useEffect(() => {
    obtenerRedPublica()
      .then(setRed)
      .catch(() => setRed(null))
  }, [])

  return (
    <div className="sin-evidentia">
      <h1>Verificar sin evidentIA</h1>
      <p className="subtitulo sin-evidentia__intro">
        No hace falta confiar en la plataforma: la huella de cada informe y de cada imagen está publicada en Hedera, una
        red pública que nadie puede modificar, ni siquiera evidentIA. Podés comprobarlo con tu computadora y un
        explorador público.
      </p>

      <ol className="sin-evidentia__pasos">
        <li>
          <h2>Calculá la huella del PDF</h2>
          <p>
            La huella SHA-256 es como una «huella digital» del archivo: si cambia aunque sea un carácter, la huella es
            otra. Guardá el informe como <code>informe.pdf</code> y, en la misma carpeta, ejecutá:
          </p>
          <ul className="sin-evidentia__comandos">
            {COMANDOS.map(({ sistema, comando, donde }) => (
              <li key={sistema}>
                <strong>{sistema}</strong> <small className="nota">({donde})</small>
                <code>{comando}</code>
              </li>
            ))}
          </ul>
          <p className="nota">El resultado son 64 letras y números. También sirve cualquier calculadora SHA-256.</p>
        </li>
        <li>
          <h2>Abrí el registro público en HashScan</h2>
          {red ? (
            <p>
              Las huellas se publican en la red <strong>{red.red}</strong> de Hedera, en el tema{' '}
              <strong>{red.tema}</strong>.{' '}
              <a href={red.enlace_tema} target="_blank" rel="noopener noreferrer">
                Abrir el tema en HashScan
              </a>
              .
            </p>
          ) : (
            <p>
              Abrí <strong>hashscan.io</strong>, el explorador público de Hedera, y buscá el tema que figura en el
              recuadro «Verificar sin evidentIA» del informe.
            </p>
          )}
        </li>
        <li>
          <h2>Buscá el mensaje con esa huella</h2>
          <p>
            Cada mensaje del tema tiene la forma <code>{'{"v":1,"tipo":"informe","sha256":"…"}'}</code>. Entre los
            mensajes de la fecha del informe, buscá el que tenga en <code>sha256</code> la misma huella que calculaste.
            Si está, el PDF es idéntico al que se registró en esa fecha. Las imágenes se comprueban igual, con su
            propia huella (tipo <code>imagen</code>).
          </p>
        </li>
      </ol>

      <p className="nota sin-evidentia__aviso">
        La plataforma usa la red de prueba de Hedera (testnet). Esa red se reinicia cada tanto: si no encontrás un
        mensaje antiguo, puede ser por un reinicio, no por una alteración. La plataforma conserva el recibo de cada
        sello.
      </p>
      <p>
        <Link to="/verificar">Volver a verificar un informe</Link>
      </p>
    </div>
  )
}
