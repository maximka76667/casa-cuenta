import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { ChakraProvider } from '@chakra-ui/react'
import AddExpensePopup from '../AddExpensePopup'

const mockPersons = [
  { id: '1', name: 'John' },
  { id: '2', name: 'Jane' }
]

const renderWithChakra = (component: React.ReactElement) => {
  return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('AddExpensePopup', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders form fields correctly', () => {
    renderWithChakra(
      <AddExpensePopup
        clickedPayer="1"
        persons={mockPersons}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      />
    )

    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Amount')).toBeInTheDocument()
    expect(screen.getByText('Who pays?')).toBeInTheDocument()
    expect(screen.getByText('Who shares?')).toBeInTheDocument()
  })

  it('calls onSubmit with correct data when form is submitted', async () => {
    renderWithChakra(
      <AddExpensePopup
        clickedPayer="1"
        persons={mockPersons}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      />
    )

    const nameInput = screen.getByRole('textbox')
    const amountInput = screen.getByRole('spinbutton')
    
    fireEvent.change(nameInput, { target: { value: 'Test Expense' } })
    fireEvent.change(amountInput, { target: { value: '50' } })
    
    fireEvent.click(screen.getByRole('button', { name: /submit/i }))

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'Test Expense',
        amount: 50,
        payerId: '1',
        debtors: ['1', '2']
      })
    })
  })

  it('prevents submission with empty required fields', async () => {
    renderWithChakra(
      <AddExpensePopup
        clickedPayer="1"
        persons={mockPersons}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /submit/i }))

    await waitFor(() => {
      expect(mockOnSubmit).not.toHaveBeenCalled()
    })
  })

  it('toggles debtor selection correctly', () => {
    renderWithChakra(
      <AddExpensePopup
        clickedPayer="1"
        persons={mockPersons}
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      />
    )

    const johnCheckbox = screen.getByRole('checkbox', { name: /john/i })
    expect(johnCheckbox).toBeChecked()

    fireEvent.click(johnCheckbox)
    expect(johnCheckbox).not.toBeChecked()

    fireEvent.click(johnCheckbox)
    expect(johnCheckbox).toBeChecked()
  })
})
