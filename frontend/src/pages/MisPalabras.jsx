import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api, mensajes } from '../api'
import Estado, { Barra } from '../components/Estado'
import { useCarga } from '../useCarga'

const VACIA = { ingles: '', espanol: '', ejemplo: '' }

export default function MisPalabras() {
  const carga = useCarga('/api/mis-palabras/')

  return (
    <>
      <h1>Mis palabras</h1>
      <Estado carga={carga}>
        {({ estado, puede_agregar: puedeAgregar, palabras }) => (
          <>
            {puedeAgregar ? (
              <Formulario alAgregar={carga.recargar} />
            ) : (
              <div className="card">
                <h2>Todavía bloqueado</h2>
                <p>
                  Esta función se desbloquea cuando domines unas <b>{estado.desbloquea_en}</b> palabras. Llevas{' '}
                  <b>{estado.total}</b>.
                </p>
                <Barra valor={estado.porcentaje_meta} />
                <div className="fila">
                  <Link className="btn" to="/tarjetas">
                    Practicar
                  </Link>
                  <Link className="btn sec" to="/nivel">
                    Hacer el test de nivel
                  </Link>
                </div>
              </div>
            )}

            <div className="card">
              <h2>Tu lista ({palabras.length})</h2>
              {palabras.length ? (
                palabras.map((p) => <Fila key={p.id} palabra={p} alBorrar={carga.recargar} />)
              ) : (
                <p className="muted">Aún no agregaste palabras.</p>
              )}
            </div>
          </>
        )}
      </Estado>
    </>
  )
}

function Formulario({ alAgregar }) {
  const [datos, setDatos] = useState(VACIA)
  const [errores, setErrores] = useState([])
  const [enviando, setEnviando] = useState(false)

  const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value })

  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    setErrores([])
    try {
      await api.post('/api/mis-palabras/', datos)
      setDatos(VACIA)
      alAgregar()
    } catch (err) {
      setErrores(err.datos?.errores ? mensajes(err.datos.errores) : [err.message])
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="card">
      <h2>Agregar una palabra</h2>
      <form onSubmit={enviar}>
        {errores.length > 0 && (
          <ul className="errores">
            {errores.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        )}
        <label className="campo">
          Inglés
          <input type="text" value={datos.ingles} onChange={cambiar('ingles')} maxLength={80} required />
        </label>
        <label className="campo">
          Español
          <input type="text" value={datos.espanol} onChange={cambiar('espanol')} maxLength={80} required />
        </label>
        <label className="campo">
          Ejemplo (opcional)
          <input type="text" value={datos.ejemplo} onChange={cambiar('ejemplo')} maxLength={200} />
        </label>
        <button className="btn" type="submit" disabled={enviando}>
          Agregar
        </button>
      </form>
      <p className="muted">Tus palabras entran en las tarjetas y en el quiz junto con las demás.</p>
    </div>
  )
}

function Fila({ palabra, alBorrar }) {
  const [error, setError] = useState(null)

  async function borrar() {
    try {
      await api.borrar(`/api/mis-palabras/${palabra.id}/`)
      alBorrar()
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="fila" style={{ alignItems: 'center', margin: '0 0 4px' }}>
      <span style={{ flex: 1 }}>
        <b>{palabra.ingles}</b> = {palabra.espanol}
        {palabra.ejemplo && <span className="muted"> · {palabra.ejemplo}</span>}
        {error && <span className="error"> {error}</span>}
      </span>
      <button className="btn sec" type="button" onClick={borrar}>
        Borrar
      </button>
    </div>
  )
}
