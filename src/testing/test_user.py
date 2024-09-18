# @fileName: test_user.py
# @creation_date: 18/09/2024
# @authors: averyark

from account import user

# birthday constraint test
def test_validateBirthday():
    user.validateUserData({
        'birthday': '2005-09-21',
        'email': 'first@gmail.com',
        'firstName': 'first',
        'lastName': 'last'
    })
    user.validateUserData({
            'birthday': '20050921',
            'email': 'first@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
    })

    try:
        user.validateUserData({
            'birthday': 20050921,
            'email': 'first@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

    try:
        user.validateUserData({
            'birthday': '09-21-2005',
            'email': 'first@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

    try:
        user.validateUserData({
            'birthday': '09-2005-21',
            'email': 'first@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid birthday")

# email constraint test
def test_validateEmail():

    user.validateUserData({
        'birthday': '2005-09-21',
        'email': 'first@gmail.com',
        'firstName': 'first',
        'lastName': 'last'
    })
    user.validateUserData({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'firstName': 'first',
        'lastName': 'last'
    })

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': f'{"a"*50}@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 1,
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first_last@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': '@gmail.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first@gmail',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first.com',
            'firstName': 'first',
            'lastName': 'last'
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")

# name constraint test
def test_validateName():
    user.validateUserData({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'firstName': 'first',
        'lastName': 'last'
    })
    user.validateUserData({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'firstName': 'first middle',
        'lastName': 'last'
    })

    user.validateUserData({
        'birthday': '2005-09-21',
        'email': 'first.last@gmail.com',
        'firstName': 'first middle',
        'lastName': 'last last2'
    })

    try:
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 1,
            'firstName': 'first.',
            'lastName': 'last'
        })
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'firstName': 'first',
            'lastName': 'last.'
        })
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'firstName': 'a'*51,
            'lastName': 'last'
        })
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'firstName': 'first',
            'lastName': 'a'*51
        })
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'firstName': 1,
            'lastName': 'last'
        })
        user.validateUserData({
            'birthday': '2005-09-21',
            'email': 'first.last@gmail.com',
            'firstName': 1,
            'lastName': 2,
        })
    except:
        pass
    else:
        raise ValueError("Validation passed for invalid email")
