def get_role_based_bullets(role):
    bullets = {
        "Software Engineer": [
            "Designed scalable RESTful APIs following best practices",
            "Applied data structures and algorithms to optimize performance",
            "Worked on modular, maintainable backend architecture"
        ],

        "Data Analyst": [
            "Analyzed large datasets to extract actionable insights",
            "Built interactive dashboards for business decision-making",
            "Used SQL queries to optimize reporting workflows"
        ],

        "ML Engineer": [
            "Trained and evaluated machine learning models",
            "Performed feature engineering and model optimization",
            "Deployed ML models using Flask-based APIs"
        ],

        "Web Developer": [
            "Developed responsive UI using modern frontend technologies",
            "Integrated backend APIs with frontend components",
            "Ensured cross-browser compatibility and performance"
        ]
    }

    return bullets.get(role, [])