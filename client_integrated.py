import sqlite3
import socket
import threading
import time
from tkinter import *
from tkinter import Toplevel, Tk, Label, Entry, Button, PhotoImage, messagebox, Scrollbar, Text, END, Listbox, CENTER, TOP, BOTTOM, BOTH, RIGHT
from PIL import Image, ImageTk
import pickle
import rsa
import binascii
import bcrypt

class LoginApp:
    def __init__(self, master):
        self.master = master
        master.title("Login")
        master.resizable(width=False, height=False)
        master.geometry("800x400")

        # Welcome Label
        self.label_welcome = Label(master, text="Welcome To SecureChat", font=("Arial", 20, "bold"))
        self.label_welcome.place(relheight=0.15, relx=0.5, rely=0.2, anchor="center")

        # Username Label
        self.label_username = Label(master, text="Login : ", justify= CENTER)
        self.label_username.place(relheight=0.1, relx=0.1, rely=0.3)

        # Username Entry
        self.entry_username = Entry(master)
        self.entry_username.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.3)
        self.entry_username.focus()

        # Password Label
        self.label_password = Label(master, text="Password : ", justify= CENTER)
        self.label_password.place(relheight=0.1, relx=0.1, rely=0.45)

        # Password Entry
        self.entry_password = Entry(master, show='*')
        self.entry_password.place(relwidth=0.4, relheight=0.08, relx=0.3, rely=0.45)

        # Login Button
        self.login_button = Button(master, text="Login", command=self.login)
        self.login_button.place(relx=0.3, rely=0.6, relwidth=0.4, relheight=0.1)

        
    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        if not (username and password):
            messagebox.showerror("Error", "Both username and password are required.")
            return

        # Check username and password against the database
        conn = sqlite3.connect('chat_app.db')
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE LOWER(username) = LOWER(?)', (username,))
        user = cursor.fetchone()

        conn.close()

        print(f"Entered Username: {username}")
        print(f"Database User: {user}")
        print(f"Entered Password: {password}")
        print(f"Stored Hashed Password: {user[4]}")

        stored_hashed_password = user[4]

        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            messagebox.showinfo("Success", "Login successful!")
            #self.master.destroy()
            self.master.destroy()
            chatroom_root = Tk()
            chatroom_app = ChatroomApp(chatroom_root, username, "nps logo.png")
            #chatroom_app.start() 
            chatroom_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password. Please try again.")

class ChatroomApp:
    def __init__(self, master, name, image_path):
        self.master = master
        self.name = name
        self.image_path = image_path
        self.public, self.private = rsa.generate_keypair(1024)
        self.msg = pickle.dumps(self.public)
        self.input_root = None  # Initialize input_root
        self.start()  # Call the start method in __init__

    def start(self):
        print("inside start of chatroom")
        self.input_root = Toplevel(self.master)
        
        img = Image.open(self.image_path)
        tk_img = ImageTk.PhotoImage(img)

        label = Label(self.input_root, image=tk_img)
        label.image = tk_img  # Keep a reference to the image to prevent garbage collection
        label.pack()

        self.edit_text_ip = Entry(self.input_root)
        self.edit_text_port = Entry(self.input_root)
        self.ip_label = Label(self.input_root, text="Enter IP:")
        self.port_label = Label(self.input_root, text="Enter Port:")
        self.connect_btn = Button(self.input_root, text="Connect To Server", command=self.set_ip, bg='#668cff', fg="white")
        # Variables for GUI elements

        # Show GUI elements
        self.ip_label.pack(fill=X, side=TOP)
        self.edit_text_ip.pack(fill=X, side=TOP)
        self.port_label.pack(fill=X, side=TOP)
        self.edit_text_port.pack(fill=X, side=TOP)
        self.connect_btn.pack(fill=X, side=BOTTOM)
        self.input_root.title(self.name)
        self.input_root.geometry("400x400")
        self.input_root.resizable(width=False, height=False)

    def set_ip(self):
        print("inside set_ip")
        ip = "127.0.0.1"
        port = "3456"
        global client
        client = socket.socket()
        client.connect((ip, int(port)))

        # Destroy input root
        self.input_root.destroy()

        # Sending details
        self.name1 = client.recv(1024).decode()
        client.send(str.encode(self.name))
        rmsg = client.recv(1024)
        self.pkey = pickle.loads(rmsg)

        client.send(self.msg)

        # Main Root GUI
        self.show_main_gui()

    def show_main_gui(self):
        print("inside show main gui")
        img = Image.open(self.image_path)
        tk_img = ImageTk.PhotoImage(img)

        label = Label(self.master, image=tk_img)
        label.image = tk_img  # Keep a reference to the image to prevent garbage collection
        label.pack()

        Label(self.master, text="Welcome to the Chatroom", font=("Helvetica", 16)).pack()

        # Scrollbar
        scrollbar = Scrollbar(self.master)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox = Listbox(self.master, yscrollcommand=scrollbar.set)
        self.listbox.pack(fill=BOTH, side=TOP)
        scrollbar.config(command=self.listbox.yview)

        button = Button(self.master, text="Send Message", command=self.send, bg='#4040bf', fg="white")
        button.pack(fill=X, side=BOTTOM)
        self.edit_text = Entry(self.master)
        self.edit_text.pack(fill=X, side=BOTTOM)

        self.master.title(self.name)
        self.master.geometry("400x700")
        self.master.resizable(width=True, height=True)

        threading.Thread(target=self.recv).start()

    def send(self):
        if str(self.edit_text.get()).strip() != "":
            message = str.encode(self.edit_text.get())
            hex_data = binascii.hexlify(message)
            plain_text = int(hex_data, 16)
            ctt = rsa.encrypt(plain_text, self.pkey)
            client.send(str(ctt).encode())
            # Scrollbar
            self.listbox.insert(END, message)
            self.edit_text.delete(0, END)

    def recv(self):
        while True:
            self.response_message = int(client.recv(1024).decode())
            print(self.response_message)
            decrypted_msg = rsa.decrypt(self.response_message, self.private)
            # Scrollbar
            self.listbox.insert(END, self.name1 + " : " + str(decrypted_msg))
            self.edit_text.delete(0, END)

# Example usage
def main():
    root = Tk()
    login_app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
