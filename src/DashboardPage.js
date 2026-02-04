import React, { useEffect, useState } from "react";
import { api } from "./api";

export default function DashboardPage({ user, onLogout }) {
  const [skillInput, setSkillInput] = useState("");
  const [skills, setSkills] = useState([]);
  const [recs, setRecs] = useState([]);
  const [message, setMessage] = useState("");

  const loadSkills = async () => {
    const res = await api.get(`/users/${user.id}/skills`);
    setSkills(res.data.skills);
  };

  useEffect(() => {
    loadSkills().catch(() => setMessage("Could not load skills"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const addSkill = async () => {
    setMessage("");
    const skill = skillInput.trim();
    if (!skill) return;

    try {
      await api.post(`/users/${user.id}/skills`, { skill });
      setSkillInput("");
      await loadSkills();
    } catch (err) {
      if (err?.response?.status === 409){
        setMessage("That skill is already saved to your profile.");
        return;
      }
      const msg = err?.response?.data?.error || "Add skill failed";
      setMessage(msg);
    }
  };

  const removeSkill = async (skill) => {
    setMessage("");
    try {
      await api.delete(`/users/${user.id}/skills/${encodeURIComponent(skill)}`);
      await loadSkills();
    } catch (err) {
      setMessage("Remove skill failed");
    }
  };

  const getRecommendations = async () => {
    setMessage("");
    try {
      const res = await api.get(`/users/${user.id}/recommendations`);
      setRecs(res.data.recommendations);
    } catch (err) {
      setMessage("Recommendation request failed");
    }
  };

  return (
    <div style={{ maxWidth: 760, margin: "40px auto", fontFamily: "Arial" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2>Welcome, {user.username}</h2>
        <button onClick={onLogout}>Logout</button>
      </div>

      <h3>Add Skills</h3>
      <div style={{ display: "flex", gap: 10 }}>
        <input
          style={{ flex: 1, padding: 10 }}
          value={skillInput}
          onChange={(e) => setSkillInput(e.target.value)}
          placeholder="Type one skill and click Add"
        />
        <button onClick={addSkill}>Add</button>
      </div>

      {message && <p style={{ marginTop: 10 }}>{message}</p>}

      <h4 style={{ marginTop: 22 }}>Saved Skills</h4>
      {skills.length === 0 ? (
        <p>No skills added yet.</p>
      ) : (
        <ul>
          {skills.map((s) => (
            <li key={s} style={{ marginBottom: 6 }}>
              {s}{" "}
              <button onClick={() => removeSkill(s)} style={{ marginLeft: 10 }}>
                remove
              </button>
            </li>
          ))}
        </ul>
      )}

      <hr style={{ margin: "28px 0" }} />

      <h3>Recommendations</h3>
      <button onClick={getRecommendations}>Generate Recommendations</button>

      {recs.length > 0 && (
        <div style={{ marginTop: 18 }}>
          {recs.map((r) => (
            <div key={r.career} style={{ padding: 14, border: "1px solid #ccc", marginBottom: 12 }}>
              <h4 style={{ margin: 0 }}>{r.career}</h4>
              <p style={{ margin: "8px 0" }}>
                <strong>Score:</strong> {r.score}
              </p>
              <p style={{ margin: "8px 0" }}>
                <strong>Matched:</strong> {r.matched_skills.join(", ") || "None"}
              </p>
              <p style={{ margin: "8px 0" }}>
                <strong>Missing:</strong> {r.missing_skills.join(", ") || "None"}
              </p>

              {r.next_steps?.length > 0 && (
                <>
                  <p style={{ margin: "10px 0 6px 0" }}><strong>Next steps:</strong></p>
                  <ul>
                    {r.next_steps.slice(0, 3).map((ns) => (
                      <li key={ns.skill}>
                        {ns.skill}:{" "}                       
                         <a href={ns.url} target="_blank" rel="noreferrer">
                          {ns.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
