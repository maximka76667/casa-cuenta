import { useParams, Link } from "react-router-dom";
import { useCallback, useEffect, useState } from "react";
import {
  getDebtors,
  getExpenses,
  getGroupPersons,
  submitExpense,
  getGroup,
  addPerson,
  getGroupBalances,
  deleteExpense,
} from "../api/api";
import { Person } from "../interfaces/Person";
import AddExpensePopup from "../components/AddExpensePopup";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import { Group as GroupType } from "../interfaces/Group";
import PersonInfo from "../components/PersonInfo";
import {
  Card,
  Heading,
  Text,
  Container,
  VStack,
  HStack,
  Button,
  Input,
  Box,
  Badge,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  IconButton,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import { useNotifications } from "../hooks/useNotifications";
import { ExpenseCreateWithoutGroupId } from "../interfaces/ExpenseCreate";
import { PersonFinancials } from "../interfaces/PersonFinancials";

const Group = () => {
  const { groupId } = useParams();

  const [group, setGroup] = useState<GroupType | null>(null);
  const [persons, setPersons] = useState<Person[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [debtorsExpenses, setDebtorsExpenses] = useState<DebtorsExpense[]>([]);
  const [balances, setBalances] = useState<{
    [personId: string]: PersonFinancials;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Add person state
  const [newPersonName, setNewPersonName] = useState("");
  const [isAddingPerson, setIsAddingPerson] = useState(false);

  // Expense popup state
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [clickedPersonId, setClickedPersonId] = useState("");

  // Person info popup state
  const [isPersonInfoOpen, setIsPersonInfoOpen] = useState(false);
  const [activePerson, setActivePerson] = useState<Person | null>(null);

  const { showError, showSuccess } = useNotifications();

  const handleAddPerson = async () => {
    if (!newPersonName.trim() || !groupId) {
      showError({
        title: "Error",
        description: "Please enter a person's name",
      });
      return;
    }

    setIsAddingPerson(true);
    try {
      const { person: newPerson } = await addPerson(newPersonName, groupId);
      setPersons([...persons, newPerson[0]]);
      setNewPersonName("");
      showSuccess({
        title: "Success",
        description: `${newPerson.name} added to the group!`,
      });
      fetchData();
    } catch (error) {
      console.error("Error adding person:", error);
      showError({
        title: "Error",
        description: "Failed to add person. Please try again.",
      });
    } finally {
      setIsAddingPerson(false);
    }
  };

  const handleAddExpense = (clickedPersonId: string) => {
    setIsPopupOpen(true);
    setClickedPersonId(clickedPersonId);
  };

  const handleSubmitExpense = async (data: ExpenseCreateWithoutGroupId) => {
    if (!groupId) return;

    try {
      const newExpense = {
        name: data.name,
        groupId,
        amount: data.amount,
        payerId: data.payerId,
        debtors: data.debtors,
      };

      await submitExpense(newExpense);

      showSuccess({
        title: "Success",
        description: "Expense added successfully!",
      });

      // Refresh data
      fetchData();
      setIsPopupOpen(false);
    } catch (error) {
      console.error("Error adding expense:", error);
      showError({
        title: "Error",
        description: "Failed to add expense. Please try again.",
      });
    }
  };

  const handleClosePopup = () => {
    setClickedPersonId("");
    setIsPopupOpen(false);
  };

  const handleClosePersonInfoPopup = () => {
    setActivePerson(null);
    setIsPersonInfoOpen(false);
  };

  const handlePersonClick = (person: Person) => {
    setIsPersonInfoOpen(true);
    setActivePerson(person);
  };

  const handleDeleteExpense = async (expenseId: string) => {
    try {
      await deleteExpense(expenseId);

      showSuccess({
        title: "Success",
        description: "Expense deleted successfully!",
      });

      // Refresh data to update balances
      fetchData();
    } catch (error) {
      console.error("Error deleting expense:", error);
      showError({
        title: "Error",
        description: "Failed to delete expense. Please try again.",
      });
    }
  };

  const fetchData = useCallback(
    async (controller?: AbortController) => {
      if (!groupId) return;

      setIsLoading(true);

      try {
        const [
          groupData,
          personsData,
          expensesData,
          debtorsData,
          balancesData,
        ] = await Promise.all([
          getGroup(groupId, controller),
          getGroupPersons(groupId, controller),
          getExpenses(groupId, controller),
          getDebtors(groupId, controller),
          getGroupBalances(groupId, controller),
        ]);

        setGroup(groupData);
        setPersons(personsData);
        setExpenses(expensesData);
        setDebtorsExpenses(debtorsData);
        setBalances(balancesData.balances);
      } catch (err: unknown) {
        if (err instanceof Error) {
          if (err.name === "CanceledError") return; // ignore cancellation
          console.error("Failed to fetch data:", err);
          showError({
            title: "Error",
            description:
              "Failed to load group data. Please check the group ID.",
          });
        } else {
          console.error("Unexpected error", err);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [groupId, showError]
  );

  useEffect(() => {
    const controller = new AbortController();
    fetchData(controller);

    return () => {
      controller.abort();
    };
  }, [groupId, fetchData]);

  if (isLoading) {
    return (
      <Container maxW="6xl" py={8}>
        <Text textAlign="center">Loading group data...</Text>
      </Container>
    );
  }

  if (!group) {
    return (
      <Container maxW="6xl" py={8}>
        <VStack spacing={4}>
          <Text textAlign="center" color="red.500">
            Group not found. Please check the group ID.
          </Text>
          <Link to="/">
            <Button colorScheme="blue">Go Home</Button>
          </Link>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            {group.name}
          </Heading>
          <Text color="gray.500" fontSize="sm">
            Group ID: {groupId}
          </Text>
          <Text color="gray.600" fontSize="sm" mt={1}>
            Share this URL with others to let them join and add expenses
          </Text>
        </Box>

        {/* Add Person Section */}
        <Card p={4}>
          <VStack spacing={3}>
            <Heading size="md">Add Person to Group</Heading>
            <HStack w="100%">
              <Input
                placeholder="Enter person's name"
                value={newPersonName}
                onChange={(e) => setNewPersonName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddPerson()}
              />
              <Button
                colorScheme="green"
                onClick={handleAddPerson}
                isLoading={isAddingPerson}
                loadingText="Adding..."
              >
                Add Person
              </Button>
            </HStack>
          </VStack>
        </Card>

        {/* Persons Section */}
        <Box>
          <Heading size="lg" mb={4}>
            People ({persons.length})
          </Heading>
          {persons.length === 0 ? (
            <Text color="gray.500" textAlign="center" py={8}>
              No people in this group yet. Add someone above to get started!
            </Text>
          ) : (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {persons.map((person) => (
                <Card
                  key={person.id}
                  p={4}
                  cursor="pointer"
                  onClick={() => handlePersonClick(person)}
                >
                  <VStack spacing={2}>
                    <Text fontWeight="bold">{person.name}</Text>
                    {balances && balances[person.id] && (
                      <VStack spacing={1}>
                        <Text fontSize="sm" color="gray.600">
                          Paid: ${balances[person.id].paid.toFixed(2)}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          Owes: ${balances[person.id].owes.toFixed(2)}
                        </Text>
                        <Badge
                          colorScheme={
                            balances[person.id].balance >= 0 ? "green" : "red"
                          }
                        >
                          {balances[person.id].balance >= 0 ? "+" : ""}$
                          {balances[person.id].balance.toFixed(2)}
                        </Badge>
                      </VStack>
                    )}
                    <Button
                      size="sm"
                      colorScheme="blue"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleAddExpense(person.id);
                      }}
                    >
                      Add Expense
                    </Button>
                  </VStack>
                </Card>
              ))}
            </SimpleGrid>
          )}
        </Box>

        {/* Expenses Section */}
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
                      onClick={() => handleDeleteExpense(expense.id)}
                    />
                  </HStack>
                </Card>
              ))}
            </SimpleGrid>
          )}
        </Box>

        {/* Balances Summary */}
        {balances && Object.keys(balances).length > 0 && (
          <Box>
            <Heading size="lg" mb={4}>
              Balance Summary
            </Heading>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {Object.entries(balances).map(
                ([personId, personFinancials]: [string, PersonFinancials]) => (
                  <Card key={personId} p={4}>
                    <Stat>
                      <StatLabel>{personFinancials.name}</StatLabel>
                      <StatNumber
                        color={
                          personFinancials.balance >= 0
                            ? "green.500"
                            : "red.500"
                        }
                      >
                        {personFinancials.balance >= 0 ? "+" : ""}$
                        {personFinancials.balance.toFixed(2)}
                      </StatNumber>
                      <StatHelpText>
                        {personFinancials.balance >= 0
                          ? "Should receive"
                          : "Should pay"}
                      </StatHelpText>
                    </Stat>
                  </Card>
                )
              )}
            </SimpleGrid>
          </Box>
        )}

        {/* Back to Home */}
        <Box textAlign="center">
          <Link to="/">
            <Button variant="outline">Create Another Group</Button>
          </Link>
        </Box>
      </VStack>

      {/* Popup modals */}
      {isPopupOpen && (
        <AddExpensePopup
          persons={persons}
          onClose={handleClosePopup}
          onSubmit={handleSubmitExpense}
          clickedPayer={clickedPersonId}
        />
      )}
      {isPersonInfoOpen && activePerson && (
        <PersonInfo
          isOpen={isPersonInfoOpen}
          handleClosePopup={handleClosePersonInfoPopup}
          activePerson={activePerson}
          expenses={debtorsExpenses.filter(
            (expense) => expense.person_id === activePerson.id
          )}
          payedExpenses={expenses}
          groupPersons={persons}
        />
      )}
    </Container>
  );
};

export default Group;
