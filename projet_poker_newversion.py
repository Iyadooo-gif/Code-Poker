import tkinter as tk
from tkinter import messagebox
import random

# Classe Carte
class Carte:
    RANGS = ['2', '3', '4', '5', '6', '7', '8', '9', 'X', 'V', 'D', 'R', 'A']
    COULEURS = ['P', 'C', 'K', 'T']  # Pique, Cœur, Carreau, Trèfle

    def __init__(self, rang, couleur):
        self.rang = rang
        self.couleur = couleur

    def __repr__(self):
        return f"{self.rang}{self.couleur}"


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
        if montant > self.tapis:
            montant = self.tapis
        self.tapis -= montant
        return montant

    def __repr__(self):
        return f"{self.nom} (Jetons : {self.tapis}, Cartes : {self.cartes})"


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

    def __repr__(self):
        return f"Croupier(Paquet : {len(self.paquet)} cartes)"


# Classe Partie
class Partie:
    def __init__(self, joueurs):
        self.joueurs = joueurs
        self.croupier = Croupier()
        self.cartes_communes = []
        self.pot = 0

    def nouvelle_partie(self):
        for joueur in self.joueurs:
            joueur.reset_cartes()
        self.cartes_communes = []
        self.pot = 0
        self.croupier.rassembler()
        self.croupier.melanger()
        self.croupier.couper()

    def distribuer_cartes(self):
        # Distribuer 2 cartes privatives à chaque joueur
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
        # Simulation pour évaluer les mains (à remplacer par un vrai moteur de combinaisons)
        return {joueur: random.randint(1, 100) for joueur in self.joueurs}

    def __repr__(self):
        return f"Pot : {self.pot}, Communes : {self.cartes_communes}"


# Classe Application Tkinter
class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Texas Hold'em")

        # Initialisation des joueurs
        self.joueurs = [Joueur("Alice"), Joueur("Bob", ia=True), Joueur("Carl", ia=True)]
        self.partie = Partie(self.joueurs)

        # Interface graphique
        self.label = tk.Label(self.root, text="Bienvenue au Poker Texas Hold'em !", font=("Arial", 16))
        self.label.pack(pady=10)

        self.texte = tk.Text(self.root, height=20, width=50)
        self.texte.pack(pady=10)

        self.bouton_nouvelle_partie = tk.Button(self.root, text="Nouvelle partie", command=self.nouvelle_partie)
        self.bouton_nouvelle_partie.pack(pady=5)

        self.bouton_flop = tk.Button(self.root, text="Flop", command=self.jouer_flop, state=tk.DISABLED)
        self.bouton_flop.pack(pady=5)

        self.bouton_turn = tk.Button(self.root, text="Turn", command=self.jouer_turn, state=tk.DISABLED)
        self.bouton_turn.pack(pady=5)

        self.bouton_river = tk.Button(self.root, text="River", command=self.jouer_river, state=tk.DISABLED)
        self.bouton_river.pack(pady=5)

        self.bouton_abattage = tk.Button(self.root, text="Abattage", command=self.abattre, state=tk.DISABLED)
        self.bouton_abattage.pack(pady=5)

    def afficher_etat(self, message=""):
        self.texte.delete("1.0", tk.END)
        if message:
            self.texte.insert(tk.END, f"{message}\n\n")
        for joueur in self.joueurs:
            self.texte.insert(tk.END, f"{joueur}\n")
        self.texte.insert(tk.END, f"Cartes communes : {self.partie.cartes_communes}\n")
        self.texte.insert(tk.END, f"Pot : {self.partie.pot}\n")

    def nouvelle_partie(self):
        self.partie.nouvelle_partie()
        self.partie.distribuer_cartes()
        self.afficher_etat("Nouvelle partie commencée !")
        self.bouton_flop.config(state=tk.NORMAL)
        self.bouton_turn.config(state=tk.DISABLED)
        self.bouton_river.config(state=tk.DISABLED)
        self.bouton_abattage.config(state=tk.DISABLED)

    def jouer_flop(self):
        self.partie.flop()
        self.afficher_etat("Flop joué !")
        self.bouton_flop.config(state=tk.DISABLED)
        self.bouton_turn.config(state=tk.NORMAL)

    def jouer_turn(self):
        self.partie.turn_or_river()
        self.afficher_etat("Turn joué !")
        self.bouton_turn.config(state=tk.DISABLED)
        self.bouton_river.config(state=tk.NORMAL)

    def jouer_river(self):
        self.partie.turn_or_river()
        self.afficher_etat("River jouée !")
        self.bouton_river.config(state=tk.DISABLED)
        self.bouton_abattage.config(state=tk.NORMAL)

    def abattre(self):
        combinaisons = self.partie.evaluer_combinaisons()
        gagnant = max(combinaisons, key=combinaisons.get)
        self.partie.ajouter_au_pot(50)  # Exemple de montant
        gagnant.tapis += self.partie.pot
        self.afficher_etat(f"{gagnant.nom} gagne le pot de {self.partie.pot} avec une combinaison de {combinaisons[gagnant]} !")
        self.bouton_abattage.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()
