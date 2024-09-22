import tkinter as tk
from tkinter import messagebox, simpledialog
import customtkinter
import sqlite3
import bcrypt
from customtkinter import CTkToplevel

# Create a global reference for the main window
main_window = customtkinter.CTk()

def custom_input_dialog(parent, title, prompt):
    top = tk.Toplevel(parent)
    #top = CTkToplevel(parent)
    top.title(title)

    label_font = ("Arial", 18)  # Adjust the font size as needed
    entry_font = ("Arial", 18)  # Adjust the font size as needed

    label = tk.Label(top, text=prompt, font=label_font)
    label.pack(pady=10)

    entry_var = tk.StringVar()
    entry = tk.Entry(top, textvariable=entry_var, font=entry_font)
    entry.pack(pady=10)

    def ok():
        top.destroy()

    button_ok = tk.Button(top, text="OK", command=ok, font=label_font)
    button_ok.pack(pady=10)

    top.geometry('500x300')  # Set the size of the custom dialog

    top.wait_window()

    return entry_var.get()

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

def register():
    user = {
        'username': main_window.entryPseudo.get(),
        'password': main_window.entryPwd.get(),
        'firstname': main_window.entryFirstName.get(),
        'lastname': main_window.entryLastName.get()
    }

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())

    conn = sqlite3.connect('chat_app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ?', (user['username'],))
    existing_user = cursor.fetchone()

    if existing_user:
        messagebox.showerror("Error", "Login name already exists. Please choose a different one.")
    else:
        cursor.execute('''INSERT INTO users (username, firstname, lastname, password)
            VALUES (?, ?, ?, ?)''', (user['username'], user['firstname'], user['lastname'], hashed_password))
        messagebox.showinfo("Success", "User registration successful!")

    conn.commit()
    conn.close()

def update_user_window():
    username_to_update = custom_input_dialog(main_window, "Input", "Enter the username to update:")
    
    if not username_to_update:
        return

    conn = sqlite3.connect('chat_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username_to_update,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        messagebox.showerror("Error", "User not found.")
        return

    update_window = customtkinter.CTk()
    update_window.title("Update User")
    update_window.resizable(width=False, height=False)
    update_window.configure(width=800, height=600)

    labelNewFirstName = customtkinter.CTkLabel(update_window, text="New First Name: ", justify=tk.CENTER)
    labelNewFirstName.place(relheight=0.1, relx=0.1, rely=0.2)
    entryNewFirstName = customtkinter.CTkEntry(update_window)
    entryNewFirstName.insert(0, user[2])  # Set the default value to the current first name
    entryNewFirstName.place(relwidth=0.4, relheight=0.08, relx=0.5, rely=0.2)  # Adjusted relx value

    labelNewLastName = customtkinter.CTkLabel(update_window, text="New Last Name: ", justify=tk.CENTER)
    labelNewLastName.place(relheight=0.1, relx=0.1, rely=0.3)
    entryNewLastName = customtkinter.CTkEntry(update_window)
    entryNewLastName.insert(0, user[3])  # Set the default value to the current last name
    entryNewLastName.place(relwidth=0.4, relheight=0.08, relx=0.5, rely=0.3)  # Adjusted relx value

    labelNewPassword = customtkinter.CTkLabel(update_window, text="New Password: ", justify=tk.CENTER)
    labelNewPassword.place(relheight=0.1, relx=0.1, rely=0.4)
    entryNewPassword = customtkinter.CTkEntry(update_window, show='*')
    entryNewPassword.place(relwidth=0.4, relheight=0.08, relx=0.5, rely=0.4)  # Adjusted relx value


    def update_user():
        new_firstname = entryNewFirstName.get()
        new_lastname = entryNewLastName.get()
        new_password = entryNewPassword.get()

        # Hash the new password before updating
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()
        cursor.execute('''UPDATE users SET firstname=?, lastname=?, password=? WHERE username=?''',
                       (new_firstname, new_lastname, hashed_password, username_to_update))
        messagebox.showinfo("Success", "User updated successfully!")
        conn.commit()
        conn.close()
        update_window.destroy()

    buttonUpdate = customtkinter.CTkButton(update_window, text="Update User", command=update_user)
    buttonUpdate.place(relx=0.3, rely=0.6)

    update_window.mainloop()


def delete_user():
    #username_to_delete = simpledialog.askstring("Input", "Enter the username to delete:")
    username_to_delete = custom_input_dialog(main_window, "Input", "Enter the username to delete:")
    if not username_to_delete:
        return

    conn = sqlite3.connect('chat_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username_to_delete,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        messagebox.showerror("Error", "User not found.")
        return

    confirm = messagebox.askyesno("Confirmation", f"Do you really want to delete the user {username_to_delete}?")
    if not confirm:
        return

    conn = sqlite3.connect('chat_app.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username_to_delete,))
    messagebox.showinfo("Success", "User deleted successfully!")
    conn.commit()
    conn.close()

# Rest of your code...

main_window.labelPseudo = customtkinter.CTkLabel(main_window, text="Login : ", justify=tk.CENTER)
main_window.labelPseudo.place(relheight=0.1, relx=0.1, rely=0.2)
main_window.entryPseudo = customtkinter.CTkEntry(main_window)
main_window.entryPseudo.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.2)

main_window.title("Register or update or delete users")

main_window.labelFirstName = customtkinter.CTkLabel(main_window, text="FirstName : ", justify=tk.CENTER)
main_window.labelFirstName.place(relheight=0.1, relx=0.1, rely=0.3)
main_window.entryFirstName = customtkinter.CTkEntry(main_window)
main_window.entryFirstName.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.3)

main_window.labelLastName = customtkinter.CTkLabel(main_window, text="LastName : ", justify=tk.CENTER)
main_window.labelLastName.place(relheight=0.1, relx=0.1, rely=0.4)
main_window.entryLastName = customtkinter.CTkEntry(main_window)
main_window.entryLastName.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.4)
main_window.labelPwd = customtkinter.CTkLabel(main_window, text="Password : ",justify=tk.CENTER)
main_window.labelPwd.place(relheight=0.1, relx=0.1, rely=0.5)
main_window.entryPwd = customtkinter.CTkEntry(main_window, show='*')
main_window.entryPwd.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.5)

main_window.create_user_button = customtkinter.CTkButton(main_window, text="Create User", command=register)
main_window.create_user_button.place(relx=0.4, rely=0.65, relwidth=0.2)

main_window.update_user_button = customtkinter.CTkButton(main_window, text="Update User", command=update_user_window)
main_window.update_user_button.place(relx=0.3, rely=0.85, relwidth=0.2)

main_window.delete_user_button = customtkinter.CTkButton(main_window, text="Delete User", command=delete_user)
main_window.delete_user_button.place(relx=0.55, rely=0.85, relwidth=0.2)

main_window.configure(width=1000, height=600)

main_window.mainloop()
