import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  HStack,
  Text,
  Spacer,
  Badge,
  VStack,
  Box,
  Divider,
} from "@chakra-ui/react";
import { Expense } from "../interfaces/Expense";
import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import ExpensePayerInfo from "./ExpensePayerInfo";
import ExpenseDivisionBreakdown from "./ExpenseDivisionBreakdown";
import ExpenseSummary from "./ExpenseSummary";

interface ExpenseDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  expense: Expense | null;
  persons: Person[];
  debtorsExpenses: DebtorsExpense[];
}

const ExpenseDetailModal = ({
  isOpen,
  onClose,
  expense,
  persons,
  debtorsExpenses,
}: ExpenseDetailModalProps) => {
  if (!expense) return null;

  const expenseDebtors = debtorsExpenses.filter(
    (debtor) => debtor.expense_id === expense.id
  );

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack>
            <Text fontSize="xl" fontWeight="bold">
              {expense.name}
            </Text>
            <Spacer />
            <Badge colorScheme="green" fontSize="md" px={3} py={1}>
              €{expense.amount.toFixed(2)}
            </Badge>
          </HStack>
        </ModalHeader>

        <ModalBody>
          <VStack spacing={4} align="stretch">
            <ExpensePayerInfo expense={expense} persons={persons} />

            <Divider />

            <ExpenseDivisionBreakdown
              expense={expense}
              persons={persons}
              debtors={expenseDebtors}
            />

            <ExpenseSummary expense={expense} debtors={expenseDebtors} />
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button colorScheme="blue" onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default ExpenseDetailModal;
