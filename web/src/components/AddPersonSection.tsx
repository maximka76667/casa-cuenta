import { Button, Card, Heading, HStack, Input, VStack } from "@chakra-ui/react";
import React, { useState } from "react";
import { useNotifications } from "../hooks/useNotifications";

interface AddPersonSectionProps {
  groupId: string;
  onPersonsChange: (newPersonName: string) => void;
}

const AddPersonSection = ({
  onPersonsChange,
  groupId,
}: AddPersonSectionProps) => {
  // Add person state
  const [newPersonName, setNewPersonName] = useState("");
  const [isAddingPerson, setIsAddingPerson] = useState(false);

  const { showError } = useNotifications();

  const handleAddPerson = async () => {
    if (!newPersonName.trim() || !groupId) {
      showError({
        title: "Error",
        description: "Please enter a person's name",
      });
      return;
    }

    setIsAddingPerson(true);

    await onPersonsChange(newPersonName);

    setIsAddingPerson(false);
    setNewPersonName("");
  };

  return (
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
  );
};

export default AddPersonSection;
