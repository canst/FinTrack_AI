import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

# --- CLASSE DE GESTION DES DONNÉES---
class TransactionManager:
    def __init__(self, filename="transactions.csv"):
        self.filename = filename
        self.transactions = self.load_transactions()

    def load_transactions(self):
        """Charge les transactions depuis le fichier CSV et les trie par date."""
        if not os.path.exists(self.filename):
            return []
        
        transactions = []
        with open(self.filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                transactions.append(row)
        try:
            transactions.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%d-%m-%Y'), reverse=True)
        except (ValueError, KeyError):
            pass
        return transactions

    def add_transaction(self, date, description, amount, category):
        """Ajoute une nouvelle transaction en haut de la liste et la sauvegarde."""
        transaction = {
            "date": date,
            "description": description,
            "amount": amount,
            "category": category
        }
        self.transactions.insert(0, transaction)
        self.save_transactions()
        return transaction

    def save_transactions(self):
        """Sauvegarde toutes les transactions dans le fichier CSV."""
        if not self.transactions:
            with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
                pass
            return
        
        with open(self.filename, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = self.transactions[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.transactions)
            
    def delete_transaction(self, transaction_to_delete):
        """Supprime une transaction spécifique."""
        self.transactions = [t for t in self.transactions if t != transaction_to_delete]
        self.save_transactions()

    def update_transaction(self, old_transaction, new_data):
        """Met à jour une transaction."""
        try:
            index = self.transactions.index(old_transaction)
            self.transactions[index] = new_data
            self.save_transactions()
        except ValueError:
            messagebox.showerror("Erreur", "Impossible de trouver la transaction à mettre à jour.")

# --- CLASSE DE L'APPLICATION---
class FinTrackApp(tk.Tk):
    def __init__(self, transaction_manager):
        super().__init__()
        
        self.transaction_manager = transaction_manager
        self.selected_item_id = None

        self.title("FinTrack AI - Gestionnaire de Finances")
        self.geometry("1000x750")

        # --- Définition des styles et couleurs ---
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        self.style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10))
        self.style.configure("Success.TButton", foreground="white", background="#28a745") # Vert
        self.style.configure("Warning.TButton", foreground="black", background="#ffc107") # Orange
        self.style.configure("Danger.TButton", foreground="white", background="#dc3545")  # Rouge
        self.style.configure("Info.TButton", foreground="white", background="#17a2b8")   # Bleu

        self.categories = ["Alimentation", "Transport", "Loisirs", "Factures", "Santé", "Éducation", "Salaire", "Autres"]

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', pady=5, padx=5)

        self.transactions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_tab, text="Transactions")

        self.viz_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_tab, text="Tableau de Bord")
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.create_transactions_widgets()
        self.create_viz_widgets()
        self.refresh_treeview()

    def create_transactions_widgets(self):
        """Crée les widgets pour l'onglet 'Transactions'."""
        main_frame = ttk.Frame(self.transactions_tab, padding="10")
        main_frame.pack(expand=True, fill="both")

        entry_frame = ttk.LabelFrame(main_frame, text="Nouvelle Transaction", padding="15")
        entry_frame.pack(fill=tk.X, pady=5)

        ttk.Label(entry_frame, text="Date :").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.date_entry = DateEntry(entry_frame, width=18, date_pattern='dd-mm-yyyy', background='darkblue', foreground='white')
        self.date_entry.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(entry_frame, text="Description :").grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.desc_entry = ttk.Entry(entry_frame, width=40)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=8, columnspan=2)

        ttk.Label(entry_frame, text="Montant (€) :").grid(row=0, column=2, padx=5, pady=8, sticky="w")
        self.amount_entry = ttk.Entry(entry_frame, width=15)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=8)

        ttk.Label(entry_frame, text="Catégorie :").grid(row=1, column=3, padx=5, pady=8, sticky="w")
        self.category_combobox = ttk.Combobox(entry_frame, values=self.categories, width=18)
        self.category_combobox.grid(row=1, column=4, padx=5, pady=8)
        self.category_combobox.set("Autres")

        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=1, columnspan=3, pady=20)
        
        self.add_button = ttk.Button(button_frame, text="Ajouter", command=self.add_new_transaction, style="Success.TButton")
        self.add_button.pack(side=tk.LEFT, padx=10)

        self.edit_button = ttk.Button(button_frame, text="Modifier", command=self.edit_selected_transaction, style="Warning.TButton", state="disabled")
        self.edit_button.pack(side=tk.LEFT, padx=10)

        self.delete_button = ttk.Button(button_frame, text="Supprimer", command=self.delete_selected_transaction, style="Danger.TButton", state="disabled")
        self.delete_button.pack(side=tk.LEFT, padx=10)

        self.save_button = ttk.Button(button_frame, text="Enregistrer", command=self.save_edited_transaction, style="Info.TButton")
        
        tree_frame = ttk.LabelFrame(main_frame, text="Historique des Transactions", padding="10")
        tree_frame.pack(expand=True, fill="both", pady=10)
        
        columns = ("date", "description", "amount", "category")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Date")
        self.tree.heading("description", text="Description")
        self.tree.heading("amount", text="Montant (€)")
        self.tree.heading("category", text="Catégorie")
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("description", width=400)
        self.tree.column("amount", width=120, anchor="e")
        self.tree.column("category", width=150, anchor="center")
        
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
    
    def create_viz_widgets(self):
        """Crée les widgets pour le tableau de bord."""
        main_frame = ttk.Frame(self.viz_tab, padding="10")
        main_frame.pack(expand=True, fill="both")

        stats_frame = ttk.LabelFrame(main_frame, text="Résumé du Mois en Cours", padding="15")
        stats_frame.pack(fill="x", pady=(0, 20))
        
        self.total_income_label = ttk.Label(stats_frame, text="Revenus: 0.00 €", font=("Helvetica", 12, "bold"), foreground="green")
        self.total_income_label.pack(side="left", expand=True)

        self.total_expense_label = ttk.Label(stats_frame, text="Dépenses: 0.00 €", font=("Helvetica", 12, "bold"), foreground="red")
        self.total_expense_label.pack(side="left", expand=True)
        
        self.net_balance_label = ttk.Label(stats_frame, text="Solde: 0.00 €", font=("Helvetica", 12, "bold"))
        self.net_balance_label.pack(side="left", expand=True)

        charts_frame = ttk.Frame(main_frame)
        charts_frame.pack(expand=True, fill="both")
        
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.subplots_adjust(hspace=0.4, wspace=0.3)
        
        self.ax_pie = self.fig.add_subplot(1, 2, 1)
        self.ax_bar = self.fig.add_subplot(1, 2, 2)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def update_dashboard(self):
        """
        Met à jour toutes les visualisations du tableau de bord.
        Logique corrigée: Le revenu est défini par la catégorie 'Salaire', tout le reste est une dépense.
        """
        now = datetime.datetime.now()
        income = 0.0
        expense = 0.0
        
        expenses_by_category = defaultdict(float)
        monthly_totals = defaultdict(lambda: {'income': 0, 'expense': 0})

        for t in self.transaction_manager.transactions:
            try:
                trans_date = datetime.datetime.strptime(t['date'], '%d-%m-%Y')
                # On utilise abs() pour toujours travailler avec des montants positifs
                amount = abs(float(str(t['amount']).replace(',', '.')))
                category = t['category']

                # Pour les stats du mois en cours
                if trans_date.month == now.month and trans_date.year == now.year:
                    if category == 'Salaire':
                        income += amount
                    else:
                        expense += amount

                # Pour le graphique circulaire (toutes les dépenses)
                if category != 'Salaire':
                    expenses_by_category[category] += amount
                
                # Pour le graphique en barres
                month_key = trans_date.strftime('%Y-%m')
                if category == 'Salaire':
                    monthly_totals[month_key]['income'] += amount
                else:
                    monthly_totals[month_key]['expense'] += amount

            except (ValueError, KeyError):
                continue
        
        self.total_income_label.config(text=f"Revenus: {income:.2f} €")
        self.total_expense_label.config(text=f"Dépenses: {expense:.2f} €")
        net = income - expense
        color = "green" if net >= 0 else "red"
        self.net_balance_label.config(text=f"Solde: {net:.2f} €", foreground=color)

        self.ax_pie.clear()
        if expenses_by_category:
            self.ax_pie.pie(expenses_by_category.values(), labels=expenses_by_category.keys(), autopct='%1.1f%%', startangle=140)
            self.ax_pie.set_title("Répartition des Dépenses")
        else:
            self.ax_pie.text(0.5, 0.5, "Aucune dépense", horizontalalignment='center')
        self.ax_pie.axis('equal')

        self.ax_bar.clear()
        sorted_months = sorted(monthly_totals.keys())
        if sorted_months:
            months_to_show = sorted_months[-6:]
            incomes = [monthly_totals[m]['income'] for m in months_to_show]
            expenses = [monthly_totals[m]['expense'] for m in months_to_show]
            
            bar_width = 0.35
            index = range(len(months_to_show))
            
            self.ax_bar.bar(index, incomes, bar_width, label='Revenus', color='g')
            self.ax_bar.bar([i + bar_width for i in index], expenses, bar_width, label='Dépenses', color='r')
            
            self.ax_bar.set_ylabel('Montant (€)')
            self.ax_bar.set_title('Revenus vs Dépenses Mensuels')
            self.ax_bar.set_xticks([i + bar_width / 2 for i in index])
            self.ax_bar.set_xticklabels([datetime.datetime.strptime(m, '%Y-%m').strftime('%b %y') for m in months_to_show], rotation=45)
            self.ax_bar.legend()
        else:
            self.ax_bar.text(0.5, 0.5, "Aucune donnée mensuelle", horizontalalignment='center')
        
        self.canvas.draw()
    
    def add_new_transaction(self):
        date = self.date_entry.get()
        desc = self.desc_entry.get()
        amount_str = self.amount_entry.get().replace(',', '.')
        category = self.category_combobox.get()

        if not all([date, desc, amount_str, category]):
            messagebox.showwarning("Champs incomplets", "Veuillez remplir tous les champs.")
            return
        try:
            float(amount_str)
        except ValueError:
            messagebox.showerror("Erreur de format", "Le montant doit être un nombre.")
            return

        self.transaction_manager.add_transaction(date, desc, amount_str, category)
        self.refresh_treeview()
        self.clear_entries()

    def edit_selected_transaction(self):
        if not self.selected_item_id: return
        item_values = self.tree.item(self.selected_item_id)['values']
        self.clear_entries()
        self.date_entry.set_date(datetime.datetime.strptime(item_values[0], '%d-%m-%Y'))
        self.desc_entry.insert(0, item_values[1])
        self.amount_entry.insert(0, item_values[2])
        self.category_combobox.set(item_values[3])
        self.add_button.pack_forget()
        self.save_button.pack(side=tk.LEFT, padx=10)

    def save_edited_transaction(self):
        if not self.selected_item_id: return
        old_item_values = self.tree.item(self.selected_item_id)['values']
        old_transaction = {"date": old_item_values[0], "description": old_item_values[1], "amount": str(old_item_values[2]), "category": old_item_values[3]}
        new_data = {"date": self.date_entry.get(), "description": self.desc_entry.get(), "amount": self.amount_entry.get().replace(',', '.'), "category": self.category_combobox.get()}
        self.transaction_manager.update_transaction(old_transaction, new_data)
        self.refresh_treeview()
        self.clear_entries()
        self.save_button.pack_forget()
        self.add_button.pack(side=tk.LEFT, padx=10)
    
    def delete_selected_transaction(self):
        if not self.selected_item_id: return
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette transaction ?"):
            item_values = self.tree.item(self.selected_item_id)['values']
            transaction_to_delete = {"date": item_values[0], "description": item_values[1], "amount": str(item_values[2]), "category": item_values[3]}
            self.transaction_manager.delete_transaction(transaction_to_delete)
            self.refresh_treeview()

    def on_tab_changed(self, event):
        """Met à jour le tableau de bord quand l'onglet est sélectionné."""
        selected_tab_index = self.notebook.index(self.notebook.select())
        if selected_tab_index == 1:
            self.update_dashboard()

    def on_item_select(self, event):
        """Active/désactive les boutons en fonction de la sélection."""
        if self.tree.selection():
            self.selected_item_id = self.tree.selection()[0]
            self.edit_button.config(state="normal")
            self.delete_button.config(state="normal")
        else:
            self.selected_item_id = None
            self.edit_button.config(state="disabled")
            self.delete_button.config(state="disabled")

    def refresh_treeview(self):
        """Met à jour le tableau des transactions."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        for transaction in self.transaction_manager.transactions:
            self.tree.insert("", tk.END, values=(transaction['date'], transaction['description'], transaction['amount'], transaction['category']))
        self.on_item_select(None)

    def clear_entries(self):
        """Vide les champs de saisie."""
        self.date_entry.set_date(datetime.date.today())
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_combobox.set("Autres")
        
# --- LANCEUR DE L'APPLICATION---
if __name__ == "__main__":
    manager = TransactionManager()
    app = FinTrackApp(manager)
    app.mainloop()