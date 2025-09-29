export interface DebtorsExpense {
  id: string;
  expense_id: string;
  person_id: string;
  amount: number; // This now contains raw portions/percentages, not euros amounts
  split_type: string;
  created_at: string;
}
