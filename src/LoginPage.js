import React, { useState } from "react";
import { api } from "./api";

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [message, setMessage] = useState("");

  const createProfile = async () => {
    setMessage("");
    try {
      const res = await api.post("/users", { username });
      onLogin(res.data); // {id, username}
    } catch (err) {
      const msg = err?.response?.data?.error || "Create failed";
      setMessage(msg);
    }
  };

  const login = async () => {
    setMessage("");
    try {
      const res = await api.post("/login", { username });
      onLogin(res.data); // {id, username}
    } catch (err) {
      const msg = err?.response?.data?.error || "Login failed";
      setMessage(msg);
    }
  };

  return (
    <div style={{ maxWidth: 520, margin: "40px auto", fontFamily: "Arial" }}>
      <h1>CareerCraft</h1>
      <p>Create a profile or log in, then add skills to get recommendations.</p>

      <label>Username</label>
      <input
        style={{ width: "100%", padding: 10, marginTop: 6, marginBottom: 12 }}
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Enter username"
      />

      <div style={{ display: "flex", gap: 10 }}>
        <button onClick={createProfile}>Create Profile</button>
        <button onClick={login}>Login</button>
      </div>

      {message && <p style={{ marginTop: 12 }}>{message}</p>}
    </div>
  );
}
