// Cliente de la API de Django. Guarda los tokens JWT y renueva el de acceso cuando caduca.
export const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const CLAVE = 'english-lab-tokens'

export function leerTokens() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE))
  } catch {
    return null
  }
}

export function guardarTokens(tokens) {
  try {
    localStorage.setItem(CLAVE, JSON.stringify(tokens))
  } catch {
    // sin almacenamiento disponible: la sesión dura lo que dure la pestaña
  }
}

export function borrarTokens() {
  try {
    localStorage.removeItem(CLAVE)
  } catch {
    // nada que borrar
  }
}

export class ErrorApi extends Error {
  constructor(status, datos) {
    super(datos?.detail ?? `Error ${status}`)
    this.status = status
    this.datos = datos
  }
}

let alCaducarSesion = () => {}
export function alCerrarSesion(fn) {
  alCaducarSesion = fn
}

let renovando = null

function renovar() {
  renovando ??= (async () => {
    const tokens = leerTokens()
    if (!tokens?.refresh) throw new ErrorApi(401, { detail: 'Sesión caducada.' })
    const r = await fetch(`${BASE}/api/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokens.refresh }),
    })
    if (!r.ok) throw new ErrorApi(401, { detail: 'Sesión caducada.' })
    const nuevos = await r.json()
    guardarTokens({ ...tokens, ...nuevos })
  })().finally(() => {
    renovando = null
  })
  return renovando
}

async function pedir(ruta, { metodo = 'GET', cuerpo, auth = true } = {}, reintento = true) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const tokens = leerTokens()
    if (tokens?.access) headers.Authorization = `Bearer ${tokens.access}`
  }
  const r = await fetch(`${BASE}${ruta}`, {
    method: metodo,
    headers,
    body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
  })

  if (r.status === 401 && auth && reintento) {
    try {
      await renovar()
    } catch (e) {
      borrarTokens()
      alCaducarSesion()
      throw e
    }
    return pedir(ruta, { metodo, cuerpo, auth }, false)
  }

  const datos = r.status === 204 ? null : await r.json().catch(() => null)
  if (!r.ok) throw new ErrorApi(r.status, datos)
  return datos
}

export const api = {
  get: (ruta) => pedir(ruta),
  post: (ruta, cuerpo) => pedir(ruta, { metodo: 'POST', cuerpo }),
  borrar: (ruta) => pedir(ruta, { metodo: 'DELETE' }),
  // sin token: entrar y crear cuenta
  publico: (ruta, cuerpo) => pedir(ruta, { metodo: 'POST', cuerpo, auth: false }),
}

/** Aplana los errores de formulario de Django ({campo: [{message}]}) a una lista de textos. */
export function mensajes(errores) {
  return Object.values(errores ?? {}).flatMap((lista) => lista.map((e) => e.message))
}
