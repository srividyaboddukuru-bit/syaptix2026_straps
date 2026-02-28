from flask import Flask, request, render_template_string, redirect, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "hackathon_secret_key"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- USERS ----------------
USERS = {
    "student1": {"password": "stud123", "role": "student"},
    "provider1": {"password": "prov123", "role": "provider"}
}

# ---------------- STORAGE ----------------
INTERNSHIPS = []
STUDENT_APPLICATIONS = []

# ---------------- MATCH ENGINE ----------------
def normalize_score(score):
    return min(max(score, 20), 95)

def calculate_match(student_form, internship):
    weighted_sum = 0
    total_weight = 0
    matched = 0
    reasoning = []
    contributions = []

    for skill, weight in internship["skills"].items():
        val = student_form["skills"].get(skill)
        score = normalize_score(val) if val is not None else 50
        if val is not None:
            matched += 1
        contribution = score * weight
        weighted_sum += contribution
        total_weight += weight
        reasoning.append(f"{skill}: {score}/100 × {round(weight,2)}")
        contributions.append((skill, round(contribution,2)))

    competency = weighted_sum / total_weight if total_weight else 0
    coverage = (matched / len(internship["skills"])) * 100 if internship["skills"] else 0
    cgpa_score = (student_form["cgpa"] / 10) * 100

    final = round(0.5*competency + 0.3*coverage + 0.2*cgpa_score,2)
    summary = "Excellent Match" if final>=80 else "Good Match" if final>=60 else "Partial Match"
    return final, reasoning, contributions, summary

# ---------------- BASE STYLE ----------------
BASE_STYLE = """
<style>
body{
margin:0;
font-family:'Segoe UI';
background:#a8d0e6;
display:flex;
justify-content:center;
align-items:center;
min-height:100vh;
}
.container{
background:rgba(255,255,255,0.95);
padding:50px 40px;
border-radius:20px;
box-shadow:0 20px 40px rgba(0,0,0,0.3);
width:600px;
max-height:90vh;
overflow-y:auto;
text-align:center;
}
input,textarea,select{
width:95%;
display:block;
padding:10px;
margin:10px auto;
border-radius:10px;
border:1px solid #ccc;
font-size:15px;
}
button{
padding:12px 20px;
border:none;
border-radius:12px;
background:#0066ff;
color:white;
font-weight:bold;
cursor:pointer;
}
button:hover{
background:#004dcc;
}
.card{
background:#f2f2f2;
padding:8px;
margin:6px 0;
border-radius:8px;
text-align:left;
}
a{color:#0066ff;text-decoration:none;}
a:hover{text-decoration:underline;}
label{
display:block;
margin-top:10px;
font-weight:bold;
}
</style>
"""

# ---------------- LOGIN ----------------
LOGIN_PAGE = BASE_STYLE + """
<div class="container">
<h2>Login</h2>
<form method="POST">
<input name="username" placeholder="Username" required>
<input name="password" type="password" placeholder="Password" required>
<div style="color:red">{{error}}</div>
<button>Login</button>
</form>
</div>
"""

@app.route("/", methods=["GET","POST"])
def login():
    error=""
    if request.method=="POST":
        u=request.form["username"]
        p=request.form["password"]
        if u in USERS and USERS[u]["password"]==p:
            session["user"]=u
            session["role"]=USERS[u]["role"]
            return redirect("/dashboard")
        error="Invalid Credentials"
    return render_template_string(LOGIN_PAGE,error=error)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    html = BASE_STYLE + f"<div class='container'><h2>Welcome {session['user']} ({session['role']})</h2>"
    if session["role"]=="student":
        html += "<a href='/student_form'>Apply Internship</a><br><br>"
        html += "<a href='/student_applications'>My Applications</a><br><br>"
    else:
        html += "<a href='/provider_form'>Create Internship</a><br><br>"
        html += "<a href='/view_applicants'>View Applicants</a><br><br>"
    html += "<a href='/logout'>Logout</a></div>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- PROVIDER FORM ----------------
PROVIDER_PAGE = BASE_STYLE + """
<div class="container">
<h2>Create Internship</h2>
<form method="POST">
<input name="title" placeholder="Internship Title" required>
<select name="type" required>
<option>AI Intern</option>
<option>Web Developer</option>
<option>Data Analyst</option>
<option>ML Intern</option>
<option>Other</option>
</select>
<input name="duration" type="number" placeholder="Duration (weeks)" required>
<input name="stipend" type="number" step="0.01" placeholder="Stipend">
<input name="cgpa_cutoff" type="number" step="0.01" placeholder="CGPA Cutoff" required>

<h4>Skills</h4>
<div id="skillsContainer"></div>
<button type="button" onclick="addSkill()">Add Skill</button><br><br>

<button>Create</button>
</form>

<script>
function addSkill(){
let div=document.createElement("div");
div.innerHTML="Skill: <input name='skill_name[]' required> Weight: <input name='skill_weight[]' required><br>";
document.getElementById("skillsContainer").appendChild(div);
}
</script>
</div>
"""

@app.route("/provider_form", methods=["GET","POST"])
def provider_form():
    if session.get("role")!="provider":
        return redirect("/")
    if request.method=="POST":
        names=request.form.getlist("skill_name[]")
        weights=request.form.getlist("skill_weight[]")
        skills={n:float(w) for n,w in zip(names,weights)}
        total=sum(skills.values())
        for k in skills:
            skills[k]/=total
        INTERNSHIPS.append({
            "title":request.form["title"],
            "type":request.form["type"],
            "duration":int(request.form["duration"]),
            "stipend":float(request.form.get("stipend",0)),
            "cgpa_cutoff":float(request.form["cgpa_cutoff"]),
            "skills":skills
        })
        return redirect("/dashboard")
    return render_template_string(PROVIDER_PAGE)

