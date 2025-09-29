import { Box, Text, Card, VStack, Flex, HStack, Badge } from "@chakra-ui/react";
import { Expense } from "../interfaces/Expense";
import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { calculateDebtorAmount } from "../utils/calculateDebtorAmount";

interface ExpenseDivisionBreakdownProps {
  expense: Expense;
  persons: Person[];
  debtors: DebtorsExpense[];
}

const ExpenseDivisionBreakdown = ({
  expense,
  persons,
  debtors,
}: ExpenseDivisionBreakdownProps) => {
  const getPersonName = (personId: string) => {
    return persons.find((p) => p.id === personId)?.name || "Unknown";
  };

  return (
    <Box>
      <Text fontWeight="semibold" color="gray.700" mb={2}>
        📊 How it's divided:
      </Text>
      <VStack spacing={2} align="stretch">
        {debtors.map((debtor) => {
          const personName = getPersonName(debtor.person_id);
          const calculatedAmount = calculateDebtorAmount(
            debtor,
            expense.amount,
            debtors
          );
          const percentage = (
            (calculatedAmount / expense.amount) *
            100
          ).toFixed(1);

          return (
            <Card
              key={debtor.id}
              p={3}
              bg="gray.50"
              borderWidth={1}
              borderColor="gray.200"
            >
              <Flex justify="space-between" align="center">
                <HStack>
                  <Text fontWeight="medium">{personName}</Text>
                  <Badge colorScheme="gray" fontSize="xs">
                    {percentage}%
                  </Badge>
                </HStack>
                <Text fontWeight="bold" color="gray.700">
                  €{calculatedAmount.toFixed(2)}
                </Text>
              </Flex>
            </Card>
          );
        })}
      </VStack>
    </Box>
  );
};

export default ExpenseDivisionBreakdown;
