export interface ExpenseCreate {
  name: string;
  amount: number;
  groupId: string;
  payerId: string;
  debtors: string[];
}
