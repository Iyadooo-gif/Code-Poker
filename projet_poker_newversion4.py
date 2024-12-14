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
    def __init__(self, joueur_humain, joueur_ia):
        self.joueur_humain = joueur_humain
        self.joueur_ia = joueur_ia
        self.croupier = Croupier()
        self.cartes_communes = []
        self.pot = 0
        self.mise_actuelle = 0

    def nouvelle_partie(self):
        self.joueur_humain.reset_cartes()
        self.joueur_ia.reset_cartes()
        self.cartes_communes = []
        self.pot = 0
        self.mise_actuelle = 0
        self.croupier.rassembler()
        self.croupier.melanger()
        self.croupier.couper()

    def distribuer_cartes(self):
        self.croupier.distribuer(2, [self.joueur_humain, self.joueur_ia])

    def flop(self):
        self.croupier.paquet.pop()  # Brûler une carte
        self.cartes_communes.extend([self.croupier.paquet.pop() for _ in range(3)])

    def turn_or_river(self):
        self.croupier.paquet.pop()  # Brûler une carte
        self.cartes_communes.append(self.croupier.paquet.pop())

    def ajouter_au_pot(self, montant):
        self.pot += montant

    def evaluer_combinaisons(self):
        # Simulation pour évaluer les mains
        return {
            self.joueur_humain: random.randint(1, 100),
            self.joueur_ia: random.randint(1, 100),
        }

    def ia_jouer(self):
        # Logique avancée pour l'IA
        force_main = random.randint(1, 100)
        if not self.joueur_ia.actif:
            return "L'IA s'est déjà couchée."

        if force_main > 60:  # Bonne main, mise agressive
            mise = random.randint(10, min(20, self.joueur_ia.tapis))
        elif 30 <= force_main <= 60:  # Moyenne main, mise faible
            mise = random.randint(5, min(10, self.joueur_ia.tapis))
        else:  # Mauvaise main, l'IA se couche
            self.joueur_ia.actif = False
            return "L'IA se couche."

        self.mise_actuelle = mise
        self.ajouter_au_pot(self.joueur_ia.miser(mise))
        return f"L'IA mise {mise} jetons."


# Classe Application Tkinter
class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Texas Hold'em")

        # Initialisation des joueurs
        self.joueur_humain = Joueur("Vous")
        self.joueur_ia = Joueur("IA", ia=True)
        self.partie = Partie(self.joueur_humain, self.joueur_ia)

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

        # Affichage du joueur et de l'IA
        self.afficher_cartes(self.joueur_humain, 200, 400)
        self.afficher_cartes(self.joueur_ia, 200, 150, face_cachee=True)

        self.bouton_miser.config(state=tk.NORMAL)
        self.bouton_suivre.config(state=tk.NORMAL)
        self.bouton_coucher.config(state=tk.NORMAL)

    def miser(self):
        mise = simpledialog.askinteger("Mise", "Entrez votre mise (min 10) :", minvalue=10,
                                       maxvalue=self.joueur_humain.tapis)
        if mise:
            self.partie.ajouter_au_pot(self.joueur_humain.miser(mise))
            messagebox.showinfo("Mise", f"Vous avez misé {mise} jetons.")
            self.afficher_cartes_communes()

            # L'IA joue après le joueur
            ia_action = self.partie.ia_jouer()
            messagebox.showinfo("Tour de l'IA", ia_action)

    def suivre(self):
        pass

    def coucher(self):
        self.afficher_cartes(self.joueur_ia, 200, 150)  # Montrer les cartes de l'IA
        messagebox.showinfo("Défaite", "Vous vous êtes couché. L'IA gagne cette manche.")
        self.bouton_miser.config(state=tk.DISABLED)
        self.bouton_suivre.config(state=tk.DISABLED)
        self.bouton_coucher.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()
