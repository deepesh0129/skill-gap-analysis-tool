"""
career_data.py
----------------
Static knowledge base used by the Career Requirement Agent (Agent 2).

Each role stores its required skills as a dict of {skill: weight}.
Weight (1-5) represents how critical that skill is for the role, and is
used later by the Skill Gap Agent / Recommendation Agent to prioritize
what a student should learn next (not just "how many skills are missing"
but "which missing skills matter most").
"""

DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Electronics & Communication",
    "Mechanical Engineering",
    "Business Administration",
    "Statistics / Mathematics",
    "Other",
]

STATUS_OPTIONS = ["Student", "Intern", "Fresher / Job Seeker", "Working Professional"]

CAREER_ROLES = {
    "Data Analyst": {
        "skills": {
            "Excel": 4, "SQL": 5, "Python": 4, "Statistics": 4,
            "Data Visualization": 5, "Power BI": 4, "Tableau": 3,
            "Pandas": 4, "Communication": 3, "A/B Testing": 2,
        },
        "projects": {
            "beginner": ["Sales data cleaning & visualization in Excel/Power BI",
                         "SQL queries on a retail database"],
            "intermediate": ["End-to-end dashboard (Power BI) on public dataset",
                              "Exploratory Data Analysis with Pandas & Seaborn"],
            "advanced": ["A/B testing framework for a product decision",
                         "Automated reporting pipeline (Python + Power BI + SQL)"],
        },
        "certifications": ["Google Data Analytics Certificate", "Microsoft PL-300 (Power BI)",
                            "SQL for Data Science (Coursera)"],
    },
    "Data Scientist": {
        "skills": {
            "Python": 5, "Statistics": 5, "Machine Learning": 5, "SQL": 4,
            "Pandas": 4, "NumPy": 3, "Scikit-learn": 4, "Deep Learning": 3,
            "Data Visualization": 3, "Communication": 3, "MLOps": 2,
        },
        "projects": {
            "beginner": ["Titanic / house price prediction with Scikit-learn",
                         "EDA + visualization on a Kaggle dataset"],
            "intermediate": ["Customer churn prediction model with feature engineering",
                              "NLP sentiment analysis mini-project"],
            "advanced": ["End-to-end ML pipeline with deployment (Flask/FastAPI)",
                         "Deep learning image/text classifier with model tracking"],
        },
        "certifications": ["IBM Data Science Professional Certificate",
                            "Google Advanced Data Analytics", "DeepLearning.AI ML Specialization"],
    },
    "AI / ML Engineer": {
        "skills": {
            "Python": 5, "Machine Learning": 5, "Deep Learning": 5, "TensorFlow/PyTorch": 4,
            "Scikit-learn": 3, "MLOps": 4, "Statistics": 3, "Data Structures & Algorithms": 3,
            "SQL": 2, "Cloud (AWS/GCP/Azure)": 3,
        },
        "projects": {
            "beginner": ["Image classifier using CNN", "Basic chatbot with rule-based logic"],
            "intermediate": ["Fine-tuning a pretrained transformer for text classification",
                              "Recommendation system with collaborative filtering"],
            "advanced": ["Deploy an ML model with CI/CD and monitoring (MLOps)",
                         "Multi-agent / RAG based AI application"],
        },
        "certifications": ["TensorFlow Developer Certificate", "AWS Certified ML - Specialty",
                            "DeepLearning.AI MLOps Specialization"],
    },
    "Software Engineer": {
        "skills": {
            "Data Structures & Algorithms": 5, "Python/Java/C++": 5, "Git/GitHub": 4,
            "System Design": 3, "SQL": 3, "OOP": 4, "REST APIs": 3,
            "Testing": 2, "Cloud Basics": 2, "Communication": 2,
        },
        "projects": {
            "beginner": ["CLI-based task manager", "Simple REST API with Flask/Express"],
            "intermediate": ["Full-stack CRUD web application", "Design & implement a URL shortener"],
            "advanced": ["Distributed system design (e.g., mini load balancer)",
                         "Open-source contribution to a mid-size repo"],
        },
        "certifications": ["Meta Back-End / Front-End Developer Certificate",
                            "AWS Certified Developer - Associate"],
    },
    "Web Developer": {
        "skills": {
            "HTML/CSS": 5, "JavaScript": 5, "React/Angular/Vue": 4, "Node.js": 3,
            "Git/GitHub": 4, "REST APIs": 3, "Databases (SQL/NoSQL)": 3,
            "Responsive Design": 4, "UI/UX Basics": 2,
        },
        "projects": {
            "beginner": ["Personal portfolio website", "To-do list app with local storage"],
            "intermediate": ["Full-stack e-commerce app (React + Node + MongoDB)",
                              "Real-time chat app with WebSockets"],
            "advanced": ["Progressive Web App with offline support",
                         "Scalable multi-tenant SaaS front-end"],
        },
        "certifications": ["Meta Front-End Developer Certificate", "freeCodeCamp Full Stack"],
    },
    "Business Analyst": {
        "skills": {
            "Excel": 5, "SQL": 4, "Business Communication": 5, "Requirement Gathering": 4,
            "Power BI": 3, "Process Modeling": 3, "Statistics": 2,
            "Stakeholder Management": 3, "Agile/Scrum": 2,
        },
        "projects": {
            "beginner": ["Business process documentation for a mock case study",
                         "Excel dashboard for KPI tracking"],
            "intermediate": ["Requirement analysis & user story writing for a product",
                              "Power BI dashboard for business performance"],
            "advanced": ["End-to-end business case with cost-benefit & data analysis",
                         "Process re-engineering proposal backed by data"],
        },
        "certifications": ["CBAP / ECBA (IIBA)", "Google Project Management Certificate"],
    },
    "Cloud Engineer": {
        "skills": {
            "Linux": 4, "Networking": 4, "AWS/Azure/GCP": 5, "Docker": 4,
            "Kubernetes": 3, "CI/CD": 3, "Scripting (Python/Bash)": 3,
            "Terraform/IaC": 3, "Security Basics": 2,
        },
        "projects": {
            "beginner": ["Host a static website on AWS S3 + CloudFront",
                         "Set up a basic CI/CD pipeline with GitHub Actions"],
            "intermediate": ["Containerize an app with Docker & deploy to Kubernetes",
                              "Infrastructure as Code setup using Terraform"],
            "advanced": ["Multi-region highly available architecture design",
                         "Automated monitoring & auto-scaling setup"],
        },
        "certifications": ["AWS Certified Solutions Architect - Associate",
                            "Microsoft Azure Fundamentals (AZ-900)", "Certified Kubernetes Administrator"],
    },
    "Cybersecurity Analyst": {
        "skills": {
            "Networking": 5, "Linux": 3, "Security Fundamentals": 5, "SIEM Tools": 3,
            "Ethical Hacking Basics": 4, "Risk Assessment": 3, "Python/Scripting": 2,
            "Cloud Security": 2, "Incident Response": 3,
        },
        "projects": {
            "beginner": ["Set up a home lab (VM) and practice basic pentesting on CTF platforms",
                         "Vulnerability scan report using open-source tools"],
            "intermediate": ["Build a simple SIEM alerting pipeline",
                              "Network traffic analysis project"],
            "advanced": ["End-to-end incident response simulation",
                         "Security automation script suite"],
        },
        "certifications": ["CompTIA Security+", "Certified Ethical Hacker (CEH)",
                            "Google Cybersecurity Certificate"],
    },
}

SKILL_LEVEL_TAGS = {
    0: "Beginner", 1: "Beginner", 2: "Beginner",
    3: "Intermediate", 4: "Intermediate",
    5: "Advanced",
}
