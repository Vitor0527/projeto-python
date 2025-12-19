## Importar utils e menus
from utils import read_json, save_json
from client_menu import menu_client
from admin_menu import menu_admin

## Função de login
def login():
    users = read_json('data/users.json')
    email = input('Enter you email: ')
    user = None

    ## Procurar user por email
    for u in users:
        if u['email'] == email:
            user = u
            break

    ## Se user não existe -> criar novo user
    if user is None:
        newuser = {'email': email, 'tipo': 'cliente'}
        users.append(newuser)
        save_json('data/users.json', users)
        return newuser, newuser['tipo']

    ## Se for admin -> pedir password
    if user['tipo'] == 'admin':
        senha = input('Introduza a sua password: ')
        if senha == user['senha']:
            return user, user['tipo']
        else:
            print('Password incorreto!')
            return None,None

    ## Se for cliente -> entrar diretamente
    return user, user['tipo']

if __name__ == "__main__":
    while True:
        current_user, user_type = login()

        ## Se login falhou (password errada)
        if current_user is None:
            continue

        ## Verifica tipo de utilizador
        if user_type == "cliente":
            menu_client(current_user)
        else:
            menu_admin(current_user)
