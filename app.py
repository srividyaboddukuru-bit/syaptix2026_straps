from flask import Flask, request, render_template_string

app = Flask(__name__)

# -------------------------------------------------
# Internship Requirement Model
# -------------------------------------------------
PROJECT = {
    "python": 80,
    "ml": 70,
    "communication": 65,
    "problem_solving": 75
}

WEIGHTS = {
    "competency": 0.35,
    "requirement": 0.25,
    "experience": 0.20,
    "learning": 0.10,
    "fairness": 0.10
}

def fairness_boost(resource):
    return 100 - resource


# -------------------------------------------------
# Explainable Score Calculation
# -------------------------------------------------
def calculate_score(form):

    skills = {
        "python": int(form["python"]),
        "ml": int(form["ml"]),
        "communication": int(form["communication"]),
        "problem_solving": int(form["problem_solving"])
    }

    experience = int(form["experience"])
    learning = int(form["learning"])
    resource = int(form["resource"])

    reasoning = []

    alignment = sum(min(skills[k], PROJECT[k]) for k in PROJECT)/len(PROJECT)
    reasoning.append("Skills aligned with internship competency requirements.")

    gaps = [abs(PROJECT[k]-skills[k]) for k in PROJECT]
    requirement_fit = 100 - (sum(gaps)/len(gaps))
    reasoning.append("Requirement mapping computed using skill-gap analysis.")

    fairness = fairness_boost(resource)
    reasoning.append("Fairness-aware adjustment applied.")

    final_score = (
        alignment*WEIGHTS["competency"] +
        requirement_fit*WEIGHTS["requirement"] +
        experience*WEIGHTS["experience"] +
        learning*WEIGHTS["learning"] +
        fairness*WEIGHTS["fairness"]
    )

    reasoning.append(f"✅ Final Match Score = {final_score:.2f}")

    return round(final_score,2), reasoning


# -------------------------------------------------
# WEB APPLICATION UI
# -------------------------------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Explainable Internship Application</title>

<style>

/* 🌈 VIBGYOR BACKGROUND */
body{
margin:0;
font-family:Segoe UI;
background:linear-gradient(
90deg,
#9400D3,
#4B0082,
#0000FF,
#00FF00,
#FFFF00,
#FF7F00,
#FF0000
);
background-size:400% 400%;
animation:gradientMove 12s ease infinite;
color:white;
}

@keyframes gradientMove{
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

.container{
width:520px;
margin:40px auto;
background:rgba(0,0,0,0.45);
padding:25px;
border-radius:15px;
backdrop-filter:blur(12px);
box-shadow:0 0 25px rgba(0,0,0,0.5);
}

h1{text-align:center;}

input{
width:100%;
padding:10px;
margin:8px 0;
border:none;
border-radius:6px;
}

/* BUTTON COLORS */
.primary-btn{
background:#00e5ff;
color:black;
font-weight:bold;
padding:12px;
border:none;
border-radius:8px;
cursor:pointer;
width:100%;
}

.primary-btn:hover{
background:#00bcd4;
}

.submit-btn{
background:#00ff95;
color:black;
font-weight:bold;
padding:12px;
border:none;
border-radius:8px;
cursor:pointer;
width:100%;
margin-top:10px;
}

.submit-btn:hover{
background:#00cc77;
}

.skill-section{
display:none;
margin-top:15px;
background:rgba(255,255,255,0.1);
padding:15px;
border-radius:10px;
}

.result{
margin-top:20px;
background:rgba(0,0,0,0.4);
padding:15px;
border-radius:10px;
}

.thankyou{
text-align:center;
color:#00ff95;
font-size:20px;
font-weight:bold;
margin-top:15px;
}

</style>

<script>
function showSkills(){
document.getElementById("skills").style.display="block";
}
</script>

</head>

<body>

<div class="container">

<h1>🌟 Internship Application</h1>

<form method="POST">

<!-- BASIC DETAILS -->
<input name="name" placeholder="Full Name" required>
<input name="gmail" placeholder="Gmail Address" required>
<input name="college" placeholder="College Name" required>

<button type="button" class="primary-btn" onclick="showSkills()">
Enter Skill Details
</button>

<!-- SKILL DETAILS -->
<div id="skills" class="skill-section">

<h3>Skill Assessment (1–100)</h3>

<input name="python" placeholder="Python Skill" required>
<input name="ml" placeholder="Machine Learning Skill" required>
<input name="communication" placeholder="Communication Skill" required>
<input name="problem_solving" placeholder="Problem Solving Skill" required>
<input name="experience" placeholder="Experience Level" required>
<input name="learning" placeholder="Learning Potential" required>
<input name="resource" placeholder="Resource Access Index" required>

<button class="submit-btn">Submit Application</button>

</div>

</form>

{% if score %}

<div class="result">
<h2>Match Score: {{score}}</h2>

<ul>
{% for r in reasoning %}
<li>{{r}}</li>
{% endfor %}
</ul>

<div class="thankyou">
✅ Thank you for registration! Your internship application has been submitted.
</div>

</div>

{% endif %}

</div>

</body>
</html>
"""


@app.route("/", methods=["GET","POST"])
def home():
    score=None
    reasoning=None

    if request.method=="POST":
        score, reasoning = calculate_score(request.form)

    return render_template_string(TEMPLATE,
                                  score=score,
                                  reasoning=reasoning)


if __name__ == "__main__":
    app.run(debug=True)
