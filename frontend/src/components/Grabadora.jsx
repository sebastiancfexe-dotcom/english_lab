import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { callar } from '../voz'

const formato = (s) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

/** Cronómetro y grabación local. El audio nunca sale del navegador; solo se envían la duración y la calificación. */
export default function Grabadora({ preguntaId }) {
  const navegar = useNavigate()
  const [fase, setFase] = useState('inicial') // inicial | grabando | terminado
  const [segundos, setSegundos] = useState(0)
  const [duracion, setDuracion] = useState(0)
  const [audioUrl, setAudioUrl] = useState(null)
  const [aviso, setAviso] = useState(null)
  const [nota, setNota] = useState('')
  const [notas, setNotas] = useState('')
  const [error, setError] = useState(null)
  const [guardando, setGuardando] = useState(false)

  const grabador = useRef(null)
  const flujo = useRef(null)
  const inicio = useRef(0)
  const intervalo = useRef(null)

  // Al salir de la pantalla se libera el micrófono y el cronómetro.
  useEffect(
    () => () => {
      clearInterval(intervalo.current)
      flujo.current?.getTracks().forEach((t) => t.stop())
    },
    [],
  )
  useEffect(() => () => audioUrl && URL.revokeObjectURL(audioUrl), [audioUrl])

  async function empezar() {
    callar()
    setAudioUrl(null)
    setAviso(null)
    setSegundos(0)
    setFase('grabando')
    const trozos = []
    try {
      flujo.current = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(flujo.current)
      mr.ondataavailable = (e) => trozos.push(e.data)
      mr.onstop = () => {
        flujo.current?.getTracks().forEach((t) => t.stop())
        setAudioUrl(URL.createObjectURL(new Blob(trozos, { type: mr.mimeType })))
      }
      mr.start()
      grabador.current = mr
    } catch {
      grabador.current = null
      setAviso('No pude usar el micrófono, así que usa solo el cronómetro: habla en voz alta y pulsa «Terminar».')
    }
    inicio.current = Date.now()
    intervalo.current = setInterval(() => setSegundos(Math.floor((Date.now() - inicio.current) / 1000)), 250)
  }

  function terminar() {
    clearInterval(intervalo.current)
    if (grabador.current && grabador.current.state !== 'inactive') grabador.current.stop()
    setDuracion(Math.round((Date.now() - inicio.current) / 1000))
    setFase('terminado')
  }

  async function guardar(e) {
    e.preventDefault()
    setGuardando(true)
    setError(null)
    try {
      await api.post('/api/oral/registrar/', {
        pregunta_id: preguntaId,
        duracion,
        autoevaluacion: Number(nota),
        notas,
      })
      navegar('/oral/historial')
    } catch (err) {
      setError(err.message)
      setGuardando(false)
    }
  }

  return (
    <div className="card">
      <h2>Responde en voz alta</h2>
      <p className="muted">
        Habla 1 o 2 minutos. La grabación no se sube ni se guarda: queda solo en tu navegador para que te escuches.{' '}
        <b>La app no evalúa tu pronunciación</b>; tú la calificas al final.
      </p>
      <div className="grande">{formato(fase === 'terminado' ? duracion : segundos)}</div>
      <div className="fila">
        {fase === 'grabando' ? (
          <button className="btn bad" type="button" onClick={terminar}>
            Terminar
          </button>
        ) : (
          <button className="btn" type="button" onClick={empezar}>
            {fase === 'terminado' ? 'Grabar de nuevo' : 'Empezar'}
          </button>
        )}
      </div>
      {aviso && <p className="muted">{aviso}</p>}
      {audioUrl && fase === 'terminado' && <audio src={audioUrl} controls style={{ width: '100%', marginTop: 12 }} />}

      {fase === 'terminado' && (
        <form onSubmit={guardar}>
          {error && <p className="error">{error}</p>}
          <p>
            <label>
              ¿Qué tan fluido te sentiste?
              <select value={nota} onChange={(e) => setNota(e.target.value)} required>
                <option value="">Elige…</option>
                <option value="1">1 · Muy difícil, me quedé en blanco</option>
                <option value="2">2 · Difícil, muchas pausas</option>
                <option value="3">3 · Regular, me entendería con esfuerzo</option>
                <option value="4">4 · Bien, con pocas pausas</option>
                <option value="5">5 · Muy fluido</option>
              </select>
            </label>
          </p>
          <p>
            <label>
              ¿Qué mejorarías? (opcional)
              <input
                type="text"
                value={notas}
                onChange={(e) => setNotas(e.target.value)}
                maxLength={300}
                placeholder="Ej.: me faltó vocabulario para describir el reto"
              />
            </label>
          </p>
          <button className="btn" type="submit" disabled={guardando}>
            Guardar en mi registro
          </button>
        </form>
      )}
    </div>
  )
}
