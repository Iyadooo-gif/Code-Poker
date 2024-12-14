import tkinter as tk
from tkinter import simpledialog, messagebox
import random
from PIL import Image, ImageTk


# Classe Carte
class Carte:
    RANGS = ['2', '3', '4', '5', '6', '7', '8', '9', 'X', 'V', 'D', 'R', 'A']
    COULEURS = ['P', 'C', 'K', 'T']  # Pique, Cœur, Carreau, Trèfle
    SYMBOLES = {'P': '♠', 'C': '♥', 'K': '♦', 'T': '♣'}

    def __init__(self, rang, couleur):
        self.rang = rang
        self.couleur = couleur

    def __repr__(self):
        return f"{self.rang}{self.couleur}"

    def valeur(self):
        """Retourne une valeur numérique de la carte pour le classement."""
        return Carte.RANGS.index(self.rang)


# Classe Joueur
class Joueur:
    def __init__(self, nom, ia=False):
        self.nom = nom
        self.cartes = []
        self.ia = ia
        self.tapis = 100  # Jetons initiaux
        self.actif = True

    def recevoir(self, cartes):
        self.cartes.extend(cartes)

    def reset_cartes(self):
        self.cartes = []

    def miser(self, montant):
        montant = min(montant, self.tapis)
        self.tapis -= montant
        return montant

    def __repr__(self):
        return f"{self.nom} (Jetons : {self.tapis})"


# Classe Croupier
class Croupier:
    def __init__(self):
        self.paquet = []

    def rassembler(self):
        self.paquet = [Carte(rang, couleur) for couleur in Carte.COULEURS for rang in Carte.RANGS]

    def melanger(self):
        random.shuffle(self.paquet)

    def couper(self):
        pivot = random.randint(0, len(self.paquet))
        self.paquet = self.paquet[pivot:] + self.paquet[:pivot]

    def distribuer(self, nombre, joueurs):
        for _ in range(nombre):
            for joueur in joueurs:
                if self.paquet:
                    joueur.recevoir([self.paquet.pop()])


