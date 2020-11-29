import os
import uuid
import datetime


import pymongo

from passlib.apps import custom_app_context as pwd_context

mongo_username = os.environ['DB_USER_USERNAME']
mongo_password = os.environ['DB_USER_PASSWORD']
mongo_addr = os.environ['DB_MONGO_LINK']
mongo_dbname = os.environ['DB_MONGO_DATABASE']
mongo_uri = "mongodb+srv://{username}:{password}@{db_mongo_addr}/{db_mongo_name}?retryWrites=true&w=majority".format(username=mongo_username, password=mongo_password, db_mongo_addr=mongo_addr, db_mongo_name=mongo_dbname)

client = pymongo.MongoClient(mongo_uri)
db = client[mongo_dbname]


def default_categories():
    categories = {"default": ["To be budgeted"],
                  "Immediate Obligations": ["Rent", "Water", "Eletric", "Internet", "Groceries", "Transportation"],
                  "True Expenses": ["Medical", "Clothing", "Gifts", "Pets", "Stuff I Forgot"],
                  "Fun": ["Dining out", "Fun"]
                  }
    


def user_create(email, password):
    u = {"email": email,
         "password": pwd_context.hash(password),
         "creation_date": datetime.datetime.utcnow(),
         "budgets": [],
         "settings": {"default_budget": None,
                      "last_login": None
                     }
        }
    new_user = db.users.insert_one(u)
    new_user = db.users.find_one({'email': email})
    budget_insert("My Budget", new_user["_id"])
    return new_user
    

def user_get(email, password):
    u = db.users.find_one({"email":email, "password": pwd_context.hash(password)})
    return u

def user_login(email, password):
    u = db.users.find_one({"email":email})
    if u and pwd_context.hash(password) == u.password:
        return True
    else:
        return False

def category_group_create(name, budget_id, categories=[]):
    g = {"name": name,
         "budget_id": budget_id,
         "categories": categories,
         "hidden": False
         }
    return g

    
def category_group_insert(name, budget_id, categories=[]):
    groups = db.category_groups
    budgets = db.budgets

    g = category_group_create(name, budget_id, categories)

    new_group = groups.insert_one(g)

    # update original budget
    budget = budgets.find_one({"_id": budget_id})
    budget['category_groups'].append(new_group.inserted_id)
    budgets.replace_one({'_id': budget_id}, budget)
    
    return new_group


def category_create(name, group_id):
    c = {"name": name,
         "category_group_id": group_id,
         "note": "",
         "hidden": False
         }
    return c

            
default_categories = {
    "default": ["To be budgeted"],
    "Immediate Obligations": ["Rent", "Water", "Eletric", "Internet", "Groceries", "Transportation"],
    "True Expenses": ["Auto Maintenance", "House Maintenance", "Medical", "Clothing", "Gifts", "Giving", "Pets", "Software subscriptions", "Stuff I Forgot"],
    "Quality of life": ["Vacation", "Fitness", "Education"],
    "Just for fun": ["Dining out", "Music", "Games", "Activities"]
}


def budget_create(name, user_id):
    b = {"user_id": user_id,
         "name": name,
         "budgetlines": [],
         "accounts": [],
         "category_groups":[],
         "creation_date": datetime.datetime.utcnow(),
         }
    return b


def budget_insert(name, user_id):
    budgets = db.budgets
    users = db.users
    category_groups = db.category_groups
    categories = db.categories

    # create budget
    b = budget_create(name, user_id)
    print(b)
    new_budget = budgets.insert_one(b)
    new_budget = budgets.find_one({"_id": new_budget.inserted_id})

    # link new budget to user
    user = db.users.find_one({"_id": user_id})
    user["budgets"].append(new_budget["_id"])
    user["settings"]["default_budget"] = new_budget["_id"]
    users.replace_one({"_id": user_id}, user)

    for group, cat_lst in default_categories.items():
        g = category_group_create(group, new_budget["_id"])
        new_group = category_groups.insert_one(g)
        new_group = category_groups.find_one({"_id": new_group.inserted_id})

        # link new group to budget
        new_budget["category_groups"].append(new_group["_id"])

        for cat in cat_lst:
            c = category_create(cat, new_group["_id"])
            new_category = categories.insert_one(c)

            # link new category to group
            new_group["categories"].append(new_category.inserted_id)

        # update category group after categories are created
        category_groups.replace_one({"_id": new_group["_id"]}, new_group)

    # update budget after all category groups are created
    budgets.replace_one({"_id": new_budget["_id"]}, new_budget)

    return new_budget

        

    

    
