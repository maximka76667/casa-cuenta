import { Box, Heading, Text, SimpleGrid, Card, HStack, VStack, IconButton } from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import { Expense } from "../interfaces/Expense";
import { Person } from "../interfaces/Person";

interface ExpensesListProps {
  expenses: Expense[];
  persons: Person[];
  onDeleteExpense: (expenseId: string) => void;
}

const ExpensesList = ({
  expenses,
  persons,
  onDeleteExpense,
}: ExpensesListProps) => {
  return (
    <Box>
      <Heading size="lg" mb={4}>
        Expenses ({expenses.length})
      </Heading>
      {expenses.length === 0 ? (
        <Text color="gray.500" textAlign="center" py={8}>
          No expenses yet. Click "Add Expense" on a person's card to get
          started!
        </Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {expenses.map((expense) => (
            <Card key={expense.id} p={4}>
              <HStack justify="space-between" align="start">
                <VStack align="start" spacing={2} flex={1}>
                  <Text fontWeight="bold">{expense.name}</Text>
                  <Text fontSize="lg" color="green.600">
                    ${expense.amount.toFixed(2)}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    Paid by:{" "}
                    {persons.find((p) => p.id === expense.payer_id)?.name ||
                      "Unknown"}
                  </Text>
                </VStack>
                <IconButton
                  aria-label="Delete expense"
                  icon={<DeleteIcon />}
                  size="sm"
                  colorScheme="red"
                  variant="ghost"
                  onClick={() => onDeleteExpense(expense.id)}
                />
              </HStack>
            </Card>
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
};

export default ExpensesList;
