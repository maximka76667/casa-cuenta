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

type Person = {
  id: string;
  name: string;
};

interface AddExpensePopupProps {
  clickedPayer: string;
  persons: Person[];
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    amount: number;
    payerId: string;
    debtors: string[];
  }) => void;
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
    if (!amount || !payer || debtors.length === 0 || !name) return;

    await onSubmit({
      name,
      amount: parseFloat(amount),
      payerId: payer,
      debtors,
    });

    onClose();
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
            <ModalHeader fontSize="lg" fontWeight="bold">
              Add Expense
            </ModalHeader>

            <ModalBody>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium my-2">Name</label>
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
                          type="checkbox"
                          checked={debtors.includes(person.id)}
                          onChange={() => toggleParticipant(person.id)}
                        />
                        {person.name}
                      </label>
                    ))}
                  </div>
                </div>
              </form>
            </ModalBody>

            <ModalFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="green" onClick={handleSubmit} ml={3}>
                Submit
              </Button>
            </ModalFooter>
          </ModalContent>
        </ModalOverlay>
      </Modal>
      {/* <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center">
        <div className="bg-white p-6 rounded-2xl shadow-lg w-96">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium">Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 block w-full border rounded-md p-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Amount</label>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="mt-1 block w-full border rounded-md p-2"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium">Who pays?</label>
              <select
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
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium">Who shares?</label>
              <div className="mt-2 space-y-1">
                {persons.map((person) => (
                  <label key={person.id} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={debtors.includes(person.id)}
                      onChange={() => toggleParticipant(person.id)}
                    />
                    {person.name}
                  </label>
                ))}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-4">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-md border"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-md"
              >
                Add
              </button>
            </div>
          </form>
        </div>
      </div> */}
    </>
  );
}
