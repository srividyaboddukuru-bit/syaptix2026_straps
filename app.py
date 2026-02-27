from flask import Flask, request, render_template_string

app = Flask(__name__)

# ---------------- ROLE REQUIREMENTS (PROJECT MAPPING) ----------------

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

# ---------------- MATCH ENGINE ----------------

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
        if value is None or value == "":
            score = 50
            reasoning.append(
                f"{skill}: Missing → fairness neutral score (50)"
            )
        else:
            score = int(value)
            reasoning.append(
                f"{skill}: {score}/100 × weight {weight}"
            )

        contribution = round(score * weight, 2)
        contributions.append((skill, contribution))

        weighted_sum += contribution
        total_weight += weight

    final_score = round(weighted_sum / total_weight, 2)

    return final_score, reasoning, contributions


# ---------------- UI TEMPLATE ----------------

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Explainable Internship Matching AI</title>

<style>

body{
font-family:'Segoe UI';
background:linear-gradient(135deg,#ffe259,#ff7eb3,#ff9966);
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
margin:0;
}

.container{
width:560px;
background:rgba(255,255,255,0.85);
backdrop-filter:blur(15px);
padding:30px;
border-radius:18px;
box-shadow:0 15px 40px rgba(0,0,0,0.25);
animation:fade 0.6s ease;
}

@keyframes fade{
from{opacity:0;transform:translateY(20px);}
to{opacity:1;}
}

h2{text-align:center;color:#222}

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
background:#111;
color:white;
border:none;
border-radius:10px;
font-weight:bold;
cursor:pointer;
transition:.3s;
}

button:hover{
background:#ff4d6d;
transform:scale(1.04);
}

.hidden{display:none;}
.error{color:red;text-align:center}

.progress{
height:24px;
background:#eee;
border-radius:12px;
overflow:hidden;
margin-top:15px;
}

.bar{
height:100%;
background:linear-gradient(90deg,#00c6ff,#0072ff);
color:white;
text-align:center;
font-weight:bold;
}

.reason{
background:#f5f5f5;
padding:10px;
border-radius:8px;
margin-top:8px;
}

.skillbox{
background:#fafafa;
padding:8px;
margin-top:6px;
border-radius:6px;
font-size:14px;
}

</style>
</head>

<body>
<div class="container">

{% if not score %}

<!-- STEP 1 -->
<div id="step1">
<h2>AI Internship Application</h2>

<input id="name" placeholder="Full Name">
<input id="email" placeholder="Email">
<input id="college" placeholder="College">

<select id="role">
<option value="">Select Preferred Role</option>
<option>AI Intern</option>
<option>Web Developer</option>
<option>Data Analyst</option>
</select>

<div id="error1" class="error"></div>

<button onclick="generateSkills()">Continue</button>
</div>


<form method="POST" onsubmit="return validateSkills()">

<!-- STEP 2 -->
<div id="step2" class="hidden">

<h2>Skill Competency Evaluation</h2>

<div id="skillInputs"></div>

<input type="hidden" name="role" id="role_hidden">

<div id="error2" class="error"></div>

<button>Generate Explainable Match</button>

</div>

</form>

{% endif %}


{% if score %}

<h2>AI Match Analysis</h2>

<p><b>Final Match Score:</b> {{score}}%</p>

<div class="progress">
<div class="bar" style="width:{{score}}%">
{{score}}%
</div>
</div>

<h3>Explainable Reasoning</h3>

{% for r in reasoning %}
<div class="reason">{{r}}</div>
{% endfor %}

<h3>Skill Contribution</h3>

{% for s,c in contributions %}
<div class="skillbox">
{{s}} Contribution → {{c}}
</div>
{% endfor %}

<p style="margin-top:15px">
<b>Thank you for registering. Opportunities are allocated using transparent AI evaluation.</b>
</p>

<form method="GET">
<button>Submit Another Response</button>
</form>

{% endif %}

</div>

<script>

const roleSkills={
"AI Intern":["Python","Machine Learning","Statistics"],
"Web Developer":["HTML","CSS","JavaScript"],
"Data Analyst":["Python","SQL","Statistics"]
};

function generateSkills(){

let name=v("name");
let email=v("email");
let college=v("college");
let role=v("role");

if(!name||!email||!college||!role){
document.getElementById("error1").innerText=
"All details required.";
return;
}

document.getElementById("role_hidden").value=role;

let skills=roleSkills[role];
let div=document.getElementById("skillInputs");
div.innerHTML="";

skills.forEach(skill=>{

let label=document.createElement("label");
label.innerText=skill+" proficiency (1-100)";

let input=document.createElement("input");
input.type="number";
input.min="1";
input.max="100";
input.name="score_"+skill;
input.className="skillScore";

div.appendChild(label);
div.appendChild(input);

});

document.getElementById("step1").classList.add("hidden");
document.getElementById("step2").classList.remove("hidden");
}

function validateSkills(){

let scores=document.getElementsByClassName("skillScore");

for(let i=0;i<scores.length;i++){
if(scores[i].value===""){
document.getElementById("error2").innerText=
"All skill scores required.";
return false;
}
}
return true;
}

function v(id){
return document.getElementById(id).value.trim();
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

    if request.method=="POST":
        score, reasoning, contributions = calculate_match(request.form)

    return render_template_string(
        PAGE,
        score=score,
        reasoning=reasoning,
        contributions=contributions
    )


if __name__=="__main__":
    app.run(debug=True)
