# Copyright © 2026 Anas Boutaghroucht
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

import time
import secrets
import sqlite3
import bcrypt
import tkinter as tk
from tkinter import messagebox, simpledialog

# ─── Configuration ──────────────────────────────────────────
DB_FILE = "atm.db"
MAX_TENTATIVES = 3
BLOCAGE_SECONDES = 30

_tentatives_globales = {}
_bloque_global = {}
SESSION_ID = secrets.token_hex(4)

# ═══════════════════════════════════════════════════════════
# 🗄️  LOGIQUE BASE DE DONNÉES & SÉCURITÉ
# ═══════════════════════════════════════════════════════════

def connexion():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialiser_db():
    """Crée les tables et un utilisateur de test si vide."""
    with connexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pin_hash TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                prenom TEXT NOT NULL,
                email TEXT NOT NULL,
                solde REAL NOT NULL DEFAULT 0,
                tentatives INTEGER NOT NULL DEFAULT 0,
                bloque_jusqu REAL NOT NULL DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                montant REAL NOT NULL,
                solde_apres REAL NOT NULL,
                date REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Vérification/Création d'un compte de test
        nb_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if nb_users == 0:
            print("--- Création du compte de test (PIN: 1234) ---")
            h = bcrypt.hashpw("1234".encode(), bcrypt.gensalt())
            conn.execute("""
                INSERT INTO users (pin_hash, nom, prenom, email, solde)
                VALUES (?, 'Admin', 'Test', 'admin@test.com', 1000.0)
            """, (h,))
        conn.commit()

def trouver_user_par_pin(pin):
    try:
        pin_bytes = pin.encode()
        with connexion() as conn:
            # On récupère tous les utilisateurs pour comparer les hashs
            cursor = conn.execute("SELECT * FROM users")
            for row in cursor:
                if bcrypt.checkpw(pin_bytes, row["pin_hash"]):
                    return row
    except Exception as e:
        print(f"Erreur recherche utilisateur: {e}")
    return None

# ─── OPÉRATIONS FINANCIÈRES ──────────────────────────────────

def deposer(user_id, montant):
    with connexion() as conn:
        conn.execute("UPDATE users SET solde = ROUND(solde + ?, 2) WHERE id = ?", (montant, user_id))
        res = conn.execute("SELECT solde FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.execute("INSERT INTO transactions (user_id, type, montant, solde_apres, date) VALUES (?, 'depot', ?, ?, ?)",
                     (user_id, montant, res[0], time.time()))
        conn.commit()
        return res[0]

def retirer(user_id, montant):
    with connexion() as conn:
        solde_actuel = conn.execute("SELECT solde FROM users WHERE id = ?", (user_id,)).fetchone()[0]
        if montant > solde_actuel: return None
        conn.execute("UPDATE users SET solde = ROUND(solde - ?, 2) WHERE id = ? AND solde >= ?", (montant, user_id, montant))
        res = conn.execute("SELECT solde FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.execute("INSERT INTO transactions (user_id, type, montant, solde_apres, date) VALUES (?, 'retrait', ?, ?, ?)",
                     (user_id, montant, res[0], time.time()))
        conn.commit()
        return res[0]

def transferer(expediteur_id, email_dest, montant):
    with connexion() as conn:
        dest = conn.execute("SELECT id FROM users WHERE email = ?", (email_dest,)).fetchone()
        if not dest: return "Destinataire introuvable (vérifiez l'email)."
        if dest['id'] == expediteur_id: return "Action impossible : même compte."
        
        try:
            conn.execute("BEGIN TRANSACTION")
            # Retrait
            res_upd = conn.execute("UPDATE users SET solde = ROUND(solde - ?, 2) WHERE id = ? AND solde >= ?", (montant, expediteur_id, montant))
            if res_upd.rowcount == 0:
                conn.rollback()
                return "Fonds insuffisants."
            # Dépôt
            conn.execute("UPDATE users SET solde = ROUND(solde + ?, 2) WHERE id = ?", (montant, dest['id']))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return f"Erreur SQL : {e}"

# ─── SÉCURITÉ ANTI-BRUTEFORCE ───────────────────────────────

def verifier_blocage_global():
    bloque_jusqu = _bloque_global.get(SESSION_ID, 0)
    if time.time() < bloque_jusqu:
        restant = int(bloque_jusqu - time.time())
        messagebox.showwarning("Sécurité", f"Trop d'échecs. Réessayez dans {restant}s.")
        return True
    return False

def incrementer_tentatives_global():
    _tentatives_globales[SESSION_ID] = _tentatives_globales.get(SESSION_ID, 0) + 1
    if _tentatives_globales[SESSION_ID] >= MAX_TENTATIVES:
        _bloque_global[SESSION_ID] = time.time() + BLOCAGE_SECONDES
        _tentatives_globales[SESSION_ID] = 0

