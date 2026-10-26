import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { Vacio } from '../components/Estado'
import { hablar } from '../voz'

export default function DictadoFrases() {
  const [params] = useSearchParams()
  const tema = params.get('tema') ?? ''

  const [ronda, setRonda] = useState(0)
  const [datos, setDatos] = useState(null)
  const [respuesta, setRespuesta] = useState('')
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let vigente = true
    setResultado(null)
    setRespuesta('')
    setError(null)
    api
      .get(`/api/dictado/frases/${tema ? `?tema=${encodeURIComponent(tema)}` : ''}`)
      .then((d) => {
        if (!vigente) return
        setDatos(d)
        if (d.frase) hablar(d.frase.texto)
      })
      .catch((e) => vigente && setError(e.message))
    return () => {
      vigente = false
    }
  }, [tema, ronda])

  async function comprobar(e) {
    e.preventDefault()
    try {
      setResultado(await api.post('/api/dictado/frases/', { frase_id: datos.frase.id, respuesta }))
    } catch (err) {
      setError(err.message)
    }
  }

  const texto = resultado?.frase.texto ?? datos?.frase?.texto

  return (
    <>
      <h1>Dictado de frases</h1>
      <div className="fila" style={{ margin: '0 0 16px' }}>
        <Link className={`btn ${tema ? 'sec' : ''}`} to="?">
          Todas
        </Link>
        {datos?.temas.map((t) => (
          <Link key={t.clave} className={`btn ${t.clave === tema ? '' : 'sec'}`} to={`?tema=${t.clave}`}>
            {t.nombre}
          </Link>
        ))}
      </div>

      {error && <p className="error">{error}</p>}
      {datos && !datos.frase && <Vacio />}
      {datos?.frase && (
        <div className="card">
          {resultado ? (
            <>
              <div className={`res ${resultado.correcto ? 'ok' : 'bad'}`}>
                <b>{resultado.puntaje}%</b> · {resultado.correcto ? '¡Muy bien!' : 'Casi. Repasa las palabras en rojo.'}
              </div>
              <p className="muted">Frase correcta (en rojo, lo que no coincidió):</p>
              <p className="grande" style={{ fontSize: 22 }}>
                {resultado.palabras.map((p, i) => (
                  <span key={i} className={`pal ${p.estado}`}>
                    {p.texto}{' '}
                  </span>
                ))}
              </p>
              <p>
                <span className="muted">Tú escribiste:</span> {respuesta}
              </p>
              <p>
                <span className="muted">Original:</span> {resultado.frase.texto}
              </p>
              {resultado.frase.traduccion && <p className="muted">{resultado.frase.traduccion}</p>}
              <div className="fila">
                <button className="btn sec" type="button" onClick={() => hablar(texto)}>
                  Escuchar
                </button>
                <button className="btn sec" type="button" onClick={() => hablar(texto, 0.6)}>
                  Escuchar lento
                </button>
                <button className="btn" type="button" autoFocus onClick={() => setRonda(ronda + 1)}>
                  Siguiente
                </button>
              </div>
            </>
          ) : (
            <>
              <p className="muted">Escucha la frase y escríbela completa. No importan las mayúsculas ni los signos.</p>
              <div className="fila">
                <button className="btn" type="button" onClick={() => hablar(texto)}>
                  Escuchar
                </button>
                <button className="btn sec" type="button" onClick={() => hablar(texto, 0.6)}>
                  Escuchar lento
                </button>
              </div>
              <form autoComplete="off" onSubmit={comprobar}>
                <textarea rows={3} value={respuesta} onChange={(e) => setRespuesta(e.target.value)} autoFocus required />
                <div className="fila">
                  <button className="btn" type="submit">
                    Comprobar
                  </button>
                </div>
              </form>
            </>
          )}
        </div>
      )}
    </>
  )
}
