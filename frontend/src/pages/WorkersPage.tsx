import { useEffect, useMemo, useState } from 'react'

type Worker = {
  id: number
  name: string
  title?: string | null
  hard_chores_counter: number
  outer_partner_counter: number
}

const API_BASE = (import.meta as any)?.env?.VITE_API_BASE || 'http://localhost:8000'

export default function WorkersPage() {
  const [workers, setWorkers] = useState<Worker[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [name, setName] = useState('')
  const [title, setTitle] = useState('')

  const [editingId, setEditingId] = useState<number | null>(null)
  const [editName, setEditName] = useState('')
  const [editTitle, setEditTitle] = useState('')

  const sortedWorkers = useMemo(
    () => workers.slice().sort((a, b) => a.id - b.id),
    [workers]
  )

  async function fetchWorkers() {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/api/workers`)
      if (!res.ok) throw new Error(`Failed to fetch workers: ${res.status}`)
      const data: Worker[] = await res.json()
      setWorkers(data)
    } catch (e: any) {
      setError(e.message || 'Failed to load workers')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkers()
  }, [])

  async function onAdd(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    try {
      const res = await fetch(`${API_BASE}/api/workers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), title: title.trim() || null })
      })
      if (!res.ok) throw new Error('Create failed')
      setName('')
      setTitle('')
      await fetchWorkers()
    } catch (e: any) {
      alert(e.message || 'Failed to create worker')
    }
  }

  function startEdit(w: Worker) {
    setEditingId(w.id)
    setEditName(w.name)
    setEditTitle(w.title || '')
  }

  async function saveEdit(id: number) {
    try {
      const res = await fetch(`${API_BASE}/api/workers/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editName.trim(), title: editTitle.trim() || null })
      })
      if (!res.ok) throw new Error('Update failed')
      setEditingId(null)
      await fetchWorkers()
    } catch (e: any) {
      alert(e.message || 'Failed to update worker')
    }
  }

  async function onDelete(id: number) {
    if (!confirm('Delete this worker?')) return
    try {
      const res = await fetch(`${API_BASE}/api/workers/${id}`, { method: 'DELETE' })
      if (res.status !== 204) throw new Error('Delete failed')
      await fetchWorkers()
    } catch (e: any) {
      alert(e.message || 'Failed to delete worker')
    }
  }

  return (
    <section>
      <h1>Workers</h1>
      <form onSubmit={onAdd} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input
          aria-label="Name"
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <input
          aria-label="Title"
          placeholder="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      {loading && <p>Loading...</p>}
      {error && <p role="alert" style={{ color: 'crimson' }}>{error}</p>}

      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{ textAlign: 'left' }}>Name</th>
            <th style={{ textAlign: 'left' }}>Title</th>
            <th style={{ textAlign: 'right' }}>Hard chores</th>
            <th style={{ textAlign: 'right' }}>Outer partner</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {sortedWorkers.map(w => (
            <tr key={w.id}>
              <td>
                {editingId === w.id ? (
                  <input value={editName} onChange={(e) => setEditName(e.target.value)} />
                ) : (
                  w.name
                )}
              </td>
              <td>
                {editingId === w.id ? (
                  <input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                ) : (
                  w.title || ''
                )}
              </td>
              <td style={{ textAlign: 'right' }}>{w.hard_chores_counter}</td>
              <td style={{ textAlign: 'right' }}>{w.outer_partner_counter}</td>
              <td style={{ textAlign: 'right' }}>
                {editingId === w.id ? (
                  <>
                    <button onClick={() => saveEdit(w.id)}>Save</button>{' '}
                    <button onClick={() => setEditingId(null)}>Cancel</button>
                  </>
                ) : (
                  <>
                    <button onClick={() => startEdit(w)}>Edit</button>{' '}
                    <button onClick={() => onDelete(w.id)}>Delete</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}

