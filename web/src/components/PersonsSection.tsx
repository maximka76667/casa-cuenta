import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Card,
  VStack,
  Badge,
  Button,
  IconButton,
  HStack,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";
import { Person } from "../interfaces/Person";
import { Balances } from "../interfaces/Balances";

interface PersonsListProps {
  persons: Person[];
  balances: Balances;
  onPersonClick: (person: Person) => void;
  onAddExpense: (personId: string) => void;
  onDeletePerson: (personId: string) => void;
}

const PersonsList = ({
  persons,
  balances,
  onPersonClick,
  onAddExpense,
  onDeletePerson,
}: PersonsListProps) => {
  return (
    <Box>
      <HStack mb={4}>
        <Heading size="md">People</Heading>
        <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
          {persons.length} person{persons.length !== 1 ? "s" : ""}
        </Badge>
      </HStack>
      {persons.length === 0 ? (
        <Text color="gray.500" textAlign="center" py={8}>
          No people in this group yet. Add someone above to get started!
        </Text>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
          {persons.map((person) => (
            <Card
              key={person.id}
              p={4}
              cursor="pointer"
              _hover={{
                shadow: "md",
                transform: "translateY(-2px)",
                transition: "all 0.2s",
              }}
              onClick={() => onPersonClick(person)}
              position="relative"
            >
              <HStack justify="space-between" align="start">
                <VStack spacing={2} flex={1}>
                  <Text fontWeight="bold">{person.name}</Text>
                  {balances && balances[person.id] && (
                    <VStack spacing={1}>
                      <Text fontSize="sm" color="gray.600">
                        Paid: €{balances[person.id].paid.toFixed(2)}
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        Owes: €{balances[person.id].owes.toFixed(2)}
                      </Text>
                      <Badge
                        colorScheme={
                          balances[person.id].balance >= 0 ? "green" : "red"
                        }
                      >
                        {balances[person.id].balance >= 0 ? "+" : "-"}€
                        {Math.abs(balances[person.id].balance).toFixed(2)}
                      </Badge>
                    </VStack>
                  )}
                  <Button
                    size="sm"
                    colorScheme="blue"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAddExpense(person.id);
                    }}
                  >
                    Add Expense
                  </Button>
                </VStack>
                <IconButton
                  aria-label="Delete person"
                  icon={<DeleteIcon />}
                  size="sm"
                  colorScheme="red"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeletePerson(person.id);
                  }}
                  position="absolute"
                  top={2}
                  right={2}
                />
              </HStack>
            </Card>
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
};

export default PersonsList;