# Classe Partie
class Partie:
    def __init__(self, joueurs):
        self.joueurs = joueurs
        self.croupier = Croupier()
        self.cartes_communes = []
        self.pot = 0
        self.mise_actuelle = 0
        self.tour_mise = 0  # Compteur pour savoir quel joueur doit agir
        self.gagnant = None
        self.cartes_deja_brulees = []

    def nouvelle_partie(self):
        self.pot = 0
        self.mise_actuelle = 0
        self.cartes_communes = []
        self.gagnant = None
        self.croupier.rassembler()
        self.croupier.melanger()
        self.croupier.couper()

        for joueur in self.joueurs:
            joueur.reset_cartes()

    def distribuer_cartes(self):
        self.croupier.distribuer(2, self.joueurs)

    def flop(self):
        self.croupier.paquet.pop()  # Brûler une carte
        self.cartes_communes.extend([self.croupier.paquet.pop() for _ in range(3)])

    def turn_or_river(self):
        self.croupier.paquet.pop()  # Brûler une carte
        self.cartes_communes.append(self.croupier.paquet.pop())

    def ajouter_au_pot(self, montant):
        self.pot += montant

    def evaluer_combinaisons(self):
        # Fonction d'évaluation des mains des joueurs
        mains = {}
        for joueur in self.joueurs:
            if joueur.actif:
                toutes_cartes = joueur.cartes + self.cartes_communes
                mains[joueur] = self.evaluer_main(toutes_cartes)
        return mains

    def evaluer_main(self, cartes):
        """Retourne un score basé sur la meilleure combinaison possible de la main du joueur et des cartes communes."""
        valeurs = [carte.valeur() for carte in cartes]
        couleurs = [carte.couleur for carte in cartes]
        valeurs.sort(reverse=True)

        # Vérifier si la main forme une quinte flush royale
        if self.is_quinte_flush_royale(valeurs, couleurs):
            return (10, valeurs)

        # Vérifier si la main forme une quinte flush
        if self.is_quinte_flush(valeurs, couleurs):
            return (9, valeurs)

        # Vérifier un carré (four of a kind)
        if self.is_carre(valeurs):
            return (8, valeurs)

        # Vérifier un full (full house)
        if self.is_full_house(valeurs):
            return (7, valeurs)

        # Vérifier une couleur
        if self.is_couleur(couleurs):
            return (6, valeurs)

        # Vérifier une suite (straight)
        if self.is_suite(valeurs):
            return (5, valeurs)

        # Vérifier un brelan
        if self.is_brelan(valeurs):
            return (4, valeurs)

        # Vérifier deux paires
        if self.is_deux_paires(valeurs):
            return (3, valeurs)

        # Vérifier une paire
        if self.is_paire(valeurs):
            return (2, valeurs)

        return (1, valeurs)  # Carte la plus haute (high card)

    def is_quinte_flush_royale(self, valeurs, couleurs):
        """Vérifie une quinte flush royale."""
        return sorted(valeurs) == [8, 9, 10, 11, 12] and len(set(couleurs)) == 1

    def is_quinte_flush(self, valeurs, couleurs):
        """Vérifie une quinte flush."""
        return self.is_suite(valeurs) and len(set(couleurs)) == 1

    def is_carre(self, valeurs):
        """Vérifie un carré."""
        for v in set(valeurs):
            if valeurs.count(v) == 4:
                return True
        return False

    def is_full_house(self, valeurs):
        """Vérifie un full house."""
        counts = [valeurs.count(v) for v in set(valeurs)]
        return sorted(counts) == [2, 3]

    def is_couleur(self, couleurs):
        """Vérifie une couleur."""
        return len(set(couleurs)) == 1

    def is_suite(self, valeurs):
        """Vérifie une suite."""
        return len(set(valeurs)) == 5 and max(valeurs) - min(valeurs) == 4

    def is_brelan(self, valeurs):
        """Vérifie un brelan."""
        for v in set(valeurs):
            if valeurs.count(v) == 3:
                return True
        return False

    def is_deux_paires(self, valeurs):
        """Vérifie deux paires."""
        counts = [valeurs.count(v) for v in set(valeurs)]
        return counts.count(2) == 2

    def is_paire(self, valeurs):
        """Vérifie une paire."""
        for v in set(valeurs):
            if valeurs.count(v) == 2:
                return True
        return False

    def ia_jouer(self, ia):
        # IA basée sur la force de la main
        if not ia.actif:
            return "L'IA s'est déjà couchée."

        mains = self.evaluer_combinaisons()
        force_main = mains[ia][0]  # Premier élément du tuple est le score de la main

        if force_main >= 7:  # Très bonne main (full house, carré, etc.), l'IA mise
            mise = random.randint(10, min(30, ia.tapis))
        elif force_main >= 5:  # Main moyenne (suite, brelan, etc.), l'IA suit
            mise = self.mise_actuelle
        else:  # Main faible, l'IA se couche
            ia.actif = False
            return "L'IA se couche."

        self.mise_actuelle = mise
        self.ajouter_au_pot(ia.miser(mise))
        return f"L'IA mise {mise} jetons."


