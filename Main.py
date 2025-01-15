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

        return self.entry_true  # focus initial

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
            pass  # Accepta doar numere

    def apply(self):
        try:
            self.prob_true = float(self.entry_true.get())
            self.prob_false = float(self.entry_false.get())
        except ValueError:
            messagebox.showerror("Input invalid", "Va rugam sa introduceti numere valide pentru probabilitati")
            self.prob_true = None
            self.prob_false = None


class ConditionalProbabilityDialog(simpledialog.Dialog):
    def __init__(self, parent, probabilities, child_tag, title=None):
        self.probabilities = probabilities
        self.child_tag = child_tag
        super().__init__(parent, title=title)

    def body(self, master):
        ttk.Label(master, text="Parinte 1").grid(row=0, column=0)
        ttk.Label(master, text="Parinte 2").grid(row=0, column=1)
        ttk.Label(master, text=f"P({self.child_tag} = Da)").grid(row=0, column=2)
        ttk.Label(master, text=f"P({self.child_tag} = Nu)").grid(row=0, column=3)

        self.entries = []
        for i, (p1, p2, p_true, p_false) in enumerate(self.probabilities):
            ttk.Label(master, text=p1).grid(row=i + 1, column=0)
            ttk.Label(master, text=p2).grid(row=i + 1, column=1)
            entry_true = ttk.Entry(master)
            entry_true.insert(0, str(p_true))
            entry_true.grid(row=i + 1, column=2)
            entry_false = ttk.Entry(master)
            entry_false.insert(0, str(p_false))
            entry_false.grid(row=i + 1, column=3)
            self.entries.append((entry_true, entry_false))

        return None  # Nu exista focus initial

    def apply(self):
        try:
            for i, (p1, p2, _, _) in enumerate(self.probabilities):
                p_true = float(self.entries[i][0].get())
                p_false = float(self.entries[i][1].get())
                self.probabilities[i] = (p1, p2, p_true, p_false)
        except ValueError:
            messagebox.showerror("Input invalid", "Va rugam sa introduceti numere valide pentru probabilitati")
            self.probabilities = None


