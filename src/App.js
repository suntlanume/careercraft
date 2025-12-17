import React, { useState } from "react";
import LoginPage from "./LoginPage";
import DashboardPage from "./DashboardPage";

export default function App() {
  const [user, setUser] = useState(null);

  const onLogout = () => setUser(null);

  return (
    <>
      {!user ? (
        <LoginPage onLogin={setUser} />
      ) : (
        <DashboardPage user={user} onLogout={onLogout} />
      )}
    </>
  );
}
