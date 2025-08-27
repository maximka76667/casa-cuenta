import { Link, useNavigate } from "react-router-dom";
import { useUserStore } from "../store/userStore";
import { useShallow } from "zustand/shallow";
import { useEffect, useState } from "react";
import { getUserGroups } from "../api/api";
import { Group } from "../interfaces/Group";
import { formatDate } from "../utils/formatDate";
import { Axios } from "axios";

export default function Dashboard() {
  const navigate = useNavigate();
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const { user, clearUser } = useUserStore(
    useShallow((state) => ({
      user: state.user,
      clearUser: state.clearUser,
    }))
  );

  const handleLogout = () => {
    clearUser();
    navigate("/");
  };

  useEffect(() => {
    if (!user) return;

    const controller = new AbortController();

    const fetchGroups = async () => {
      setIsLoading(true);
      try {
        const response = await getUserGroups(user.id, controller);
        setGroups(response.groups);
      } catch (err) {
        console.error("Failed to fetch user groups:", err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGroups();

    return () => {
      controller.abort();
    };
  }, [user]);

  return (
    <div className="dashboard">
      <header>
        <h1>Expense Split Dashboard</h1>
        {user && <p>Welcome, {user.email}</p>}
      </header>

      <main>
        {user ? (
          <div>
            <p>Your expenses, charts, etc.</p>
            <ul>
              {isLoading ? (
                "Loading groups..."
              ) : groups.length > 0 ? (
                groups.map((group) => (
                  <Link to={`/groups/${group.id}`}>
                    <p>{group.name}</p>
                    <p>{formatDate(group.created_at)}</p>
                  </Link>
                ))
              ) : (
                <p>No groups found</p>
              )}
            </ul>
            <button onClick={handleLogout}>Log out</button>
          </div>
        ) : (
          <div>
            <p>Please log in to see your data.</p>
            <Link to="/signin">Login</Link>
            <Link to="/signup">Signup</Link>
          </div>
        )}
      </main>
    </div>
  );
}
