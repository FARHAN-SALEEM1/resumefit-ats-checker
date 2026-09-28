"""
Curated skills keyword list for MVP-level extraction.

Why not a trained NER model for this: for week 1, a maintained keyword
list is faster to ship, fully explainable (no black box), and easy for
you to extend as you test real resumes. Flag: this list is not
exhaustive — Sprint 2/3 evaluation should surface gaps to add here.
"""

# Grouped for readability; extraction just flattens this into one set.
SKILLS_DB = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "c",
        "php", "ruby", "go", "golang", "rust", "kotlin", "swift", "r",
        "sql", "html", "css", "matlab", "scala", "dart",
    ],
    "web_frameworks": [
        "react", "angular", "vue", "django", "flask", "fastapi",
        "express", "node.js", "nodejs", "next.js", "nextjs", "spring",
        "spring boot", "laravel", "asp.net", ".net", "tailwind",
        "bootstrap", "jquery",
    ],
    "data_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch",
        "keras", "scikit-learn", "sklearn", "pandas", "numpy",
        "matplotlib", "seaborn", "nlp", "computer vision", "opencv",
        "data analysis", "data science", "data visualization",
        "power bi", "tableau", "excel",
    ],
    "databases": [
        "mysql", "postgresql", "postgres", "mongodb", "sqlite",
        "redis", "oracle", "firebase", "dynamodb", "elasticsearch",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
        "jenkins", "ci/cd", "git", "github", "gitlab", "linux",
        "terraform", "nginx", "render", "vercel", "heroku",
    ],
    "soft_general": [
        "project management", "agile", "scrum", "communication",
        "leadership", "problem solving", "team collaboration",
    ],
}


def flat_skills_set():
    flat = set()
    for group in SKILLS_DB.values():
        flat.update(group)
    return flat
