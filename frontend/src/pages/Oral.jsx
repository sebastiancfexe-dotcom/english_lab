import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { Vacio } from '../components/Estado'
import Grabadora from '../components/Grabadora'
import { callar, hablar } from '../voz'

const CLAVE_DIA = 'english-lab-oral-dia'

const hoy = () => new Date().toLocaleDateString('en-CA') // AAAA-MM-DD en la zona del navegador

function leerDia() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_DIA)) ?? {}
  } catch {
    return {}
  }
}

function guardarDia(pregunta, tema) {
  try {
    localStorage.setItem(CLAVE_DIA, JSON.stringify({ fecha: hoy(), id: pregunta.id, tema }))
  } catch {
    // sin almacenamiento: la pregunta cambiará al recargar
  }
}

export default function Oral() {
  const [params] = useSearchParams()
  const tema = params.get('tema') ?? ''
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState(null)
  const [pidiendoOtra, setPidiendoOtra] = useState(false)

  // La pregunta del día se mantiene durante todo el día; «Otra pregunta» la reemplaza.
  useEffect(() => {
    let vigente = true
    setDatos(null)
    setError(null)
    const guardada = leerDia()
    const reutilizar = guardada.fecha === hoy() && guardada.tema === tema && guardada.id
    const ruta = reutilizar ? `/api/oral/${guardada.id}/` : `/api/oral/?tema=${encodeURIComponent(tema)}`
    api
      .get(ruta)
      .catch(() => api.get(`/api/oral/?tema=${encodeURIComponent(tema)}`)) // la guardada ya no existe
      .then((d) => {
        if (!vigente) return
        if (d.pregunta) guardarDia(d.pregunta, tema)
        setDatos(d)
      })
      .catch((e) => vigente && setError(e.message))
    return () => {
      vigente = false
      callar()
    }
  }, [tema])

  async function otra() {
    setPidiendoOtra(true)
    try {
      const d = await api.get(`/api/oral/?tema=${encodeURIComponent(tema)}&excluir=${datos.pregunta.id}`)
      if (d.pregunta) guardarDia(d.pregunta, tema)
      setDatos(d)
    } catch (e) {
      setError(e.message)
    } finally {
      setPidiendoOtra(false)
    }
  }

  const p = datos?.pregunta

  return (
    <>
      <h1>Práctica oral</h1>
      <div className="fila" style={{ margin: '0 0 16px' }}>
        <Link className={`btn ${tema ? 'sec' : ''}`} to="?">
          Todas
        </Link>
        {datos?.temas.map((t) => (
          <Link key={t.clave} className={`btn ${t.clave === tema ? '' : 'sec'}`} to={`?tema=${t.clave}`}>
            {t.nombre}
          </Link>
        ))}
        <Link className="btn sec" to="/oral/historial">
          Mi historial
        </Link>
      </div>

      {error && <p className="error">{error}</p>}
      {datos && !p && <Vacio />}
      {p && (
        <>
          <div className="card">
            <p className="muted">
              Pregunta del día · {p.tema_display}
              {datos.hoy_hecho && (
                <>
                  {' '}
                  · <b>ya la practicaste hoy</b>
                </>
              )}
            </p>
            <div className="grande">{p.texto}</div>
            {p.traduccion && <p className="muted">{p.traduccion}</p>}
            <div className="fila">
              <button className="btn sec" type="button" onClick={() => hablar(p.texto)}>
                Escuchar la pregunta
              </button>
              <button className="btn sec" type="button" onClick={otra} disabled={pidiendoOtra}>
                Otra pregunta
              </button>
            </div>
          </div>

          <div className="card">
            <h2>Cómo armarla</h2>
            <p>{p.estructura}</p>
            {p.frases_utiles.length > 0 && (
              <>
                <p className="muted">Frases que te pueden servir:</p>
                <ul>
                  {p.frases_utiles.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
              </>
            )}
            <details>
              <summary>
                <b>Ver respuesta modelo</b> <span className="muted">(intenta primero sin mirarla)</span>
              </summary>
              <p>{p.modelo}</p>
              <button className="btn sec" type="button" onClick={() => hablar(p.modelo)}>
                Escuchar el modelo
              </button>
            </details>
          </div>

          <Grabadora key={p.id} preguntaId={p.id} />

          {datos.resumen_oral.total > 0 && (
            <p className="muted">
              Llevas {datos.resumen_oral.total} práctica{datos.resumen_oral.total === 1 ? '' : 's'} oral
              {datos.resumen_oral.total === 1 ? '' : 'es'} en {datos.resumen_oral.dias} día
              {datos.resumen_oral.dias === 1 ? '' : 's'}.
            </p>
          )}
        </>
      )}
    </>
  )
}
