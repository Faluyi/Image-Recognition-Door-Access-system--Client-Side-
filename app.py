import socket
import json
from cryptography.fernet import Fernet, MultiFernet
from aiModel import TM_model
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog


key1 = b'q_liNo3weVdsXduBUYcNg1NrZ_koMQ0Sz7cbQGyax3A='
key2 = b'WKzylsCkB5e4dm5JDBYzwQyYlQ8Ha5EhOsbuXgO6IXI='
cipher = MultiFernet([Fernet(key1), Fernet(key2)])

door_pass = {
    "1": "3 Palm open",
    "2": "1 like",
    "3": "4 fist"
}

class Handler:
    
    def send_request(self, command, payload):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 5000))
        
        data_dict = {
            'command': command,
            'payload': payload,
        }
        
        serialized_data = json.dumps(data_dict).encode('utf-8')
        encrypted_data = cipher.encrypt(serialized_data)
        print("encrypted data: ", encrypted_data)
        client_socket.sendall(encrypted_data)
        encrypted_response = client_socket.recv(1024)
        print("response: ", encrypted_response)
        response = cipher.decrypt(encrypted_response).decode('utf-8')
        
        print(f"Server response: {response}")
        client_socket.close()
        return response

    def register(self, username, password):
        payload = {
            "username": username,
            "password": password
        }
        return self.send_request('REGISTER', payload)
        
    def login(self, username, password):
        try:
            payload = {
                "username": username,
                "password": password
            }
            return self.send_request('LOGIN', payload)
        except Exception as e:
            print("Invalid username or password")
            print(f"Error: {e}")
            return "Error"

    def authenticate(self, door_number):
        if door_number not in range(1, 4):
            print("Please enter a valid door number")
            return False

        class_name, confidence_score = TM_model().get_prediction_from_webcam()
        if door_pass[str(door_number)].lower() == class_name.lower():
            return True
        else:
            return False

class App:
    def __init__(self, root):
        self.handler = Handler()
        self.root = root
        self.root.title("User Authentication System")

        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)

        self.choice_label = tk.Label(self.frame, text="Do you want to register or login? (register/login):")
        self.choice_label.pack()

        self.choice_entry = tk.Entry(self.frame)
        self.choice_entry.pack()

        self.username_label = tk.Label(self.frame, text="Enter username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.frame)
        self.username_entry.pack()

        self.password_label = tk.Label(self.frame, text="Enter password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.frame, show="*")
        self.password_entry.pack()

        self.submit_button = tk.Button(self.frame, text="Submit", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        choice = self.choice_entry.get().strip().lower()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if choice == 'register':
            response = self.handler.register(username, password)
            messagebox.showinfo("Response", response)
            
        elif choice == 'login':
            response = self.handler.login(username, password)
            messagebox.showinfo("Response", response)
            if response and response.lower() == "login successful":
                self.door_access()
                
        else:
            messagebox.showerror("Error", "Invalid choice")

    def door_access(self):
        try:
            door_number = int(simpledialog.askstring("Input", "Please enter the door number (1/2/3):"))
            authenticated = self.handler.authenticate(door_number)
            
            if authenticated:
                messagebox.showinfo("Access Granted", "Access granted!\nDoor opened!")
                payload = {
                    "username": self.username_entry.get().strip(),
                    "door": door_number
                }
                self.handler.send_request('LOG', payload)
            else:
                messagebox.showerror("Access Denied", "Access denied!")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid door number")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
