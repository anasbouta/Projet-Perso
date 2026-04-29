---

# 🏦 Python Bank ATM v3.0

![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/Language-Python-blue)
![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey)

**ATM 3.0** est une simulation avancée de distributeur automatique de billets développée en Python. Cette version met l'accent sur une architecture robuste utilisant une base de données locale et des protocoles de sécurité pour protéger les transactions des utilisateurs.

## 🌟 Fonctionnalités Clés

* **Système d'Authentification :** Accès sécurisé par code PIN pour chaque utilisateur.
* **Transactions Bancaires Complètes :**
    * **Dépôt :** Mise à jour instantanée du solde en base de données.
    * **Retrait :** Vérification automatique des fonds disponibles avant validation.
    * **Transfert :** Envoi d'argent de compte à compte avec validation de l'existence du destinataire.
* **Persistance des Données :** Utilisation de **SQLite3** pour stocker les soldes et les informations utilisateurs de manière permanente.
* **Interface Graphique (GUI) :** Interface claire et moderne construite avec **Tkinter**.
* **Hachage des PIN:** PIN hacher pour plus de securiter

## 🛡️ Sécurité & Robustesse

* **Protection Anti-Injection SQL :** Utilisation systématique de requêtes SQL paramétrées (`?`) pour empêcher toute manipulation malveillante de la base de données via les champs de saisie.
* **Gestion des Erreurs :** Système de notifications (Pop-ups) pour alerter l'utilisateur en cas de solde insuffisant, de code PIN incorrect ou d'erreurs de transfert.
* **Intégrité des Données :** Utilisation de `commit()` et `rollback()` pour garantir que les transactions sont complètes ou annulées en cas de problème technique.
* **Hachage des PIN:** PIN hacher pour plus de securité
## 🚀 Installation rapide

1.  **Récupérer le code :**
    ```bash
    git clone https://github.com/anasbouta/Projet-Perso.git
    ```
2.  **Lancer l'application :**
    ```bash
    python "ATM 3.0.py"
    ```
OU:

<a href="https://github.com/anasbouta/Projet-Perso/archive/refs/heads/main.zip">Télécharger tout le projet ici</a> et extracter le fichier "ATM 3.0.py"
*Note : Le fichier de base de données `.db` sera créé automatiquement lors du premier lancement.*

## ⚖️ Licence

Ce projet est distribué sous la **Licence MIT**.
*Copyright (c) 2026 Anas Boutaghroucht.*

---