# Classe Application Tkinter
class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Texas Hold'em")

        # Initialisation des joueurs
        self.joueur_humain = Joueur("Vous")
        self.joueur_ia = Joueur("IA", ia=True)
        self.joueur_ia2 = Joueur("IA2", ia=True)
        self.joueurs = [self.joueur_humain, self.joueur_ia, self.joueur_ia2]

        self.partie = Partie(self.joueurs)

        # Table de jeu
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="green")
        self.canvas.pack()

        # Boutons d'actions
        self.bouton_nouvelle_partie = tk.Button(self.root, text="Nouvelle partie", command=self.nouvelle_partie)
        self.bouton_nouvelle_partie.place(x=50, y=550)

        self.bouton_miser = tk.Button(self.root, text="Miser", command=self.miser, state=tk.DISABLED)
        self.bouton_miser.place(x=200, y=550)

        self.bouton_suivre = tk.Button(self.root, text="Suivre", command=self.suivre, state=tk.DISABLED)
        self.bouton_suivre.place(x=300, y=550)

        self.bouton_coucher = tk.Button(self.root, text="Se coucher", command=self.coucher, state=tk.DISABLED)
        self.bouton_coucher.place(x=400, y=550)

        # Chargement des images des cartes
        self.cartes_images = {}
        self.charger_images()

    def charger_images(self):
        for couleur in Carte.COULEURS:
            for rang in Carte.RANGS:
                nom = f"{rang}{couleur}"
                chemin = f"images/{nom}.png"
                try:
                    image = Image.open(chemin).resize((60, 90))
                    self.cartes_images[nom] = ImageTk.PhotoImage(image)
                except:
                    self.cartes_images[nom] = None

    def afficher_cartes(self, joueur, x_start, y_start, face_cachee=False):
        x = x_start
        for carte in joueur.cartes:
            nom = f"{carte.rang}{carte.couleur}"
            if face_cachee:
                self.canvas.create_rectangle(x, y_start, x + 60, y_start + 90, fill="gray")
                self.canvas.create_text(x + 30, y_start + 45, text="?", font=("Arial", 24))
            else:
                image = self.cartes_images.get(nom)
                if image:
                    self.canvas.create_image(x, y_start, image=image, anchor=tk.NW)
                else:
                    self.canvas.create_rectangle(x, y_start, x + 60, y_start + 90, fill="white")
                    self.canvas.create_text(x + 30, y_start + 45, text=f"{carte.rang}\n{carte.couleur}",
                                            font=("Arial", 10))
            x += 70

    def afficher_cartes_communes(self):
        x = 300
        y = 250
        for carte in self.partie.cartes_communes:
            nom = f"{carte.rang}{carte.couleur}"
            image = self.cartes_images.get(nom)
            if image:
                self.canvas.create_image(x, y, image=image, anchor=tk.NW)
            else:
                self.canvas.create_rectangle(x, y, x + 60, y + 90, fill="white")
                self.canvas.create_text(x + 30, y + 45, text=f"{carte.rang}\n{carte.couleur}", font=("Arial", 10))
            x += 70

    def nouvelle_partie(self):
        self.partie.nouvelle_partie()
        self.partie.distribuer_cartes()
        self.canvas.delete("all")
        self.canvas.create_text(400, 50, text="Poker Texas Hold'em", font=("Arial", 24), fill="white")

        # Affichage du fond de la table
        self.canvas.create_oval(50, 100, 750, 500, fill="brown")  # Table ronde de poker

        # Affichage du joueur et de l'IA (les cartes de l'IA sont cachées)
        self.afficher_cartes(self.joueur_humain, 200, 400)
        self.afficher_cartes(self.joueur_ia, 200, 100, face_cachee=True)
        self.afficher_cartes(self.joueur_ia2, 600, 100, face_cachee=True)

        self.afficher_cartes_communes()

        # Activer les boutons
        self.bouton_miser.config(state=tk.NORMAL)
        self.bouton_suivre.config(state=tk.NORMAL)
        self.bouton_coucher.config(state=tk.NORMAL)

    def miser(self):
        montant = simpledialog.askinteger("Mise", "Combien voulez-vous miser ?",
                                          minvalue=1, maxvalue=self.joueur_humain.tapis)
        if montant:
            self.partie.ajouter_au_pot(self.joueur_humain.miser(montant))
            self.canvas.create_text(400, 550, text=f"Vous avez misé {montant} jetons.", font=("Arial", 16),
                                    fill="white")
            self.partie.ia_jouer(self.joueur_ia)

    def suivre(self):
        """Permet de suivre la mise de l'adversaire."""
        montant = self.partie.mise_actuelle - self.joueur_humain.tapis
        if montant > 0:
            self.partie.ajouter_au_pot(self.joueur_humain.miser(montant))
            self.canvas.create_text(400, 550, text=f"Vous avez suivi avec {montant} jetons.", font=("Arial", 16),
                                    fill="white")
        self.partie.ia_jouer(self.joueur_ia)

    def coucher(self):
        self.joueur_humain.actif = False
        self.canvas.create_text(400, 550, text="Vous vous êtes couché.", font=("Arial", 16), fill="white")
        self.partie.ia_jouer(self.joueur_ia)


root = tk.Tk()
app = PokerApp(root)
root.mainloop()
