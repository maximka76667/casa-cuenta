import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Button, 
  Input, 
  VStack, 
  Heading, 
  Text, 
  Container, 
  Box, 
  useToast,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Spinner,
  HStack,
  Badge,
  Divider
} from "@chakra-ui/react";
import axios from "axios";
import { getAllGroups } from "../api/api";
import { Group } from "../interfaces/Group";

const API_BASE_URL = "http://localhost:8000";

const Home = () => {
  const [groupName, setGroupName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoadingGroups, setIsLoadingGroups] = useState(true);
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    const controller = new AbortController();
    
    const fetchGroups = async () => {
      try {
        const groupsData = await getAllGroups(controller);
        setGroups(groupsData);
      } catch (error) {
        if (!controller.signal.aborted) {
          console.error("Error fetching groups:", error);
          toast({
            title: "Error",
            description: "Failed to load groups",
            status: "error",
            duration: 3000,
            isClosable: true,
            position: "top",
          });
        }
      } finally {
        setIsLoadingGroups(false);
      }
    };

    fetchGroups();

    return () => {
      controller.abort();
    };
  }, [toast]);

  const createGroup = async () => {
    if (!groupName.trim()) {
      toast({
        title: "Error",
        description: "Please enter a group name",
        status: "error",
        duration: 3000,
        isClosable: true,
        position: "top",
      });
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/groups`, {
        name: groupName.trim(),
      });

      const group = response.data.group[0];
      toast({
        title: "Success",
        description: `Group "${group.name}" created successfully!`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "top",
      });

      // Refresh the groups list
      const controller = new AbortController();
      try {
        const groupsData = await getAllGroups(controller);
        setGroups(groupsData);
      } catch (error) {
        console.error("Error refreshing groups:", error);
      }

      // Clear the input
      setGroupName("");

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
        position: "top",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const joinGroup = (groupId: string) => {
    navigate(`/groups/${groupId}`);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <Container maxW="4xl" py={10}>
      <VStack spacing={8} w="100%">
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            Welcome to Casa Cuenta
          </Heading>
          <Text color="gray.600" fontSize="lg">
            Split expenses easily with friends and family
          </Text>
        </Box>

        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8} w="100%">
          {/* Create New Group Section */}
          <Box p={6} borderWidth={1} borderRadius="lg" shadow="md">
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

          {/* Existing Groups Section */}
          <Box p={6} borderWidth={1} borderRadius="lg" shadow="md">
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Heading size="md">Available Groups</Heading>
                <Badge colorScheme="blue" variant="subtle">
                  {groups.length} groups
                </Badge>
              </HStack>
              
              {isLoadingGroups ? (
                <Box textAlign="center" py={4}>
                  <Spinner size="md" />
                  <Text mt={2} color="gray.500">Loading groups...</Text>
                </Box>
              ) : groups.length === 0 ? (
                <Box textAlign="center" py={4}>
                  <Text color="gray.500">No groups available yet</Text>
                  <Text fontSize="sm" color="gray.400">
                    Create the first group to get started!
                  </Text>
                </Box>
              ) : (
                <VStack spacing={3} maxH="300px" overflowY="auto">
                  {groups.map((group) => (
                    <Card key={group.id} w="100%" size="sm" cursor="pointer" 
                          _hover={{ shadow: "md", transform: "translateY(-1px)" }}
                          transition="all 0.2s"
                          onClick={() => joinGroup(group.id)}>
                      <CardBody>
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="semibold" fontSize="md">
                            {group.name}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            Created {formatDate(group.created_at)}
                          </Text>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              )}
            </VStack>
          </Box>
        </SimpleGrid>

        <Box textAlign="center" color="gray.500">
          <Text fontSize="sm">
            No signup required! Create a group or join an existing one to start splitting expenses.
          </Text>
        </Box>
      </VStack>
    </Container>
  );
};

export default Home;