def reinitialiser_tentatives_global():
    _tentatives_globales[SESSION_ID] = 0
    _bloque_global[SESSION_ID] = 0

# ═══════════════════════════════════════════════════════════
# 🖥️  INTERFACE TKINTER
# ═══════════════════════════════════════════════════════════

class ATM_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Bank ATM")
        self.root.geometry("400x550")
        self.current_user = None
        initialiser_db()
        self.ecran_connexion()

    def nettoyer(self):
        for w in self.root.winfo_children(): w.destroy()

    def ecran_connexion(self):
        self.nettoyer()
        tk.Label(self.root, text="🏦 ATM SÉCURISÉ", font=("Arial", 20, "bold"), pady=40).pack()
        
        tk.Label(self.root, text="Code PIN :").pack()
        self.pin_var = tk.StringVar()
        entry = tk.Entry(self.root, textvariable=self.pin_var, show="*", font=("Arial", 16), justify='center', width=10)
        entry.pack(pady=10)
        entry.focus_set()

        tk.Button(self.root, text="SE CONNECTER", bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), 
                  command=self.login, width=20, height=2).pack(pady=20)
        
        tk.Label(self.root, text="Pas encore client ?", font=("Arial", 9)).pack(pady=(20,0))
        tk.Button(self.root, text="Créer un compte", command=self.ui_creer_compte, relief="flat", fg="blue").pack()
        
        tk.Label(self.root, text="(Test PIN: 1234)", font=("Arial", 8, "italic"), fg="gray").pack(side="bottom", pady=10)

    def login(self):
        if verifier_blocage_global(): return
        
        pin = self.pin_var.get()
        print(f"Tentative de login...") # Debug console
        
        user = trouver_user_par_pin(pin)
        
        if user:
            print("Login réussi !")
            self.current_user = dict(user)
            reinitialiser_tentatives_global()
            self.ecran_principal()
        else:
            print("Login échoué.")
            incrementer_tentatives_global()
            messagebox.showerror("Erreur", "PIN incorrect.")
            self.pin_var.set("") # Vide le champ

    def ecran_principal(self):
        self.nettoyer()
        # Refresh solde
        with connexion() as conn:
            self.current_user = dict(conn.execute("SELECT * FROM users WHERE id=?", (self.current_user['id'],)).fetchone())

        tk.Label(self.root, text=f"Bienvenue {self.current_user['prenom']}", font=("Arial", 12)).pack(pady=10)
        tk.Label(self.root, text=f"{self.current_user['solde']:.2f} $", font=("Arial", 24, "bold"), fg="#2980b9").pack(pady=20)

        btns = [
            ("💰 Dépôt", self.ui_depot),
            ("💸 Retrait", self.ui_retrait),
            ("🔄 Transfert", self.ui_transfert),
            ("🚪 Déconnexion", self.ecran_connexion)
        ]
        for t, c in btns:
            tk.Button(self.root, text=t, command=c, width=25, pady=8, font=("Arial", 10)).pack(pady=5)

    def ui_depot(self):
        m = simpledialog.askfloat("Dépôt", "Montant à déposer :")
        if m and m > 0:
            deposer(self.current_user['id'], m)
            self.ecran_principal()

    def ui_retrait(self):
        m = simpledialog.askfloat("Retrait", "Montant à retirer :")
        if m and m > 0:
            if retirer(self.current_user['id'], m): 
                self.ecran_principal()
            else: 
                messagebox.showerror("Erreur", "Fonds insuffisants.")

    def ui_transfert(self):
        dest = simpledialog.askstring("Transfert", "Email du bénéficiaire :")
        if not dest: return
        m = simpledialog.askfloat("Transfert", f"Montant à envoyer à {dest} :")
        if m and m > 0:
            res = transferer(self.current_user['id'], dest, m)
            if res is True:
                messagebox.showinfo("Succès", "L'argent a été transféré.")
                self.ecran_principal()
            else:
                messagebox.showerror("Erreur", res)

    def ui_creer_compte(self):
        n = simpledialog.askstring("Nouveau", "Nom :")
        p = simpledialog.askstring("Nouveau", "Prénom :")
        e = simpledialog.askstring("Nouveau", "Email :")
        if n and p and e:
            pin = str(secrets.randbelow(9000) + 1000)
            try:
                hash_p = bcrypt.hashpw(pin.encode(), bcrypt.gensalt())
                with connexion() as conn:
                    conn.execute("INSERT INTO users (pin_hash, nom, prenom, email, solde) VALUES (?,?,?,?,0)", (hash_p, n, p, e))
                    conn.commit()
                messagebox.showinfo("PIN GÉNÉRÉ", f"Voici votre code PIN secret :\n\n {pin} \n\nNotez-le bien !")
            except Exception as ex:
                messagebox.showerror("Erreur", f"Email déjà utilisé ou erreur : {ex}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ATM_GUI(root)
    root.mainloop()
