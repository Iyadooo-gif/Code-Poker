import tkinter as tk
from tkinter import simpledialog, messagebox
import random
from PIL import Image, ImageTk

# Classe Carte
class Carte:
    RANGS = ['2', '3', '4', '5', '6', '7', '8', '9', 'X', 'V', 'D', 'R', 'A']
    COULEURS = ['spades', 'hearts', 'diamonds', 'clubs']  # Pique, Cœur, Carreau, Trèfle

    def __init__(self, rang, couleur):
        self.rang = rang
        self.couleur = couleur

    def __repr__(self):
        return f"{self.rang}_{self.couleur}"

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

    def ajouter_carte_commune(self):
        self.croupier.paquet.pop()  # Brûler une carte
        if len(self.cartes_communes) < 5:  # Limiter à 5 cartes communes
            self.cartes_communes.append(self.croupier.paquet.pop())

    def ajouter_au_pot(self, montant):
        self.pot += montant

    def evaluer_combinaisons(self):
        # Simulation pour évaluer les mains
        return {
            self.joueur_humain: random.randint(1, 100),
            self.joueur_ia: random.randint(1, 100),
        }

    def determiner_gagnant(self):
        scores = self.evaluer_combinaisons()
        gagnant = max(scores, key=scores.get)
        gagnant.tapis += self.pot
        return gagnant

    def ia_jouer(self):
        force_main = random.randint(1, 100)
        if not self.joueur_ia.actif:
            return "L'IA s'est déjà couchée."

        if force_main > 60:  # Bonne main, mise agressive
            mise = random.randint(10, min(20, self.joueur_ia.tapis))
        elif 30 <= force_main <= 60:  # Moyenne main, suit la mise
            mise = max(10, self.mise_actuelle)
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

        # Zones d'information
        self.label_humain = tk.Label(self.root, text="", font=("Arial", 12), bg="green", fg="white")
        self.label_humain.place(x=50, y=10)

        self.label_ia = tk.Label(self.root, text="", font=("Arial", 12), bg="green", fg="white")
        self.label_ia.place(x=650, y=10)

        self.label_pot = tk.Label(self.root, text="", font=("Arial", 14), bg="green", fg="white")
        self.label_pot.place(x=350, y=10)

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
        self.image_dos = None
        self.charger_images()

    def charger_images(self):
        for couleur in Carte.COULEURS:
            for rang in Carte.RANGS:
                nom = f"{rang}_{couleur}"
                chemin = f"images/{nom}.png"
                try:
                    image = Image.open(chemin).resize((60, 90))
                    self.cartes_images[nom] = ImageTk.PhotoImage(image)
                except:
                    self.cartes_images[nom] = None

        try:
            dos_path = "images/back1.png"  # Image du dos des cartes
            self.image_dos = ImageTk.PhotoImage(Image.open(dos_path).resize((60, 90)))
        except:
            self.image_dos = None

    def afficher_cartes(self, joueur, x_start, y_start, face_cachee=False):
        x = x_start
        for carte in joueur.cartes:
            nom = f"{carte.rang}_{carte.couleur}"
            if face_cachee:
                self.canvas.create_image(x, y_start, image=self.image_dos, anchor=tk.NW)
            else:
                image = self.cartes_images.get(nom)
                if image:
                    self.canvas.create_image(x, y_start, image=image, anchor=tk.NW)
            x += 70

    def afficher_cartes_communes(self):
        x = 300
        y = 250
        for carte in self.partie.cartes_communes:
            nom = f"{carte.rang}_{carte.couleur}"
            image = self.cartes_images.get(nom)
            if image:
                self.canvas.create_image(x, y, image=image, anchor=tk.NW)
            x += 70

    def mettre_a_jour_jetons(self):
        self.label_humain.config(text=f"Vos jetons : {self.joueur_humain.tapis}")
        self.label_ia.config(text=f"Jetons IA : {self.joueur_ia.tapis}")
        self.label_pot.config(text=f"Pot : {self.partie.pot}")

    def nouvelle_partie(self):
        self.partie.nouvelle_partie()
        self.partie.distribuer_cartes()
        self.canvas.delete("all")

        self.afficher_cartes(self.joueur_humain, 200, 400)
        self.afficher_cartes(self.joueur_ia, 200, 150, face_cachee=True)
        self.afficher_cartes_communes()
        self.mettre_a_jour_jetons()

        self.bouton_miser.config(state=tk.NORMAL)
        self.bouton_suivre.config(state=tk.NORMAL)
        self.bouton_coucher.config(state=tk.NORMAL)

    def miser(self):
        mise = simpledialog.askinteger("Mise", "Entrez votre mise (min 10) :", minvalue=10, maxvalue=self.joueur_humain.tapis)
        if mise:
            self.partie.ajouter_au_pot(self.joueur_humain.miser(mise))
            self.mettre_a_jour_jetons()

            ia_action = self.partie.ia_jouer()
            self.mettre_a_jour_jetons()
            if not self.joueur_ia.actif:
                self.afficher_cartes(self.joueur_ia, 200, 150)

            if len(self.partie.cartes_communes) < 5:
                self.partie.ajouter_carte_commune()
                self.afficher_cartes_communes()
            else:
                gagnant = self.partie.determiner_gagnant()
                messagebox.showinfo("Fin de partie", f"{gagnant.nom} remporte la partie avec {self.partie.pot} jetons !")
                self.bouton_miser.config(state=tk.DISABLED)
                self.bouton_suivre.config(state=tk.DISABLED)
                self.bouton_coucher.config(state=tk.DISABLED)

    def suivre(self):
        mise = max(10, self.partie.mise_actuelle)
        self.partie.ajouter_au_pot(self.joueur_humain.miser(mise))
        self.mettre_a_jour_jetons()

        ia_action = self.partie.ia_jouer()
        self.mettre_a_jour_jetons()
        if not self.joueur_ia.actif:
            self.afficher_cartes(self.joueur_ia, 200, 150)

        if len(self.partie.cartes_communes) < 5:
            self.partie.ajouter_carte_commune()
            self.afficher_cartes_communes()
        else:
            gagnant = self.partie.determiner_gagnant()
            messagebox.showinfo("Fin de partie", f"{gagnant.nom} remporte la partie avec {self.partie.pot} jetons !")
            self.bouton_miser.config(state=tk.DISABLED)
            self.bouton_suivre.config(state=tk.DISABLED)
            self.bouton_coucher.config(state=tk.DISABLED)

    def coucher(self):
        self.afficher_cartes(self.joueur_ia, 200, 150)
        messagebox.showinfo("Défaite", "Vous vous êtes couché. L'IA gagne cette manche.")
        self.mettre_a_jour_jetons()
        self.bouton_miser.config(state=tk.DISABLED)
        self.bouton_suivre.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()
