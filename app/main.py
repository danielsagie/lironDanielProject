from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from json import JSONEncoder
from pymongo import MongoClient
import hashlib 
import os
from bson import ObjectId

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
app.secret_key = 'fakekey'

MONGO_URI=os.environ.get('MONGO_URI')

try:
    client = MongoClient(MONGO_URI)  
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

# registeration page
@app.route('/create-accont')
def create_account():
    return render_template('create-account.html')


# registeration function!
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    email = request.form.get('email')

    # Hash the password for security
    password = hashlib.sha256(request.form.get('password').encode()).hexdigest()

    existing_user = db.users.find_one({"username": username})
    if existing_user:
        return render_template('create-account.html', message='Username already exists.')
    # Insert new user into database
    try:
        db.users.insert_one({"username": username, "email": email, "password": password})
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred", 400
    
    # Validate inserted data
    user = db.users.find_one({"username": username, "password": password})
    if user:
        user['_id'] = str(user['_id'])
        session['first_login'] = user  # Add the username to the session
        return redirect(url_for('login_page'))

    return "Invalid username or password", 401


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
        user['_id'] = str(user['_id'])  # Convert ObjectId to string before storing in session
        session['login_user'] = user
        return redirect(url_for('my_lists')) 
    else:
        return "Invalid username or password", 401



@app.route('/new_list/<list_id>', methods=('GET', 'POST'))
def new_list_page(list_id):
    user = session.get('login_user')
    if user:
        collection = db[f"{user['username']}_lists"]
        list_data = collection.find_one({"_id": ObjectId(list_id)})
        if list_data:
            name = list_data['name']
        else:
            name = None
        items_collection = db[list_id]
        items = list(items_collection.find())
        item_ids = [str(item['_id']) for item in items]
        return render_template('new_list.html', user=user, name=name,list_data=list_data, items=items, item_ids=item_ids)
    else:
        return redirect(url_for('login_page'))
    


@app.route('/get-items', methods=['GET'])
def get_items():
    user = session.get('login_user')
    if user:
        user_items_collection = db[f"{user['username']}_lists"]
        items = list(user_items_collection.find())
        # Convert ObjectId to string
        for item in items:
            item['_id'] = str(item['_id'])  # Convert ObjectId to string
        return jsonify(items)
    else:
        return jsonify([]), 401


#insert items to the DB to a collection called by the user id
@app.route('/save-items/<list_id>', methods=['POST'])
def save_items(list_id):
    user = session.get('login_user')
    if user:
        lists_collection = db[f"{user['username']}_lists"]
        list_data = lists_collection.find_one({"_id": ObjectId(list_id)})

        if list_data:
            data = request.json
            items = data.get('items')
            if items:
                items_collection = db[list_id]
                items_collection.insert_many(items)
                return redirect(url_for('new_list_page', list_id=list_id))
    return "Something went wrong"


@app.route('/delete_item/<string:rowId>/<list_id>', methods=['DELETE'])
def delete_item(rowId, list_id):
    user = session.get('login_user')
    if user :
        collection = db[list_id]
        collection.delete_one({'_id':ObjectId(rowId)})
        return "deleted"
    else:
        return "not deleted"

# function that taking the user out of the session
@app.route('/logout')
def logout():
    user = session.get('login_user')
    if user:
        session.pop('login_user', None)
    return redirect(url_for('home_page'))



@app.route('/submit_list', methods=['POST'])
def submit_list():
    user = session.get('login_user')
    if user:
        list_name = request.form.get('list_name')
        if list_name:
            existing_list = db[f"{user['username']}_lists"].find_one({"name": list_name})
            if existing_list:
                return "List name already exists. Please choose a different name.", 400
            lists_collection = db[f"{user['username']}_lists"]
            new_list = lists_collection.insert_one({"name": list_name})
            new_list_id = new_list.inserted_id
            list_collection = str(new_list_id)
            db.create_collection(list_collection)

            return jsonify({"message": "List saved successfully", "list_id": str(new_list_id)})
        else:
            return "List name is empty", 400
    else:
        return "User not logged in", 401
    

@app.route('/my_lists')
def my_lists():
    user = session.get('login_user')
    if user:
        lists_collection = db[f"{user['username']}_lists"]
        lists = list(lists_collection.find())
        for item in lists:
            item['_id'] = str(item['_id'])
        return render_template('my_lists.html', lists=lists, user=user)
    else:
        return redirect(url_for('login_page'))


@app.route('/list/<list_id>')
def list_page(list_id):
    user = session.get('login_user')
    if user:
        lists_collection = db[f"{user['username']}_lists"]
        list_data = lists_collection.find_one({"_id": ObjectId(list_id)})
        if list_data:
            return render_template('new_list.html', user=user, list_data=list_data)
        else:
            return "List not found", 404
    else:
        return redirect(url_for('login_page'))


@app.route('/delete_list/<list_id>', methods=['DELETE'])
def delete_list(list_id):
    user = session.get('login_user')
    if user:
        db.drop_collection(list_id)
        db[f"{user['username']}_lists"].delete_one({'_id': ObjectId(list_id)})
        return jsonify({'message': 'List deleted successfully'})

    return jsonify({'message': 'List not found'}), 404

def start_app():
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        # For production, ensure that debug is set to False
        app.run(debug=False, host="0.0.0.0", port=port)

start_app()

#test3