from tkinter import Tk, Label, Entry, Button, messagebox, Toplevel, Scrollbar, Listbox, END, CENTER
from PIL import Image, ImageTk
import sqlite3
import bcrypt 
import socket
import binascii
import rsa
import threading
import pickle
import customtkinter

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

        stored_hashed_password = user[4]

        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            messagebox.showinfo("Success", "Login successful!")
            # Create Toplevel outside of the LoginApp class
            self.master.destroy()
            chatroom_root = Tk()
            chatroom_app = ChatroomApp(chatroom_root, username, "nps logo.png")
            #chatroom_app.start()  # Call the start method inside ChatroomApp
            chatroom_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password. Please try again.")


class ChatroomApp:
    def __init__(self, master, name, image_path):
        self.master = master
        self.image_path = image_path
        self.name = name
        self.public, self.private = rsa.generate_keypair(1024)
        self.msg = pickle.dumps(self.public)
        #self.input_root = None  # Initialize input_root
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
        self.connect_btn = Button(self.input_root, text="Connect To Server", command=self.set_ip, bg='#668cff',
                                  fg="white")

        # show elements:
        self.ip_label.pack(fill="both", side="top")
        self.edit_text_ip.pack(fill="both", side="top")
        self.port_label.pack(fill="both", side="top")
        self.edit_text_port.pack(fill="both", side="top")
        self.connect_btn.pack(fill="both", side="bottom")

        self.input_root.title(self.name)
        self.input_root.geometry("400x400")
        self.input_root.resizable(width=False, height=False)

        #self.input_root.mainloop()

    def set_ip(self):
        print("inside set ip")
        ip = self.edit_text_ip.get()
        port = self.edit_text_port.get()
        ip = "127.0.0.1"
        port = "3456"

        # Define Server:
        server = socket.socket()
        server.bind((ip, int(port)))
        server.listen()

        global conn
        conn, addr = server.accept()

        # Update the existing input root
        self.input_root.destroy()

        # sending username and keys(details)-----------
        conn.send(str.encode(self.name))
        self.name1 = conn.recv(1024).decode()
        conn.send(self.msg)  # sending public key
        rmsg = conn.recv(1024)  # recv pub key
        self.pkey = pickle.loads(rmsg)
        self.show_main_gui()

    def show_main_gui(self):
        print("inside show main gui")
        # Update the existing input root
        self.input_root = Toplevel(self.master)
        img = Image.open(self.image_path)
        tk_img = ImageTk.PhotoImage(img)

        label = Label(self.input_root, image=tk_img)
        label.image = tk_img  # Keep a reference to the image to prevent garbage collection
        label.pack()

        Label(self.input_root, text="Welcome to the Chatroom", font=("Helvetica", 16)).pack()

        #self.bgimage2 = ImageTk.PhotoImage(Image.open("nps logo.png"))

        # Scrollbar:
        self.scrollbar = Scrollbar(self.input_root)
        self.scrollbar.pack(side="right", fill="y")
        self.listbox = Listbox(self.input_root, yscrollcommand=self.scrollbar.set)
        self.listbox.pack(fill="both", side="top")
        self.scrollbar.config(command=self.listbox.yview)

        self.button = Button(self.input_root, text="Send Message", command=self.send, bg='#29a329', fg="white")
        self.edit_text = Entry(self.input_root)

        self.button.pack(fill="both", side="bottom")
        self.edit_text.pack(fill="both", side="bottom")

        self.input_root.title(self.name)
        self.input_root.geometry("400x700")
        self.input_root.resizable(width=True, height=True)

        threading.Thread(target=self.recv).start()

        #self.input_root.mainloop()



    def send(self):
        if str(self.edit_text.get()).strip() != "":
            message = str.encode(self.edit_text.get())
            # converting it into numb
            hex_data = binascii.hexlify(message)
            plain_text = int(hex_data, 16)
            ctt = rsa.encrypt(plain_text, self.pkey)
            conn.send(str(ctt).encode())
            # scrollbar:
            self.listbox.insert(END, message)
            self.edit_text.delete(0, END)

    def recv(self):
        while True:
            self.response_message = int(conn.recv(1024).decode())
            print(self.response_message)
            decrypted_msg = rsa.decrypt(self.response_message, self.private)
            # scrollbar:
            self.listbox.insert(END, self.name1 + " : " + str(decrypted_msg))
            self.edit_text
def main():
    root = Tk()
    login_app = LoginApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()