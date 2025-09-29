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
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
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

type SplitType = "equal" | "percentage" | "portion";

interface DebtorWithValue {
  id: string;
  value: number;
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
  const [splitType, setSplitType] = useState<SplitType>("equal");

  // For equal split
  const [selectedDebtors, setSelectedDebtors] = useState<string[]>(
    persons.map((p) => p.id)
  );

  // For percentage and portion splits
  const [debtorsWithValues, setDebtorsWithValues] = useState<DebtorWithValue[]>(
    persons.map((p) => ({ id: p.id, value: 0 }))
  );

  const cancelRef = useRef(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!amount || !payer || !name) {
      return;
    }

    // Prepare debtors based on split type
    let debtors: string[] | DebtorWithValue[];

    if (splitType === "equal") {
      if (selectedDebtors.length === 0) {
        return;
      }
      debtors = selectedDebtors;
    } else {
      // For percentage and portion, filter out zero values
      const activeDebtors = debtorsWithValues.filter((d) => d.value > 0);
      if (activeDebtors.length === 0) {
        return;
      }

      // Validate percentages add up to 100
      if (splitType === "percentage") {
        const totalPercentage = activeDebtors.reduce(
          (sum, d) => sum + d.value,
          0
        );
        if (Math.abs(totalPercentage - 100) > 0.01) {
          alert("Percentages must add up to 100%");
          return;
        }
      }

      debtors = activeDebtors;
    }

    try {
      await onSubmit({
        name,
        amount: parseFloat(amount),
        payerId: payer,
        debtors,
        splitType,
      });
    } catch (error) {
      console.error("Error submitting expense:", error);
    }
  };

  const toggleParticipant = (id: string) => {
    setSelectedDebtors((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    );
  };

  const updateDebtorValue = (id: string, value: number) => {
    setDebtorsWithValues((prev) =>
      prev.map((d) => (d.id === id ? { ...d, value } : d))
    );
  };

  const handleTabChange = (index: number) => {
    const types: SplitType[] = ["equal", "percentage", "portion"];
    setSplitType(types[index]);

    // Reset values when switching to percentage/portion
    if (index > 0) {
      setDebtorsWithValues(persons.map((p) => ({ id: p.id, value: 0 })));
    }
  };

  const getTotalPercentage = () => {
    return debtorsWithValues.reduce((sum, d) => sum + d.value, 0);
  };

  const getTotalPortions = () => {
    return debtorsWithValues.reduce((sum, d) => sum + d.value, 0);
  };

  return (
    <>
      <Modal isOpen={true} onClose={onClose} size="lg">
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

                  <div className="mt-1">
                    <label className="block text-sm font-medium my-2">
                      Amount
                    </label>
                    <NumberInput
                      value={amount}
                      onChange={(valueString) => setAmount(valueString)}
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
                    <label className="block text-sm font-medium mb-3">
                      How to split?
                    </label>
                    <Tabs onChange={handleTabChange} colorScheme="green">
                      <TabList>
                        <Tab>Equal</Tab>
                        <Tab>Percentage</Tab>
                        <Tab>Portions</Tab>
                      </TabList>

                      <TabPanels>
                        {/* Equal Split */}
                        <TabPanel px={0}>
                          <div className="mt-2 space-y-1">
                            {persons.map((person) => (
                              <label
                                key={person.id}
                                className="flex items-center gap-2"
                              >
                                <Checkbox
                                  isChecked={selectedDebtors.includes(
                                    person.id
                                  )}
                                  onChange={() => toggleParticipant(person.id)}
                                />
                                {person.name}
                                {selectedDebtors.includes(person.id) &&
                                  amount && (
                                    <span className="text-sm text-gray-500 ml-auto">
                                      $
                                      {(
                                        parseFloat(amount) /
                                        selectedDebtors.length
                                      ).toFixed(2)}
                                    </span>
                                  )}
                              </label>
                            ))}
                          </div>
                        </TabPanel>

                        {/* Percentage Split */}
                        <TabPanel px={0}>
                          <div className="mt-2 space-y-2">
                            {persons.map((person) => {
                              const debtor = debtorsWithValues.find(
                                (d) => d.id === person.id
                              );
                              return (
                                <div
                                  key={person.id}
                                  className="flex items-center gap-2"
                                >
                                  <span className="flex-1">{person.name}</span>
                                  <NumberInput
                                    size="sm"
                                    value={debtor?.value || 0}
                                    onChange={(valueString) =>
                                      updateDebtorValue(
                                        person.id,
                                        parseFloat(valueString) || 0
                                      )
                                    }
                                    min={0}
                                    max={100}
                                    w="100px"
                                  >
                                    <NumberInputField />
                                    <NumberInputStepper>
                                      <NumberIncrementStepper />
                                      <NumberDecrementStepper />
                                    </NumberInputStepper>
                                  </NumberInput>
                                  <span className="text-sm w-8">%</span>
                                  {debtor && debtor.value > 0 && amount && (
                                    <span className="text-sm text-gray-500 w-20 text-right">
                                      $
                                      {(
                                        (parseFloat(amount) * debtor.value) /
                                        100
                                      ).toFixed(2)}
                                    </span>
                                  )}
                                </div>
                              );
                            })}
                            <div className="mt-2 pt-2 border-t">
                              <span
                                className={`text-sm font-medium ${
                                  Math.abs(getTotalPercentage() - 100) < 0.01
                                    ? "text-green-600"
                                    : "text-red-600"
                                }`}
                              >
                                Total: {getTotalPercentage().toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </TabPanel>

                        {/* Portions Split */}
                        <TabPanel px={0}>
                          <div className="mt-2 space-y-2">
                            {persons.map((person) => {
                              const debtor = debtorsWithValues.find(
                                (d) => d.id === person.id
                              );
                              const totalPortions = getTotalPortions();
                              return (
                                <div
                                  key={person.id}
                                  className="flex items-center gap-2"
                                >
                                  <span className="flex-1">{person.name}</span>
                                  <NumberInput
                                    size="sm"
                                    value={debtor?.value || 0}
                                    onChange={(valueString) =>
                                      updateDebtorValue(
                                        person.id,
                                        parseFloat(valueString) || 0
                                      )
                                    }
                                    min={0}
                                    w="100px"
                                  >
                                    <NumberInputField />
                                    <NumberInputStepper>
                                      <NumberIncrementStepper />
                                      <NumberDecrementStepper />
                                    </NumberInputStepper>
                                  </NumberInput>
                                  <span className="text-sm w-16">portions</span>
                                  {debtor &&
                                    debtor.value > 0 &&
                                    amount &&
                                    totalPortions > 0 && (
                                      <span className="text-sm text-gray-500 w-20 text-right">
                                        $
                                        {(
                                          (parseFloat(amount) * debtor.value) /
                                          totalPortions
                                        ).toFixed(2)}
                                      </span>
                                    )}
                                </div>
                              );
                            })}
                            {getTotalPortions() > 0 && (
                              <div className="mt-2 pt-2 border-t">
                                <span className="text-sm font-medium text-green-600">
                                  Total Portions: {getTotalPortions()}
                                </span>
                              </div>
                            )}
                          </div>
                        </TabPanel>
                      </TabPanels>
                    </Tabs>
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
