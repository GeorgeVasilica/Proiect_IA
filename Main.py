import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class ProbabilityDialog(simpledialog.Dialog):
    def __init__(self, parent, prob_true=0.5, prob_false=0.5, title=None):
        self.prob_true = prob_true
        self.prob_false = prob_false
        super().__init__(parent, title=title)

    def body(self, master):
        ttk.Label(master, text="Probabilitatea pentru True:").grid(row=0, column=0)
        self.entry_true = ttk.Entry(master)
        self.entry_true.insert(0, str(self.prob_true))
        self.entry_true.grid(row=0, column=1)

        ttk.Label(master, text="Probabilitatea pentru False:").grid(row=1, column=0)
        self.entry_false = ttk.Entry(master)
        self.entry_false.insert(0, str(self.prob_false))
        self.entry_false.grid(row=1, column=1)

        self.entry_true.bind("<KeyRelease>", self.update_probabilities)
        self.entry_false.bind("<KeyRelease>", self.update_probabilities)

        return self.entry_true  # initial focus

    def update_probabilities(self, event):
        try:
            prob_true = float(self.entry_true.get())

            if 0 <= prob_true <= 1:
                prob_false = 1 - prob_true
                self.entry_false.delete(0, tk.END)
                self.entry_false.insert(0, str(round((prob_false), 2)))
                self.prob_true = prob_true
                self.prob_false = prob_false

        except ValueError:
            pass  # Acceptam doar numere

    def apply(self):
        try:
            self.prob_true = float(self.entry_true.get())
            self.prob_false = float(self.entry_false.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numbers for probabilities")
            self.prob_true = None
            self.prob_false = None


class Interfata:
    def __init__(self):
        super().__init__()

        """Mainframe"""
        self.root = tk.Tk()
        self.root.geometry('720x480')
        self.root.title('Proiect IA GUI')

        self.mainframe = tk.Frame(self.root, background='white')
        self.mainframe.pack(fill='both', expand=True)

        """Frame Canvas"""
        self.create_canvas_frame()

        self.probabilities = {}  # Dictionar pentru a stoca probabilitatile fiecarui cerc
        self.connections = {}  # Dictionar pentru a stoca relatiile parent-child

        self.root.mainloop()

    def create_canvas_frame(self):
        self.my_canvas = tk.Canvas(self.mainframe, bg='white', width=400, height=300)
        self.my_canvas.pack(fill='both', expand=True)

        self.my_canvas.bind("<Button-1>", self.on_click)
        self.my_canvas.bind("<B1-Motion>", self.on_drag)
        self.my_canvas.bind("<Double-1>", self.on_double_click)

        # Adaugarea butoanelor pentru crearea formelor si stergerea continutului canvas-ului
        btn_frame = ttk.Frame(self.mainframe)
        btn_frame.pack(fill='x', expand=True)

        ttk.Button(btn_frame, text="Creeaza Linie", command=self.create_line).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Creeaza Cerc", command=self.create_circle).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Sterge Tot", command=self.delete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Help", command=self.show_help).pack(side='left', padx=5)

        self.selected_circle = None  # Pentru a urmari primul cerc selectat pentru crearea sagetii
        self.create_line_mode = False  # Pentru a urmari daca butonul "Creeaza Linie" este activ

    def on_click(self, event):
        selected = self.my_canvas.find_overlapping(event.x - 10, event.y - 10, event.x + 10, event.y + 10)
        if selected:
            self.my_canvas.selected = selected[-1]  # selecteaza elementul de sus
            self.my_canvas.startxy = (event.x, event.y)

            # Obtine tag-ul grupului asociat cu elementul selectat
            tags = self.my_canvas.gettags(self.my_canvas.selected)
            if "circle" in tags:
                group_tag = tags[0]
                self.my_canvas.selected = self.my_canvas.find_withtag(group_tag)[0]

                if self.selected_circle is None:
                    # Primul cerc selectat, stocheaza ID-ul si centrul
                    self.selected_circle = self.my_canvas.selected
                else:
                    if self.create_line_mode:
                        # Al doilea cerc selectat, deseneaza sageata
                        self.draw_arrow(self.selected_circle, self.my_canvas.selected)
                        self.add_connection(self.selected_circle, self.my_canvas.selected)
                        self.selected_circle = None  # Reseteaza pentru a permite selectarea unui nou cerc
        else:
            self.my_canvas.selected = None

    def on_drag(self, event):
        if self.my_canvas.selected:
            dx, dy = event.x - self.my_canvas.startxy[0], event.y - self.my_canvas.startxy[1]
            tags = self.my_canvas.gettags(self.my_canvas.selected)

            if "circle" in tags:
                group_tag = tags[0]
                self.my_canvas.move(group_tag, dx, dy)

            self.my_canvas.startxy = (event.x, event.y)

    def on_double_click(self, event):
        selected = self.my_canvas.find_overlapping(event.x - 10, event.y - 10, event.x + 10, event.y + 10)
        if selected:
            self.my_canvas.selected = selected[-1]
            tags = self.my_canvas.gettags(self.my_canvas.selected)
            if "circle" in tags:
                prob_true, prob_false = self.probabilities.get(self.my_canvas.selected, (0.5, 0.5))
                dialog = ProbabilityDialog(self.root, prob_true, prob_false, title="Introdu probabilitatile")
                if dialog.prob_true is not None and dialog.prob_false is not None:
                    self.probabilities[self.my_canvas.selected] = (dialog.prob_true, dialog.prob_false)
                    self.update_child_probabilities(self.my_canvas.selected)
                    print(
                        f"Probabilitati pentru cercul {self.my_canvas.selected}: True = {dialog.prob_true}, False = {dialog.prob_false}")

    def delete(self):
        self.create_line_mode = False
        msg = messagebox.askyesnocancel('Info', 'Stergeti toate elementele din canvas?')
        if msg == True:
            self.my_canvas.delete("all")
            self.probabilities.clear()  # Clear the probabilities dictionary
            self.connections.clear()  # Clear the connections dictionary

    def create_line(self):
        self.create_line_mode = True  # Seteaza flag-ul pentru desenarea liniilor
        self.selected_circle = None  # Reseteaza cercul selectat imediat cand se apasa "Creeaza Linie"

    def create_circle(self):
        self.create_line_mode = False  # Reseteaza flag-ul pentru crearea liniei
        # Prompt pentru introducerea textului pentru cerc
        text = simpledialog.askstring("Input", "Introdu text pentru cerc:")
        if text is None:
            return  # Daca dialogul este anulat, nu crea cercul

        # Creeaza cerc
        circle_id = self.my_canvas.create_oval(10, 10, 70, 70, fill='orange', outline='blue', tags="circle")

        # Calculeaza centrul cercului
        coords = self.my_canvas.coords(circle_id)
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2

        # Creeaza un tag unic pentru grup
        group_tag = f"group_{circle_id}"

        # Adauga tag-ul grupului la cerc
        self.my_canvas.itemconfig(circle_id, tags=(group_tag, "circle"))

        # Creeaza text in centrul cercului
        text_id = self.my_canvas.create_text(x, y, text=text, tags=(group_tag,))

        # Asigura ca textul este vizibil deasupra cercului
        self.my_canvas.tag_raise(text_id, circle_id)

        # Initialize the probabilities for the new circle
        self.probabilities[circle_id] = (0.5, 0.5)

    def show_help(self):
    messagebox.showinfo("Help", "Prin apăsarea butonului 'Creează Linie', selectați două cercuri pentru a desena o linie între ele. Prin apăsarea butonului 'Creează Cerc', puteți adăuga un nou cerc în canvas. Butonul 'Șterge Tot' va elimina toate elementele din canvas.")

    def draw_arrow(self, circle1_id, circle2_id):
        # Obtine coordonatele ambelor cercuri
        coords1 = self.my_canvas.coords(circle1_id)
        coords2 = self.my_canvas.coords(circle2_id)

        # Calculeaza centrul cercurilor
        x1 = (coords1[0] + coords1[2]) / 2
        y1 = (coords1[1] + coords1[3]) / 2
        x2 = (coords2[0] + coords2[2]) / 2
        y2 = (coords2[1] + coords2[3]) / 2

        # Calculeaza vectorii de directie de la centru la marginea cercului
        radius1 = (coords1[2] - coords1[0]) / 2
        radius2 = (coords2[2] - coords2[0]) / 2

        # Calculeaza punctele de pe marginea cercurilor
        angle1 = self.angle_to_point(x1, y1, x2, y2)
        angle2 = self.angle_to_point(x2, y2, x1, y1)

        # Calculeaza punctele exterioare ale cercurilor bazate pe unghiuri
        x1_outer = x1 + radius1 * angle1[0]
        y1_outer = y1 + radius1 * angle1[1]
        x2_outer = x2 + radius2 * angle2[0]
        y2_outer = y2 + radius2 * angle2[1]

        # Deseneaza o linie intre punctele exterioare ale ambelor cercuri
        arrow_line = self.my_canvas.create_line(x1_outer, y1_outer, x2_outer, y2_outer, arrow=tk.LAST, width=2,
                                                fill="black")

        self.my_canvas.tag_raise(arrow_line)

    def angle_to_point(self, x1, y1, x2, y2):
        # Calculeaza unghiul intre doua puncte
        dx = x2 - x1
        dy = y2 - y1
        length = (dx ** 2 + dy ** 2) ** 0.5

        # Verifica daca lungimea este zero pentru a evita ZeroDivisionError
        if length == 0:
            return (1, 0)  # Returneaza o directie implicita (orientata spre dreapta)

        return (dx / length, dy / length)

    def add_connection(self, parent_id, child_id):
        if child_id not in self.connections:
            self.connections[child_id] = []
        self.connections[child_id].append(parent_id)

    def update_child_probabilities(self, parent_id):
        for child_id, parents in self.connections.items():
            if parent_id in parents:
                child_prob_true = self.calculate_conditional_probability(child_id)
                self.probabilities[child_id] = (child_prob_true, 1 - child_prob_true)
                print(f"Updated probabilities for child {child_id}: True = {child_prob_true}, False = {1 - child_prob_true}")

    def calculate_conditional_probability(self, child_id):
        parents = self.connections.get(child_id, [])
        if not parents:
            return self.probabilities[child_id][0]

        # Calculate the conditional probabilities
        prob_true = 0.0
        for parent in parents:
            parent_prob_true = self.probabilities[parent][0]
            prob_true += parent_prob_true / len(parents)

        return prob_true


if __name__ == "__main__":
    Interfata()
