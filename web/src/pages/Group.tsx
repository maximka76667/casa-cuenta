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
  deletePerson,
} from "../api/api";
import { Person } from "../interfaces/Person";
import AddExpensePopup from "../components/AddExpensePopup";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import { Group as GroupType } from "../interfaces/Group";
import PersonInfo from "../components/PersonInfo";
import { Text, Container, VStack, Button, Box } from "@chakra-ui/react";
import { useNotifications } from "../hooks/useNotifications";
import { ExpenseCreateWithoutGroupId } from "../interfaces/ExpenseCreate";
import AddPersonSection from "../components/AddPersonSection";
import PersonsList from "../components/PersonsSection";
import ExpensesList from "../components/ExpensesList";
import BalancesSummary from "../components/BalancesSummary";
import GroupHeader from "../components/GroupHeader";
import GroupNotFound from "../components/GroupNotFound";
import { Balances } from "../interfaces/Balances";

const Group = () => {
  const { groupId } = useParams();

  const [group, setGroup] = useState<GroupType | null>(null);
  const [persons, setPersons] = useState<Person[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [debtorsExpenses, setDebtorsExpenses] = useState<DebtorsExpense[]>([]);
  const [balances, setBalances] = useState<Balances | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Expense popup state
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [clickedPersonId, setClickedPersonId] = useState("");

  // Person info popup state
  const [isPersonInfoOpen, setIsPersonInfoOpen] = useState(false);
  const [activePerson, setActivePerson] = useState<Person | null>(null);

  const { showError, showSuccess } = useNotifications();

  const handleAddExpense = (clickedPersonId: string) => {
    setIsPopupOpen(true);
    setClickedPersonId(clickedPersonId);
  };

  const handlePersonsChange = async (newPersonName: string) => {
    try {
      const { person: newPerson } = await addPerson(newPersonName, groupId!);
      setPersons([...persons, newPerson[0]]);
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
    }
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

  const handleDeletePerson = async (personId: string) => {
    try {
      await deletePerson(personId);

      showSuccess({
        title: "Success",
        description: "Person deleted successfully!",
      });

      // Refresh data to update persons list and balances
      fetchData();
    } catch (error) {
      console.error("Error deleting person:", error);
      showError({
        title: "Error",
        description: "Failed to delete person. Please try again.",
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

  if (!group || !groupId) {
    return <GroupNotFound />;
  }

  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <GroupHeader groupName={group.name} groupId={groupId!} />

        {/* Add Person Section */}
        <AddPersonSection
          groupId={groupId}
          onPersonsChange={handlePersonsChange}
        />

        {/* Persons Section */}
        {balances ? (
          <PersonsList
            persons={persons}
            balances={balances}
            onPersonClick={handlePersonClick}
            onAddExpense={handleAddExpense}
            onDeletePerson={handleDeletePerson}
          />
        ) : (
          <p>Loading balances...</p>
        )}

        {/* Expenses Section */}
        <ExpensesList
          expenses={expenses}
          persons={persons}
          onDeleteExpense={handleDeleteExpense}
        />

        {/* Balances Summary */}
        {balances ? (
          <BalancesSummary balances={balances} />
        ) : (
          <p>Loading balances...</p>
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
