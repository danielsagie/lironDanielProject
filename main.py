from flask import Flask, render_template, request, url_for, redirect, session
from pymongo import MongoClient
import hashlib  # for password hashing
from bson import json_util
from bson import ObjectId
app = Flask(__name__)

app.secret_key = 'fakekey'

#create DB
try:
    client = MongoClient('mongodb://localhost:27017/')  
    db = client['Website_db']
    print("mongo connect")
except Exception:
    print("enable to connect mongodb")

#route to home page
@app.route('/', methods=('GET', 'POST'))
@app.route('/home', methods=('GET', 'POST'))
def home_page():
    return render_template('index.html')
# about page
@app.route('/about_page')
def about_page():
    return render_template('about.html')

#first list to create after registeration
@app.route('/first-list', methods=['GET','POST'])
def first_list_page():
    user = session.get('user')
    if not user:
        return redirect(url_for('register'))
    item = request.form.get('item')
    quantity = request.form.get('quantity')
    if request.method == 'POST':
        # ...
        if item and quantity:
            user_items_collection = db[user['_id']]  # Use the user's id as collection name
            user_items_collection.insert_one({"item": item, "quantity": quantity})

    user_items_collection = db[user['_id']]  # Use the user's id as collection name
    items = user_items_collection.find()

    return render_template('first-list.html', user=user, items=items)


#insert items to the DB to a collection called by the user id
@app.route('/save-items', methods=['POST'])
def save_items():
    user = session.get('user')
    if not user:
        return "User not in session", 401

    data = request.json
    items = data.get('items')

    if items:
        user_items_collection = db[user['_id']]  # Use the user's id as collection name
        user_items_collection.insert_many(items)
        return redirect(url_for('new_list'))
    else:
        return {"message": "No items provided"}, 400


# create new list when you already have an account
@app.route('/new_list', methods=('GET', 'POST'))
def new_list_page():
    user = session.get('login_user')
    if user:
        user_items_collection = db[user['_id']]  # Use the user's id as collection name
        items = user_items_collection.find()  # Retrieve all items from the collection
        return render_template('new_list.html', items=items)
    else:
        return redirect(url_for('login_page'))
   
# registeration page
@app.route('/create-accont')
def create_account():
    return render_template('create-account.html')


# registeration function
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')

    # Hash the password for security
    password = hashlib.sha256(request.form.get('password').encode()).hexdigest()

    try:
        db.users.insert_one({"username": username, "email": email, "password": password})
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred", 400
    
    user = db.users.find_one({"username": username, "password": password})
    if user:
        user['_id'] = str(user['_id'])
        session['user'] = user # Add the username to the session
        return redirect(url_for('first_list_page'))
    else:
        return "Invalid username or password", 401
    # return redirect(url_for('login_page'))


# login page
@app.route('/login_page')
def login_page():
    return render_template('login.html')

# function that check if user exist and create a session
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    
    password = hashlib.sha256(request.form.get('password').encode()).hexdigest()

    
    user = db.users.find_one({"username": username, "password": password})

    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        session['login_user'] = user  # Store the entire user document in the session
        return redirect(url_for('new_list_page'))
    else:
        return "Invalid username or password", 401
    
# create temporary collection
@app.route('/temp_col', methods=['POST'])
def temp_col():
    user = session.get('login_user')
    if user:
        temp_collection_name = f"temp{db[user['_id']]}"  # Use the _id from the user document
        temp_collection = db[temp_collection_name]

        data = request.json
        items = data.get('items')

        if items:
            documents = [{"item": item["item"], "quantity": item["quantity"]} for item in items]
            temp_collection.insert_many(documents)
            return {"message": "Items added to temporary collection"}
        else:
            return {"message": "No items provided"}, 400
    else:
        return redirect(url_for('login_page'))

# function that taking the user out of the session
@app.route('/logout')
def logout():
    user = session.get('login_user')
    if user:
        temp_collection_name = f"temp{db[user['_id']]}"
        db.drop_collection(temp_collection_name)  # Delete the temporary collection
    session.pop('login_user', None)
    return redirect(url_for('home_page'))


if __name__ == '__main__':
  app.run(debug=True, host="0.0.0.0")
