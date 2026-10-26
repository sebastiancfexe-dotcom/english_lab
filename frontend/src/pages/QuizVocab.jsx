import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { Vacio } from '../components/Estado'
import { hablar } from '../voz'

export default function QuizVocab() {
  const [params] = useSearchParams()
  const modo = params.get('modo') === 'dictado' ? 'dictado' : 'traducir'
  const categoria = params.get('categoria') ?? ''

  const [ronda, setRonda] = useState(0)
  const [pregunta, setPregunta] = useState(null) // null = cargando
  const [respuesta, setRespuesta] = useState('')
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let vigente = true
    setPregunta(null)
    setResultado(null)
    setRespuesta('')
    setError(null)
    const consulta = new URLSearchParams({ modo })
    if (categoria) consulta.set('categoria', categoria)
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
  }, [modo, categoria, ronda])

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
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>{modo === 'dictado' ? 'Dictado' : 'Quiz de vocabulario'}</h1>
      {error && <p className="error">{error}</p>}
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
              <button className="btn" type="button" autoFocus onClick={() => setRonda(ronda + 1)}>
                Siguiente
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
