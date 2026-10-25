import { ref } from 'vue'
import type { User } from '../types/chat'
import { useAuthFetch } from './useAuthFetch'

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8000'

// Module-level reactive state to make this composable behave like a
// singleton store. This ensures every call to `useUsers()` returns the
// same refs so different components share personas/availablePersonas.
const personas = ref<User[]>([])
const availablePersonas = ref<User[]>([])
const currentPersona = ref<User | null>(null)
let loadedFile: string | null = null
let loadInFlight: { file: string; promise: Promise<void> } | null = null

export function useUsers() {
  const { authFetch } = useAuthFetch()

  const loadUsers = (file: string): Promise<void> => {
    if (loadedFile === file) return Promise.resolve()
    if (loadInFlight?.file === file) return loadInFlight.promise

    personas.value = []
    availablePersonas.value = []
    currentPersona.value = null

    const promise = (async () => {
      // preserve folder separators when sending a file path to the backend
      let res = await authFetch(`${API_BASE}/api/users/${encodeURI(file)}`)
      // If the backend expects just the basename, retry using it when 404
      if (!res.ok && res.status === 404) {
        const base = file.split('/').pop() || file
        if (base !== file) {
          res = await authFetch(`${API_BASE}/api/users/${encodeURI(base)}`)
        }
      }
      if (!res.ok) {
        let detail = `HTTP ${res.status}`
        try {
          const error = await res.json()
          detail = error.detail || detail
        } catch {
          // Keep the HTTP status when the response has no JSON error body.
        }
        throw new Error(`Failed to load users: ${detail}`)
      }
      console.log('Fetching users from backend')
      const data = await res.json()
      const users = Array.isArray(data.users) ? data.users : data
      personas.value = users.map((user: any) => ({
        name: user.speaker,
        description: user.description,
      }))

      availablePersonas.value = personas.value.map((persona, index) => ({
        id: index + 2,
        name: persona.name,
        description: persona.description,
      }))

      currentPersona.value = availablePersonas.value[0] || null
      loadedFile = file
    })().finally(() => {
      if (loadInFlight?.promise === promise) loadInFlight = null
    })

    loadInFlight = { file, promise }
    return promise
  }

  const switchPersona = (personaName: string) => {
    const persona = availablePersonas.value.find((p) => p.name === personaName)
    if (persona) {
      currentPersona.value = persona
    }
  }

  return {
    personas,
    availablePersonas,
    currentPersona,
    loadUsers,
    switchPersona,
  }
}
