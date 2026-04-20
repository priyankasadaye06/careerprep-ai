import sqlite3

def get_questions(company, skills, difficulty=None):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    skills = [s.lower() for s in skills]

    query = "SELECT question FROM questions WHERE company = ?"
    params = [company]

    # 🔥 Skill filter
    if skills:
        query += f" AND LOWER(skill) IN ({','.join(['?']*len(skills))})"
        params.extend(skills)

    # 🔥 Difficulty filter
    if difficulty and difficulty != "all":
        query += " AND LOWER(difficulty) = ?"
        params.append(difficulty.lower())

    # 🔥 Random + limit
    query += " ORDER BY RANDOM() LIMIT 5"

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    questions = [r[0] for r in results]

    # 🔥 fallback
    if not questions:
        return [
            "Tell me about yourself.",
            "Explain your main project.",
            "What are your strengths?",
            "Explain OOP.",
            "What is SQL?"
        ]

    return questions