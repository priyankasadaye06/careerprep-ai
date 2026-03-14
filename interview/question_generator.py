def generate_questions(skills):

    question_bank = {
        "python": [
            "Explain Python decorators.",
            "What are Python generators?",
            "Difference between list and tuple."
        ],

        "sql": [
            "Explain SQL joins.",
            "What is indexing in SQL?",
            "Difference between WHERE and HAVING."
        ],

        "machine learning": [
            "Explain supervised vs unsupervised learning.",
            "What is overfitting?",
            "Explain model evaluation metrics."
        ],

        "flask": [
            "What is Flask?",
            "Explain routing in Flask.",
            "Difference between Flask and Django."
        ],

        "javascript": [
            "Explain closures in JavaScript.",
            "What is event loop?",
            "Difference between var, let, const."
        ]
    }

    questions = []

    for skill in skills:
        if skill in question_bank:
            questions.extend(question_bank[skill])

    if len(questions) == 0:
        questions = [
            "Tell me about yourself.",
            "Explain your main project.",
            "What challenges did you face?"
        ]

    return questions[:8]