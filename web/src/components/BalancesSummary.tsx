import { Box, Heading, SimpleGrid, Card, Stat, StatLabel, StatNumber, StatHelpText } from "@chakra-ui/react";

interface BalancesSummaryProps {
  balances: any;
}

const BalancesSummary = ({ balances }: BalancesSummaryProps) => {
  if (!balances || Object.keys(balances).length === 0) {
    return null;
  }

  return (
    <Box>
      <Heading size="lg" mb={4}>
        Balance Summary
      </Heading>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
        {Object.entries(balances).map(
          ([personId, balance]: [string, any]) => (
            <Card key={personId} p={4}>
              <Stat>
                <StatLabel>{balance.name}</StatLabel>
                <StatNumber
                  color={balance.balance >= 0 ? "green.500" : "red.500"}
                >
                  {balance.balance >= 0 ? "+" : ""}$
                  {balance.balance.toFixed(2)}
                </StatNumber>
                <StatHelpText>
                  {balance.balance >= 0 ? "Should receive" : "Should pay"}
                </StatHelpText>
              </Stat>
            </Card>
          )
        )}
      </SimpleGrid>
    </Box>
  );
};

export default BalancesSummary;
