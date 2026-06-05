import { useState, type FormEvent } from "react";

import { useAuth } from "../hooks/useAuth";


export const Auth = () => {
  const { login, register, isLoading, error } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"login" | "register">("login");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    try {
      if (mode === "login") {
        await login(username, password);
        return;
      }

      await register(username, password);
    } catch {}
  };

  return (
    <section className="hud-panel grid min-h-[min(84vh,780px)] w-full content-center p-[clamp(2.4rem,4.4vw,5rem)]">
      <div className="text-center">
        <p className="hud-label text-xl">Smart Presence Coach</p>
        <h1 className="hud-title mt-[1.4vh] text-[clamp(3.4rem,6.2vw,5.8rem)] font-bold leading-none">
          {mode === "login" ? "Welcome Back" : "Create Account"}
        </h1>
        <p className="mt-[2vh] text-[clamp(1.35rem,1.65vw,1.7rem)] font-medium leading-10 text-[#d8f3ff]">
          {mode === "login" ? "Sign in to continue your analysis." : "Create a user to start analyzing sessions."}
        </p>
      </div>

      <form className="mt-[4.5vh] grid gap-[1.6vh]" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          className="hud-input w-full px-6 py-[clamp(1.25rem,2vh,1.7rem)] text-2xl font-medium"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="hud-input w-full px-6 py-[clamp(1.25rem,2vh,1.7rem)] text-2xl font-medium"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="hud-button hud-button-primary w-full px-6 py-[clamp(1.25rem,2vh,1.75rem)] text-2xl disabled:opacity-50"
        >
          {isLoading ? "Loading..." : mode === "login" ? "Login" : "Register"}
        </button>
      </form>

      {error ? (
        <p className="mt-[1.5vh] rounded-md border border-rose-400/40 bg-rose-950/40 px-5 py-4 text-lg text-rose-200">
          {error}
        </p>
      ) : null}

      <button
        type="button"
        onClick={() => setMode((current) => (current === "login" ? "register" : "login"))}
        className="mt-[2.2vh] text-center text-xl font-semibold text-cyan-100 underline"
      >
        {mode === "login" ? "Need an account?" : "Already have an account?"}
      </button>
    </section>
  );
};
