import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import { calculateDebtorAmount } from "../utils/calculateDebtorAmount";
import {
  Badge,
  Box,
  Card,
  Divider,
  Flex,
  Heading,
  HStack,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Spacer,
  Text,
  VStack,
} from "@chakra-ui/react";

interface PersonInfoProps {
  isOpen: boolean;
  groupPersons: Person[];
  activePerson: Person;
  expenses: DebtorsExpense[];
  payedExpenses: Expense[];
  handleClosePopup: () => void;
}

const PersonInfo = ({
  isOpen,
  expenses,
  payedExpenses,
  activePerson,
  groupPersons,
  handleClosePopup,
}: PersonInfoProps) => {
  const result = payedExpenses.reduce((acc, expense) => {
    // find all debtors for this expense
    const relatedDebtors = expenses.filter((d) => d.expense_id === expense.id);

    // sum their calculated amounts
    const totalAmount = relatedDebtors.reduce(
      (sum, d) =>
        sum + calculateDebtorAmount(d, expense.amount, relatedDebtors),
      0
    );

    // find payer
    const payer = groupPersons.find((p) => p.id === expense.payer_id);

    // accumulate into result
    if (!acc[expense.payer_id]) {
      acc[expense.payer_id] = {
        amount: 0,
        person: payer ? payer.name : "Unknown",
      };
    }
    if (!activePerson) return acc;
    if (expense.payer_id == activePerson.id) {
      acc[expense.payer_id].amount -= totalAmount;
    } else {
      acc[expense.payer_id].amount += totalAmount;
    }

    return acc;
  }, {} as Record<string, { amount: number; person: string }>);

  // Convert Object.entries to a more structured format
  const balanceEntries = Object.entries(result).map(
    ([payerId, { amount, person: personName }]) => ({
      payerId,
      amount,
      personName,
      isActivePerson: payerId === activePerson.id,
      owesOrOwed: amount > 0 ? "owes" : "owed",
      absoluteAmount: Math.abs(amount),
    })
  );

  // Separate debts and credits for better organization
  const debts = balanceEntries.filter((entry) => entry.amount > 0);
  const credits = balanceEntries.filter((entry) => entry.amount < 0);

  return (
    <Modal isOpen={isOpen} onClose={handleClosePopup}>
      <ModalOverlay />

      <ModalContent
        className={`${
          isOpen ? "flex" : "hidden"
        } absolute top-0 left-0 bg-white min-w-1/2 min-h-full flex-col py-3`}
      >
        <ModalHeader>
          <HStack>
            <Text fontSize="2xl" fontWeight="bold">
              {activePerson.name}'s Financial Summary
            </Text>
            <Spacer />
            <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
              {expenses.length} expense{expenses.length !== 1 ? "s" : ""}
            </Badge>
          </HStack>
        </ModalHeader>
        <ModalBody>
          <VStack spacing={6} align="stretch">
            {/* Individual Expenses Section */}
            <Box>
              <Heading size="md" mb={3} color="gray.700">
                Individual Expenses
              </Heading>
              <VStack spacing={2} align="stretch">
                {expenses.map((expense) => {
                  const currentExpense = payedExpenses.find(
                    (payedExpense) => payedExpense.id === expense.expense_id
                  );

                  const payerId = currentExpense?.payer_id;
                  const isPaidByActivePerson = activePerson.id === payerId;

                  // Calculate the actual amount for this debtor
                  const expenseDebtors = expenses.filter(
                    (d) => d.expense_id === expense.expense_id
                  );
                  const calculatedAmount = calculateDebtorAmount(
                    expense,
                    currentExpense?.amount || 0,
                    expenseDebtors
                  );

                  return (
                    <Card
                      key={expense.id}
                      p={4}
                      borderWidth={2}
                      borderColor="cyan.200"
                      bg="gray.50"
                    >
                      <Flex align="center">
                        <Box flex={1}>
                          <Heading size="sm" color="gray.700">
                            {currentExpense?.name}
                          </Heading>
                          <Text fontSize="xs" color="gray.600" mt={1}>
                            {isPaidByActivePerson
                              ? "✅ Paid by this person"
                              : `💰 Paid by ${
                                  groupPersons.find(
                                    (groupPerson) => payerId === groupPerson.id
                                  )?.name ?? "Unknown"
                                }`}
                          </Text>
                        </Box>
                        <Text fontSize="lg" fontWeight="bold" color="gray.800">
                          €{calculatedAmount.toFixed(2)}
                        </Text>
                      </Flex>
                    </Card>
                  );
                })}
              </VStack>
            </Box>

            <Divider />

            {/* Balance Summary Section */}
            <Box>
              <Heading size="md" mb={3} color="gray.700">
                Balance Summary
              </Heading>

              {/* Money Owed (Debts) */}
              {debts.length > 0 && (
                <Box mb={4}>
                  <Text fontWeight="semibold" color="red.600" mb={2}>
                    💸 Money You Owe:
                  </Text>
                  <VStack spacing={2} align="stretch">
                    {debts.map((entry) => (
                      <Card
                        key={entry.payerId}
                        p={3}
                        bg="red.50"
                        borderColor="red.200"
                        borderWidth={1}
                      >
                        <Flex justify="space-between" align="center">
                          <Text color="gray.700">
                            To:{" "}
                            <Text as="span" fontWeight="semibold">
                              {entry.personName}
                            </Text>
                          </Text>
                          <Text fontWeight="bold" color="red.600">
                            €{entry.absoluteAmount.toFixed(2)}
                          </Text>
                        </Flex>
                      </Card>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Money Owed To You (Credits) */}
              {credits.length > 0 && (
                <Box>
                  <Text fontWeight="semibold" color="green.600" mb={2}>
                    💰 Money Owed To You:
                  </Text>
                  <VStack spacing={2} align="stretch">
                    {credits.map((entry) => (
                      <Card
                        key={entry.payerId}
                        p={3}
                        bg="green.50"
                        borderColor="green.200"
                        borderWidth={1}
                      >
                        <Flex justify="space-between" align="center">
                          <Text color="gray.700">
                            From:{" "}
                            <Text as="span" fontWeight="semibold">
                              {entry.personName}
                            </Text>
                          </Text>
                          <Text fontWeight="bold" color="green.600">
                            €{entry.absoluteAmount.toFixed(2)}
                          </Text>
                        </Flex>
                      </Card>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* No Balance */}
              {debts.length === 0 && credits.length === 0 && (
                <Card p={4} bg="blue.50" borderColor="blue.200" borderWidth={1}>
                  <Text
                    textAlign="center"
                    color="blue.700"
                    fontWeight="semibold"
                  >
                    🎉 All settled up! No outstanding balances.
                  </Text>
                </Card>
              )}
            </Box>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <button onClick={handleClosePopup}>Close</button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default PersonInfo;
