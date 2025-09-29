import {
  Box,
  Card,
  HStack,
  Text,
} from "@chakra-ui/react";
import { Expense } from "../interfaces/Expense";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { calculateDebtorAmount } from "../utils/calculateDebtorAmount";

interface ExpenseSummaryProps {
  expense: Expense;
  debtors: DebtorsExpense[];
}

const ExpenseSummary = ({ expense, debtors }: ExpenseSummaryProps) => {
  const totalDebtorAmount = debtors.reduce(
    (sum, debtor) => sum + calculateDebtorAmount(debtor, expense.amount, debtors), 
    0
  );

  const hasDiscrepancy = Math.abs(totalDebtorAmount - expense.amount) > 0.01;

  return (
    <Box>
      <Card p={3} bg="green.50" borderColor="green.200" borderWidth={1}>
        <HStack justify="space-between">
          <Text fontWeight="semibold" color="green.700">
            Total Split Amount:
          </Text>
          <Text fontWeight="bold" color="green.700">
            €{totalDebtorAmount.toFixed(2)}
          </Text>
        </HStack>
        {hasDiscrepancy && (
          <Text fontSize="xs" color="orange.600" mt={1}>
            ⚠️ Note: Split doesn't equal total expense amount
          </Text>
        )}
      </Card>
    </Box>
  );
};

export default ExpenseSummary;

