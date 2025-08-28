import {
  Button,
  Checkbox,
  Input,
  Modal,
  ModalBody,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Select,
} from "@chakra-ui/react";
import { useRef, useState } from "react";
import { ExpenseCreateWithoutGroupId } from "../interfaces/ExpenseCreate";
import { Person } from "../interfaces/Person";

interface AddExpensePopupProps {
  clickedPayer: string;
  persons: Person[];
  onClose: () => void;
  onSubmit: (data: ExpenseCreateWithoutGroupId) => void;
}

export default function AddExpensePopup({
  clickedPayer,
  persons,
  onClose,
  onSubmit,
}: AddExpensePopupProps) {
  const [name, setName] = useState("");
  const [amount, setAmount] = useState("");
  const [payer, setPayer] = useState(clickedPayer);

  const [debtors, setDebtors] = useState<string[]>(persons.map((p) => p.id));

  const cancelRef = useRef(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!amount || !payer || debtors.length === 0 || !name) {
      return;
    }

    try {
      await onSubmit({
        name,
        amount: parseFloat(amount),
        payerId: payer,
        debtors,
      });
      // onClose() is now called from the parent component after successful submission
    } catch (error) {
      console.error("Error submitting expense:", error);
    }
  };

  const toggleParticipant = (id: string) => {
    setDebtors((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  return (
    <>
      <Modal isOpen={true} onClose={onClose}>
        <ModalOverlay>
          <ModalContent>
            <form onSubmit={handleSubmit}>
              <ModalHeader fontSize="lg" fontWeight="bold">
                Add Expense
              </ModalHeader>

              <ModalBody>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium my-2">
                      Name
                    </label>
                    <Input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="mt-1 block w-full border rounded-md p-2"
                      required
                    />
                  </div>

                  <div className="mt-1 ">
                    <label className="block text-sm font-medium my-2">
                      Amount
                    </label>
                    <NumberInput
                      value={amount}
                      onChange={(valueString) => setAmount(valueString)}
                      // className="mt-1 block w-full border rounded-md p-2"
                    >
                      <NumberInputField />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </div>

                  <div>
                    <label className="block text-sm font-medium my-2">
                      Who pays?
                    </label>
                    <Select
                      value={payer}
                      onChange={(e) => setPayer(e.target.value)}
                      className="mt-1 block w-full border rounded-md p-2"
                      required
                    >
                      <option value="">Select</option>
                      {persons.map((person) => (
                        <option key={person.id} value={person.id}>
                          {person.name}
                        </option>
                      ))}
                    </Select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium">
                      Who shares?
                    </label>
                    <div className="mt-2 space-y-1">
                      {persons.map((person) => (
                        <label
                          key={person.id}
                          className="flex items-center gap-2"
                        >
                          <Checkbox
                            isChecked={debtors.includes(person.id)}
                            onChange={() => toggleParticipant(person.id)}
                          />
                          {person.name}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </ModalBody>

              <ModalFooter>
                <Button ref={cancelRef} onClick={onClose}>
                  Cancel
                </Button>
                <Button colorScheme="green" type="submit" ml={3}>
                  Submit
                </Button>
              </ModalFooter>
            </form>
          </ModalContent>
        </ModalOverlay>
      </Modal>
    </>
  );
}
