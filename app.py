from flask import Flask, request, render_template_string

app = Flask(__name__)

# ---------------- ROLE REQUIREMENTS (Requirement Mapping) ----------------

ROLE_REQUIREMENTS = {
    "Web Developer Intern": {
        "HTML":0.4,
        "CSS":0.3,
        "Python":0.3
    },
    "ML Intern":{
        "Python":0.5,
        "ML":0.4,
        "Statistics":0.1
    },
    "Software Developer Intern":{
        "Python":0.4,
        "DSA":0.4,
        "ProblemSolving":0.2
    }
}

# ---------------- HTML TEMPLATE ----------------

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Explainable Internship Matching</title>

<style>
body{
font-family:Arial;
background:linear-gradient(to right,yellow,pink,orange);
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
margin:0;
}

.container{
background:white;
padding:25px;
border-radius:12px;
width:480px;
box-shadow:0 0 15px rgba(0,0,0,0.25);
}

input,select{
width:100%;
padding:10px;
margin:6px 0 12px 0;
border-radius:6px;
border:1px solid #ccc;
}

button{
width:100%;
padding:12px;
background:black;
color:white;
border:none;
border-radius:6px;
cursor:pointer;
}

.hidden{display:none;}
.reason{background:#f5f5f5;padding:10px;border-radius:8px;margin-top:10px;}
.error{color:red;text-align:center;}
</style>
</head>

<body>
<div class="container">

{% if not score %}

<div id="slide1">
<h2>Basic Details</h2>
<input id="name" placeholder="Full Name">
<input id="email" placeholder="Email">
<input id="college" placeholder="College">
<button onclick="nextSlide(2)">Next</button>
</div>

<div id="slide2" class="hidden">
<h2>Role & Skills</h2>

<select id="role">
<option value="">Select Preferred Internship Role</option>
<option>Web Developer Intern</option>
<option>ML Intern</option>
<option>Software Developer Intern</option>
</select>

<input id="skills" placeholder="Skills (Python,HTML,ML)">

<label>
<input type="checkbox" id="confirm">
I confirm information is correct
</label>

<div id="error1" class="error"></div>

<button onclick="goToSkills()">Proceed</button>
</div>

<form method="POST" onsubmit="return validateSkills()">

<div id="step2" class="hidden">
<h2>Skill Proficiency (1-100)</h2>

<div id="skillInputs"></div>

<input type="hidden" name="skill_names" id="skill_names">
<input type="hidden" name="role_name" id="role_name">

<div id="error2" class="error"></div>

<button>Calculate Match Score</button>
</div>

</form>

{% endif %}

{% if score %}

<h2>Match Score: {{score}}%</h2>

<div class="reason">
<b>Reasoning:</b>
<ul>
{% for r in reasoning %}
<li>{{r}}</li>
{% endfor %}
</ul>
</div>

<p><b>Thanks for registering in internship.</b></p>
<p><b>Further details will be send to respected mail.</b></p>

<form method="GET">
<button>Other Response</button>
</form>

{% endif %}

</div>

<script>

function nextSlide(n){
document.getElementById("slide1").classList.add("hidden");
document.getElementById("slide2").classList.remove("hidden");
}

let skillsArray=[];

function goToSkills(){

let role=document.getElementById("role").value;
let skills=document.getElementById("skills").value.trim();
let confirm=document.getElementById("confirm").checked;

if(!role||!skills||!confirm){
document.getElementById("error1").innerText=
"Role, skills and confirmation required.";
return;
}

skillsArray=skills.split(",").map(s=>s.trim());

let div=document.getElementById("skillInputs");
div.innerHTML="";

skillsArray.forEach(skill=>{
let label=document.createElement("label");
label.innerText=skill+" Skill Level";

let input=document.createElement("input");
input.type="number";
input.min="1";
input.max="100";
input.name="score_"+skill;
input.className="skillScore";

div.appendChild(label);
div.appendChild(input);
});

document.getElementById("skill_names").value=skillsArray.join(",");
document.getElementById("role_name").value=role;

document.getElementById("slide2").classList.add("hidden");
document.getElementById("step2").classList.remove("hidden");
}

function validateSkills(){
let scores=document.getElementsByClassName("skillScore");
for(let i=0;i<scores.length;i++){
if(scores[i].value===""){
document.getElementById("error2").innerText="All scores required.";
return false;
}
}
return true;
}

</script>

</body>
</html>
"""

# ---------------- MATCHING LOGIC ----------------

def calculate_match(form):

    role=form.get("role_name")
    requirements=ROLE_REQUIREMENTS.get(role,{})

    user_skills=form.get("skill_names").split(",")

    reasoning=[]
    total_score=0

    for skill,weight in requirements.items():

        if skill in user_skills:
            level=int(form.get(f"score_{skill}",50))
        else:
            # fairness-aware neutral handling
            level=50
            reasoning.append(f"{skill} not provided → neutral fairness score applied")

        contribution=level*weight
        total_score+=contribution

        if level>75:
            reasoning.append(f"{skill} strong match (+{round(contribution,1)})")
        elif level>50:
            reasoning.append(f"{skill} moderate match (+{round(contribution,1)})")
        else:
            reasoning.append(f"{skill} needs improvement (+{round(contribution,1)})")

    return round(total_score,2), reasoning


@app.route("/",methods=["GET","POST"])
def home():
    score=None
    reasoning=None

    if request.method=="POST":
        score,reasoning=calculate_match(request.form)

    return render_template_string(TEMPLATE,score=score,reasoning=reasoning)


if __name__=="__main__":
    app.run(debug=True)
