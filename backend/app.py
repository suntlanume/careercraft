from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "careercraft.db"

app = Flask(__name__)
CORS(app)


# -----------------------------
# Database helpers
# -----------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_skills (
        user_id INTEGER NOT NULL,
        skill TEXT NOT NULL,
        UNIQUE(user_id, skill),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS careers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS career_skills (
        career_id INTEGER NOT NULL,
        skill TEXT NOT NULL,
        UNIQUE(career_id, skill),
        FOREIGN KEY(career_id) REFERENCES careers(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS resources (
        skill TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        url TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def seed_data():
    """
    Seeds:
      - 3 careers and required skills
      - simple resources per skill (mock links)
    Safe to run multiple times.
    """
    careers = {
        "ServiceNow Developer": [
            "Troubleshooting", "Creativity", "Scripting", "Configuration", "Integration", "Flexibility"
        ],
        "Biomedical Equipment Technician": [
            "Troubleshooting", "Schematics", "Hardware", "Organization", "Adaptability", "Magnets"
        ],
        "Penguin Counter": [
            "Basic Statistics", "Patience", "Attention to Detail", "Resistance to Cold", "Computer"
        ]
    }

    # Basic “next step” resources for skills 
    resources = {
        "Troubleshooting": ("Root Cause Analysis Basics", "https://example.com/root-cause-analysis"),
        "Creativity": ("Creative Problem Solving Toolkit", "https://example.com/creative-problem-solving"),
        "Scripting": ("Intro to Scripting Concepts", "https://example.com/scripting-intro"),
        "Configuration": ("Configuration Management Overview", "https://example.com/config-management"),
        "Integration": ("API Integration Fundamentals", "https://example.com/api-integration"),
        "Flexibility": ("Working in Agile Environments", "https://example.com/agile-flexibility"),
        "Schematics": ("Reading Technical Schematics", "https://example.com/schematics"),
        "Hardware": ("Hardware Fundamentals", "https://example.com/hardware-fundamentals"),
        "Organization": ("Basic Technical Documentation Skills", "https://example.com/documentation"),
        "Adaptability": ("Adaptability at Work", "https://example.com/adaptability"),
        "Magnets": ("MRI Safety and Magnet Awareness", "https://example.com/mri-safety"),
        "Basic Statistics": ("Statistics for Beginners", "https://example.com/basic-stats"),
        "Patience": ("Developing Focus and Patience", "https://example.com/patience"),
        "Attention to Detail": ("Quality Checking Techniques", "https://example.com/attention-to-detail"),
        "Resistance to Cold": ("Cold Weather Field Readiness", "https://example.com/cold-weather"),
        "Computer": ("Computer Basics Refresher", "https://example.com/computer-basics"),
    }

    conn = get_conn()
    cur = conn.cursor()

    # Insert careers and career skills
    for career_name, skills in careers.items():
        cur.execute("INSERT OR IGNORE INTO careers(name) VALUES (?)", (career_name,))
        cur.execute("SELECT id FROM careers WHERE name = ?", (career_name,))
        career_id = cur.fetchone()["id"]

        for s in skills:
            s_norm = normalize_skill(s)
            cur.execute(
                "INSERT OR IGNORE INTO career_skills(career_id, skill) VALUES (?, ?)",
                (career_id, s_norm)
            )

    # Insert resources
    for skill, (title, url) in resources.items():
        cur.execute(
            "INSERT OR IGNORE INTO resources(skill, title, url) VALUES (?, ?, ?)",
            (normalize_skill(skill), title, url)
        )

    conn.commit()
    conn.close()


def normalize_skill(skill: str) -> str:
    """
    Clean up user input and return consistently formatted version of a skill for storage and comparison
    """
    return " ".join(skill.strip().split()).title()


def get_user_by_username(username: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def get_user_skills(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT skill FROM user_skills WHERE user_id = ? ORDER BY skill ASC", (user_id,))
    skills = [r["skill"] for r in cur.fetchall()]
    conn.close()
    return skills


def compute_recommendations(user_skills, top_n=3):
    """
    Returns ranked career recommendations:
      - score = matched/required
      - matched skills
      - missing skills
      - next steps/resources for missing skills
    """
    user_set = set(user_skills)

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM careers ORDER BY name ASC")
    careers = cur.fetchall()

    results = []
    for c in careers:
        cur.execute("SELECT skill FROM career_skills WHERE career_id = ?", (c["id"],))
        required = [r["skill"] for r in cur.fetchall()]
        required_set = set(required)

        matched = sorted(list(user_set.intersection(required_set)))
        missing = sorted(list(required_set - user_set))

        if len(required) == 0:
            score = 0.0
        else:
            score = len(matched) / len(required)

        # Pull resources for missing skills
        next_steps = []
        for ms in missing:
            cur.execute("SELECT title, url FROM resources WHERE skill = ?", (ms,))
            rr = cur.fetchone()
            if rr:
                next_steps.append({"skill": ms, "title": rr["title"], "url": rr["url"]})
            else:
                next_steps.append({"skill": ms, "title": f"Learn {ms}", "url": "https://example.com"})

        results.append({
            "career": c["name"],
            "score": round(score, 3),
            "matched_skills": matched,
            "missing_skills": missing,
            "next_steps": next_steps
        })

    conn.close()

    # Rank by score desc, then by matched count desc, then by name
    results.sort(key=lambda x: (x["score"], len(x["matched_skills"])), reverse=True)
    return results[:top_n]


# Initialize DB + seed on startup
init_db()
seed_data()


# -----------------------------
# API endpoints
# -----------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"error": "username is required"}), 400

    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO users(username) VALUES (?)", (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"error": "username already exists"}), 409

    user_id = cur.lastrowid
    conn.close()
    return jsonify({"id": user_id, "username": username})


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"error": "username is required"}), 400

    row = get_user_by_username(username)
    if not row:
        return jsonify({"error": "user not found"}), 404

    return jsonify({"id": row["id"], "username": row["username"]})


@app.route("/api/users/<int:user_id>/skills", methods=["GET"])
def list_skills(user_id):
    skills = get_user_skills(user_id)
    return jsonify({"user_id": user_id, "skills": skills})


@app.route("/api/users/<int:user_id>/skills", methods=["POST"])
def add_skill(user_id):
    data = request.get_json(force=True)
    skill = normalize_skill(data.get("skill", ""))

    if not skill:
        return jsonify({"error": "skill is required"}), 400

    # Ensure user exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if not cur.fetchone():
        conn.close()
        return jsonify({"error": "user not found"}), 404

    try:
        cur.execute("INSERT OR IGNORE INTO user_skills(user_id, skill) VALUES (?, ?)", (user_id, skill))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

    conn.close()
    return jsonify({"message": "skill added", "skill": skill})


@app.route("/api/users/<int:user_id>/skills/<path:skill>", methods=["DELETE"])
def delete_skill(user_id, skill):
    skill_norm = normalize_skill(skill)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_skills WHERE user_id = ? AND skill = ?", (user_id, skill_norm))
    conn.commit()
    conn.close()
    return jsonify({"message": "skill removed", "skill": skill_norm})


@app.route("/api/users/<int:user_id>/recommendations", methods=["GET"])
def recommendations(user_id):
    skills = get_user_skills(user_id)
    recs = compute_recommendations(skills, top_n=3)
    return jsonify({
        "user_id": user_id,
        "user_skills": skills,
        "recommendations": recs
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)
