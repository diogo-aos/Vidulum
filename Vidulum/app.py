from flask import Flask, render_template, url_for, request, session, redirect
#from flask.ext.pymongo import PyMongo
import bcrypt
import mongo

import datetime
import os


app = Flask(__name__)
app.secret_key = b'mysecret'

mongo_username = os.environ['DB_USER_USERNAME']
mongo_password = os.environ['DB_USER_PASSWORD']
mongo_addr = os.environ['DB_MONGO_LINK']
mongo_dbname = os.environ['DB_MONGO_DATABASE']
mongo_uri = "mongodb+srv://{username}:{password}@{db_mongo_addr}/{db_mongo_name}?retryWrites=true&w=majority".format(username=mongo_username, password=mongo_password, db_mongo_addr=mongo_addr, db_mongo_name=mongo_dbname)

app.config['MONGO_DBNAME'] = mongo_dbname
app.config['MONGO_URI'] = mongo_uri

#mongo = PyMongo(app)

@app.route('/')
def index():
    if 'email' in session:
        return render_template('dashboard.html', email=session['email'])
        return 'You are logged in as ' + session['email']

    return render_template('index.html')



@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'email' : request.form['email']})

    if login_user:
        if mongo.pwd_context.verify(request.form['password'], login_user['password']):
            session['email'] = login_user['email']

            login_user['settings']['last_login'] = datetime.datetime.utcnow()
            users.replace_one({'email':login_user['email']}, login_user)

            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('email')
    return redirect(url_for('index'))
    


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'email' : request.form['email']})
        print('result from mongo query:', existing_user)

        if existing_user is None:
            print('password is ', request.form['password'])
            mongo.user_create(request.form['email'], request.form['password'])
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')

@app.route('/budget', methods=['POST'])
def create_budget():
    if 'email' not in session:
        return 'you must log in'

    budgets = mongo.db.users
    budgets = mongo.db.budgets
    
    user = users.find_one({'email' : session['email']})





    if login_user:
        if mongo.pwd_context.verify(request.form['password'], login_user['password']):
            session['email'] = login_user['email']

            login_user['settings']['last_login'] = datetime.datetime.utcnow()
            users.replace_one({'email':login_user['email']}, login_user)

            return redirect(url_for('index'))

    return 'Invalid username/password combination'




#
#
#
#
#
#


def create_test_data():
    print('Adding test data to database...')
    u = db.User(email='akins.daos@gmail.com')

    b = db.Budget(name='firstBudget', user=u)
    #u.budgets.append(b)

    categories = {'House': ['Rent + expenses', 'Groceries', 'Pet'],
            'Transport': ['Fuel', 'Parts'],
            'Fun': ['Eat out', 'Fun']}

    # application necessary categories
    mc0 = db.MetaCategory(name='Vindulum', budget=b)
    c0 = db.Category(name='To Be Budgeted', MC=mc0)
    #mc0.categories.append(c0)
    #b.meta_categories.append(mc0)
    
    # user categories
    for metac, cats in categories.items():
        mc = db.MetaCategory(name=metac, budget=b)
        for c in cats:
            c = db.Category(name=c, MC=mc)
            #mc.categories.append(c)
        #b.meta_categories.append(mc)

    a0 = db.Account(name='AB Checking', budget=b)
    #b.accounts.append(a0)

    t0 = db.Transaction(value=50, category=c0, account=a0, date=datetime.datetime.today().date(), memo='test')

    #a1.transactions.append(t0)

    print('Finished adding test data to database...')

        
@app.route('/populate')
def populate():
    create_test_data()
    return 'good'




@app.route('/dashboard/<string:email>')
def dashboard(email):
    with db.db_session:
        users = db.select(u for u in db.User if u.email == email)[:]
        if len(users) == 0:
            return 'not found'
        user = users[0]
        budgets = list(user.budgets)
        if len(budgets) == 0:
            return 'user with no budgets'
        budget = budgets[0]
        if len(budget.meta_categories) == 0:
            return 'budget with no metacategories'
        categories = []        
        for mc in budget.meta_categories:
            for c in mc.categories:
                categories.append('{} - {}'.format(mc.name, c.name))
        # return '# categories={}'.format(len(categories))
        return render_template('dashboard.html', budget_lines=sorted(categories))


