import {
  Card,
  HStack,
  VStack,
  IconButton,
  Text,
  Badge,
} from "@chakra-ui/react";
import { DeleteIcon, InfoIcon } from "@chakra-ui/icons";
import { Expense } from "../interfaces/Expense";
import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";

interface ExpenseCardProps {
  expense: Expense;
  persons: Person[];
  debtorsExpenses: DebtorsExpense[];
  onExpenseClick: (expense: Expense) => void;
  onDeleteExpense: (expenseId: string) => void;
}

const ExpenseCard = ({
  expense,
  persons,
  debtorsExpenses,
  onExpenseClick,
  onDeleteExpense,
}: ExpenseCardProps) => {
  const getExpenseDebtors = (expenseId: string) => {
    return debtorsExpenses.filter((debtor) => debtor.expense_id === expenseId);
  };

  const getPersonName = (personId: string) => {
    return persons.find((p) => p.id === personId)?.name || "Unknown";
  };

  const debtors = getExpenseDebtors(expense.id);
  const payerName = getPersonName(expense.payer_id);

  return (
    <Card
      p={4}
      cursor="pointer"
      _hover={{
        shadow: "md",
        transform: "translateY(-2px)",
        transition: "all 0.2s",
      }}
      onClick={() => onExpenseClick(expense)}
      position="relative"
    >
      <HStack justify="space-between" align="start">
        <VStack align="start" spacing={2} flex={1}>
          <HStack>
            <Text fontWeight="bold">{expense.name}</Text>
            <InfoIcon color="blue.400" boxSize={3} />
          </HStack>
          <Text fontSize="lg" color="green.600" fontWeight="semibold">
            €{expense.amount.toFixed(2)}
          </Text>
          <Text fontSize="sm" color="gray.600">
            Paid by:{" "}
            <Text as="span" fontWeight="medium">
              {payerName}
            </Text>
          </Text>
          <HStack spacing={2} flexWrap="wrap">
            <Text fontSize="xs" color="gray.500">
              Split between:
            </Text>
            <Badge colorScheme="blue" fontSize="xs">
              {debtors.length} person{debtors.length !== 1 ? "s" : ""}
            </Badge>
          </HStack>
        </VStack>
        <IconButton
          aria-label="Delete expense"
          icon={<DeleteIcon />}
          size="sm"
          colorScheme="red"
          variant="ghost"
          onClick={(e) => {
            e.stopPropagation();
            onDeleteExpense(expense.id);
          }}
          position="absolute"
          top={2}
          right={2}
        />
      </HStack>
    </Card>
  );
};

export default ExpenseCard;

