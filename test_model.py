import tkinter as tk
from tkinter import ttk, messagebox, StringVar, Listbox, Scrollbar, Entry, Button, Label
import sqlite3

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter Frame Switching Example")
        self.geometry("600x400")

        # Создаем контейнер для фреймов
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # Создаем фреймы
        self.frames = {}
        for F in (StartPage, DatabasePage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Показываем первый фрейм
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = ttk.Label(self, text="Добро пожаловать в программу закупок")
        label.pack(pady=10, padx=10)

        button = ttk.Button(self, text="Войти",
                            command=lambda: controller.show_frame("DatabasePage"))
        button.pack()

class DatabasePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Инициализация базы данных
        self.db = DB()

        # Создаем надписи для полей ввода и размещаем их по сетке
        l1 = Label(self, text="Название")
        l1.grid(row=0, column=0)

        l2 = Label(self, text="Стоимость")
        l2.grid(row=0, column=2)

        l3 = Label(self, text="Комментарий")
        l3.grid(row=1, column=0)

        # Создаем поле ввода названия покупки, говорим, что это будут строковые переменные и размещаем их тоже по сетке
        self.product_text = StringVar()
        self.e1 = Entry(self, textvariable=self.product_text)
        self.e1.grid(row=0, column=1)

        # То же самое для комментариев и цен
        self.price_text = StringVar()
        self.e2 = Entry(self, textvariable=self.price_text)
        self.e2.grid(row=0, column=3)

        self.comment_text = StringVar()
        self.e3 = Entry(self, textvariable=self.comment_text)
        self.e3.grid(row=1, column=1)

        # Создаем список, где появятся наши покупки, и сразу определяем его размеры в окне
        self.list1 = Listbox(self, height=25, width=65)
        self.list1.grid(row=2, column=0, rowspan=6, columnspan=2)

        # На всякий случай добавим сбоку скролл, чтобы можно было быстро прокручивать длинные списки
        sb1 = Scrollbar(self)
        sb1.grid(row=2, column=2, rowspan=6)

        # Привязываем скролл к списку
        self.list1.configure(yscrollcommand=sb1.set)
        sb1.configure(command=self.list1.yview)

        # Привязываем выбор любого элемента списка к запуску функции выбора
        self.list1.bind('<<ListboxSelect>>', self.get_selected_row)

        # Создаем кнопки действий и привязываем их к своим функциям
        # Кнопки размещаем тоже по сетке
        b1 = Button(self, text="Посмотреть все", width=12, command=self.view_command)
        b1.grid(row=2, column=3)

        b2 = Button(self, text="Поиск", width=12, command=self.search_command)
        b2.grid(row=3, column=3)

        b3 = Button(self, text="Добавить", width=12, command=self.add_command)
        b3.grid(row=4, column=3)

        b4 = Button(self, text="Обновить", width=12, command=self.update_command)
        b4.grid(row=5, column=3)

        b5 = Button(self, text="Удалить", width=12, command=self.delete_command)
        b5.grid(row=6, column=3)

        b6 = Button(self, text="Закрыть", width=12, command=self.on_closing)
        b6.grid(row=7, column=3)

        # Обновляем общий список расходов
        self.view_command()

    def get_selected_row(self, event):
        global selected_tuple
        index = self.list1.curselection()[0]
        selected_tuple = self.list1.get(index)
        self.e1.delete(0, tk.END)
        self.e1.insert(tk.END, selected_tuple[1])
        self.e2.delete(0, tk.END)
        self.e2.insert(tk.END, selected_tuple[2])
        self.e3.delete(0, tk.END)
        self.e3.insert(tk.END, selected_tuple[3])

    def view_command(self):
        self.list1.delete(0, tk.END)
        for row in self.db.view():
            self.list1.insert(tk.END, row)

    def search_command(self):
        self.list1.delete(0, tk.END)
        for row in self.db.search(self.product_text.get()):
            self.list1.insert(tk.END, row)

    def add_command(self):
        self.db.insert(self.product_text.get(), self.price_text.get(), self.comment_text.get())
        self.view_command()

    def delete_command(self):
        self.db.delete(selected_tuple[0])
        self.view_command()

    def update_command(self):
        self.db.update(selected_tuple[0], self.product_text.get(), self.price_text.get())
        self.view_command()

    def on_closing(self):
        if messagebox.askokcancel("", "Закрыть программу?"):
            self.controller.destroy()

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("mybooks.db")
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS buy (id INTEGER PRIMARY KEY, product TEXT, price TEXT, comment TEXT)")
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def view(self):
        self.cur.execute("SELECT * FROM buy")
        rows = self.cur.fetchall()
        return rows

    def insert(self, product, price, comment):
        self.cur.execute("INSERT INTO buy VALUES (NULL,?,?,?)", (product, price, comment,))
        self.conn.commit()

    def update(self, id, product, price):
        self.cur.execute("UPDATE buy SET product=?, price=? WHERE id=?", (product, price, id,))
        self.conn.commit()

    def delete(self, id):
        self.cur.execute("DELETE FROM buy WHERE id=?", (id,))
        self.conn.commit()

    def search(self, product="", price=""):
        self.cur.execute("SELECT * FROM buy WHERE product=?", (product,))
        rows = self.cur.fetchall()
        return rows

if __name__ == "__main__":
    app = App()
    app.mainloop()
