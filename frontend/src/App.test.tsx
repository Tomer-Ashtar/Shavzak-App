import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from './App'

test('renders nav and pages placeholders', () => {
  render(<MemoryRouter><App /></MemoryRouter>)
  expect(screen.getByRole('heading', { name: /workers/i })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /calendar/i })).toBeInTheDocument()
  expect(screen.getByRole('link', { name: /today/i })).toBeInTheDocument()
})

