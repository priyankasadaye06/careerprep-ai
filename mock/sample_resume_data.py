# mock/sample_resume_data.py

def get_sample_resume_data():
    return {
        "name": "Charles Bloomberg",
        "email": "charlesbloomberg@gmail.com",
        "phone": "+1 012 637 5053",
        "linkedin": "linkedin.com/in/cbloomberg",
        "github": "github.com/cbloomberg",
        "summary": "Software engineer with 3+ years of experience in designing scalable backend systems and cloud-native applications.",

        "role": "Software Engineer",

        "education": [
            {
                "degree": "Master of Engineering, Computer Science",
                "college": "MIT",
                "year": "2017",
                "cgpa": "9.1"
            },
            {
                "degree": "Bachelor of Engineering, Computer Science",
                "college": "MIT",
                "year": "2015",
                "cgpa": "8.9"
            }
        ],

        "skills": {
            "languages": "Python, Go, C, JavaScript",
            "frameworks": "Django, Flask, React",
            "tools": "Docker, Kubernetes, Git, Helm",
            "databases": "MySQL, Redis, ElasticSearch",
            "soft": "Problem Solving, Communication"
        },

        "experience": [
            {
                "role": "Software Engineer",
                "company": "Company A",
                "duration": "Mar 2020 – Present",
                "location": "New York, NY",
                "points": [
                    "Designed REST APIs serving 4M+ users",
                    "Reduced API latency by 40% using caching",
                    "Deployed services on Kubernetes clusters"
                ]
            },
            {
                "role": "DevOps Engineer",
                "company": "Company B",
                "duration": "Jan 2019 – Feb 2020",
                "location": "New York, NY",
                "points": [
                    "Managed Kubernetes clusters with 500+ nodes",
                    "Implemented CI/CD pipelines using GitHub Actions"
                ]
            }
        ],

        "projects": [
            {
                "title": "AI Resume Builder",
                "tech": "Flask, LangChain, HTML, CSS",
                "points": [
                    "Built ATS-friendly resume generator",
                    "Integrated role-based resume customization"
                ]
            }
        ],

        "certifications": [
            "AWS Certified Solutions Architect",
            "Google Professional Cloud Engineer"
        ]
    }