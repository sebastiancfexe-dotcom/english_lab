export function hablar(texto, velocidad = 0.9) {
  if (!('speechSynthesis' in window)) return
  speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(texto)
  u.lang = 'en-US'
  u.rate = velocidad
  speechSynthesis.speak(u)
}

export function callar() {
  if ('speechSynthesis' in window) speechSynthesis.cancel()
}
