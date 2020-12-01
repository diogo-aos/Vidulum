'''
 all functions that receive _id, receive a ObjectId object from the bson standard module

'''


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


default_categories = {
    "default": ["To be budgeted"],
    "Immediate Obligations": ["Rent", "Water", "Eletric", "Internet", "Groceries", "Transportation"],
    "True Expenses": ["Auto Maintenance", "House Maintenance", "Medical", "Clothing", "Gifts", "Giving", "Pets", "Software subscriptions", "Stuff I Forgot"],
    "Quality of life": ["Vacation", "Fitness", "Education"],
    "Just for fun": ["Dining out", "Music", "Games", "Activities"]
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


def category_create(name, master_category, budget_id):
    c = {"name": name,
         "budget_id": budget_id,
         "master_category": master_category,
         "note": "",
         "hidden": False
         }
    return c

            


def budget_create_blank(name, user_id):
    b = {"user_id": user_id,
         "name": name,
         "months": [],
         "accounts": [],
         "categories":[],
         "master_categories": [],
         "payees": [],
         "creation_date": datetime.datetime.utcnow(),
         }
    return b


def budget_insert(name, user_id):

    # create budget
    b = budget_create_blank(name, user_id)
    new_budget = db.budgets.insert_one(b)
    new_budget = db.budgets.find_one({"_id": new_budget.inserted_id})

    # link new budget to user
    user = db.users.find_one({"_id": user_id})
    user["budgets"].append(new_budget["_id"])
    user["settings"]["default_budget"] = new_budget["_id"]
    db.users.replace_one({"_id": user_id}, user)

    # create default categories
    for master, categories in default_categories.items():
        # link new group to budget
        new_budget["master_categories"].append(master)

        created_categories = [category_create(c_name, master, new_budget["_id"]) for c_name in categories]
        new_categories = db.categories.insert_many(created_categories)

        # link new category to budget
        new_budget["categories"].extend(new_categories.inserted_ids)

    # update budget after all category groups are created
    db.budgets.replace_one({"_id": new_budget["_id"]}, new_budget)

    month_insert(datetime.datetime.now(), new_budget["_id"])

    return new_budget


def month_category_create(category_id, category_name):
    mc = {"category_id": category_id,
          "category_name": category_name,
          "budgeted": 0.0,
    }
    return mc


def month_create(date, budget_id):
    month_now = datetime.datetime(year=date.year, month=date.month, day=1)
    categories = db.categories.find({"budget_id": budget_id})
    month = {
        "budget_id": budget_id,
        "date": month_now,
        "month_categories": [month_category_create(c["_id"], c["name"]) for c in categories]
    }
        
    return month


def month_insert(date, budget_id):
    m = month_create(date, budget_id)
    new_month = db.months.insert_one(m)
    b = db.budgets.find_one({"_id": budget_id})
    b["months"].append(new_month.inserted_id)
    return new_month
    
    
