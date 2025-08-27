import axios from "axios";
import { Group } from "../interfaces/Group";
import { Person } from "../interfaces/Person";
import { Expense } from "../interfaces/ExpenseCreate";

const API_BASE_URL = "http://localhost:8000";

export const getAllGroups = async (controller: AbortController) => {
  const res = await axios.get<{ groups: { data: Group[] } }>(
    `${API_BASE_URL}/groups`,
    {
      signal: controller.signal,
    }
  );

  return res.data.groups.data;
};

export const getGroup = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get<Group>(
    `${API_BASE_URL}/groups/${groupId}`,
    {
      signal: controller.signal,
    }
  );

  return res.data;
};

export const getGroupPersons = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get<Person[]>(
    `${API_BASE_URL}/groups/${groupId}/persons`,
    {
      signal: controller.signal,
    }
  );

  return res.data;
};

export const addPerson = async (name: string, groupId: string) => {
  const res = await axios.post(`${API_BASE_URL}/persons`, {
    name: name.trim(),
    group_id: groupId,
  });

  return res.data;
};

export const submitExpense = async (data: Expense) => {
  console.log(data);
  const res = await axios.post(
    `${API_BASE_URL}/expenses`,
    {
      name: data.name,
      debtors: data.debtors,
      group_id: data.groupId,
      amount: data.amount,
      payer_id: data.payerId,
    }
  );

  return res.data;
};

export const getExpenses = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get<Expense[]>(`${API_BASE_URL}/expenses/${groupId}`, {
    signal: controller.signal,
  });

  return res.data;
};

export const deleteExpense = async (expenseId: string) => {
  const res = await axios.delete(`${API_BASE_URL}/expenses/${expenseId}`);
  return res.data;
};

export const getDebtors = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get(`${API_BASE_URL}/debtors/${groupId}`, {
    signal: controller.signal,
  });

  return res.data;
};

export const getGroupBalances = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get(`${API_BASE_URL}/groups/${groupId}/balances`, {
    signal: controller.signal,
  });

  return res.data;
};
