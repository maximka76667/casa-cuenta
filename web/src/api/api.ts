import axios from "axios";
import { Group } from "../interfaces/Group";
import { Person } from "../interfaces/Person";
import { Expense } from "../interfaces/ExpenseCreate";

const API_BASE_URL = "http://localhost:8000";

export const getUserGroups = async (
  userId: string,
  controller: AbortController
) => {
  const res = await axios.get<{ groups: Group[] }>(
    `${API_BASE_URL}/users/${userId}/groups`,
    {
      withCredentials: true,
      signal: controller.signal,
    }
  );

  return res.data;
};

export const getGroupPersons = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get<{ persons: Person[] }>(
    `${API_BASE_URL}/groups/${groupId}/persons`,
    {
      withCredentials: true,
      signal: controller.signal,
    }
  );

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
    },
    {
      withCredentials: true,
    }
  );

  return res.data;
};

export const getExpenses = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get(`${API_BASE_URL}/expenses/${groupId}`, {
    withCredentials: true,
    signal: controller.signal,
  });

  return res.data;
};

export const getDebtors = async (
  groupId: string,
  controller: AbortController
) => {
  const res = await axios.get(`${API_BASE_URL}/debtors/${groupId}`, {
    withCredentials: true,
    signal: controller.signal,
  });

  return res.data;
};
