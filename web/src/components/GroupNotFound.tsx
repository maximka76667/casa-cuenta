import { Button, Container, Text, VStack } from "@chakra-ui/react";
import { Link } from "react-router-dom";

const GroupNotFound = () => {
  return (
    <Container maxW="6xl" py={8}>
      <VStack spacing={4}>
        <Text textAlign="center" color="red.500">
          Group not found. Please check the group ID.
        </Text>
        <Link to="/">
          <Button colorScheme="blue">Go Home</Button>
        </Link>
      </VStack>
    </Container>
  );
};

export default GroupNotFound;
