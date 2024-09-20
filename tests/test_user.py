# @fileName: test_user.py
# @creation_date: 18/09/2024
# @authors: averyark

from ..roms.account import user

# birthday constraint test
def test_validateBirthday():
    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first',
        'lastName': 'last'
    })

    # This is not valid in py 3.9
    # reference to test: https://github.com/averyark/roms/actions/runs/10922064922/job/30315543710
    # user.validate_user_data({
    #     'birthday': '20050921',
    #     'email': 'first@gmail.com',
    #     'firstName': 'first',
    #     'lastName': 'last'
    # })

    try:
        user.validate_user_data({
            'birthday': '09-21-2005',
            'email': 'first@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

    try:
        user.validate_user_data({
            'birthday': '09-2005-21',
            'email': 'first@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

# email constraint test
def test_validateEmail():

    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first',
        'lastName': 'last'
    })
    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first',
        'lastName': 'last'
    })

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': f'{"a"*50}@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 1,
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first_last@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': '@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first@gmail',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

# name constraint test
def test_validateName():
    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first',
        'lastName': 'last'
    })
    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first middle',
        'lastName': 'last'
    })

    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first middle',
        'lastName': 'last last2'
    })

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 1,
            'password': 'somepassword@12345678',
            'firstName': 'first.',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'last.'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'a'*51,
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 'first',
            'lastName': 'a'*51
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")
    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 1,
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': 'somepassword@12345678',
            'firstName': 1,
            'lastName': 2,
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

# password constraint test
def test_validatePassword():
    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'password': 'somepassword@12345678',
        'firstName': 'first',
        'lastName': 'last'
    })
    user.validate_user_data({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'password': 'somepassword12345678',
        'firstName': 'first middle',
        'lastName': 'last'
    })

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'password': 'abc123',
            'email': 'first.last@gmail.com',
            'firstName': 'first middle',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': 'somepass@123XÆ ',
            'firstName': 'first middle',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': "a"*51,
            'firstName': 'first middle',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")

    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': "12345678",
            'firstName': 'first middle',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")


    try:
        user.validate_user_data({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'password': "abcdefgh",
            'firstName': 'first middle',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid password")
