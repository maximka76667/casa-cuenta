import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { vi } from 'vitest'
import { ChakraProvider } from '@chakra-ui/react'
import PersonCard from '../PersonCard'

const mockPerson = { id: '1', name: 'John Doe', created_at: '2023-01-01', group_id: 'group1' }
const mockExpenses = [
  { id: '1', expense_id: 'exp1', person_id: '1', amount: 25, created_at: '2023-01-01' },
  { id: '2', expense_id: 'exp2', person_id: '1', amount: 15, created_at: '2023-01-01' }
]
const mockPayedExpenses = [
  { id: '1', name: 'Test Expense', amount: 100, group_id: 'group1', payer_id: '1', debtors: ['1'] }
]

const renderWithChakra = (component: React.ReactElement) => {
  return render(<ChakraProvider>{component}</ChakraProvider>)
}

describe('PersonCard', () => {
  const mockHandleAddExpense = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays person name and calculated total', () => {
    renderWithChakra(
      <PersonCard
        person={mockPerson}
        expenses={mockExpenses}
        payedExpenses={mockPayedExpenses}
        groupPersons={[]}
        handleAddExpense={mockHandleAddExpense}
      />
    )

    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText(/total: -60/i)).toBeInTheDocument()
  })

  it('calls handleAddExpense when + button is clicked', () => {
    renderWithChakra(
      <PersonCard
        person={mockPerson}
        expenses={mockExpenses}
        payedExpenses={mockPayedExpenses}
        groupPersons={[]}
        handleAddExpense={mockHandleAddExpense}
      />
    )

    fireEvent.click(screen.getByText('+'))
    expect(mockHandleAddExpense).toHaveBeenCalledWith('1')
  })

  it('displays person ID', () => {
    renderWithChakra(
      <PersonCard
        person={mockPerson}
        expenses={mockExpenses}
        payedExpenses={mockPayedExpenses}
        groupPersons={[]}
        handleAddExpense={mockHandleAddExpense}
      />
    )

    expect(screen.getByText('1')).toBeInTheDocument()
  })

  it('calculates total correctly with no expenses', () => {
    renderWithChakra(
      <PersonCard
        person={mockPerson}
        expenses={[]}
        payedExpenses={[]}
        groupPersons={[]}
        handleAddExpense={mockHandleAddExpense}
      />
    )

    expect(screen.getByText(/total: 0/i)).toBeInTheDocument()
  })
})
