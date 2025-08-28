import { Person } from "../interfaces/Person";
import { DebtorsExpense } from "../interfaces/DebtorsExpense";
import { Expense } from "../interfaces/Expense";
import {
  Card,
  Heading,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Text,
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

    // sum their amounts
    const totalAmount = relatedDebtors.reduce((sum, d) => sum + d.amount, 0);

    // find payer
    const payer = groupPersons.find((p) => p.id === expense.payer_id);

    // accumulate into result
    if (!acc[expense.payer_id]) {
      acc[expense.payer_id] = {
        amount: 0,
        person: payer ? payer.name : "Unknown",
      };
    }
    if (!activePerson) return;
    if (expense.payer_id == activePerson.id) {
      acc[expense.payer_id].amount -= totalAmount;
    } else {
      acc[expense.payer_id].amount += totalAmount;
    }

    return acc;
  }, {} as Record<string, { amount: number; person: string }>);

  return (
    <Modal isOpen={isOpen} onClose={handleClosePopup}>
      <ModalOverlay />

      <ModalContent
        className={`${
          isOpen ? "flex" : "hidden"
        } absolute top-0 left-0 bg-white min-w-1/2 min-h-full flex-col py-3`}
      >
        <ModalHeader>
          <Text fontSize="2xl" fontWeight="bold">
            Expenses
          </Text>
        </ModalHeader>
        <ModalBody>
          <div className="flex flex-col">
            {expenses.map((expense) => {
              const currentExpense = payedExpenses.find(
                (payedExpense) => payedExpense.id === expense.expense_id
              );

              const payerId = currentExpense?.payer_id;

              return (
                <Card
                  key={expense.id}
                  className="border-b-cyan-600 p-5 border-2 m-1"
                  bgColor="#eee"
                >
                  <Heading fontSize="xl" color="blackAlpha.700">
                    {currentExpense?.name}
                  </Heading>
                  <Text fontSize="xl" fontWeight="bold" className="text-right">
                    {expense.amount.toFixed(2)} €
                  </Text>
                  <Text fontSize="xs" className="text-right">
                    {activePerson!.id === payerId
                      ? "Already payed by this person!"
                      : `To ${
                          groupPersons.find(
                            (groupPerson) => payerId === groupPerson.id
                          )?.name ?? ""
                        }`}
                  </Text>
                </Card>
              );
            })}
          </div>
          <div className="flex flex-col">
            {Object.entries(result).map(
              ([payerId, { amount, person: personName }]) => (
                <div key={payerId} className="border-b-cyan-600 p-5 border-2">
                  {payerId == activePerson!.id ? (
                    "Debts"
                  ) : (
                    <p>To: {personName}</p>
                  )}
                  <p>Amount: {amount}</p>
                </div>
              )
            )}
          </div>
        </ModalBody>
        <ModalFooter>
          <button onClick={handleClosePopup}>Close</button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default PersonInfo;
