from flask import Flask, request

app = Flask(__name__)

# Home page with internship form
@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Internship Application Form</title>
        <style>
            body { font-family: Arial; background-color: #f0f0f0; padding: 20px; }
            h2 { color: #333; }
            input, button { padding: 10px; margin: 5px 0; width: 300px; }
            button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            button:hover { background-color: #45a049; }
            .container { background: white; padding: 20px; border-radius: 8px; width: 350px; margin: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Internship Application Form</h2>
            <form action="/submit" method="post">
                <input type="text" name="name" placeholder="Full Name" required><br>
                <input type="email" name="email" placeholder="Email" required><br>
                <input type="text" name="college" placeholder="College Name" required><br>
                <input type="text" name="skills" placeholder="Skills (comma separated)" required><br>
                <button type="submit">Submit</button>
            </form>
        </div>
    </body>
    </html>
    '''

# Handle form submission
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
    <head><title>Submitted</title></head>
    <body style="font-family: Arial; padding:20px;">
        <h3>Thanks {name}, your form has been submitted!</h3>
        <p><a href="/">Submit another response</a></p>
    </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)
