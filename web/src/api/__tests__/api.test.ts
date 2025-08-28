import { vi } from "vitest";
import axios from "axios";
import {
  getAllGroups,
  addPerson,
  submitExpense,
  getGroupPersons,
  getExpenses,
} from "../api";

vi.mock("axios");
const mockedAxios = vi.mocked(axios);

describe("API functions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("getAllGroups", () => {
    it("fetches groups successfully", async () => {
      const mockGroups = [{ id: "1", name: "Test Group" }];

      vi.mocked(mockedAxios.get).mockResolvedValue({
        data: { groups: { data: mockGroups } },
      });

      const controller = new AbortController();
      const result = await getAllGroups(controller);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        "http://localhost:8000/groups",
        { signal: controller.signal }
      );
      expect(result).toEqual(mockGroups);
    });
  });

  describe("getGroupPersons", () => {
    it("fetches group persons successfully", async () => {
      const mockPersons = [{ id: "1", name: "John" }];
      vi.mocked(mockedAxios.get).mockResolvedValue({
        data: { persons: mockPersons },
      });

      const controller = new AbortController();
      const result = await getGroupPersons("group1", controller);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        "http://localhost:8000/groups/group1/persons",
        { signal: controller.signal }
      );
      expect(result).toEqual(mockPersons);
    });
  });

  describe("addPerson", () => {
    it("adds person with correct data", async () => {
      const mockResponse = {
        message: "Person added",
        person: { id: "1", name: "John" },
      };
      vi.mocked(mockedAxios.post).mockResolvedValue({ data: mockResponse });

      const result = await addPerson("John", "group1");

      expect(mockedAxios.post).toHaveBeenCalledWith(
        "http://localhost:8000/persons",
        {
          name: "John",
          group_id: "group1",
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it("trims person name before sending", async () => {
      vi.mocked(mockedAxios.post).mockResolvedValue({ data: {} });

      await addPerson("  John  ", "group1");

      expect(mockedAxios.post).toHaveBeenCalledWith(
        "http://localhost:8000/persons",
        {
          name: "John",
          group_id: "group1",
        }
      );
    });
  });

  describe("submitExpense", () => {
    it("submits expense with correct data", async () => {
      const mockExpense = {
        name: "Test Expense",
        amount: 50,
        payerId: "1",
        groupId: "1",
        debtors: ["1", "2"],
      };
      vi.mocked(mockedAxios.post).mockResolvedValue({
        data: { success: true },
      });

      const result = await submitExpense(mockExpense);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        "http://localhost:8000/expenses",
        {
          name: "Test Expense",
          debtors: ["1", "2"],
          group_id: "1",
          amount: 50,
          payer_id: "1",
        }
      );
      expect(result).toEqual({ success: true });
    });
  });

  describe("getExpenses", () => {
    it("fetches expenses for group successfully", async () => {
      const mockExpenses = [{ id: "1", name: "Test Expense", amount: 50 }];
      vi.mocked(mockedAxios.get).mockResolvedValue({
        data: { expenses: { data: mockExpenses } },
      });

      const controller = new AbortController();
      const result = await getExpenses("group1", controller);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        "http://localhost:8000/expenses/group1",
        { signal: controller.signal }
      );
      expect(result).toEqual(mockExpenses);
    });
  });
});
