## IMPORT UTILS AND MENUS

from utils import read_json, save_json
from client_menu import menu_cliente
from admin_menu import menu_admin

## LOGIN FUNCTION

def login():
    users = read_json('data/users.json')
    email = input('Enter you email: ')

    # LOOP ALL USERS TO CHECK IF EMAIL EXISTS
    for user in users:
        if user['email'] == email:
            return user, user['tipo']

    # IF USER ADMIN -> ASK FOR PASSWORD
    if user['tipo'] == 'admin':
        senha = input('Introduza a sua passowrd: ')
        if user['senha'] == user.get('senha'):
            return user, user['tipo']
        else:
            print('Password incorreto!')
            return None,None



    # IF USER NOT FOUND -> CREATE NEW USER
    newuser = {'email': email, 'tipo': 'cliente'}
    users.append(newuser)
    save_json('data/users.json', users)
    return newuser, newuser['tipo']

if __name__ == "__main__":
    while True:
        current_user, user_type = login()
        if current_user is None:
            continue
        if user_type == "cliente":
            menu_cliente(current_user)
        else:
            menu_admin(current_user)
