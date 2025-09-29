export interface ExpenseCreate {
  name: string;
  amount: number;
  groupId: string;
  payerId: string;
  debtors: string[];
  splitType: "equal" | "portion" | "percentage";
}

export type ExpenseCreateWithoutGroupId = Omit<ExpenseCreate, "groupId">;
