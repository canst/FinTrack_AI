# FinTrack_AI
FinTrack AI est une application de bureau complète et sécurisée pour la gestion de vos finances personnelles. Développée en Python, elle garantit que toutes vos données restent locales sur votre ordinateur et protégées par un mot de passe grâce à un chiffrement robuste.  Suivez vos transactions sur plusieurs comptes, définissez des budgets mensuels, automatisez vos dépenses récurrentes et analysez vos habitudes financières grâce à un tableau de bord visuel et intuitif.

# FinTrack AI 📊🔐

FinTrack AI est une application de bureau complète et sécurisée pour la gestion de vos finances personnelles. Développée en Python, elle garantit que toutes vos données restent locales sur votre ordinateur et protégées par un mot de passe grâce à un chiffrement robuste (AES).

C'est l'outil parfait pour reprendre le contrôle de ses finances sans dépendre de services en ligne.

![Aperçu de l'application]

---

## 🚀 Fonctionnalités Clés

* **🔒 Sécurité avant tout** : Toutes les données (transactions, budgets, comptes) sont chiffrées sur votre disque. L'accès à l'application est protégé par un mot de passe personnel.
* **💼 Gestion Multi-Comptes** : Créez et gérez plusieurs comptes (Compte Courant, Épargne, Carte de Crédit, etc.) pour une vue d'ensemble précise de vos actifs.
* **🎯 Suivi des Budgets** : Définissez des budgets mensuels pour chaque catégorie de dépenses et suivez votre progression en temps réel grâce à des barres de progression visuelles.
* **🔄 Transactions Récurrentes** : Automatisez la saisie de vos revenus et dépenses fixes (salaires, loyers, abonnements) pour gagner du temps et ne rien oublier.
* **📈 Tableau de Bord Visuel** : Analysez vos habitudes financières grâce à des graphiques interactifs :
    * **Répartition des dépenses** par catégorie (graphique circulaire).
    * **Comparaison revenus vs. dépenses** mensuels (graphique en barres).
    * **Résumé financier** du mois en cours (solde, total des revenus/dépenses).
* **✍️ Gestion Complète des Transactions** : Ajoutez, modifiez et supprimez facilement vos transactions via une interface intuitive.

---

## 🛠️ Technologies Utilisées

* **Langage** : Python 3
* **Interface Graphique (GUI)** : Tkinter (via `ttk` pour un look moderne)
* **Visualisation de Données** : Matplotlib
* **Sécurité** : Cryptography
* **Widgets Additionnels** : tkcalendar (pour la saisie de date)
* **Manipulation de Dates** : python-dateutil

---

## ⚙️ Installation et Lancement

1.  **Clonez le dépôt**
    ```bash
    git clone [https://github.com/votre-nom-utilisateur/FinTrack_AI.git](https://github.com/votre-nom-utilisateur/FinTrack_AI.git)
    cd FinTrack_AI
    ```

2.  **Installez les dépendances**
    Assurez-vous d'avoir Python 3 installé. Ensuite, exécutez la commande suivante dans votre terminal :
    ```bash
    pip install cryptography matplotlib tkcalendar python-dateutil
    ```
    *(Sur Windows, il est parfois plus robuste d'utiliser `py -m pip install ...`)*

3.  **Lancez l'application**
    ```bash
    python main.py
    ```

4.  **Premier Lancement**
    * Lors du tout premier lancement, une fenêtre vous demandera de **créer un mot de passe**.
    * **Attention :** Ce mot de passe est crucial. S'il est perdu, les données chiffrées seront irrécupérables.
    * Lors des lancements suivants, vous devrez entrer ce même mot de passe pour accéder à vos données.

---

## 📈 Évolutions Possibles

Ce projet a un fort potentiel d'évolution. Voici quelques idées pour de futures versions :

* **Catégorisation Automatique (IA)** : Entraîner un modèle de Machine Learning simple pour suggérer une catégorie en fonction de la description d'une transaction.
* **Importation de Fichiers CSV** : Permettre d'importer des relevés bancaires au format CSV.
* **Export en PDF/Excel** : Générer des rapports financiers mensuels ou annuels.
* **Amélioration de l'UI/UX** : Moderniser davantage l'interface et l'expérience utilisateur.