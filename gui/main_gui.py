import customtkinter as ctk
from create_gui import CreateWindow


ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.title("Window")
root.geometry('300x300')

def withdraw():
    root.withdraw()

def create():
    CreateWindow(root)
    withdraw()

button_create = ctk.CTkButton(root, text="Создание отчёта", border_width=2, border_color="grey", hover_color="#53e078",command=create)
button_create.pack(pady=20)

button_compare = ctk.CTkButton(root, text="Сравнение отчётов", border_width=2, border_color="grey", hover_color="#53e078")
button_compare.pack()

root.mainloop()