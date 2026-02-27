from flask import Flask, request, render_template_string

app = Flask(__name__)

# =====================================================
# ROLE REQUIREMENTS (PROJECT REQUIREMENT MAPPING)
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
# EXPLAINABLE FAIR MATCH ENGINE
# =====================================================

def calculate_match(form):

    role = form.get("role")
    skills_required = ROLE_REQUIREMENTS[role]

    reasoning = []
    contributions = []

    weighted_sum = 0
    total_weight = 0

    for skill, weight in skills_required.items():

        value = form.get(f"score_{skill}")

        # fairness-aware handling
        if not value:
            score = 50
            reasoning.append(
                f"{skill}: Missing score → Neutral fairness score (50)"
            )
        else:
            score = int(value)
            reasoning.append(
                f"{skill}: {score}/100 × weight {weight}"
            )

        contribution = round(score * weight, 2)

        weighted_sum += contribution
        total_weight += weight

        contributions.append((skill, contribution))

    final_score = round(weighted_sum / total_weight, 2)

    # ---------------- AI INTERPRETABLE SUMMARY ----------------
    if final_score >= 80:
        summary = "Excellent alignment with role requirements. Candidate shows strong competency across critical skills."
    elif final_score >= 60:
        summary = "Good alignment with the role. Some skills can be improved for stronger matching."
    else:
        summary = "Partial match detected. Skill development is recommended to improve suitability."

    return final_score, reasoning, contributions, summary


# =====================================================
# UI TEMPLATE
# =====================================================

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Explainable Internship Matching AI</title>

<style>

body{
font-family:Segoe UI;
background:linear-gradient(135deg,#ffe259,#ff7eb3,#ff9966);
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
margin:0;
}

.container{
width:620px;
background:white;
padding:30px;
border-radius:18px;
box-shadow:0 15px 40px rgba(0,0,0,0.25);
}

h2{text-align:center;}

input,select{
width:100%;
padding:11px;
margin:8px 0;
border-radius:8px;
border:1px solid #ccc;
}

button{
width:100%;
padding:13px;
background:black;
color:white;
border:none;
border-radius:10px;
font-weight:bold;
cursor:pointer;
}

button:hover{
background:#ff4d6d;
}

.hidden{display:none;}
.error{color:red;text-align:center;}

.progress{
height:26px;
background:#eee;
border-radius:14px;
overflow:hidden;
margin-top:15px;
}

.bar{
height:100%;
background:#0072ff;
color:white;
text-align:center;
font-weight:bold;
}

.box{
background:#f5f5f5;
padding:10px;
margin-top:8px;
border-radius:8px;
}

.summary{
background:#e8f7ff;
padding:12px;
margin-top:15px;
border-radius:10px;
font-weight:bold;
}

</style>
</head>

<body>

<div class="container">

{% if not score %}

<!-- STEP 1 -->
<div id="step1">

<h2>Step 1 — Basic Details</h2>

<input id="name" placeholder="Full Name">
<input id="email" placeholder="Email">
<input id="college" placeholder="College">
<input id="mobile" placeholder="Mobile Number">

<select id="role">
<option value="">Select Role</option>
<option>AI Intern</option>
<option>Web Developer</option>
<option>Data Analyst</option>
</select>

<div id="err1" class="error"></div>

<button onclick="goStep2()">Continue</button>

</div>


<form method="POST" onsubmit="return validateStep2()">

<!-- STEP 2 -->
<div id="step2" class="hidden">

<h2>Step 2 — Skill Competency Scores</h2>

<div id="skillsArea"></div>

<input type="hidden" name="role" id="role_hidden">

<div id="err2" class="error"></div>

<button>Generate Transparent Match Score</button>

</div>

</form>

{% endif %}


{% if score %}

<h2>Step 3 — Explainable Match Result</h2>

<h3>Final Match Score: {{score}}%</h3>

<div class="progress">
<div class="bar" style="width:{{score}}%">
{{score}}%
</div>
</div>

<div class="summary">
{{summary}}
</div>

<h3>Transparent Reasoning</h3>
{% for r in reasoning %}
<div class="box">{{r}}</div>
{% endfor %}

<h3>Skill Contributions</h3>
{% for s,c in contributions %}
<div class="box">{{s}} → {{c}}</div>
{% endfor %}

<div class="box">
<b>Scoring Formula:</b><br>
Match Score = Σ(Skill Score × Skill Weight) / Total Weight<br>
Fairness Policy: Missing skills receive neutral score (50).
</div>

<p><b>
Thanks for registering in internship. Further details will be mailed to you.
</b></p>

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

function v(id){
return document.getElementById(id).value.trim();
}

function goStep2(){

let name=v("name");
let email=v("email");
let college=v("college");
let mobile=v("mobile");
let role=v("role");

if(!name||!email||!college||!mobile||!role){
document.getElementById("err1").innerText=
"Basic details are compulsory.";
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
input.type="number";
input.name="score_"+skill;
input.min=1;
input.max=100;
input.className="skillScore";

area.appendChild(label);
area.appendChild(input);
});

step1.classList.add("hidden");
step2.classList.remove("hidden");
}

function validateStep2(){

let scores=document.getElementsByClassName("skillScore");

for(let i=0;i<scores.length;i++){
if(scores[i].value===""){
document.getElementById("err2").innerText=
"All skill scores are compulsory.";
return false;
}
}
return true;
}

</script>

</body>
</html>
"""

# =====================================================
# ROUTE
# =====================================================

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


if __name__=="__main__":
    app.run(debug=True)
