import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  useDisclosure,
  HStack,
  Badge,
} from "@chakra-ui/react";
import { Expense } from "../interfaces/Expense";
import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { useState } from "react";
import ExpenseCard from "./ExpenseCard";
import ExpenseDetailModal from "./ExpenseDetailModal";

interface ExpensesListProps {
  expenses: Expense[];
  persons: Person[];
  debtorsExpenses: DebtorsExpense[];
  onDeleteExpense: (expenseId: string) => void;
}

const ExpensesList = ({
  expenses,
  persons,
  debtorsExpenses,
  onDeleteExpense,
}: ExpensesListProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedExpense, setSelectedExpense] = useState<Expense | null>(null);

  const handleExpenseClick = (expense: Expense) => {
    setSelectedExpense(expense);
    onOpen();
  };

  return (
    <Box>
      <HStack mb={4}>
        <Heading size="md">Expenses</Heading>
        <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
          {expenses.length} expense{expenses.length !== 1 ? "s" : ""}
        </Badge>
      </HStack>

      {expenses.length === 0 ? (
        <Text color="gray.500" textAlign="center" py={8}>
          No expenses yet. Click "Add Expense" on a person's card to get
          started!
        </Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {expenses.map((expense) => (
            <ExpenseCard
              key={expense.id}
              expense={expense}
              persons={persons}
              debtorsExpenses={debtorsExpenses}
              onExpenseClick={handleExpenseClick}
              onDeleteExpense={onDeleteExpense}
            />
          ))}
        </SimpleGrid>
      )}

      <ExpenseDetailModal
        isOpen={isOpen}
        onClose={onClose}
        expense={selectedExpense}
        persons={persons}
        debtorsExpenses={debtorsExpenses}
      />
    </Box>
  );
};

export default ExpensesList;
