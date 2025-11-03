import { render, screen, waitFor } from '@testing-library/react'
import WorkersPage from './WorkersPage'

beforeEach(() => {
  // @ts-ignore
  global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => [] })
})

afterEach(() => {
  // @ts-ignore
  global.fetch.mockReset?.()
})

it('renders workers table headers', async () => {
  render(<WorkersPage />)
  expect(screen.getByRole('heading', { name: /workers/i })).toBeInTheDocument()
  await waitFor(() => expect(global.fetch).toHaveBeenCalled())
  expect(screen.getByText(/hard chores/i)).toBeInTheDocument()
  expect(screen.getByText(/outer partner/i)).toBeInTheDocument()
})

