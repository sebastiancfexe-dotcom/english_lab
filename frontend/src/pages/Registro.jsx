import { useState } from 'react'
import { Link } from 'react-router-dom'
import { mensajes } from '../api'
import { useAuth } from '../auth'

export default function Registro() {
  const { registrar } = useAuth()
  const [datos, setDatos] = useState({ username: '', password1: '', password2: '' })
  const [errores, setErrores] = useState([])
  const [enviando, setEnviando] = useState(false)

  const cambiar = (campo) => (e) => setDatos({ ...datos, [campo]: e.target.value })

  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    setErrores([])
    try {
      await registrar(datos)
    } catch (err) {
      setErrores(err.datos?.errores ? mensajes(err.datos.errores) : [`No se pudo crear la cuenta: ${err.message}`])
      setEnviando(false)
    }
  }

  return (
    <div className="card">
      <h1>Crear cuenta</h1>
      <form onSubmit={enviar}>
        {errores.length > 0 && (
          <ul className="errores">
            {errores.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        )}
        <label className="campo">
          Usuario
          <input type="text" value={datos.username} onChange={cambiar('username')} autoFocus required />
        </label>
        <label className="campo">
          Contraseña
          <input type="password" value={datos.password1} onChange={cambiar('password1')} required />
        </label>
        <label className="campo">
          Repite la contraseña
          <input type="password" value={datos.password2} onChange={cambiar('password2')} required />
        </label>
        <button className="btn" type="submit" disabled={enviando}>
          Registrarme
        </button>{' '}
        <Link className="btn sec" to="/entrar">
          Ya tengo cuenta
        </Link>
      </form>
    </div>
  )
}
