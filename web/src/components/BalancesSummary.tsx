import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  HStack,
} from "@chakra-ui/react";
import { Balances } from "../interfaces/Balances";

interface BalancesSummaryProps {
  balances: Balances;
}

const BalancesSummary = ({ balances }: BalancesSummaryProps) => {
  if (!balances || Object.keys(balances).length === 0) {
    return null;
  }

  return (
    <Box>
      <HStack mb={4}>
        <Heading size="md">Balance Summary</Heading>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
        {Object.entries(balances).map(([personId, balanceSummary]) => (
          <Card key={personId} p={4}>
            <Stat>
              <StatLabel>{balanceSummary.name}</StatLabel>
              <StatNumber
                color={balanceSummary.balance >= 0 ? "green.500" : "red.500"}
              >
                {balanceSummary.balance >= 0 ? "+" : "-"}€
                {Math.abs(balanceSummary.balance).toFixed(2)}
              </StatNumber>
              <StatHelpText>
                {balanceSummary.balance >= 0 ? "Should receive" : "Should pay"}
              </StatHelpText>
            </Stat>
          </Card>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default BalancesSummary;
