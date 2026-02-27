from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    return '''
<html>
<head>
<title>✨ Internship Form ✨</title>
<style>
/* Full page gradient */
body {
    margin: 0;
    height: 100vh;
    font-family: 'Arial', sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    background: linear-gradient(135deg, #ff6a00, #ee0979);
}

/* Glassmorphism card */
.card {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 40px;
    width: 380px;
    box-shadow: 0 8px 32px 0 rgba(0,0,0,0.25);
    text-align: center;
    color: white;
    animation: fadeIn 1s ease;
}

/* Floating label style */
input {
    width: 100%;
    padding: 14px 10px;
    margin: 10px 0 20px 0;
    border: none;
    border-bottom: 2px solid white;
    background: transparent;
    color: white;
    font-size: 16px;
    outline: none;
    transition: 0.3s;
}
input:focus {
    border-bottom: 2px solid #fff700;
}
input::placeholder {
    color: rgba(255,255,255,0.7);
}

/* Button style */
button {
    padding: 12px;
    width: 100%;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #ff6a00;
    background: white;
    transition: 0.4s;
}
button:hover {
    background: #fff700;
    color: #ee0979;
}

/* Title animation */
h2 {
    margin-bottom: 30px;
    text-shadow: 0 0 10px #fff700;
    animation: glow 1.5s infinite alternate;
}

/* Animations */
@keyframes glow {
    from { text-shadow: 0 0 5px #fff700; }
    to { text-shadow: 0 0 20px #fff700; }
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(-20px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
</head>
<body>
<div class="card">
<h2>🚀 Internship Application</h2>
<form action="/submit" method="post">
<input type="text" name="name" placeholder="Full Name" required>
<input type="email" name="email" placeholder="Email" required>
<input type="text" name="college" placeholder="College Name" required>
<input type="text" name="skills" placeholder="Skills (comma separated)" required>
<button type="submit">Submit ✨</button>
</form>
</div>
</body>
</html>
'''

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    college = request.form['college']
    skills = request.form['skills']

    # Save data to CSV
    with open('submissions.csv', 'a') as file:
        file.write(f"{name},{email},{college},{skills}\n")

    return f'''
<html>
<head>
<title>Submitted!</title>
<style>
body {{
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    background: linear-gradient(135deg, #ee0979, #ff6a00);
    font-family: 'Arial', sans-serif;
}}
.success {{
    background: rgba(255,255,255,0.2);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}}
.success h3 {{
    font-size: 24px;
    margin-bottom: 15px;
    animation: glow 1.5s infinite alternate;
    text-shadow: 0 0 10px #fff700;
}}
.success a {{
    display: inline-block;
    margin-top: 20px;
    padding: 12px 20px;
    border-radius: 10px;
    background: white;
    color: #ee0979;
    text-decoration: none;
    font-weight: bold;
    transition: 0.3s;
}}
.success a:hover {{
    background: #fff700;
    color: #ee0979;
}}
@keyframes glow {{
    from {{ text-shadow: 0 0 5px #fff700; }}
    to {{ text-shadow: 0 0 20px #fff700; }}
}}
</style>
</head>
<body>
<div class="success">
<h3>🎉 Thanks {name}!</h3>
<p>Your internship application has been submitted successfully.</p>
<a href="/">Submit Another</a>
</div>
</body>
</html>
'''

if __name__ == "__main__":
    app.run(debug=True)
