export interface Expense {
  id: string;
  name: string;
  amount: number;
  group_id: string;
  payer_id: string;
  debtors: string[];
}