# ---------------- STUDENT FORM ----------------
STUDENT_PAGE = BASE_STYLE + """
<div class="container">
<h2>Apply Internship</h2>
<form method="POST" enctype="multipart/form-data">

<label for="name">Full Name:</label>
<input type="text" id="name" name="name" placeholder="Full Name" required>

<input name="cgpa" type="number" step="0.01" placeholder="CGPA" required>
<input name="projects" placeholder="Projects / Achievements">

<h4>Select Internship</h4>
<select name="internship_idx" required>
{% for internship in internships %}
<option value="{{ loop.index0 }}">
{{ internship['title'] }} - Duration: {{ internship['duration'] }} weeks, Stipend: {{ internship['stipend'] }}, CGPA Cutoff: {{ internship['cgpa_cutoff'] }}
</option>
{% endfor %}
</select>

<h4>Skills</h4>
{% for skill in all_skills %}
<input type="number" name="skill_{{skill}}" placeholder="{{skill}}" required>
{% endfor %}

<h4>Resume (Upload File)</h4>
<input type="file" name="resume" required>

<h4>Cover Letter</h4>
<textarea name="cover_letter" placeholder="Write your cover letter here..." rows="5" required></textarea>

<button>Submit</button>
</form>
</div>
"""

@app.route("/student_form", methods=["GET","POST"])
def student_form():
    if session.get("role")!="student":
        return redirect("/")
    if not INTERNSHIPS:
        return BASE_STYLE + "<div class='container'>No internships yet</div>"

    all_skills = list({s for i in INTERNSHIPS for s in i["skills"]})

    if request.method=="POST":
        name = request.form.get("name")
        skills = {s:int(request.form[f"skill_{s}"]) for s in all_skills}
        cgpa = float(request.form["cgpa"])
        idx = int(request.form["internship_idx"])
        internship = INTERNSHIPS[idx]

        resume = request.files["resume"]
        resume_path = os.path.join(UPLOAD_FOLDER, secure_filename(resume.filename))
        resume.save(resume_path)

        cover_letter_text = request.form["cover_letter"]

        student = {
            "name": name,
            "skills": skills,
            "cgpa": cgpa,
            "resume": resume_path,
            "cover_letter": cover_letter_text,
            "projects": request.form.get("projects","")
        }

        score, reason, contri, summary = calculate_match(student, internship)
        STUDENT_APPLICATIONS.append({
            "student": student,
            "internship_title": internship["title"],
            "score": score,
            "reasoning": reason,
            "contributions": contri,
            "summary": summary,
            "selected": None
        })

        output = BASE_STYLE + "<div class='container'>"
        output += f"<h2>{summary}</h2><h3>Score: {score}%</h3>"
        output += "<h4>Reasoning:</h4>"
        for r in reason: output+=f"<div class='card'>{r}</div>"
        output += "<h4>Skill Contributions:</h4>"
        for s,c in contri: output+=f"<div class='card'>{s} → {c}</div>"
        output += "<br><a href='/student_applications'>View My Applications</a>"
        output += "<br><a href='/student_form'>Submit Another Response</a>"
        output += "</div>"
        return output

    return render_template_string(STUDENT_PAGE, internships=INTERNSHIPS, all_skills=all_skills)

# ---------------- STUDENT APPLICATION STATUS ----------------
@app.route("/student_applications")
def student_applications():
    if session.get("role")!="student":
        return redirect("/")
    html = BASE_STYLE + "<div class='container'><h2>My Applications</h2>"
    for app in STUDENT_APPLICATIONS:
        html += f"<b>{app['student']['name']}</b> applied for {app['internship_title']}<br>"
        html += f"CGPA: {app['student']['cgpa']}<br>"
        html += f"Projects: {app['student'].get('projects','')}<br>"
        html += f"Score: {app['score']}%<br>"
        status = app['selected']
        html += f"Status: {'Pending' if status is None else ('Selected' if status else 'Rejected')}<br><hr>"
    html += "<a href='/dashboard'>Back</a></div>"
    return html

# ---------------- VIEW APPLICANTS FOR PROVIDER ----------------
@app.route("/view_applicants")
def view_applicants():
    if session.get("role")!="provider":
        return redirect("/")
    html = BASE_STYLE + "<div class='container'><h2>Applicants</h2>"
    for idx, a in enumerate(STUDENT_APPLICATIONS):
        html += f"<b>{a['student'].get('name','Unknown')}</b> applied for {a['internship_title']}<br>"
        html += f"CGPA: {a['student']['cgpa']}, Score: {a['score']}%<br>"
        html += f"Projects: {a['student'].get('projects','')}<br>"
        html += f"<b>Summary:</b> {a['summary']}<br>"
        status = a['selected']
        html += f"Status: {'Pending' if status is None else ('Selected' if status else 'Rejected')}<br>"
        html += f"<a href='/select/{idx}'>Select</a> | <a href='/reject/{idx}'>Reject</a><hr>"
    html += "<a href='/dashboard'>Back</a></div>"
    return html

@app.route("/select/<int:idx>")
def select(idx):
    if idx<len(STUDENT_APPLICATIONS): STUDENT_APPLICATIONS[idx]["selected"]=True
    return redirect("/view_applicants")

@app.route("/reject/<int:idx>")
def reject(idx):
    if idx<len(STUDENT_APPLICATIONS): STUDENT_APPLICATIONS[idx]["selected"]=False
    return redirect("/view_applicants")

# ---------------- RUN ----------------
if __name__=="__main__":
    app.run(debug=True)
