# standard
import datetime
import os
import bson

# third party libraries
from flask import Flask, render_template, url_for, request, session, redirect


# my app
import mongo


app = Flask(__name__)
app.secret_key = b'mysecret'

mongo_username = os.environ['DB_USER_USERNAME']
mongo_password = os.environ['DB_USER_PASSWORD']
mongo_addr = os.environ['DB_MONGO_LINK']
mongo_dbname = os.environ['DB_MONGO_DATABASE']
mongo_uri = "mongodb+srv://{username}:{password}@{db_mongo_addr}/{db_mongo_name}?retryWrites=true&w=majority".format(username=mongo_username, password=mongo_password, db_mongo_addr=mongo_addr, db_mongo_name=mongo_dbname)

app.config['MONGO_DBNAME'] = mongo_dbname
app.config['MONGO_URI'] = mongo_uri


@app.route('/')
def index():
    if "user_id" in session:
        user = mongo.db.users.find_one({"_id": bson.ObjectId(session["user_id"])})
        user_budget = mongo.db.budgets.find_one({"_id": user["settings"]["default_budget"]})
        print("redirecting to ", user_budget["_id"])
        print(url_for("budget", budget_id=str(user_budget["_id"])))
        return redirect(url_for("budget", budget_id=str(user_budget["_id"])))

    return render_template('index.html')



@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email' : request.form['email']})

    if login_user:
        if mongo.pwd_context.verify(request.form['password'], login_user['password']):
            session['email'] = login_user['email']
            session["user_id"] = str(login_user["_id"])
            print("user logged in:", login_user["email"])

            login_user['settings']['last_login'] = datetime.datetime.utcnow()
            users.replace_one({'email':login_user['email']}, login_user)

            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/logout', methods=['GET'])
def logout():
    session.pop("email")
    session.pop("user_id")
    return redirect(url_for('index'))
    


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email' : request.form['email']})

        if existing_user is None:
            mongo.user_create(request.form['email'], request.form['password'])
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')


@app.route("/api/v<version>/budget/<budget_id>")
def api_budget(api_version, budget_id):
    if "user_id" not in session:
        return {"error": "not authenticated"}

    user = mongo.db.users.find_one({"_id": bson.ObjectId(session["user_id"])})
    budget = mongo.db.budgets.find_one({"_id": bson.ObjectId(budget_id)})

    if not budget:
        return {"error": "budget does not exist"}

    if budget["_id"] not in user["budgets"]:
        return {"error": "budget does not belong to user"}

    categories = {}
    render_categories = []
    for g_id in budget["category_groups"]:
        group = mongo.db.category_groups.find_one({"_id": g_id})
        categories[group["name"]] = []
        for c_id in group["categories"]:
            category = mongo.db.categories.find_one({"_id": c_id})
            categories[group["name"]].append(category)
            render_categories.append('{} - {}'.format(group["name"], category["name"]))

    

@app.route('/budget/<budget_id>')
def budget(budget_id):
    print("inside budget")
    # check if: user is logged in, budget exists, budget belongs to logged user
    if "user_id" not in session:
        return "you need to login"
        return redirect(url_for("index"))

    user = mongo.db.users.find_one({"_id": bson.ObjectId(session["user_id"])})
    print(user)
    budget = mongo.db.budgets.find_one({"_id": bson.ObjectId(budget_id)})

    if not budget:
        return "budget does not exist"

    if budget["_id"] not in user["budgets"]:
        return "this budget does not belong to you"

    categories = {}
    render_categories = []
    for g_id in budget["category_groups"]:
        group = mongo.db.category_groups.find_one({"_id": g_id})
        categories[group["name"]] = []
        for c_id in group["categories"]:
            category = mongo.db.categories.find_one({"_id": c_id})
            categories[group["name"]].append(category)
            render_categories.append('{} - {}'.format(group["name"], category["name"]))
            
    return render_template('dashboard.html', email=user["email"], budget_lines=sorted(render_categories))




if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True, host="0.0.0.0", port=80)

