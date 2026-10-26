import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { alCerrarSesion, api, borrarTokens, guardarTokens, leerTokens } from './api'

const Auth = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(() => Boolean(leerTokens()))

  const salir = useCallback(() => {
    borrarTokens()
    setUsuario(null)
  }, [])

  useEffect(() => {
    alCerrarSesion(salir)
    if (!leerTokens()) return
    api
      .get('/api/auth/yo/')
      .then(setUsuario)
      .catch(() => {})
      .finally(() => setCargando(false))
  }, [salir])

  const iniciar = useCallback(async (ruta, datos) => {
    guardarTokens(await api.publico(ruta, datos))
    setUsuario(await api.get('/api/auth/yo/'))
  }, [])

  const valor = useMemo(
    () => ({
      usuario,
      cargando,
      salir,
      entrar: (username, password) => iniciar('/api/auth/token/', { username, password }),
      registrar: (datos) => iniciar('/api/auth/registro/', datos),
    }),
    [usuario, cargando, salir, iniciar],
  )

  return <Auth.Provider value={valor}>{children}</Auth.Provider>
}

export function useAuth() {
  return useContext(Auth)
}
