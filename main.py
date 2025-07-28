import os
import json
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from collections import defaultdict
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import time
from dateutil.relativedelta import relativedelta
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


# 1. CLASSE DE SÉCURITÉ

class CryptoManager:
    def __init__(self, password):
        self.password = password
        print("CryptoManager: Dérivation de la clé de chiffrement...")
        
        # RÉDUIRE LES ITÉRATIONS POUR ACCÉLÉRER LE DÉMARRAGE PENDANT LES TESTS
        # La valeur de production devrait être 100 000 ou plus.
        self.iterations = 100 
        
        self.key = self._derive_key()
        print("CryptoManager: Clé dérivée avec succès.")

    def _derive_key(self):
        salt = b'salt_for_fintrack_ai_final'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.iterations, # Utilise la nouvelle variable
            backend=default_backend()
        )
        return b64encode(kdf.derive(self.password.encode()))

    # Le reste de la classe CryptoManager est inchangé...
    def encrypt(self, data):
        f = Fernet(self.key)
        return f.encrypt(data.encode('utf-8'))

    def decrypt(self, encrypted_data):
        try:
            f = Fernet(self.key)
            return f.decrypt(encrypted_data).decode('utf-8')
        except Exception:
            return None


# 2. GESTIONNAIRE DE CHEMINS & CLASSES DE DONNÉES

def get_app_data_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_path, 'fintrack_data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, filename)

class DataManager:
    def __init__(self, filename, crypto_manager):
        self.filename = get_app_data_path(f"{filename}.json.enc")
        self.crypto = crypto_manager
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.filename):
            return self._get_default_data()
        with open(self.filename, 'rb') as f:
            encrypted_data = f.read()
            if not encrypted_data: return self._get_default_data()
            decrypted_json = self.crypto.decrypt(encrypted_data)
            if decrypted_json:
                try: return json.loads(decrypted_json)
                except json.JSONDecodeError: return self._get_default_data()
        return None

    def _save(self):
        json_data = json.dumps(self.data, indent=4)
        encrypted_data = self.crypto.encrypt(json_data)
        with open(self.filename, 'wb') as f: f.write(encrypted_data)

    def _get_default_data(self):
        return []

class AccountManager(DataManager):
    def _get_default_data(self):
        return ["Compte Courant", "Épargne"]

class TransactionManager(DataManager):
    def add(self, transaction):
        self.data.append(transaction)
        self._sort_transactions()
        self._save()

    def delete(self, transaction_id):
        self.data = [t for t in self.data if t.get('id') != transaction_id]
        self._save()

    def update(self, transaction_id, new_data):
        for i, t in enumerate(self.data):
            if t.get('id') == transaction_id:
                self.data[i] = new_data
                self._sort_transactions()
                self._save()
                return

    def _sort_transactions(self):
        self.data.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%d-%m-%Y'), reverse=True)

class BudgetManager(DataManager):
    def get_budget(self, category):
        for budget in self.data:
            if budget['category'] == category: return float(budget['amount'])
        return 0.0

    def set_budget(self, category, amount):
        for budget in self.data:
            if budget['category'] == category:
                budget['amount'] = amount
                self._save()
                return
        self.data.append({'category': category, 'amount': amount})
        self._save()

class RecurringManager(DataManager):
    def add(self, recurring_data):
        self.data.append(recurring_data)
        self._save()

    def delete(self, recurring_id):
        self.data = [r for r in self.data if r.get('id') != recurring_id]
        self._save()


# 3. FENÊTRES AUXILIAIRES (POPUPS)

class BudgetWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.budget_manager = parent.budget_manager
        self.title("Gérer les Budgets Mensuels")
        self.transient(parent)
        self.grab_set()

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill="both")
        
        self.budget_entries = {}
        for i, category in enumerate(self.parent.categories):
            if category == "Salaire": continue
            ttk.Label(main_frame, text=f"{category} :").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = ttk.Entry(main_frame, width=15)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, str(self.budget_manager.get_budget(category)))
            self.budget_entries[category] = entry

        save_btn = ttk.Button(self, text="Enregistrer", command=self.save_budgets)
        save_btn.pack(pady=10)

    def save_budgets(self):
        try:
            for category, entry in self.budget_entries.items():
                amount = float(entry.get().replace(',', '.'))
                self.budget_manager.set_budget(category, amount)
            messagebox.showinfo("Succès", "Budgets enregistrés !", parent=self)
            self.parent.update_dashboard()
            self.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des montants valides.", parent=self)

class RecurringWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Gérer les Transactions Récurrentes")
        self.transient(parent)
        self.grab_set()
        # This window is a placeholder for a more complex UI
        ttk.Label(self, text="La gestion des transactions récurrentes est à implémenter ici.").pack(padx=20, pady=20)



# 4. CLASSE PRINCIPALE DE L'APPLICATION

