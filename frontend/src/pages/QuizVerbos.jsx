import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { useCarga } from '../useCarga'
import { Vacio } from '../components/Estado'

export default function QuizVerbos() {
  const [params] = useSearchParams()
  const tiempo = params.get('tiempo') ?? 'pasado'
  const { datos: inicio } = useCarga('/api/inicio/')

  const [ronda, setRonda] = useState(0)
  const [ejercicio, setEjercicio] = useState(null)
  const [respuesta, setRespuesta] = useState('')
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let vigente = true
    setEjercicio(null)
    setResultado(null)
    setRespuesta('')
    setError(null)
    api
      .get(`/api/quiz/verbos/?tiempo=${encodeURIComponent(tiempo)}`)
      .then((datos) => vigente && setEjercicio(datos))
      .catch((e) => vigente && setError(e.message))
    return () => {
      vigente = false
    }
  }, [tiempo, ronda])

  async function comprobar(e) {
    e.preventDefault()
    try {
      setResultado(await api.post('/api/quiz/verbos/', { ticket: ejercicio.ticket, respuesta }))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <h1>Verbos</h1>
      <div className="fila" style={{ margin: '0 0 16px' }}>
        {inicio?.tiempos.map((t) => (
          <Link key={t.clave} className={`btn ${t.clave === tiempo ? '' : 'sec'}`} to={`?tiempo=${t.clave}`}>
            {t.nombre}
          </Link>
        ))}
      </div>

      {error && <p className="error">{error}</p>}
      {ejercicio?.vacio && <Vacio />}
      {ejercicio?.ticket && (
        <div className="card">
          <p className="muted">
            Completa la oración ({ejercicio.pista}). Verbo: <b>{ejercicio.verbo.infinitivo}</b> ={' '}
            {ejercicio.verbo.espanol}
          </p>
          <div className="grande">{ejercicio.enunciado}</div>

          {resultado ? (
            <>
              <div className={`res ${resultado.correcto ? 'ok' : 'bad'}`}>
                {resultado.correcto ? '¡Correcto!' : `Incorrecto. Escribiste «${respuesta}».`}
                <br />
                Respuesta: <b>{resultado.correcta}</b>
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
