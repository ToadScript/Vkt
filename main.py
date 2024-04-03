import os

from flask import Flask, render_template, request, session, redirect,url_for
from pyairtable import Api

#----------#

app = Flask(__name__)
app.secret_key = "VKT"

secret = os.environ
api = Api(secret['TOKEN'])

#----------#

def update_session(data):
  session['name'] = data['Name']
  session['email'] = data['Email']
  session['password'] = data['Password']
  session['record_id'] = data['RECORD_ID']

@app.route('/', methods=['GET'])
def get_books():
  table = api.table(secret['APP'], 'Books')
  books = []
  
  for record in table.all():
    #print(record)
    name = record["fields"].get("Name")
    cover_url = record["fields"].get("Cover")[0].get("url")
    id = record["fields"].get("RECORD_ID")
    
    print(cover_url)
    book = {
      "name": name,
      "cover_url": cover_url,
      "id": id
    }
    books.append(book)
  return render_template('books.html', data=books)

@app.route('/login', methods=['GET'])
def render_login():
  return render_template('login.html')

@app.route('/signup', methods=['GET'])
def render_signup():
  return render_template('signup.html')

#----------#

@app.route('/add-answer', methods=['POST'])
def add_answer():
  context = request.form['context']
  #attachment = request.form['attachment']
  id = request.form['id']
 # attachment = request.files['attachment']
  session['submission_id'] = id
  table = api.table(secret['APP'], 'Answers')
  
  table.create({
    'Answer': context,
    #'Attachment': [attachment],
    'Submission': [id],
    'Submitters': [session["record_id"]],
  })
  
  return redirect(url_for('get_submission_2'))


@app.route('/book', methods=['POST'])
def get_book():
  id = request.form['id']
  
  table = api.table(secret['APP'], 'Books')
  record = table.get(id)
  table = api.table(secret['APP'], 'Submissions')
  formula = "{Book} = '" + id + "'"
  submissions = table.all(formula=formula)

  name = record["fields"].get("Name")
  cover_url = record["fields"].get("Cover")[0].get("url")

  book = {
    "name": name,
    "cover_url": cover_url
  }

  return render_template('book.html', book=book, submissions=submissions)

@app.route('/submission', methods=['POST'])
def get_submission():
  id = request.form['id']
  
  table = api.table(secret['APP'], 'Answers')
  record = table.get(id)
  formula = "{Submission} = '" + id + "'"

  answers = table.all(formula=formula)

  name = record["fields"].get("Content")
  cover_url = record["fields"].get("Attachment")[0].get("url")
  
  submission = {
    "name": name,
    "cover_url": cover_url,
    "id": id,
  }
  
  return render_template('submission.html', submission=submission, answers=answers)

@app.route('/submission', methods=['GET'])
def get_submission_2():
  id = session['submission_id']
  session['submission_id'] = None
  
  table = api.table(secret['APP'], 'Answers')
  record = table.get(id)
  formula = "{Submission} = '" + id + "'"

  answers = table.all(formula=formula)

  name = record["fields"].get("Content")
  cover_url = record["fields"].get("Attachment")[0].get("url")

  submission = {
    "name": name,
    "cover_url": cover_url,
    "id": id,
  }

  return render_template('submission.html', submission=submission, answers=answers)

#----------#

@app.route('/login', methods=['POST'])
def login():
  table = api.table(secret['APP'], secret['SUBMITTERS_TABLE'])
  
  email = request.form['email']
  password = request.form['password']

  record = table.first(formula=f'Email = "{email}"')
 
  if record:
    data = record['fields']
    
    if data['Password'] == password:
      update_session(data)
      
      return redirect('/')
    else:
      return render_template('login.html', email=email, error='Wrong email or password')
  else:
    return render_template('login.html', email=email, error='Wrong email or password')
    
@app.route('/signup', methods=['POST'])
def signup():
  api = Api(secret['TOKEN'])
  table = api.table(secret['APP'], secret['SUBMITTERS_TABLE'])
  
  # Info
  name = request.form['name']
  email = request.form['email']
  password = request.form['password']
  
  record = table.first(formula=f'Email = "{email}"')

  if record:
    return render_template('signup.html', name=name, email=email, error='Email already exists')
  else:
    table.create({'Name': name, 'Email': email, 'Password': password})
    return redirect('/')

@app.route('/logout', methods=['GET'])
def logout():
  session.clear()
  return redirect('/')

#----------#

app.run(host='0.0.0.0', port=81)
