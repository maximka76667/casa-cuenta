import { Card, VStack, Heading, HStack, Input, Button } from "@chakra-ui/react";

interface AddPersonFormProps {
  newPersonName: string;
  setNewPersonName: (name: string) => void;
  onAddPerson: () => void;
  isAddingPerson: boolean;
}

const AddPersonForm = ({
  newPersonName,
  setNewPersonName,
  onAddPerson,
  isAddingPerson,
}: AddPersonFormProps) => {
  return (
    <Card p={4}>
      <VStack spacing={3}>
        <Heading size="md">Add Person to Group</Heading>
        <HStack w="100%">
          <Input
            placeholder="Enter person's name"
            value={newPersonName}
            onChange={(e) => setNewPersonName(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && onAddPerson()}
          />
          <Button
            colorScheme="green"
            onClick={onAddPerson}
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

export default AddPersonForm;
