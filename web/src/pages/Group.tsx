import { useParams } from "react-router-dom";
import { useUserStore } from "../store/userStore";
import { useShallow } from "zustand/shallow";
import { useEffect, useState } from "react";
import {
  getDebtors,
  getExpenses,
  getGroupPersons,
  submitExpense,
} from "../api/api";
import { Person } from "../interfaces/Person";
import AddExpensePopup from "../components/AddExpensePopup";
import PersonCard from "../components/PersonCard";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import PersonInfo from "../components/PersonInfo";
import { Card, Heading, Text } from "@chakra-ui/react";

const Group = () => {
  const { groupId } = useParams();
  const user = useUserStore(useShallow((state) => state.user));

  const [isPopupOpen, setIsPopupOpen] = useState(false);

  const [isPersonInfoOpen, setIsPersonInfoOpen] = useState(false);
  const [activePerson, setActivePerson] = useState<Person | null>(null);

  const [persons, setPersons] = useState<Person[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [debtorsExpenses, setDebtorsExpenses] = useState<DebtorsExpense[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [clickedPersonId, setClickedPersonId] = useState("");

  const handleAddExpense = (clickedPersonId: string) => {
    setIsPopupOpen(true);
    setClickedPersonId(clickedPersonId);
  };

  console.log(expenses);

  const handleSubmitExpense = async (data) => {
    if (!groupId) return;

    const newExpense = {
      name: data.name,
      groupId,
      amount: data.amount,
      payerId: data.payerId,
      debtors: data.debtors,
    };

    const response = await submitExpense(newExpense);

    console.log("submit expense", newExpense);
    console.log(response);
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

  useEffect(() => {
    if (!user) return;

    const controller = new AbortController();

    const fetchData = async () => {
      setIsLoading(true);

      try {
        if (!groupId) return;

        const [{ persons }, { expenses }, { debtors }] = await Promise.all([
          getGroupPersons(groupId, controller),
          getExpenses(groupId, controller),
          getDebtors(groupId, controller),
        ]);

        console.log("Expenses: ", expenses.data);
        console.log("Debtors: ", debtors);

        // const response = await getGroupPersons(groupId, controller);
        setPersons(persons);
        setExpenses(expenses.data);
        setDebtorsExpenses(debtors);
      } catch (err) {
        console.error("Failed to fetch data:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();

    return () => {
      controller.abort();
    };
  }, [user]);

  return (
    <div className="relative p-10">
      <Heading fontSize="2xl" className="text-center">
        Group
      </Heading>
      <Text
        fontSize="md"
        color="GrayText"
        className="text-center"
        marginBottom="5"
      >
        {groupId}
      </Text>
      <Heading fontSize="2xl" className="text-center font-bold">
        Expenses
      </Heading>
      <div className="w-full flex justify-between gap-2 p-2">
        {expenses.map((expense) => (
          <Card className="w-1/3 min-h-20 p-5 border-2 border-amber-400">
            <p>{expense.name}</p>
            <p>{expense.amount}</p>
          </Card>
        ))}
      </div>
      <h2 className="text-center font-bold text-xl">Persons</h2>
      <div className="flex">
        {isLoading
          ? "Loading persons..."
          : persons.length > 0
          ? persons.map((person) => (
              <button
                className="w-1/3"
                onClick={() => handlePersonClick(person)}
              >
                <PersonCard
                  groupPersons={persons}
                  person={person}
                  expenses={debtorsExpenses.filter(
                    (expense) => expense.person_id == person.id
                  )}
                  payedExpenses={expenses}
                  handleAddExpense={handleAddExpense}
                />
              </button>
            ))
          : "No persons for now!"}
      </div>
      {/* Popup modal */}
      {isPopupOpen && (
        <AddExpensePopup
          persons={persons}
          onClose={handleClosePopup}
          onSubmit={handleSubmitExpense}
          clickedPayer={clickedPersonId}
        />
      )}
      {isPersonInfoOpen && (
        <PersonInfo
          isOpen={isPersonInfoOpen}
          handleClosePopup={handleClosePersonInfoPopup}
          activePerson={activePerson!}
          expenses={debtorsExpenses.filter(
            (expense) => expense.person_id == activePerson!.id
          )}
          payedExpenses={expenses}
          groupPersons={persons}
        />
      )}
    </div>
  );
};

export default Group;
