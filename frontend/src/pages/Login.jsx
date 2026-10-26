import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Login() {
  const { entrar } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [enviando, setEnviando] = useState(false)

  async function enviar(e) {
    e.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      await entrar(username, password)
    } catch (err) {
      setError(err.status === 401 ? 'Usuario o contraseña incorrectos.' : `No se pudo entrar: ${err.message}`)
      setEnviando(false)
    }
  }

  return (
    <div className="card">
      <h1>Entrar</h1>
      <form onSubmit={enviar}>
        {error && <p className="error">{error}</p>}
        <label className="campo">
          Usuario
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} autoFocus required />
        </label>
        <label className="campo">
          Contraseña
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button className="btn" type="submit" disabled={enviando}>
          Entrar
        </button>{' '}
        <Link className="btn sec" to="/registro">
          Crear cuenta
        </Link>
      </form>
    </div>
  )
}
