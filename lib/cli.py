from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, Session
import bcrypt
import re
import pwinput
from cryptography.fernet import Fernet
from texttable import Texttable
import string
import secrets

Base = declarative_base()

# Generate the key only once and store it in a file
try:
    with open('key.key', 'rb') as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open('key.key', 'wb') as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)

class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True)
    password_hash = Column(String)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Password(Base):
    __tablename__ = 'passwords'
    id = Column(Integer, primary_key=True)
    website = Column(String)
    username = Column(String)
    password_hash = Column(String)
    user_id = Column(String, ForeignKey('users.username'))
    user = relationship("User", backref="passwords")

    def set_password(self, password):
        encrypted_password = cipher_suite.encrypt(password.encode('utf-8'))
        self.password_hash = encrypted_password.decode('utf-8')

    def get_decrypted_password(self):
        decrypted_password = cipher_suite.decrypt(self.password_hash.encode('utf-8'))
        return decrypted_password.decode('utf-8')

def start_screen():
    print('Welcome to Encrypto.')
    print('1. Sign Up')
    print('2. Login')
    print('3. Quit')
    action = input("Please select an option: ")

    if action == '1':
        sign_up()
    elif action == '2':
        login()
    elif action == '3':
        quit()
    else:
        print('Invalid option. Please select a valid option.')
        start_screen()

def validate_username(username):
    if not isinstance(username, str):
        return False
    if len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False
    return True

def validate_password(password):
    if not isinstance(password, str):
        return False
    if len(password) < 8:
        return False
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$', password):
        return False
    return True

def sign_up():
    while True:
        print('Please enter your desired username (or "cancel" to go back):')
        username = input("> ")
        if username.lower() == 'cancel':
            start_screen()
        elif validate_username(username):
            break
        print('Invalid username. Please try again.')

    while True:
        print('Please enter your desired password (or "cancel" to go back):')
        password = pwinput.pwinput("> ")
        if password.lower() == 'cancel':
            start_screen()
        elif validate_password(password):
            break
        print('Invalid password. Please try again.')

    while True:
        print('Confirm your password (or "cancel" to go back):')
        confirm_password = pwinput.pwinput("> ")
        if confirm_password.lower() == 'cancel':
            start_screen()
        elif password == confirm_password:
            break
        print("Passwords do not match! Please try again.")

    user = session.query(User).filter_by(username=username).first()
    if user:
        print('Username already exists. Please choose a different username.')
        sign_up()
    else:
        new_user = User(username=username)
        new_user.set_password(password)
        session.add(new_user)
        session.commit()
        print('Account created successfully.')
        start_screen()

def login():
    while True:
        print('Please enter your username:')
        username = input("> ")
        user = session.query(User).filter_by(username=username).first()
        if not user:
            print("Invalid username. Please try again.")
            continue
        break

    while True:
        print('Please enter your password (or "reset" to reset your password):')
        password = pwinput.pwinput("> ")
        if password.lower() == 'reset':
            reset_password(username)
        elif not user.check_password(password):
            print("Invalid password. Please try again.")
            continue
        break

    print("Login successful!")
    current_user = user
    menu(current_user)

def reset_password(username):
    user = session.query(User).filter_by(username=username).first()
    if user:
        print("Reset password for", username)
        new_password = pwinput.pwinput("Enter new password: ")
        confirm_password = pwinput.pwinput("Confirm new password: ")

        if new_password == confirm_password:
            user.set_password(new_password)
            session.commit()
            print("Password reset successfully. Please login again.")
            login()
        else:
            print("Passwords do not match. Please try again.")
            reset_password(username)
    else:
        print("User not found. Please try again.")
        login()

def menu(current_user):
    print("Welcome to Encrypto. What would you like to do?:")
    print("0. Help.")
    print("1. Create a new password.")
    print("2. Manage passwords.")
    print("3. Manage Account.")
    print("4. Sign Out.")
    print("5. Quit.")
    action = input("Please select an option: ")

    if action == "0":
        help_section(current_user)
    elif action == "1":
        create_password(current_user)
    elif action == "2":
        manage_passwords(current_user)
    elif action == "3":
        manage_account(current_user)
    elif action == "4":
        start_screen()
    elif action == "5":
        quit()
    else:
        print("Invalid option. Please try again.")
        menu(current_user)

def help_section(current_user):
    print("Welcome to the Help Section!")
    print("Here are some tips to get you started:")
    print("")
    print("1. Sign Up: Create a new account by selecting the Sign Up option.")
    print("   - Enter a unique username and password to create your account.")
    print("   - You will be prompted to login after creating your account.")
    print("")
    print("2. Login: Login to your existing account by selecting the Login option.")
    print("   - Enter your username and password to access your account.")
    print("   - If you forget your password, you can try resetting it.")
    print("")
    print("3. Store a new password: Store a new password by selecting the Store a new password option.")
    print("   - Enter the website or application name, username, and password to store.")
    print("   - You can view your stored passwords by selecting the Manage passwords option.")
    print("")
    print("4. Manage passwords: Manage your stored passwords by selecting the Manage passwords option.")
    print("   - You can view, edit, or delete your stored passwords.")
    print("   - You can also search for specific passwords using the search function.")
    print("")
    print("5. Sign Out: Sign out of your account by selecting the Sign Out option.")
    print("   - You will be logged out of your account and returned to the login screen.")
    print("")
    print("6. Quit: Quit the application by selecting the Quit option.")
    print("   - You will be prompted to confirm before quitting the application.")
    print("")
    print("If you need further assistance, please contact our support team @HexaForce :D")
    print("Thank you for using Encrypto!")

    print("Press Enter to go back to the menu when you are done :D")
    input()
    menu(current_user)

