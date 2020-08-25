import datetime

from pony.orm import *

db = Database()

class Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    MC = Required('MetaCategory')
    blines = Set('BudgetLine')
    transactions = Set('Transaction')

class MetaCategory(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    categories = Set(Category)
    budget = Required('Budget')

class BudgetLine(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(datetime.date)
    category = Required(Category)
    value = Required(int)
    budget = Required('Budget')

class Payee(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    transactions = Set('Transaction')

class Transaction(db.Entity):
    id = PrimaryKey(int, auto=True)
    value = Required(float)
    category = Required(Category)
    date = Required(datetime.date)
    flag = Optional(int)
    memo = Optional(str)
    payee = Optional(Payee)
    account = Required('Account')

class Account(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    transactions = Set(Transaction)
    budget = Required('Budget')
    
class Budget(db.Entity):
    id = PrimaryKey(int, auto=True)
    budget_lines = Set(BudgetLine)
    accounts = Set(Account)
    meta_categories = Set(MetaCategory)
    name = Required(str)
    user = Required('User')


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    email = Required(str, unique=True)
    budgets = Set(Budget)
    
    def __str__(self):
        return 'User<id={}, email={}>'.format(self.id, self.email)
        


#db.bind(provider='sqlite', filename=':memory:')
#sql_debug(True)
#db.generate_mapping(create_tables=True)


    
@db_session
def new_user(email):
    u = User(email=email)
    return u


@db_session
def new_budget(user, name):
    b = Budget(name=name)
    user.budgets.append(b)
    return b


@db_session
def new_metacategory(budget, name, categories=[]):
    mc = MetaCategory(name=name, categories=categories)
    budget.meta_categories.append(mc)
    return mc



@db_session
def new_category(meta_category, name):
    c = Category(name=name, categories=categories)
    meta_category.categories.append(c)
    return c



@db_session
def new_budget_line(budget, value, date, category):
    bl = BudgetLine(value=value, date=date, category=category)
    budget.budget_lines.append(bl)
    return b



