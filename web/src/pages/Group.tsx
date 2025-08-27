import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
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
import PersonCard from "../components/PersonCard";
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
  useToast,
  Box,
  Divider,
  Badge,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  IconButton,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";

const Group = () => {
  const { groupId } = useParams();
  const toast = useToast();

  const [group, setGroup] = useState<GroupType | null>(null);
  const [persons, setPersons] = useState<Person[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [debtorsExpenses, setDebtorsExpenses] = useState<DebtorsExpense[]>([]);
  const [balances, setBalances] = useState<any>(null);
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

  const handleAddPerson = async () => {
    if (!newPersonName.trim() || !groupId) {
      toast({
        title: "Error",
        description: "Please enter a person's name",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsAddingPerson(true);
    try {
      const newPerson = await addPerson(newPersonName, groupId);
      setPersons([...persons, newPerson]);
      setNewPersonName("");
      toast({
        title: "Success",
        description: `${newPerson.name} added to the group!`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error("Error adding person:", error);
      toast({
        title: "Error",
        description: "Failed to add person. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsAddingPerson(false);
    }
  };

  const handleAddExpense = (clickedPersonId: string) => {
    setIsPopupOpen(true);
    setClickedPersonId(clickedPersonId);
  };

  const handleSubmitExpense = async (data: any) => {
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
      
      toast({
        title: "Success",
        description: "Expense added successfully!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      // Refresh data
      fetchData();
      setIsPopupOpen(false);
    } catch (error) {
      console.error("Error adding expense:", error);
      toast({
        title: "Error",
        description: "Failed to add expense. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
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
      
      toast({
        title: "Success",
        description: "Expense deleted successfully!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      // Refresh data to update balances
      fetchData();
    } catch (error) {
      console.error("Error deleting expense:", error);
      toast({
        title: "Error",
        description: "Failed to delete expense. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const fetchData = async () => {
    if (!groupId) return;

    setIsLoading(true);
    const controller = new AbortController();

    try {
      const [groupData, personsData, expensesData, debtorsData, balancesData] = await Promise.all([
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
    } catch (err) {
      console.error("Failed to fetch data:", err);
      toast({
        title: "Error",
        description: "Failed to load group data. Please check the group ID.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [groupId]);

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
                onKeyPress={(e) => e.key === "Enter" && handleAddPerson()}
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
                <Card key={person.id} p={4} cursor="pointer" onClick={() => handlePersonClick(person)}>
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
                          colorScheme={balances[person.id].balance >= 0 ? "green" : "red"}
                        >
                          {balances[person.id].balance >= 0 ? "+" : ""}
                          ${balances[person.id].balance.toFixed(2)}
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
              No expenses yet. Click "Add Expense" on a person's card to get started!
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
                        Paid by: {persons.find(p => p.id === expense.payer_id)?.name || "Unknown"}
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
              {Object.entries(balances).map(([personId, balance]: [string, any]) => (
                <Card key={personId} p={4}>
                  <Stat>
                    <StatLabel>{balance.name}</StatLabel>
                    <StatNumber color={balance.balance >= 0 ? "green.500" : "red.500"}>
                      {balance.balance >= 0 ? "+" : ""}${balance.balance.toFixed(2)}
                    </StatNumber>
                    <StatHelpText>
                      {balance.balance >= 0 ? "Should receive" : "Should pay"}
                    </StatHelpText>
                  </Stat>
                </Card>
              ))}
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