def create_password(current_user):
    print("Welcome to the Create Password Section!")
    website = input("Website/Application Name: ")
    username = input("Username: ")
    
    print("Do you want to:")
    print("1. Generate a random password")
    print("2. Input your own password")
    action = input("Please select an option: ")
    
    if action == "1":
        password = generate_random_password()
    elif action == "2":
        password = pwinput.pwinput("Password: ")
    else:
        print("Invalid option. Please try again.")
        create_password(current_user)
    
    password_obj = Password(website=website, username=username, user_id=current_user.username)
    password_obj.set_password(password)
    session.add(password_obj)
    session.commit()
    print("Password stored successfully!")
    print("Press Enter to go back to the menu when you are done.")
    input()
    menu(current_user)

def generate_random_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password) 
                and any(c.isupper() for c in password) 
                and any(c.isdigit() for c in password) 
                and any(c in string.punctuation for c in password)):
            return password

def manage_passwords(current_user):
    print("Welcome to the Manage Passwords Section!")
    print("What would you like to do:")
    print("1. View stored passwords")
    print("2. Update stored passwords")
    print("3. Delete stored passwords")
    print("4. Search for passwords")
    print("5. Back to menu")
    action = input("Please select an option: ")

    if action == "1":
        view_passwords(current_user)
    elif action == "2":
        edit_password(current_user)
    elif action == "3":
        delete_password(current_user)
    elif action == "4":
        search_password(current_user)
    elif action == "5":
        menu(current_user)
    else:
        print("Invalid option. Please try again.")
        manage_passwords(current_user)

def view_passwords(current_user):
    print("Here are your stored passwords:")
    passwords = session.query(Password).filter_by(user_id=current_user.username).all()
    if not passwords:
        print("No passwords stored yet.")
    else:
        table = Texttable()
        table.header(["Website", "Username", "Password"])
        for password in passwords:
            decrypted_password = password.get_decrypted_password()
            table.add_row([password.website, password.username, decrypted_password])
        print(table.draw())
    print("Press Enter to go back to the menu when you are done.")
    input()
    manage_passwords(current_user)

def edit_password(current_user):
    print("Edit Password Section!")
    website = input("Enter the website of the password you want to edit: ")
    password_obj = session.query(Password).filter_by(website=website, user_id=current_user.username).first()
    if password_obj:
        new_password = pwinput.pwinput("Enter the new password: ")
        password_obj.set_password(new_password)
        session.commit()
        print("Password updated successfully!")
        print("Press Enter to go back to the menu when you are done.")
        input()
        manage_passwords(current_user)
    else:
        print("Password not found. Please try again.")
        edit_password(current_user)

def delete_password(current_user):
    print("Delete Password Section!")
    website = input("Enter the website of the password you want to delete: ")
    password_obj = session.query(Password).filter_by(website=website, user_id=current_user.username).first()
    if password_obj:
        session.delete(password_obj)
        session.commit()
        print("Password deleted successfully!")
        print("Press Enter to go back to the menu when you are done.")
        input()
        manage_passwords(current_user)
    else:
        print("Password not found. Please try again.")
        delete_password(current_user)

def search_password(current_user):
    print("Search Password Section!")
    website = input("Enter the website of the password you want to search: ")
    website_lower = website.lower() 
    password_obj = session.query(Password).filter_by(user_id=current_user.username).all()
    for password in password_obj:
        if website_lower in password.website.lower(): 
            decrypted_password = password.get_decrypted_password()
            print(f"Website: {password.website}, Username: {password.username}, Password: {decrypted_password}")
    print("Press Enter to go back to the menu when you are done.")
    input()
    manage_passwords(current_user)

def manage_account(current_user):
    print("Manage Account Section!")
    print("1. Edit Username")
    print("2. Change Password")
    print("3. Delete Account")
    print("4. Back to menu")
    action = input("Please select an option: ")
    if action == "1":
        edit_username(current_user)
    elif action == "2":
        change_password(current_user)
    elif action == "3":
        delete_account(current_user)
    elif action == "4":
        menu(current_user)
    else:
        print("Invalid option. Please try again.")

def edit_username(current_user):
    print("Edit Username Section!")
    old_username = current_user.username  # Store the old username
    new_username = input("Enter your new username: ")
    current_user.username = new_username
    session.commit()  # Update the username in the users table

    # Update the user_id in the passwords table
    password_obj = session.query(Password).filter_by(user_id=old_username).all()
    for password in password_obj:
        password.user_id = new_username
    session.commit() 

    print("Username updated successfully!")
    print("Press Enter to go back to the menu when you are done.")
    input()
    manage_account(current_user)

def change_password(current_user):
    old_password = pwinput.pwinput("Enter your current password: ")
    if current_user.check_password(old_password):
        new_password = pwinput.pwinput("Enter your new password: ")
        confirm_password = pwinput.pwinput("Confirm your new password: ")
        if new_password == confirm_password:
            current_user.set_password(new_password)
            session.commit()
            print("Password updated successfully!")
            print("Press Enter to go back when you are done.")
            input()
            manage_account(current_user)
        else:
            print("Passwords do not match. Please try again.")
            change_password(current_user)
    else:
        print("Invalid password. Please try again.")
        change_password(current_user)

def delete_account(current_user):
    password = pwinput.pwinput("Enter your password to confirm: ")
    if current_user.check_password(password):
        session.delete(current_user)
        session.commit()
        print("Account deleted successfully!")
        start_screen()
    else:
        print("Invalid password. Please try again.")
        delete_account(current_user)

if __name__ == '__main__':
    engine = create_engine('sqlite:///passwords.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    start_screen()