from Vidulum.mongo import user_create

def test_user_create():
    email = "test@email.com"
    password = "myeasypass"

    u = user_create(email, password)
    assert u["email"] == email
    #assert u["password"] = 
