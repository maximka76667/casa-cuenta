// src/pages/SignIn.tsx
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signin } from "../api/auth";
import { Button, Description, Field, Input, Label } from "@headlessui/react";
import clsx from "clsx";

export default function SignIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSignIn(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await signin(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "0 auto" }}>
      <h1>Sign In</h1>
      <form className="flex justify-center flex-col" onSubmit={handleSignIn}>
        <Field>
          <Label className="text-sm/6 font-medium text-black">Email</Label>

          <Input
            onChange={(e) => setEmail(e.target.value)}
            type="email"
            placeholder="Email"
            value={email}
            required
            className={clsx(
              "mt-1.5 mb-3 block w-full rounded-lg border-none bg-black/5 px-3 py-1.5 text-sm/6 text-black",
              "focus:not-data-focus:outline-none data-focus:outline-2 data-focus:-outline-offset-2 data-focus:outline-black/25"
            )}
          />
        </Field>
        <Field>
          <Label className="text-sm/6 font-medium text-black">Password</Label>

          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className={clsx(
              "mt-1.5 mb-3 block w-full rounded-lg border-none bg-black/5 px-3 py-1.5 text-sm/6 text-black",
              "focus:not-data-focus:outline-none data-focus:outline-2 data-focus:-outline-offset-2 data-focus:outline-black/25"
            )}
          />
        </Field>

        <Button
          className="rounded bg-green-600 px-4 py-2 text-sm text-white data-active:bg-green-700 data-hover:bg-green-500"
          disabled={loading}
          type="submit"
        >
          {loading ? "Signing in..." : "Sign In"}
        </Button>

        {error && <p style={{ color: "red" }}>{error}</p>}
      </form>
      <p>
        No account? <Link to="/signup">Sign Up</Link>
      </p>
    </div>
  );
}
