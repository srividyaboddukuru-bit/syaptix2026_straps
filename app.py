from flask import Flask, request, render_template_string

app = Flask(__name__)

# ------------------------------------------------
# Matching Model
# ------------------------------------------------
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


# ------------------------------------------------
# Score Calculation (STEP 3)
# ------------------------------------------------
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
    reasoning.append("Competency alignment calculated from submitted skills.")

    gaps = [abs(PROJECT[k]-skills[k]) for k in PROJECT]
    requirement_fit = 100 - (sum(gaps)/len(gaps))
    reasoning.append("Requirement mapping based on skill-gap analysis.")

    fairness = fairness_boost(resource)
    reasoning.append("Fairness-aware adjustment applied.")

    final_score = (
        alignment*WEIGHTS["competency"]
        + requirement_fit*WEIGHTS["requirement"]
        + experience*WEIGHTS["experience"]
        + learning*WEIGHTS["learning"]
        + fairness*WEIGHTS["fairness"]
    )

    reasoning.append(f"✅ Final Match Score = {final_score:.2f}")

    return round(final_score,2), reasoning


# ------------------------------------------------
# WEB APP TEMPLATE
# ------------------------------------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Explainable Internship Platform</title>

<style>

body{
margin:0;
font-family:Segoe UI;
background:linear-gradient(135deg,#ff9a9e,#ffb347,#ffe066);
height:100vh;
display:flex;
justify-content:center;
align-items:center;
color:#222;
}

.container{
width:520px;
background:white;
padding:30px;
border-radius:15px;
box-shadow:0 8px 25px rgba(0,0,0,0.25);
}

h1{text-align:center;color:#ff5e78;}

input{
width:100%;
padding:10px;
margin:8px 0;
border:1px solid #ccc;
border-radius:6px;
}

button{
width:100%;
padding:12px;
border:none;
border-radius:8px;
font-weight:bold;
cursor:pointer;
margin-top:10px;
color:white;
}

.next-btn{background:#ff7f50;}
.submit-btn{background:#ff5e78;}

.section{display:none;}

.result{
background:#fff3cd;
padding:15px;
border-radius:10px;
margin-top:15px;
}

.thankyou{
text-align:center;
font-size:22px;
color:#28a745;
font-weight:bold;
margin-top:15px;
}

.error{
color:red;
text-align:center;
}

</style>

<script>

/* STEP CONTROL */
function goToStep2(){
let name=document.getElementById("name").value.trim();
let gmail=document.getElementById("gmail").value.trim();
let college=document.getElementById("college").value.trim();

if(!name || !gmail || !college){
document.getElementById("error1").innerText =
"⚠ Fill all basic details first.";
return;
}

document.getElementById("step1").style.display="none";
document.getElementById("step2").style.display="block";
}

/* validate skills before submit */
function validateStep2(){
let inputs=document.querySelectorAll("#step2 input");
for(let i=0;i<inputs.length;i++){
if(inputs[i].value===""){
alert("Please complete all skill details.");
return false;
}
}
return true;
}

</script>

</head>

<body>

<div class="container">

<h1>🌟 Internship Application</h1>

<form method="POST" onsubmit="return validateStep2()">

<!-- STEP 1 -->
<div id="step1">

<input id="name" name="name" placeholder="Full Name">
<input id="gmail" name="gmail" placeholder="Gmail Address">
<input id="college" name="college" placeholder="College Name">

<div id="error1" class="error"></div>

<button type="button" class="next-btn" onclick="goToStep2()">
Next → Skills
</button>

</div>

<!-- STEP 2 -->
<div id="step2" class="section">

<h3>Skill Assessment (1–100)</h3>

<input name="python" placeholder="Python Skill">
<input name="ml" placeholder="Machine Learning Skill">
<input name="communication" placeholder="Communication Skill">
<input name="problem_solving" placeholder="Problem Solving Skill">
<input name="experience" placeholder="Experience Level">
<input name="learning" placeholder="Learning Potential">
<input name="resource" placeholder="Resource Access Index">

<button class="submit-btn">
Submit Application
</button>

</div>

</form>

{% if score %}

<!-- STEP 3 RESULT -->
<div class="result">

<h2>Match Score: {{score}}</h2>

<ul>
{% for r in reasoning %}
<li>{{r}}</li>
{% endfor %}
</ul>

<div class="thankyou">
🎉 Thank you for registering!  
Your internship application has been submitted successfully.
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

    return render_template_string(
        TEMPLATE,
        score=score,
        reasoning=reasoning
    )


if __name__ == "__main__":
    app.run(debug=True)
