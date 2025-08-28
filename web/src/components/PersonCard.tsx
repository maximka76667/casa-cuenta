import React, { MouseEventHandler, useState, useMemo } from "react";
import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import {
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Heading,
  Text,
} from "@chakra-ui/react";

interface PersonCardProps {
  person: Person;
  expenses: DebtorsExpense[];
  payedExpenses: Expense[];
  handleAddExpense: (data: string) => void;
}

const PersonCard = React.memo(({
  person,
  expenses,
  payedExpenses,
  handleAddExpense,
}: PersonCardProps) => {
  const defaultToPay = useMemo(() => 
    expenses.reduce((sum, expense) => (sum += expense.amount), 0),
    [expenses]
  );

  const defaultPayed = useMemo(() => 
    payedExpenses
      .filter((e) => e.payer_id == person.id)
      .reduce((sum, expense) => (sum += expense.amount), 0),
    [payedExpenses, person.id]
  );

  const [total, setTotal] = useState(defaultToPay - defaultPayed);

  // Step 1: create lookup for expense_id -> payer_id
  const expenseToPayer: Record<string, string> = {};
  for (const exp of payedExpenses) {
    expenseToPayer[exp.id] = exp.payer_id;
  }

  const handleAddExpenseClick: MouseEventHandler<HTMLButtonElement> = (e) => {
    e.stopPropagation();
    handleAddExpense(person.id);
  };

  return (
    <Card className="min-h-10 p-5 text-center m-2">
      <CardHeader>
        <Heading fontSize="2xl">{person.name}</Heading>
        <Text fontSize="xs" color="GrayText">
          {person.id}
        </Text>
      </CardHeader>
      <CardBody>
        <button className="w-full" onClick={handleAddExpenseClick}>
          +
        </button>
      </CardBody>
      <CardFooter>
        <Text className="text-center w-full">Total: {total}</Text>
      </CardFooter>
    </Card>
  );
});

export default PersonCard;
