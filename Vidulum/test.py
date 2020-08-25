import datetime

import database as db


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

if __name__ == '__main__':
    create_test_data()