@app.route('/in')
def hello_world():
    with db.db_session:
        # get all categories from user
        users = [u for u in User]
        for u in users:
            print('user:', u.email)
            for b in u.budgets:
                print('\tBudget:', b.name)
                print('Categories')
                for mc in b.meta_categories:
                    for c in mc.categories:
                        print('\t\t',mc,'-',c)
        return 'Hello, World!'




# # # # # # # # # # # # # # # # # # # # #
#
#         API    API    API    API
#
# # # # # # # # # # # # # # # # # # # # #

#budgets/{budget_id}
#budgets/{budget_id}/accounts
#budgets/{budget_id}/categories
#budgets/{budget_id}/months
#budgets/{budget_id}/payees
#budgets/{budget_id}/transactions
#budgets/{budget_id}/scheduled_transactions


# # # # User


@app.route('/user')
def user():
    # authenticated user info
    with db.db_session:
        users = db.select(u for u in db.User)
        print('all users:')
        for u in users:
            print(u)
        users = list(users)
    ret_str = '{} users\n'.format(len(users))
    return ret_str


# # # # Budgets

@app.route('/budgets')
def budgets():
    # list of budgets
    pass

@app.route('/budgets/<string:budget_id>')
def budget(budget_id):
    # budget info
    pass


@app.route('/budgets/<string:budget_id>/settings')
def budget_settings(budget_id):
    # budget settings info
    pass

# # # # Accounts
@app.route('/budgets/<string:budget_id>/accounts')
def accounts(budget_id):
    # list acounts or create new accounts
    pass

@app.route('/budgets/<string:budget_id>/<string:account_id>')
def account(budget_id, account_id):
    # account info
    pass


# # # # Categories

@app.route('/budgets/<string:budget_id>/categories')
def categories(budget_id):
    # list categories
    pass

@app.route('/budgets/<string:budget_id>/categories/<string:category_id>')
def category(budget_id, category_id):
    # category info
    pass


@app.route('/budgets/<string:budget_id>/months/<string:month>/categories/<string:category_id>')
def category_month(budget_id, month, category_id):
    # get OR update category info for specific month
    pass




# # # # Payees
@app.route('/budgets/<string:budget_id>/payees')
def payees(budget_id):
    # list acounts or create new accounts
    pass


@app.route('/budgets/<string:budget_id>/payees/<string:payee_id>')
def payee(budget_id, payee_id):
    # payee info
    pass


# # # # Months
@app.route('/budgets/<string:budget_id>/months')
def months(budget_id):
    # list months
    pass

@app.route('/budgets/<string:budget_id>/months/<string:month>')
def get_month(budget_id, month):
    # month info
    pass

# # # # Transactions
@app.route('/budgets/<string:budget_id>/transactions')
def transactions(budget_id):
    # get, post or update transactions
    pass

@app.route('/budgets/<string:budget_id>/months/<string:transactions_id>')
def month(budget_id, transaction_id):
    # get or update specific transaction
    pass

@app.route('/budgets/<string:budget_id>/accounts/<string:account_id>/transactions')
def transactions_account(budget_id_, account_id):
    # get account transactions
    pass

@app.route('/budgets/<string:budget_id>/categories/<string:category_id>/transactions')
def transactions_category(budget_id_, category_id):
    # get category transactions
    pass

@app.route('/budgets/<string:budget_id>/payees/<string:payee_id>/transactions')
def transactions_payee(budget_id_, payee_id):
    # get payee transactions
    pass



# # # # Schedueld Transactions

@app.route('/budgets/<string:budget_id>/scheduled_transactions')
def transactions_scheduled(budget_id):
    # list scheduled transactions
    pass

@app.route('/budgets/<string:budget_id>/scheduled_transactions/<string:scheduled_transaction_id>')
def transaction_scheduled(budget_id, scheduled_transaction_id):
    # list scheduled transaction info
    pass


if __name__ == '__main__':

    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

