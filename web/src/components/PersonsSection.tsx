import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Card,
  VStack,
  Badge,
  Button,
} from "@chakra-ui/react";
import { Person } from "../interfaces/Person";
import { Balances } from "../interfaces/Balances";

interface PersonsListProps {
  persons: Person[];
  balances: Balances;
  onPersonClick: (person: Person) => void;
  onAddExpense: (personId: string) => void;
}

const PersonsList = ({
  persons,
  balances,
  onPersonClick,
  onAddExpense,
}: PersonsListProps) => {
  return (
    <Box>
      <Heading size="lg" mb={4}>
        People ({persons.length})
      </Heading>
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
              onClick={() => onPersonClick(person)}
            >
              <VStack spacing={2}>
                <Text fontWeight="bold">{person.name}</Text>
                {balances && balances[person.id] && (
                  <VStack spacing={1}>
                    <Text fontSize="sm" color="gray.600">
                      Paid: ${balances[person.id].paid.toFixed(2)}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      Owes: ${balances[person.id].owes.toFixed(2)}
                    </Text>
                    <Badge
                      colorScheme={
                        balances[person.id].balance >= 0 ? "green" : "red"
                      }
                    >
                      {balances[person.id].balance >= 0 ? "+" : ""}$
                      {balances[person.id].balance.toFixed(2)}
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
            </Card>
          ))}
        </SimpleGrid>
      )}
    </Box>
  );
};

export default PersonsList;
