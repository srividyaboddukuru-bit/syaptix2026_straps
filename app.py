from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Internship Application</title>

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
width:450px;
box-shadow:0 0 15px rgba(0,0,0,0.25);
}

h2{text-align:center}

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
font-weight:bold;
}

.hidden{display:none;}
.error{color:red;text-align:center;}
</style>
</head>

<body>
<div class="container">

{% if not score %}

<!-- SLIDE 1 -->
<div id="slide1">
<h2>Personal Details</h2>
<input id="name" placeholder="Full Name">
<input id="email" placeholder="Email">
<input id="mobile" placeholder="Mobile">
<input id="city" placeholder="City">
<button onclick="nextSlide(2)">Next</button>
</div>

<!-- SLIDE 2 -->
<div id="slide2" class="hidden">
<h2>Academic Details</h2>
<input id="college" placeholder="College Name">
<input placeholder="Degree">
<input placeholder="Branch">
<input placeholder="Year of Study">
<button onclick="nextSlide(3)">Next</button>
</div>

<!-- SLIDE 3 -->
<div id="slide3" class="hidden">
<h2>Skills & Preferences</h2>

<input id="skills" placeholder="Technical Skills (Python,ML,HTML)">

<input placeholder="Preferred Internship Role">

<select>
<option>Work Mode</option>
<option>Remote</option>
<option>Hybrid</option>
<option>Onsite</option>
</select>

<label>
<input type="checkbox" id="confirm">
I confirm the information is correct
</label>

<div id="error1" class="error"></div>

<button onclick="goToSkills()">Proceed to Skill Scoring</button>
</div>

<form method="POST" onsubmit="return validateSkills()">

<div id="step2" class="hidden">
<h2>Skill Proficiency (1-100)</h2>

<div id="skillInputs"></div>

<input type="hidden" name="skill_names" id="skill_names">

<div id="error2" class="error"></div>

<button>Submit Application</button>
</div>

</form>

{% endif %}

{% if score %}

<h2>Match Score</h2>

<p><b>Your Match Score:</b> {{score}}%</p>

<p><b>Thanks for registering in internship... further details will be mailed to you.</b></p>

<form method="GET">
<button>Other Response</button>
</form>

{% endif %}

</div>

<script>

function nextSlide(n){
document.querySelectorAll("[id^='slide']")
.forEach(s=>s.classList.add("hidden"));
document.getElementById("slide"+n)
.classList.remove("hidden");
}

let skillsArray=[];

function goToSkills(){

let name=v("name");
let email=v("email");
let mobile=v("mobile");
let college=v("college");
let skills=v("skills");
let confirm=document.getElementById("confirm").checked;

if(!name||!email||!mobile||!college||!skills||!confirm){
document.getElementById("error1").innerText=
"Please complete required details.";
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

document.getElementById("skill_names").value=
skillsArray.join(",");

document.querySelectorAll("[id^='slide']")
.forEach(s=>s.classList.add("hidden"));

document.getElementById("step2")
.classList.remove("hidden");
}

function v(id){
return document.getElementById(id).value.trim();
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

</script>

</body>
</html>
"""

def calculate_score(form):
    skills=form.get("skill_names").split(",")
    total=sum(int(form.get(f"score_{s}")) for s in skills)
    return round(total/len(skills),2)

@app.route("/",methods=["GET","POST"])
def home():
    score=None
    if request.method=="POST":
        score=calculate_score(request.form)
    return render_template_string(TEMPLATE,score=score)

if __name__=="__main__":
    app.run(debug=True)
