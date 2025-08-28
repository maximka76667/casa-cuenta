import { PersonFinancials } from "./PersonFinancials";

export interface Balances {
  [personId: string]: PersonFinancials;
}
