import { Box, Heading, Text } from "@chakra-ui/react";

interface GroupHeaderProps {
  groupName: string;
  groupId: string;
}

const GroupHeader = ({ groupName, groupId }: GroupHeaderProps) => {
  return (
    <Box textAlign="center">
      <Heading size="xl" mb={2}>
        {groupName}
      </Heading>
      <Text color="gray.500" fontSize="sm">
        Group ID: {groupId}
      </Text>
      <Text color="gray.600" fontSize="sm" mt={1}>
        Share this URL with others to let them join and add expenses
      </Text>
    </Box>
  );
};

export default GroupHeader;
