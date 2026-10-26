import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import Estado, { Barra, Vacio } from '../components/Estado'
import { useCarga } from '../useCarga'
import { hablar } from '../voz'

export default function NivelTest() {
  const carga = useCarga('/api/nivel/test/')

  return (
    <>
      <h1>Test de nivel</h1>
      <Estado carga={carga}>
        {({ preguntas }) => (preguntas.length ? <Preguntas preguntas={preguntas} /> : <Vacio />)}
      </Estado>
    </>
  )
}

function Preguntas({ preguntas }) {
  const navegar = useNavigate()
  const [i, setI] = useState(0)
  const [respuestas, setRespuestas] = useState([])
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  async function enviar(todas) {
    setEnviando(true)
    setError(null)
    try {
      await api.post('/api/nivel/test/', { respuestas: todas })
      navegar('/nivel/resultado')
    } catch (e) {
      setError(e.message)
      setEnviando(false)
    }
  }

  function responder(elegidaId) {
    const todas = [...respuestas, { palabra_id: preguntas[i].id, elegida_id: elegidaId }]
    setRespuestas(todas)
    if (i + 1 < preguntas.length) setI(i + 1)
    else enviar(todas)
  }

  if (enviando) return <div className="card">Calculando tu nivel…</div>
  if (error) {
    return (
      <div className="card">
        <p className="error">No se pudo guardar el resultado: {error}</p>
        <button className="btn" type="button" onClick={() => enviar(respuestas)}>
          Reintentar
        </button>
      </div>
    )
  }

  const q = preguntas[i]
  return (
    <>
      <p className="muted">
        Pregunta {i + 1} de {preguntas.length}
      </p>
      <div style={{ marginBottom: 16 }}>
        <Barra valor={(100 * i) / preguntas.length} />
      </div>
      <div className="card">
        <p className="muted">¿Qué significa?</p>
        <div className="grande">{q.ingles}</div>
        <button className="btn sec" type="button" onClick={() => hablar(q.ingles)}>
          Escuchar
        </button>
        <div style={{ display: 'grid', gap: 8, marginTop: 16 }}>
          {q.opciones.map((o) => (
            <button key={o.id} className="btn sec" type="button" onClick={() => responder(o.id)}>
              {o.espanol}
            </button>
          ))}
        </div>
        <div className="fila">
          <button className="btn sec" type="button" onClick={() => responder(null)}>
            No la sé
          </button>
        </div>
      </div>
    </>
  )
}
