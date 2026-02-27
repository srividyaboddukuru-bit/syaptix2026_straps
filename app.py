from flask import Flask, jsonify

app = Flask(__name__)

# Sample Candidates
candidates = [
    {"name": "vidya", "skills": {"python": 8, "sql": 7, "ml": 6}},
    {"name": "vyshu", "skills": {"python": 6, "sql": 9, "ml": 5}},
    {"name": "lakshmi", "skills": {"python": 9, "sql": 6, "ml": 8}}
]

# Project Skill Requirements with Weights
project_requirements = {
    "python": 0.4,
    "sql": 0.3,
    "ml": 0.3
}

# Match Score Calculation
def calculate_match_score(candidate):
    total_score = 0
    explanation = {}

    for skill, weight in project_requirements.items():
        level = candidate["skills"].get(skill, 0)
        contribution = level * weight
        total_score += contribution

        explanation[skill] = {
            "candidate_level": level,
            "weight": weight,
            "contribution": round(contribution, 2)
        }

    return round(total_score, 2), explanation


@app.route('/')
def home():
    return "Skill Matching Platform Running 🚀"


@app.route('/rank')
def rank():
    results = []

    for candidate in candidates:
        score, explanation = calculate_match_score(candidate)
        results.append({
            "name": candidate["name"],
            "match_score": score,
            "explanation": explanation
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
