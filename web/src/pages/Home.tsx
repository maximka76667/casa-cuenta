import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Input, VStack, Heading, Text, Container, Box, useToast } from "@chakra-ui/react";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

const Home = () => {
  const [groupName, setGroupName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const toast = useToast();

  const createGroup = async () => {
    if (!groupName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a group name",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/groups`, {
        name: groupName.trim(),
      });

      const group = response.data;
      toast({
        title: "Success",
        description: `Group "${group.name}" created successfully!`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });

      // Navigate to the group page
      navigate(`/groups/${group.id}`);
    } catch (error) {
      console.error("Error creating group:", error);
      toast({
        title: "Error",
        description: "Failed to create group. Please try again.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="md" centerContent py={10}>
      <VStack spacing={6} w="100%">
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            Welcome to Casa Cuenta
          </Heading>
          <Text color="gray.600" fontSize="lg">
            Split expenses easily with friends and family
          </Text>
        </Box>

        <Box w="100%" p={6} borderWidth={1} borderRadius="lg" shadow="md">
          <VStack spacing={4}>
            <Heading size="md">Create a New Group</Heading>
            <Input
              placeholder="Enter group name (e.g., 'Weekend Trip', 'Roommates')"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && createGroup()}
            />
            <Button
              colorScheme="blue"
              size="lg"
              w="100%"
              onClick={createGroup}
              isLoading={isLoading}
              loadingText="Creating..."
            >
              Create Group
            </Button>
          </VStack>
        </Box>

        <Box textAlign="center" color="gray.500">
          <Text fontSize="sm">
            No signup required! Share the group link with others to start splitting expenses.
          </Text>
        </Box>
      </VStack>
    </Container>
  );
};

export default Home;
