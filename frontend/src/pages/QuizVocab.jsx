import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import BarrasNivel from '../components/BarrasNivel'
import Estado, { Vacio } from '../components/Estado'
import { useCarga } from '../useCarga'
import { hablar } from '../voz'

export default function QuizVocab() {
  const [params] = useSearchParams()
  const modo = params.get('modo') === 'dictado' ? 'dictado' : 'traducir'
  const categoria = params.get('categoria') ?? ''
  const titulo = modo === 'dictado' ? 'Dictado' : 'Quiz de vocabulario'

  // Sin categoría el quiz es una ronda con dificultad creciente; con categoría es práctica libre.
  const carga = useCarga('/api/nivel/')
  if (categoria) return <Quiz titulo={titulo} modo={modo} categoria={categoria} />
  return (
    <Estado carga={carga}>
      {({ perfil, niveles, quiz }) => (
        <Quiz
          titulo={titulo}
          modo={modo}
          niveles={niveles}
          config={quiz}
          nivelInicial={Math.min(Math.max(perfil.nivel_inicial, 1), niveles.length)}
        />
      )}
    </Estado>
  )
}

const SESION_NUEVA = (nivel) => ({
  nivel, racha: 0, fallosSeguidos: 0, respondidas: 0, aciertos: 0, nivelMaximo: nivel, fallidas: [],
})

function Quiz({ titulo, modo, categoria = '', niveles, config, nivelInicial = 1 }) {
  const progresivo = !categoria
  const [ronda, setRonda] = useState(0)
  const [sesion, setSesion] = useState(() => SESION_NUEVA(nivelInicial))
  const [pregunta, setPregunta] = useState(null) // null = cargando
  const [respuesta, setRespuesta] = useState('')
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState(null)
  const [fin, setFin] = useState(false)
  const ultima = progresivo && sesion.respondidas >= config.preguntas

  // El nivel de la pregunta se lee al cambiar `ronda` (al pulsar «Siguiente»), no en cuanto cambia la sesión,
  // para que la corrección siga a la vista mientras el nivel nuevo ya se ve en las barras.
  useEffect(() => {
    if (fin) return undefined
    let vigente = true
    setPregunta(null)
    setResultado(null)
    setRespuesta('')
    setError(null)
    const consulta = new URLSearchParams({ modo })
    if (categoria) consulta.set('categoria', categoria)
    if (progresivo) consulta.set('nivel', sesion.nivel)
    api
      .get(`/api/quiz/vocabulario/?${consulta}`)
      .then((datos) => {
        if (!vigente) return
        setPregunta(datos)
        if (modo === 'dictado' && datos.palabra) hablar(datos.palabra.ingles)
      })
      .catch((e) => vigente && setError(e.message))
    return () => {
      vigente = false
    }
    // oxlint-disable-next-line react-hooks/exhaustive-deps
  }, [modo, categoria, ronda, fin])

  async function comprobar(e) {
    e.preventDefault()
    try {
      const datos = await api.post('/api/quiz/vocabulario/', {
        palabra_id: pregunta.palabra.id,
        modo,
        respuesta,
      })
      setResultado(datos)
      hablar(datos.palabra.ingles)
      if (progresivo) setSesion((s) => registrar(s, datos, respuesta, config, niveles.length))
    } catch (err) {
      setError(err.message)
    }
  }

  function siguiente() {
    if (ultima) setFin(true)
    else setRonda(ronda + 1)
  }

  function reiniciar() {
    setSesion(SESION_NUEVA(nivelInicial))
    setFin(false)
    setRonda(ronda + 1)
  }

  if (fin) return <Resumen sesion={sesion} config={config} niveles={niveles} onOtra={reiniciar} />

  return (
    <>
      {titulo && <h1>{titulo}</h1>}
      {error && <p className="error">{error}</p>}
      {progresivo && <Barras sesion={sesion} config={config} niveles={niveles} />}
      {pregunta?.vacio && <Vacio />}
      {pregunta?.palabra && (
        <div className="card">
          {modo === 'dictado' ? (
            <>
              <p className="muted">Escucha y escribe la palabra en inglés.</p>
              <button className="btn sec" type="button" onClick={() => hablar(pregunta.palabra.ingles)}>
                Escuchar
              </button>
            </>
          ) : (
            <>
              <p className="muted">¿Cómo se dice en inglés?</p>
              <div className="grande">{pregunta.palabra.espanol}</div>
            </>
          )}

          {resultado ? (
            <>
              <div className={`res ${resultado.correcto ? 'ok' : 'bad'}`}>
                {resultado.correcto ? '¡Correcto!' : `Incorrecto. Escribiste «${respuesta}».`}
                <br />
                <b>{resultado.palabra.ingles}</b> = {resultado.palabra.espanol}
                {resultado.palabra.ejemplo && (
                  <>
                    <br />
                    <i>{resultado.palabra.ejemplo}</i>
                  </>
                )}
              </div>
              {progresivo && <Aviso sesion={sesion} niveles={niveles} />}
              <button className="btn" type="button" autoFocus onClick={siguiente}>
                {ultima ? 'Ver resultado' : 'Siguiente'}
              </button>
            </>
          ) : (
            <form className="fila" autoComplete="off" onSubmit={comprobar}>
              <input type="text" value={respuesta} onChange={(e) => setRespuesta(e.target.value)} autoFocus required />
              <button className="btn" type="submit">
                Comprobar
              </button>
            </form>
          )}
        </div>
      )}
    </>
  )
}

