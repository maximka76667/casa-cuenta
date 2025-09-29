import {
  Box,
  Text,
  Card,
  HStack,
} from "@chakra-ui/react";
import { Expense } from "../interfaces/Expense";
import { Person } from "../interfaces/Person";

interface ExpensePayerInfoProps {
  expense: Expense;
  persons: Person[];
}

const ExpensePayerInfo = ({ expense, persons }: ExpensePayerInfoProps) => {
  const getPersonName = (personId: string) => {
    return persons.find(p => p.id === personId)?.name || "Unknown";
  };

  return (
    <Box>
      <Text fontWeight="semibold" color="gray.700" mb={2}>
        💳 Paid by:
      </Text>
      <Card p={3} bg="blue.50" borderColor="blue.200" borderWidth={1}>
        <HStack justify="space-between">
          <Text fontWeight="medium">
            {getPersonName(expense.payer_id)}
          </Text>
          <Text fontWeight="bold" color="blue.600">
            €{expense.amount.toFixed(2)}
          </Text>
        </HStack>
      </Card>
    </Box>
  );
};

export default ExpensePayerInfo;

