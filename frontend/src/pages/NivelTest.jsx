import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import BarrasNivel from '../components/BarrasNivel'
import { hablar } from '../voz'

/** Examen adaptativo: el servidor corrige y decide la siguiente pregunta según el historial de respuestas. */
export default function NivelTest() {
  const navegar = useNavigate()
  const [historial, setHistorial] = useState([])
  const [paso, setPaso] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(null)

  const pedir = useCallback(
    async (respuestas) => {
      setCargando(true)
      setError(null)
      try {
        const datos = await api.post('/api/nivel/examen/', { historial: respuestas })
        if (datos.terminado) navegar('/nivel/resultado')
        else {
          setPaso(datos)
          setCargando(false)
        }
      } catch (e) {
        setError(e.message)
        setCargando(false)
      }
    },
    [navegar],
  )

  useEffect(() => {
    pedir([])
  }, [pedir])

  function responder(elegidaId) {
    const todas = [...historial, { palabra_id: paso.pregunta.id, elegida_id: elegidaId }]
    setHistorial(todas)
    pedir(todas)
  }

  if (error) {
    return (
      <>
        <h1>Examen de nivel</h1>
        <div className="card">
          <p className="error">No se pudo continuar el examen: {error}</p>
          <button className="btn" type="button" onClick={() => pedir(historial)}>
            Reintentar
          </button>
        </div>
      </>
    )
  }
  if (!paso) return <p className="muted">Cargando…</p>

  const { pregunta, progreso } = paso
  return (
    <>
      <h1>Examen de nivel</h1>
      <p className="muted">Pregunta {progreso.respondidas + 1}. Cada nivel es más difícil que el anterior.</p>
      <BarrasNivel
        avance={progreso.avance}
        textoAvance={`${progreso.avance}% del examen`}
        niveles={progreso.niveles}
        nivel={progreso.nivel}
        aprobados={progreso.aprobados}
        racha={progreso.aciertos_nivel}
        rachaMeta={progreso.necesarios}
        textoRacha={`${progreso.aciertos_nivel} de ${progreso.necesarios} aciertos · ${progreso.fallos_nivel} de ${progreso.max_fallos} fallos`}
      />
      <div className="card">
        <p className="muted">¿Qué significa?</p>
        <div className="grande">{pregunta.ingles}</div>
        <button className="btn sec" type="button" onClick={() => hablar(pregunta.ingles)}>
          Escuchar
        </button>
        <div style={{ display: 'grid', gap: 8, marginTop: 16 }}>
          {pregunta.opciones.map((o) => (
            <button key={o.id} className="btn sec" type="button" disabled={cargando} onClick={() => responder(o.id)}>
              {o.espanol}
            </button>
          ))}
        </div>
        <div className="fila">
          <button className="btn sec" type="button" disabled={cargando} onClick={() => responder(null)}>
            No la sé
          </button>
        </div>
      </div>
    </>
  )
}
