from flask import Flask, request, render_template_string

app = Flask(__name__)

# =====================================================
# ROLE REQUIREMENTS
# =====================================================

ROLE_REQUIREMENTS = {
    "AI Intern": {
        "Python": 0.35,
        "Machine Learning": 0.40,
        "Statistics": 0.25
    },
    "Web Developer": {
        "HTML": 0.30,
        "CSS": 0.30,
        "JavaScript": 0.40
    },
    "Data Analyst": {
        "Python": 0.40,
        "SQL": 0.30,
        "Statistics": 0.30
    }
}

# =====================================================
# FAIRNESS-AWARE MATCH ENGINE
# =====================================================

def normalize_score(score):
    """Fairness normalization"""
    return min(max(score, 20), 95)


def calculate_match(form):

    role = form.get("role")
    role_skills = ROLE_REQUIREMENTS[role]

    reasoning = []
    contributions = []

    weighted_sum = 0
    total_weight = 0
    matched_skills = 0

    for skill, weight in role_skills.items():

        value = form.get(f"score_{skill}")

        # ---------- FAIRNESS 1: Neutral handling ----------
        if not value:
            score = 50
            reasoning.append(
                f"{skill}: Missing → Neutral fairness score (50)"
            )
        else:
            score = int(value)
            score = normalize_score(score)  # FAIRNESS 2
            reasoning.append(
                f"{skill}: Normalized score {score}/100 × weight {weight}"
            )
            matched_skills += 1

        contribution = score * weight

        weighted_sum += contribution
        total_weight += weight

        contributions.append((skill, round(contribution,2)))

    # competency score
    competency_score = weighted_sum / total_weight

    # ---------- FAIRNESS 3: Skill coverage ----------
    coverage_score = (matched_skills / len(role_skills)) * 100

    final_score = round(
        (0.7 * competency_score) +
        (0.3 * coverage_score), 2
    )

    reasoning.append(
        f"Competency Score = {round(competency_score,2)}"
    )
    reasoning.append(
        f"Skill Coverage Score = {round(coverage_score,2)}"
    )
    reasoning.append(
        "Final Score = 0.7×Competency + 0.3×Coverage (Fairness-aware evaluation)"
    )

    # interpretation
    if final_score >= 80:
        summary = "Excellent and equitable alignment with role requirements."
    elif final_score >= 60:
        summary = "Good match with fair competency balance."
    else:
        summary = "Partial alignment. Skill improvement recommended."

    return final_score, reasoning, contributions, summary


# =====================================================
# UI (UNCHANGED STYLE)
# =====================================================

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Fair Explainable Internship Matching</title>

<style>
body{
font-family:Segoe UI;
background:linear-gradient(135deg,#ffe259,#ff7eb3,#ff9966);
display:flex;justify-content:center;align-items:center;
min-height:100vh;margin:0;
}
.container{
width:620px;background:white;padding:30px;
border-radius:18px;box-shadow:0 15px 40px rgba(0,0,0,0.25);
}
input,select{width:100%;padding:10px;margin:8px 0;}
button{width:100%;padding:12px;background:black;color:white;border:none;border-radius:8px;}
.hidden{display:none;}
.box{background:#f4f4f4;padding:10px;margin-top:8px;border-radius:8px;}
.bar{height:26px;background:#0072ff;color:white;text-align:center;}
.progress{background:#eee;border-radius:12px;overflow:hidden;}
</style>
</head>

<body>
<div class="container">

{% if not score %}

<div id="step1">
<h2>Step 1 — Details</h2>

<input id="name" placeholder="Name">
<input id="email" placeholder="Email">
<input id="college" placeholder="College">
<input id="mobile" placeholder="Mobile">

<select id="role">
<option value="">Select Role</option>
<option>AI Intern</option>
<option>Web Developer</option>
<option>Data Analyst</option>
</select>

<button onclick="goStep2()">Continue</button>
</div>

<form method="POST">

<div id="step2" class="hidden">
<h2>Step 2 — Skill Scores</h2>

<div id="skillsArea"></div>
<input type="hidden" name="role" id="role_hidden">

<button>Generate Fair Match Score</button>
</div>

</form>

{% endif %}

{% if score %}

<h2>Step 3 — Fair Explainable Result</h2>

<h3>Match Score: {{score}}%</h3>

<div class="progress">
<div class="bar" style="width:{{score}}%">{{score}}%</div>
</div>

<div class="box"><b>{{summary}}</b></div>

<h3>Reasoning</h3>
{% for r in reasoning %}
<div class="box">{{r}}</div>
{% endfor %}

<h3>Contributions</h3>
{% for s,c in contributions %}
<div class="box">{{s}} → {{c}}</div>
{% endfor %}

<form method="GET">
<button>New Application</button>
</form>

{% endif %}

</div>

<script>

const roleSkills={
"AI Intern":["Python","Machine Learning","Statistics"],
"Web Developer":["HTML","CSS","JavaScript"],
"Data Analyst":["Python","SQL","Statistics"]
};

function goStep2(){

let role=document.getElementById("role").value;
document.getElementById("role_hidden").value=role;

let skills=roleSkills[role];
let area=document.getElementById("skillsArea");
area.innerHTML="";

skills.forEach(skill=>{
let label=document.createElement("label");
label.innerText=skill+" score (1-100)";
let input=document.createElement("input");
input.type="number";
input.name="score_"+skill;
area.appendChild(label);
area.appendChild(input);
});

step1.classList.add("hidden");
step2.classList.remove("hidden");
}

</script>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():

    score=None
    reasoning=None
    contributions=None
    summary=None

    if request.method=="POST":
        score, reasoning, contributions, summary = calculate_match(request.form)

    return render_template_string(
        PAGE,
        score=score,
        reasoning=reasoning,
        contributions=contributions,
        summary=summary
    )

if __name__ == "__main__":
    app.run(debug=True)
