import axios from "axios";
import { Group } from "../interfaces/Group";
import { Person } from "../interfaces/Person";
import { ExpenseCreate } from "../interfaces/ExpenseCreate";
import { Expense } from "../interfaces/Expense";

const API_BASE_URL = "http://localhost:8000";

export const getAllGroups = async (controller?: AbortController) => {
  const res = await axios.get<{ groups: Group[] }>(`${API_BASE_URL}/groups`, {
    signal: controller?.signal,
  });

  return res.data.groups;
};

export const getGroup = async (
  groupId: string,
  controller?: AbortController
) => {
  const res = await axios.get<Group>(`${API_BASE_URL}/groups/${groupId}`, {
    signal: controller?.signal,
  });

  return res.data;
};

export const getGroupPersons = async (
  groupId: string,
  controller?: AbortController
) => {
  const res = await axios.get<{ persons: Person[] }>(
    `${API_BASE_URL}/groups/${groupId}/persons`,
    {
      signal: controller?.signal,
    }
  );

  return res.data.persons;
};

export const addPerson = async (name: string, groupId: string) => {
  const res = await axios.post(`${API_BASE_URL}/persons`, {
    name: name.trim(),
    group_id: groupId,
  });

  return res.data;
};

export const submitExpense = async (data: ExpenseCreate) => {
  const res = await axios.post(`${API_BASE_URL}/expenses`, {
    name: data.name,
    debtors: data.debtors,
    group_id: data.groupId,
    amount: data.amount,
    payer_id: data.payerId,
  });

  return res.data;
};

export const getExpenses = async (
  groupId: string,
  controller?: AbortController
) => {
  const res = await axios.get<{ expenses: Expense[] }>(
    `${API_BASE_URL}/expenses/${groupId}`,
    {
      signal: controller?.signal,
    }
  );

  return res.data.expenses;
};

export const deleteExpense = async (expenseId: string) => {
  const res = await axios.delete(`${API_BASE_URL}/expenses/${expenseId}`);
  return res.data;
};

export const deletePerson = async (personId: string) => {
  const res = await axios.delete(`${API_BASE_URL}/persons/${personId}`);
  return res.data;
};

export const getDebtors = async (
  groupId: string,
  controller?: AbortController
) => {
  const res = await axios.get(`${API_BASE_URL}/debtors/${groupId}`, {
    signal: controller?.signal,
  });

  return res.data.debtors;
};

export const getGroupBalances = async (
  groupId: string,
  controller?: AbortController
) => {
  const res = await axios.get(`${API_BASE_URL}/groups/${groupId}/balances`, {
    signal: controller?.signal,
  });

  return res.data;
};
