import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api'
import Estado, { Vacio } from '../components/Estado'
import { useCarga } from '../useCarga'
import { hablar } from '../voz'

export default function Tarjetas() {
  const [params] = useSearchParams()
  const categoria = params.get('categoria')
  const carga = useCarga(`/api/tarjetas/${categoria ? `?categoria=${encodeURIComponent(categoria)}` : ''}`)

  return (
    <>
      <h1>Tarjetas</h1>
      <Estado carga={carga}>
        {({ palabras }) =>
          palabras.length ? <Sesion palabras={palabras} repetir={carga.recargar} /> : <Vacio />
        }
      </Estado>
    </>
  )
}

function Sesion({ palabras, repetir }) {
  const [i, setI] = useState(0)
  const [volteada, setVolteada] = useState(false)
  const [aciertos, setAciertos] = useState(0)
  const terminado = i >= palabras.length
  const p = palabras[i]

  if (terminado) {
    return (
      <div className="card">
        <h2>¡Terminaste!</h2>
        <p>
          Sabías <b>{aciertos}</b> de {palabras.length}.
        </p>
        <button
          className="btn"
          type="button"
          onClick={() => {
            setI(0)
            setAciertos(0)
            repetir()
          }}
        >
          Repetir
        </button>
      </div>
    )
  }

  function voltear() {
    if (!volteada) hablar(p.ingles)
    setVolteada(!volteada)
  }

  function responder(correcto) {
    if (correcto) setAciertos((n) => n + 1)
    api.post('/api/tarjetas/registrar/', { palabra_id: p.id, correcto }).catch(() => {})
    setVolteada(false)
    setI(i + 1)
  }

  return (
    <>
      <p className="muted">
        {i + 1} de {palabras.length} · toca la tarjeta para voltearla
      </p>
      <div className="card tarjeta" onClick={voltear}>
        <div className="grande">{volteada ? p.espanol : p.ingles}</div>
        {volteada && (
          <>
            <div className="muted">{p.ingles}</div>
            <div className="muted">{p.ejemplo}</div>
          </>
        )}
      </div>
      <div className="fila">
        <button className="btn sec" type="button" onClick={() => hablar(p.ingles)}>
          Escuchar
        </button>
        <button className="btn bad" type="button" onClick={() => responder(false)}>
          No la sabía
        </button>
        <button className="btn ok" type="button" onClick={() => responder(true)}>
          La sabía
        </button>
      </div>
    </>
  )
}
