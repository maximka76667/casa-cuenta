import { DebtorsExpense } from "../interfaces/DebtorsExpense";

/**
 * Calculate the actual dollar amount for a debtor based on split type
 * @param debtor - The debtor expense record (amount field contains raw value)
 * @param totalExpenseAmount - The total expense amount
 * @param allDebtors - All debtors for this expense (needed for portion calculation)
 * @returns The calculated dollar amount
 */
export const calculateDebtorAmount = (
  debtor: DebtorsExpense,
  totalExpenseAmount: number,
  allDebtors?: DebtorsExpense[]
): number => {
  switch (debtor.split_type) {
    case "equal":
      // For equal split, each person has amount = 1
      // Total dollar amount = totalExpenseAmount / number of debtors
      if (!allDebtors || allDebtors.length === 0) return 0;
      return totalExpenseAmount / allDebtors.length;

    case "percentage":
      // amount field contains percentage (e.g., 50 for 50%)
      return (totalExpenseAmount * debtor.amount) / 100;

    case "portion":
      // amount field contains raw portions (e.g., 30, 15, 15)
      if (!allDebtors || allDebtors.length === 0) return 0;
      const totalPortions = allDebtors.reduce((sum, d) => sum + d.amount, 0);
      if (totalPortions === 0) return 0;
      return (totalExpenseAmount * debtor.amount) / totalPortions;

    default:
      return 0;
  }
};

/**
 * Calculate all debtor amounts for an expense
 * @param debtors - All debtors for an expense
 * @param totalExpenseAmount - The total expense amount
 * @returns Map of debtor id to calculated dollar amount
 */
export const calculateAllDebtorAmounts = (
  debtors: DebtorsExpense[],
  totalExpenseAmount: number
): Map<string, number> => {
  const amounts = new Map<string, number>();

  debtors.forEach((debtor) => {
    const amount = calculateDebtorAmount(debtor, totalExpenseAmount, debtors);
    amounts.set(debtor.id, amount);
  });

  return amounts;
};