/**
 * Anota una respuesta: con `racha_sube` aciertos seguidos se sube de nivel y con `racha_baja` fallos seguidos se baja.
 * `cambio` dice qué pasó para poder avisarlo; el nivel nuevo se aplica a la pregunta siguiente.
 */
function registrar(s, datos, respuesta, config, maximo) {
  const correcto = datos.correcto
  let { nivel, racha, fallosSeguidos } = s
  let cambio = null
  if (correcto) {
    racha += 1
    fallosSeguidos = 0
    if (racha >= config.racha_sube) {
      racha = 0
      if (nivel < maximo) {
        nivel += 1
        cambio = 'sube'
      } else cambio = 'tope'
    }
  } else {
    racha = 0
    fallosSeguidos += 1
    if (fallosSeguidos >= config.racha_baja) {
      fallosSeguidos = 0
      if (nivel > 1) {
        nivel -= 1
        cambio = 'baja'
      }
    }
  }
  return {
    nivel, racha, fallosSeguidos, cambio,
    respondidas: s.respondidas + 1,
    aciertos: s.aciertos + (correcto ? 1 : 0),
    nivelMaximo: Math.max(s.nivelMaximo, nivel),
    fallidas: correcto
      ? s.fallidas
      : [...s.fallidas, { ingles: datos.palabra.ingles, espanol: datos.palabra.espanol, respuesta }],
  }
}

function Barras({ sesion, config, niveles }) {
  // Tras responder, `racha` ya refleja la respuesta; al subir de nivel vuelve a 0 y el aviso explica por qué.
  return (
    <BarrasNivel
      avance={Math.round((100 * sesion.respondidas) / config.preguntas)}
      textoAvance={`${sesion.respondidas} de ${config.preguntas} preguntas`}
      niveles={niveles}
      nivel={sesion.nivel}
      aprobados={sesion.nivel - 1}
      racha={sesion.racha}
      rachaMeta={config.racha_sube}
      textoRacha={`${sesion.racha} de ${config.racha_sube} aciertos seguidos para subir`}
    />
  )
}

function Aviso({ sesion, niveles }) {
  const nombre = niveles.find((n) => n.numero === sesion.nivel)?.nombre
  if (sesion.cambio === 'sube') {
    return <p>⬆ ¡Subes al nivel {sesion.nivel} ({nombre})!</p>
  }
  if (sesion.cambio === 'baja') {
    return <p className="muted">⬇ Bajas al nivel {sesion.nivel} ({nombre}) para reforzar.</p>
  }
  if (sesion.cambio === 'tope') {
    return <p>¡Estás en el nivel más alto y sigues acertando!</p>
  }
  return null
}

function Resumen({ sesion, config, niveles, onOtra }) {
  const final = niveles.find((n) => n.numero === sesion.nivelMaximo)
  return (
    <>
      <h1>Ronda terminada</h1>
      <div className="card grid">
        <div className="stat">
          <b>
            {sesion.aciertos}/{config.preguntas}
          </b>
          <span>aciertos</span>
        </div>
        <div className="stat">
          <b>{sesion.nivelMaximo}</b>
          <span>
            nivel más alto: {final?.nombre} ({final?.cefr})
          </span>
        </div>
      </div>
      <div className="card">
        <h2>Palabras que fallaste</h2>
        {sesion.fallidas.length ? (
          <table>
            <thead>
              <tr>
                <th>Inglés</th>
                <th>Significa</th>
                <th>Tu respuesta</th>
              </tr>
            </thead>
            <tbody>
              {sesion.fallidas.map((f, i) => (
                <tr key={i}>
                  <td>
                    <b>{f.ingles}</b>
                  </td>
                  <td>{f.espanol}</td>
                  <td className="muted">
                    <s>{f.respuesta}</s>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>¡No fallaste ninguna palabra!</p>
        )}
      </div>
      <div className="fila">
        <button className="btn" type="button" onClick={onOtra}>
          Otra ronda
        </button>
        <Link className="btn sec" to="/nivel">
          Hacer el examen de nivel
        </Link>
      </div>
    </>
  )
}
