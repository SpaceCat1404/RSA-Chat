import tkinter
from tkinter import *
from tkinter import messagebox
import customtkinter
import sqlite3
import bcrypt

Windowreg = customtkinter.CTk()
Windowreg.title("Register")
Windowreg.resizable(width=False,
				height=False)
Windowreg.configure(width=800,
				height=600)
pls = customtkinter.CTkLabel(Windowreg,
						text="Create an Account",
						font=("Arial",20,"bold"))
pls.place(relheight=0.15, relx=0.5,rely=0.1, anchor="center")

Windowreg.labelPseudo = customtkinter.CTkLabel(Windowreg, text="Login : ", justify=CENTER)
Windowreg.labelPseudo.place(relheight=0.1, relx=0.1, rely=0.2)
Windowreg.entryPseudo = customtkinter.CTkEntry(Windowreg)
Windowreg.entryPseudo.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.2)

Windowreg.labelFirstName = customtkinter.CTkLabel(Windowreg, text="FirstName : ", justify=CENTER)
Windowreg.labelFirstName.place(relheight=0.1, relx=0.1, rely=0.3)
Windowreg.entryFirstName = customtkinter.CTkEntry(Windowreg)
Windowreg.entryFirstName.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.3)

Windowreg.labelLastName = customtkinter.CTkLabel(Windowreg,text="LastName : ", justify=CENTER)
Windowreg.labelLastName.place(relheight=0.1, relx=0.1, rely=0.4)
Windowreg.entryLastName = customtkinter.CTkEntry(Windowreg)
Windowreg.entryLastName.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.4)
Windowreg.labelPwd = customtkinter.CTkLabel(Windowreg, text="Password : ",justify=CENTER)
Windowreg.labelPwd.place(relheight=0.1, relx=0.1, rely=0.5)
Windowreg.entryPwd = customtkinter.CTkEntry(Windowreg, show='*')
Windowreg.entryPwd.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.5)

def redirLog():
    Windowreg.withdraw()
    import server_integrated
    server_integrated.main()  # Replace 'main()' with the actual function you want to execute


def create_database():
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

create_database()

def register():
    user = {
        'username': Windowreg.entryPseudo.get(),
        'password': Windowreg.entryPwd.get(),
        'firstname': Windowreg.entryFirstName.get(),
        'lastname': Windowreg.entryLastName.get()
    }

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
    print(f"Entered Password: {user['password']}")
    print(f"Hashed Password: {hashed_password}")

    conn = sqlite3.connect('chat_app.db')
    cursor = conn.cursor()

    # Check if the login name is already in use
    cursor.execute('SELECT * FROM users WHERE username = ?', (user['username'],))
    existing_user = cursor.fetchone()

    if existing_user:
        messagebox.showerror("Error", "Login name already exists. Please choose a different one.")
    else:
        # Insert the new user into the database
        cursor.execute('''INSERT INTO users (username, firstname, lastname, password)
            VALUES (?, ?, ?, ?)'''
            , (user['username'], user['firstname'], user['lastname'], hashed_password))
        messagebox.showinfo("Success", "User registration successful!")

    conn.commit()
    conn.close()


Windowreg.go = customtkinter.CTkButton(Windowreg,
						text="REGISTER",
						command= register)
Windowreg.go.place(relx=0.15,
					rely=0.75)

Windowreg.go = customtkinter.CTkButton(Windowreg,
										  text="go back to login",
										  command=redirLog)

Windowreg.go.place(relx=0.55,
					  rely=0.75)

Windowreg.mainloop()