from flask import Flask, render_template

import datetime
import database as db


app = Flask(__name__)

db.sql_debug(True)
db.db.bind(provider='sqlite', filename='test_db.sqlite', create_db=True)
db.db.generate_mapping(create_tables=True)

@db.db_session
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


@app.route('/user')
def user():
    with db.db_session:
        users = db.select(u for u in db.User)
        print('all users:')
        for u in users:
            print(u)
        users = list(users)
    ret_str = '{} users\n'.format(len(users))
    return ret_str


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


@app.route('/')
def hello_world():

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