class FinTrackApp(tk.Tk):
    def __init__(self, crypto_manager):
        super().__init__()
        self.crypto = crypto_manager
        self.selected_item_id = None
        
        # Init Managers
        self.account_manager = AccountManager(self.crypto)
        self.budget_manager = BudgetManager(self.crypto)
        self.recurring_manager = RecurringManager(self.crypto)
        self.transaction_manager = TransactionManager(self.crypto)
        
        # Window Setup
        self.title("FinTrack AI - Gestionnaire de Finances")
        self.geometry("1200x800")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Styles
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, font=('Helvetica', 10))
        self.style.configure("Success.TButton", foreground="white", background="#28a745")
        self.style.configure("Warning.TButton", foreground="black", background="#ffc107")
        self.style.configure("Danger.TButton", foreground="white", background="#dc3545")
        self.style.configure("Info.TButton", foreground="white", background="#17a2b8")
        self.style.configure("Budget.TProgressbar", troughcolor='#d3d3d3', background='#007bff')
        self.style.configure("Overbudget.TProgressbar", troughcolor='#d3d3d3', background='#dc3545')
        
        self.categories = ["Alimentation", "Transport", "Loisirs", "Factures", "Santé", "Éducation", "Salaire", "Autres"]

        self.create_widgets()
        self.process_recurring_transactions()
        self.refresh_treeview()

    def create_widgets(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Gérer les Budgets", command=self.open_budget_window)
        #file_menu.add_command(label="Gérer les Transactions Récurrentes", command=self.open_recurring_window)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both', pady=5, padx=5)
        self.transactions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.viz_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.viz_tab, text="Tableau de Bord")
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.create_transactions_widgets()
        self.create_viz_widgets()

    def create_transactions_widgets(self):
        main_frame = ttk.Frame(self.transactions_tab, padding="10")
        main_frame.pack(expand=True, fill="both")
        entry_frame = ttk.LabelFrame(main_frame, text="Ajouter / Modifier une Transaction", padding="15")
        entry_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(entry_frame, text="Date :").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = DateEntry(entry_frame, width=18, date_pattern='dd-mm-yyyy')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text="Description :").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(entry_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Label(entry_frame, text="Montant (€) :").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(entry_frame, width=15)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(entry_frame, text="Catégorie :").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.category_combobox = ttk.Combobox(entry_frame, values=self.categories, width=18)
        self.category_combobox.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Label(entry_frame, text="Compte :").grid(row=1, column=4, sticky="w", padx=5, pady=5)
        self.account_combobox = ttk.Combobox(entry_frame, values=self.account_manager.data, width=18)
        self.account_combobox.grid(row=1, column=5, padx=5, pady=5)

        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=0, columnspan=6, pady=10)
        self.add_button = ttk.Button(button_frame, text="Ajouter", style="Success.TButton", command=self.add_new_transaction)
        self.add_button.pack(side="left", padx=5)
        self.save_button = ttk.Button(button_frame, text="Enregistrer", style="Info.TButton", command=self.save_edited_transaction)
        self.clear_button = ttk.Button(button_frame, text="Effacer", command=self.clear_entries)
        self.clear_button.pack(side="left", padx=5)

        tree_actions_frame = ttk.Frame(main_frame)
        tree_actions_frame.pack(fill="x", pady=5)
        ttk.Button(tree_actions_frame, text="Modifier la sélection", style="Warning.TButton", command=self.edit_selected_transaction).pack(side="left")
        ttk.Button(tree_actions_frame, text="Supprimer la sélection", style="Danger.TButton", command=self.delete_selected_transaction).pack(side="left", padx=10)
        
        tree_frame = ttk.LabelFrame(main_frame, text="Historique", padding="10")
        tree_frame.pack(expand=True, fill="both", pady=10)
        columns = ("id", "date", "description", "amount", "category", "account")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", displaycolumns=columns[1:])
        
        for col in columns[1:]: self.tree.heading(col, text=col.capitalize())
        self.tree.column("amount", anchor="e")
        self.tree.pack(side="left", expand=True, fill="both")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def create_viz_widgets(self):
        self.viz_main_frame = ttk.Frame(self.viz_tab, padding="10")
        self.viz_main_frame.pack(expand=True, fill="both")
        
        filter_frame = ttk.Frame(self.viz_main_frame)
        filter_frame.pack(fill="x", pady=5)
        ttk.Label(filter_frame, text="Filtrer par compte :").pack(side="left", padx=5)
        self.account_filter_cb = ttk.Combobox(filter_frame, values=["Tous les comptes"] + self.account_manager.data, state="readonly")
        self.account_filter_cb.current(0)
        self.account_filter_cb.pack(side="left", padx=5)
        self.account_filter_cb.bind("<<ComboboxSelected>>", self.on_tab_changed)

        stats_frame = ttk.LabelFrame(self.viz_main_frame, text="Résumé du Mois", padding="15")
        stats_frame.pack(fill="x", pady=(0, 10))
        self.total_income_label = ttk.Label(stats_frame, text="Revenus: 0.00 €", font=("Helvetica", 12, "bold"), foreground="green")
        self.total_income_label.pack(side="left", expand=True)
        self.total_expense_label = ttk.Label(stats_frame, text="Dépenses: 0.00 €", font=("Helvetica", 12, "bold"), foreground="red")
        self.total_expense_label.pack(side="left", expand=True)
        self.net_balance_label = ttk.Label(stats_frame, text="Solde: 0.00 €", font=("Helvetica", 12, "bold"))
        self.net_balance_label.pack(side="left", expand=True)

        self.budget_frame = ttk.LabelFrame(self.viz_main_frame, text="Suivi des Budgets du Mois", padding="15")
        self.budget_frame.pack(fill="x", pady=(0, 20))

        charts_frame = ttk.Frame(self.viz_main_frame)
        charts_frame.pack(expand=True, fill="both")
        self.fig = Figure(figsize=(10, 6), dpi=100, tight_layout=True)
        self.ax_pie = self.fig.add_subplot(1, 2, 1)
        self.ax_bar = self.fig.add_subplot(1, 2, 2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.draw()
    
    def process_recurring_transactions(self):
        today = datetime.date.today()
        made_changes = False
        for recurring in self.recurring_manager.data:
            next_date = datetime.datetime.strptime(recurring['next_date'], '%d-%m-%Y').date()
            if next_date <= today:
                new_trans = {
                    'id': f"trans_{int(time.time() * 1000)}",
                    "date": next_date.strftime('%d-%m-%Y'),
                    "description": recurring['description'], "amount": recurring['amount'],
                    "category": recurring['category'], "account": recurring['account']
                }
                self.transaction_manager.add(new_trans)
                if recurring['frequency'] == 'Mensuel':
                    next_date += relativedelta(months=1)
                recurring['next_date'] = next_date.strftime('%d-%m-%Y')
                made_changes = True
        if made_changes:
            self.recurring_manager._save()
            messagebox.showinfo("Transactions Récurrentes", "Des transactions récurrentes ont été ajoutées.")

    def add_new_transaction(self):
        new_trans = {
            'id': f"trans_{int(time.time() * 1000)}",
            "date": self.date_entry.get(),
            "description": self.desc_entry.get(),
            "amount": self.amount_entry.get().replace(',', '.'),
            "category": self.category_combobox.get(),
            "account": self.account_combobox.get()
        }
        if not all(new_trans.values()):
            messagebox.showerror("Erreur", "Tous les champs sont requis.")
            return
        self.transaction_manager.add(new_trans)
        self.refresh_treeview()
        self.clear_entries()

    def edit_selected_transaction(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner une transaction à modifier.")
            return
        self.selected_item_id = selected
        
        values = self.tree.item(selected, "values")
        self.clear_entries()
        
        self.date_entry.set_date(datetime.datetime.strptime(values[0], '%d-%m-%Y'))
        self.desc_entry.insert(0, values[1])
        self.amount_entry.insert(0, values[2])
        self.category_combobox.set(values[3])
        self.account_combobox.set(values[4])
        
        self.add_button.pack_forget()
        self.save_button.pack(side="left", padx=5)

    def save_edited_transaction(self):
        if not self.selected_item_id: return
        updated_trans = {
            'id': self.selected_item_id,
            "date": self.date_entry.get(),
            "description": self.desc_entry.get(),
            "amount": self.amount_entry.get().replace(',', '.'),
            "category": self.category_combobox.get(),
            "account": self.account_combobox.get()
        }
        self.transaction_manager.update(self.selected_item_id, updated_trans)
        self.refresh_treeview()
        self.clear_entries()

    def delete_selected_transaction(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner une transaction à supprimer.")
            return
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer cette transaction ?"):
            self.transaction_manager.delete(selected)
            self.refresh_treeview()
            self.update_dashboard()

    def clear_entries(self):
        self.selected_item_id = None
        self.desc_entry.delete(0, "end")
        self.amount_entry.delete(0, "end")
        self.date_entry.set_date(datetime.date.today())
        self.category_combobox.set("Autres")
        if self.account_manager.data: self.account_combobox.current(0)
        self.save_button.pack_forget()
        self.add_button.pack(side="left", padx=5)

    def refresh_treeview(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for t in self.transaction_manager.data:
            self.tree.insert("", tk.END, values=(t['id'], t['date'], t['description'], t['amount'], t['category'], t['account']), iid=t['id'])

    def update_dashboard(self):
        selected_account = self.account_filter_cb.get()
        transactions = self.transaction_manager.data
        if selected_account != "Tous les comptes":
            transactions = [t for t in transactions if t['account'] == selected_account]

        now = datetime.datetime.now()
        income, expense = 0.0, 0.0
        monthly_expenses_cat = defaultdict(float)

        for t in transactions:
            try:
                trans_date = datetime.datetime.strptime(t['date'], '%d-%m-%Y')
                amount = abs(float(str(t['amount']).replace(',', '.')))
                if trans_date.month == now.month and trans_date.year == now.year:
                    if t['category'] == 'Salaire': income += amount
                    else: expense += amount
                if t['category'] != 'Salaire': monthly_expenses_cat[t['category']] += amount
            except (ValueError, KeyError): continue

        self.total_income_label.config(text=f"Revenus: {income:.2f} €")
        self.total_expense_label.config(text=f"Dépenses: {expense:.2f} €")
        net = income - expense
        self.net_balance_label.config(text=f"Solde: {net:.2f} €", foreground="green" if net >= 0 else "red")
        
        for widget in self.budget_frame.winfo_children(): widget.destroy()
        row = 0
        for category in self.categories:
            if category == 'Salaire': continue
            budget = self.budget_manager.get_budget(category)
            if budget > 0:
                expense_cat = monthly_expenses_cat[category]
                percent = (expense_cat / budget) * 100 if budget > 0 else 0
                ttk.Label(self.budget_frame, text=f"{category}:").grid(row=row, column=0, sticky='w')
                p_bar = ttk.Progressbar(self.budget_frame, length=200, value=percent, style="Budget.TProgressbar" if percent <= 100 else "Overbudget.TProgressbar")
                p_bar.grid(row=row, column=1, padx=5, pady=2)
                ttk.Label(self.budget_frame, text=f"{expense_cat:.2f}€ / {budget:.2f}€").grid(row=row, column=2, sticky='w')
                row += 1

        self.ax_pie.clear()
        if monthly_expenses_cat:
            self.ax_pie.pie(monthly_expenses_cat.values(), labels=monthly_expenses_cat.keys(), autopct='%1.1f%%', startangle=90)
            self.ax_pie.set_title("Répartition des Dépenses (Tous)")
        self.canvas.draw()
        
    def open_budget_window(self):
        BudgetWindow(self)

    def open_recurring_window(self):
        RecurringWindow(self)

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
            self.destroy()
            
    def on_tab_changed(self, event=None):
        if self.notebook.index(self.notebook.select()) == 1:
            self.update_dashboard()


# 5. LANCEUR DE L'APPLICATION

class AppLauncher:
    def __init__(self):
        # On ne crée plus de fenêtre racine ici.
        # La fenêtre de connexion sera temporaire et indépendante.
        print("LANCEUR: Initialisation de AppLauncher.")
        self.run()

    def run(self):
        # Crée une fenêtre racine temporaire uniquement pour la connexion
        login_root = tk.Tk()
        login_root.withdraw() # On la cache
        
        print("LANCEUR: Demande du mot de passe...")
        password = self.get_password(login_root)
        login_root.destroy() # On détruit la fenêtre temporaire

        if password:
            print("LANCEUR: Mot de passe reçu. Initialisation du CryptoManager...")
            crypto = CryptoManager(password)
            
            print("LANCEUR: Test du mot de passe en chargeant les transactions...")
            # On ne peut plus utiliser de messagebox ici car la racine est détruite,
            # on passe donc le test directement.
            tm_test = TransactionManager(crypto)
            if tm_test.data is None:
                # Si le mot de passe est mauvais, on ne peut pas afficher de message d'erreur
                # car il n'y a plus de fenêtre. On quitte simplement.
                print("LANCEUR: ERREUR - Mot de passe incorrect ou données corrompues. Fermeture.")
                return # Quitte le programme
            
            print("LANCEUR: Mot de passe correct. Lancement de l'application principale FinTrackApp...")
            app = FinTrackApp(crypto) # FinTrackApp est maintenant la fenêtre racine
            print("LANCEUR: FinTrackApp initialisée. Démarrage de la boucle principale (mainloop).")
            app.mainloop()
            print("LANCEUR: Mainloop terminée. Fermeture.")
        else:
            print("LANCEUR: Pas de mot de passe fourni. Fermeture.")
            
    def get_password(self, parent):
        # La fenêtre de connexion prend la racine temporaire comme parent
        login = LoginWindow(parent)
        parent.wait_window(login)
        return login.password

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Connexion - FinTrack AI")
        self.geometry("300x150")
        self.transient(parent)
        self.grab_set()
        self.password = None
        
        ttk.Label(self, text="Mot de passe :").pack(pady=10)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5, padx=10, fill='x')
        self.password_entry.focus()
        self.password_entry.bind("<Return>", self.on_submit)
        
        ttk.Button(self, text="Valider", command=self.on_submit).pack(pady=10)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        
    def on_submit(self, event=None):
        self.password = self.password_entry.get()
        if not self.password:
            messagebox.showerror("Erreur", "Le mot de passe ne peut pas être vide.", parent=self)
            return
        self.destroy()

    def on_cancel(self):
        self.password = None
        self.destroy()

if __name__ == "__main__":
    AppLauncher()