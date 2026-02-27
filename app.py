from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Internship Registration</title>

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
width:420px;
box-shadow:0 0 15px rgba(0,0,0,0.25);
}

h2{text-align:center;color:#222;}

input{
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
font-weight:bold;
margin-top:10px;
}

button:hover{background:#333;}

.hidden{display:none;}
.error{color:red;text-align:center;}
</style>
</head>

<body>

<div class="container">

{% if not score %}

<div id="step1">
<h2>Step 1: Basic Details</h2>

<input id="name" placeholder="Name">
<input id="email" placeholder="Email">
<input id="college" placeholder="College">
<input id="mobile" placeholder="Mobile">
<input id="skills" placeholder="Skills (Python,Java,HTML)">

<div id="error1" class="error"></div>

<button onclick="goToStep2()">Next</button>
</div>

<form method="POST" onsubmit="return validateSkills()">

<div id="step2" class="hidden">
<h2>Step 2: Skill Scores</h2>

<div id="skillInputs"></div>

<input type="hidden" name="skill_names" id="skill_names">

<div id="error2" class="error"></div>

<button>Submit Application</button>
</div>

</form>

{% endif %}

{% if score %}

<h2>Step 3: Match Score</h2>

<p><b>Your Match Score:</b> {{score}}%</p>

<p><b>Thanks for registering in internship... further details will be mailed to you.</b></p>

<form method="GET">
<button>Other Response</button>
</form>

{% endif %}

</div>

<script>

let skillsArray=[];

function goToStep2(){

let name=document.getElementById("name").value.trim();
let email=document.getElementById("email").value.trim();
let college=document.getElementById("college").value.trim();
let mobile=document.getElementById("mobile").value.trim();
let skills=document.getElementById("skills").value.trim();

if(!name || !email || !college || !mobile || !skills){
document.getElementById("error1").innerText=
"Basic details are compulsory.";
return;
}

document.getElementById("error1").innerText="";

skillsArray=skills.split(",").map(s=>s.trim());

let div=document.getElementById("skillInputs");
div.innerHTML="";

skillsArray.forEach(skill=>{

let label=document.createElement("label");
label.innerText=skill+" Score (0-100)";

let input=document.createElement("input");
input.type="number";
input.min="0";
input.max="100";
input.name="score_"+skill;
input.className="skillScore";
input.placeholder="Enter "+skill+" score";

div.appendChild(label);
div.appendChild(input);
});

document.getElementById("skill_names").value=skillsArray.join(",");

document.getElementById("step1").classList.add("hidden");
document.getElementById("step2").classList.remove("hidden");
}

function validateSkills(){

let scores=document.getElementsByClassName("skillScore");

for(let i=0;i<scores.length;i++){
if(scores[i].value===""){
document.getElementById("error2").innerText=
"Skill scores are compulsory.";
return false;
}
}
return true;
}

</script>

</body>
</html>
"""

def calculate_score(form):
    skills_text=form.get("skill_names")
    if not skills_text:
        return None
    skills=skills_text.split(",")
    total=0
    for skill in skills:
        value=form.get(f"score_{skill}")
        if value is None or value=="":
            return None
        total+=int(value)
    return round(total/len(skills),2)

@app.route("/",methods=["GET","POST"])
def home():
    score=None
    if request.method=="POST":
        score=calculate_score(request.form)
    return render_template_string(TEMPLATE,score=score)

if __name__=="__main__":
    app.run(debug=True)
