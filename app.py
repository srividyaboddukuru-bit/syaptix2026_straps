from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "hackathon_secret_key"

# ---------------- USERS (LOGIN) ----------------
USERS = {
    "admin": "admin123",
    "user1": "password1"
}

# ---------------- PROJECT/ROLE REQUIREMENTS ----------------
ROLE_REQUIREMENTS = {
    "AI Intern": {"Python": 0.35, "Machine Learning": 0.40, "Statistics": 0.25},
    "Web Developer": {"HTML": 0.30, "CSS": 0.30, "JavaScript": 0.40},
    "Data Analyst": {"Python": 0.40, "SQL": 0.30, "Statistics": 0.30}
}

# ---------------- LOGIN PAGE ----------------
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Login - Internship Platform</title>
<style>
body {
    font-family: 'Segoe UI', sans-serif;
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:100vh;
    background: linear-gradient(135deg, #a1c4fd, #c2e9fb); /* soft blue gradient */
}
.container {
    background:white;
    padding:30px;
    border-radius:12px;
    box-shadow:0 6px 20px rgba(0,0,0,0.15);
    width:360px;
}
input {
    width:100%;
    padding:10px;
    margin:8px 0;
    border-radius:6px;
    border:1px solid #ccc;
}
button {
    width:100%;
    padding:12px;
    background:#ff6fa3; /* pink button */
    color:white;
    border:none;
    border-radius:8px;
    font-weight:bold;
}
button:hover {
    background:#ff4d87;
    cursor:pointer;
}
.error {
    color:red;
    text-align:center;
}
h2 {
    color:#2c3e50;
    text-align:center;
}
</style>
</head>
<body>
<div class="container">
<h2>Login to Internship Platform</h2>
<form method="POST">
<input type="text" name="username" placeholder="Username" required autofocus>
<input type="password" name="password" placeholder="Password" required>
<div class="error">{{error}}</div>
<button type="submit">Login</button>
</form>
</div>
</body>
</html>
"""

# ---------------- ROUTE: LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password."
    return render_template_string(LOGIN_PAGE, error=error)

# ---------------- FAIRNESS-AWARE MATCH ENGINE ----------------
def normalize_score(score):
    return min(max(score, 20), 95)

def calculate_match(form):
    role = form.get("role")
    role_skills = ROLE_REQUIREMENTS[role]
    reasoning, contributions = [], []
    weighted_sum, total_weight, matched_skills = 0, 0, 0

    for skill, weight in role_skills.items():
        value = form.get(f"score_{skill}")
        if not value:
            score = 50
            reasoning.append(f"{skill}: Missing → Neutral fairness score (50)")
        else:
            score = normalize_score(int(value))
            reasoning.append(f"{skill}: Normalized score {score}/100 × weight {weight}")
            matched_skills += 1
        contribution = score * weight
        weighted_sum += contribution
        total_weight += weight
        contributions.append((skill, round(contribution,2)))

    competency_score = weighted_sum / total_weight
    coverage_score = (matched_skills / len(role_skills)) * 100
    final_score = round(0.7 * competency_score + 0.3 * coverage_score, 2)

    reasoning.append(f"Competency Score = {round(competency_score,2)}")
    reasoning.append(f"Skill Coverage Score = {round(coverage_score,2)}")
    reasoning.append("Final Score = 0.7×Competency + 0.3×Coverage (Fairness-aware evaluation)")

    if final_score >= 80:
        summary = "Excellent and equitable alignment with role requirements."
    elif final_score >= 60:
        summary = "Good match with fair competency balance."
    else:
        summary = "Partial alignment. Skill improvement recommended."

    return final_score, reasoning, contributions, summary

# ---------------- MAIN PLATFORM ----------------
PLATFORM_PAGE = """ 
<!DOCTYPE html>
<html>
<head>
<title>Internship Matching Platform</title>
<style>
body {
    font-family:'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #a1c4fd, #c2e9fb); /* soft blue gradient */
    display:flex;
    justify-content:center;
    align-items:center;
    min-height:100vh;
}
.container {
    width:620px;
    background:white;
    padding:30px;
    border-radius:12px;
    box-shadow:0 6px 20px rgba(0,0,0,0.15);
}
input,select {
    width:100%;
    padding:10px;
    margin:8px 0;
    border-radius:6px;
    border:1px solid #ccc;
}
button {
    width:100%;
    padding:12px;
    background:#ff6fa3; /* pink button */
    color:white;
    border:none;
    border-radius:8px;
    font-weight:bold;
}
button:hover {
    background:#ff4d87;
    cursor:pointer;
}
.hidden {display:none;}
.box {
    background:#f4f4f4;
    padding:10px;
    margin-top:8px;
    border-radius:8px;
}
h2,h3 {color:#2c3e50;}
</style>
</head>
<body>
<div class="container">
{% if not score %}
<div id="step1">
<h2>Step 1 — Basic Details</h2>
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
<div class="box"><b>{{summary}}</b></div>
<h3>Reasoning</h3>
{% for r in reasoning %}
<div class="box">{{r}}</div>
{% endfor %}
<h3>Contributions</h3>
{% for s,c in contributions %}
<div class="box">{{s}} → {{c}}</div>
{% endfor %}

<form action="{{ url_for('logout') }}" method="GET">
<button>New Application</button>
</form>
{% endif %}

</div>
<script>
const roleSkills={"AI Intern":["Python","Machine Learning","Statistics"],"Web Developer":["HTML","CSS","JavaScript"],"Data Analyst":["Python","SQL","Statistics"]};
function goStep2(){
    let role=document.getElementById("role").value;
    if(!role){
        alert("Please select a role before continuing.");
        return;
    }
    document.getElementById("role_hidden").value=role;
    let skills=roleSkills[role];
    let area=document.getElementById("skillsArea");
    area.innerHTML="";
    skills.forEach(skill=>{
        let label=document.createElement("label");
        label.innerText=skill+" score (1-100)";
        let input=document.createElement("input");
        input.type="number"; input.name="score_"+skill; input.min=1; input.max=100;
        area.appendChild(label); area.appendChild(input);
    });
    document.getElementById("step1").classList.add("hidden");
    document.getElementById("step2").classList.remove("hidden");
}
</script>
</body>
</html>
"""

# ---------------- ROUTE: HOME ----------------
@app.route("/home", methods=["GET","POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    score, reasoning, contributions, summary = None, None, None, None
    if request.method == "POST":
        score, reasoning, contributions, summary = calculate_match(request.form)
    return render_template_string(
        PLATFORM_PAGE,
        score=score,
        reasoning=reasoning,
        contributions=contributions,
        summary=summary
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