class Interfata:
    def __init__(self):
        super().__init__()

        self.root = tk.Tk()
        self.root.geometry('720x480')
        self.root.title('Proiect IA GUI')

        self.mainframe = tk.Frame(self.root, background='white')
        self.mainframe.pack(fill='both', expand=True)

        self.create_canvas_frame()

        self.probabilities = {}
        self.connections = {}

        self.root.mainloop()

    def create_canvas_frame(self):
        self.my_canvas = tk.Canvas(self.mainframe, bg='white', width=400, height=300)
        self.my_canvas.pack(fill='both', expand=True)

        self.my_canvas.bind("<Button-1>", self.on_click)
        self.my_canvas.bind("<B1-Motion>", self.on_drag)
        self.my_canvas.bind("<Double-1>", self.on_double_click)

        btn_frame = ttk.Frame(self.mainframe)
        btn_frame.pack(fill='x', expand=True)

        ttk.Button(btn_frame, text="Creeaza Linie", command=self.create_line).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Creeaza Cerc", command=self.create_circle).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Sterge Tot", command=self.delete).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Help", command=self.show_help).pack(side='left', padx=5)

        self.selected_circle = None
        self.create_line_mode = False

    def on_click(self, event):
        selected = self.my_canvas.find_overlapping(event.x - 10, event.y - 10, event.x + 10, event.y + 10)
        if selected:
            self.my_canvas.selected = selected[-1]
            self.my_canvas.startxy = (event.x, event.y)

            tags = self.my_canvas.gettags(self.my_canvas.selected)
            if "circle" in tags:
                group_tag = tags[0]
                self.my_canvas.selected = self.my_canvas.find_withtag(group_tag)[0]

                if self.selected_circle is None:
                    self.selected_circle = self.my_canvas.selected
                else:
                    if self.create_line_mode:
                        self.draw_arrow(self.selected_circle, self.my_canvas.selected)
                        self.add_connection(self.selected_circle, self.my_canvas.selected)
                        self.selected_circle = None
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
                if "nu_este_orfan" in tags:
                    # Nod cu parinti - afiseaza dialogul pentru probabilitati conditionate
                    child_tag = self.my_canvas.gettags(self.my_canvas.selected)[0]
                    existing_probs = self.probabilities.get(self.my_canvas.selected)

                    if existing_probs and isinstance(existing_probs, list):
                        parent_probabilities = existing_probs
                    else:
                        parents = self.connections.get(self.my_canvas.selected, [])
                        parent_tags = [self.my_canvas.gettags(p)[0] for p in parents]
                        parent_probabilities = [
                            ("Da", "Da", 0.5, 0.5),
                            ("Da", "Nu", 0.5, 0.5)
                        ]
                        if len(parents) == 2:
                            parent_probabilities.extend([
                                ("Nu", "Da", 0.5, 0.5),
                                ("Nu", "Nu", 0.5, 0.5)
                            ])

                    dialog = ConditionalProbabilityDialog(self.root, parent_probabilities, child_tag,
                                                          title="Introdu probabilitatile conditionate")
                    if dialog.probabilities:
                        self.probabilities[self.my_canvas.selected] = dialog.probabilities
                else:
                    # Nod fara parinti - afiseaza dialogul pentru probabilitati simple
                    prob_true, prob_false = self.probabilities.get(self.my_canvas.selected, (0.5, 0.5))
                    dialog = ProbabilityDialog(self.root, prob_true, prob_false, title="Introdu probabilitatile")
                    if dialog.prob_true is not None and dialog.prob_false is not None:
                        self.probabilities[self.my_canvas.selected] = (dialog.prob_true, dialog.prob_false)

    def delete(self):
        self.create_line_mode = False
        msg = messagebox.askyesnocancel('Info', 'Stergeti toate elementele din canvas?')
        if msg:
            self.my_canvas.delete("all")
            self.probabilities.clear()
            self.connections.clear()

    def create_line(self):
        self.create_line_mode = True
        self.selected_circle = None

    def create_circle(self):
        self.create_line_mode = False
        text = simpledialog.askstring("Input", "Introdu text pentru cerc:")
        if text is None:
            return

        circle_id = self.my_canvas.create_oval(10, 10, 70, 70, fill='orange', outline='blue', tags="circle")
        coords = self.my_canvas.coords(circle_id)
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        group_tag = f"group_{circle_id}"
        self.my_canvas.itemconfig(circle_id, tags=(group_tag, "circle"))
        text_id = self.my_canvas.create_text(x, y, text=text, tags=(group_tag,))
        self.my_canvas.tag_raise(text_id, circle_id)
        self.probabilities[circle_id] = (0.5, 0.5)

    def show_help(self):
        messagebox.showinfo("Help", "Prin apasarea butonului 'Creeaza Linie', selectati doua cercuri pentru a desena o linie intre ele. Prin apasarea butonului 'Creeaza Cerc', puteti adauga un nou cerc in canvas. Butonul 'Sterge Tot' va elimina toate elementele din canvas.")

    def draw_arrow(self, circle1_id, circle2_id):
        coords1 = self.my_canvas.coords(circle1_id)
        coords2 = self.my_canvas.coords(circle2_id)
        x1 = (coords1[0] + coords1[2]) / 2
        y1 = (coords1[1] + coords1[3]) / 2
        x2 = (coords2[0] + coords2[2]) / 2
        y2 = (coords2[1] + coords2[3]) / 2
        radius1 = (coords1[2] - coords1[0]) / 2
        radius2 = (coords2[2] - coords2[0]) / 2
        angle1 = self.angle_to_point(x1, y1, x2, y2)
        angle2 = self.angle_to_point(x2, y2, x1, y1)
        x1_outer = x1 + radius1 * angle1[0]
        y1_outer = y1 + radius1 * angle1[1]
        x2_outer = x2 + radius2 * angle2[0]
        y2_outer = y2 + radius2 * angle2[1]
        arrow_line = self.my_canvas.create_line(x1_outer, y1_outer, x2_outer, y2_outer, arrow=tk.LAST, width=2, fill="black")
        self.my_canvas.tag_raise(arrow_line)

    def angle_to_point(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:
            return (1, 0)
        return (dx / length, dy / length)

    def add_connection(self, parent_id, child_id):
        if child_id not in self.connections:
            self.connections[child_id] = []
        self.connections[child_id].append(parent_id)

        # Adauga tag-ul special daca nodul devine copil
        if "nu_este_orfan" not in self.my_canvas.gettags(child_id):
            self.my_canvas.addtag_withtag("nu_este_orfan", child_id)

    def calculate_conditional_probability(self, child_id):
        parents = self.connections.get(child_id, [])
        if not parents:
            return self.probabilities[child_id][0]

        prob_true = 0.0
        for parent in parents:
            parent_prob_true = self.probabilities[parent][0]
            prob_true += parent_prob_true / len(parents)

        return prob_true

    def show_probability_table(self):
        """Afiseaza un tabel al probabilitatilor pentru toate nodurile."""
        if not self.probabilities:
            messagebox.showinfo("Info", "Nu exista probabilitati de afisat!")
            return

        table_window = tk.Toplevel(self.root)
        table_window.title("Tabelul de Probabilitati")

        tree = ttk.Treeview(table_window, columns=("Nod", "Prob. True", "Prob. False", "Parinti", "Bunici"), show="headings")
        tree.heading("Nod", text="Nod")
        tree.heading("Prob. True", text="Prob. True")
        tree.heading("Prob. False", text="Prob. False")
        tree.heading("Parinti", text="Parinti")
        tree.heading("Bunici", text="Bunici")
        tree.pack(fill="both", expand=True)

        for node, (prob_true, prob_false) in self.probabilities.items():
            group_tag = self.my_canvas.gettags(node)[0]
            parents = ", ".join(self.connections.get(group_tag, []))
            grandparents = ", ".join(self.grandparent_connections.get(group_tag, []))
            tree.insert("", "end", values=(group_tag, prob_true, prob_false, parents, grandparents))


if __name__ == "__main__":
    Interfata()
