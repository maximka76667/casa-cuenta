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
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import { Group as GroupType } from "../interfaces/Group";
import PersonInfo from "../components/PersonInfo";
import GroupHeader from "../components/GroupHeader";
import AddPersonForm from "../components/AddPersonForm";
import PersonsList from "../components/PersonsList";
import ExpensesList from "../components/ExpensesList";
import BalancesSummary from "../components/BalancesSummary";
import {
  Text,
  Container,
  VStack,
  Button,
  Box,
} from "@chakra-ui/react";
import { useNotifications } from "../hooks/useNotifications";

const Group = () => {
  const { groupId } = useParams();

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
      const newPerson = await addPerson(newPersonName, groupId);
      setPersons([...persons, newPerson]);
      setNewPersonName("");
      showSuccess({
        title: "Success",
        description: `${newPerson.name} added to the group!`,
      });
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

  const fetchData = async () => {
    if (!groupId) return;

    setIsLoading(true);
    const controller = new AbortController();

    try {
      const [groupData, personsData, expensesData, debtorsData, balancesData] =
        await Promise.all([
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
      showError({
        title: "Error",
        description: "Failed to load group data. Please check the group ID.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [groupId]);

  console.log(persons);

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
        <GroupHeader groupName={group.name} groupId={groupId!} />

        {/* Add Person Section */}
        <AddPersonForm
          newPersonName={newPersonName}
          setNewPersonName={setNewPersonName}
          onAddPerson={handleAddPerson}
          isAddingPerson={isAddingPerson}
        />

        {/* Persons Section */}
        <PersonsList
          persons={persons}
          balances={balances}
          onPersonClick={handlePersonClick}
          onAddExpense={handleAddExpense}
        />

        {/* Expenses Section */}
        <ExpensesList
          expenses={expenses}
          persons={persons}
          onDeleteExpense={handleDeleteExpense}
        />

        {/* Balances Summary */}
        <BalancesSummary balances={balances} />

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
