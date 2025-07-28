# FinTrack_AI
FinTrack AI est une application de bureau complète et sécurisée pour la gestion de vos finances personnelles. Développée en Python, elle garantit que toutes vos données restent locales sur votre ordinateur.  Suivez vos transactions sur plusieurs comptes, définissez des budgets mensuels, automatisez vos dépenses récurrentes et analysez vos habitudes financières grâce à un tableau de bord visuel et intuitif.

# FinTrack AI 📊

FinTrack AI est une application de bureau simple et intuitive pour la gestion de vos finances personnelles. Développée en Python, elle vous permet de garder le contrôle total sur vos données en les stockant localement sur votre ordinateur.

C'est l'outil parfait pour suivre ses dépenses, visualiser ses habitudes financières et planifier ses budgets sans dépendre de services en ligne.

![Aperçu de l'application]: https://photos.app.goo.gl/tSktbBtyYX7A866b6


## 🚀 Fonctionnalités Clés

* **💼 Gestion Multi-Comptes** : Créez et gérez plusieurs comptes (Compte Courant, Épargne, etc.) pour une vue d'ensemble précise de vos actifs.
* **🎯 Suivi des Budgets** : Définissez des budgets mensuels pour chaque catégorie de dépenses et suivez votre progression en temps réel grâce à des barres de progression visuelles.
* **🔄 Transactions Récurrentes** : La logique pour gérer les dépenses fixes (loyers, abonnements) est intégrée pour automatiser leur ajout à chaque lancement.
* **📈 Tableau de Bord Visuel** : Analysez vos habitudes financières grâce à des graphiques clairs :
    * **Répartition des dépenses** par catégorie.
    * **Résumé financier** du mois en cours (solde, total des revenus/dépenses).
* **✍️ Gestion Complète des Transactions** : Ajoutez, modifiez et supprimez facilement vos transactions via une interface simple.
* **💾 Données Locales** : Toutes vos informations financières sont sauvegardées dans un dossier `fintrack_data` à côté de l'application, vous garantissant confidentialité et contrôle.

---

## 🛠️ Technologies Utilisées

* **Langage** : Python 3
* **Interface Graphique (GUI)** : Tkinter (avec `ttk` pour un look moderne)
* **Visualisation de Données** : Matplotlib
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
    ```bash
    pip install matplotlib tkcalendar python-dateutil
    ```
    *(Sur Windows, il est parfois plus robuste d'utiliser `py -m pip install ...`)*

3.  **Lancez l'application**
    ```bash
    python main.py
    ```
    L'application se lancera directement, sans mot de passe.

---

## 📦 Créer un Exécutable (Optionnel)

Vous pouvez facilement transformer ce projet en une application Windows (`.exe`) autonome.

1.  **Installez PyInstaller**
    ```bash
    pip install pyinstaller
    ```

2.  **Lancez la commande de création**
    Assurez-vous d'avoir un fichier `icon.ico` dans le dossier si vous souhaitez une icône personnalisée.
    ```bash
    py -m PyInstaller --name="FinTrack AI" --onefile --windowed --icon="icon.ico" main.py
    ```

3.  **Trouvez le fichier**
    Votre application `FinTrack AI.exe` se trouvera dans le dossier `dist`.

---

## 📈 Évolutions Possibles

* **Catégorisation Automatique (IA)** : Suggérer une catégorie en fonction de la description d'une transaction.
* **Importation de Fichiers CSV** : Permettre d'importer des relevés bancaires.
* **Export en PDF/Excel** : Générer des rapports financiers.