import tkinter as tk
from tkinter import simpledialog, messagebox
import random
from PIL import Image, ImageTk
from pygame import mixer

# Classe Carte
class Carte:
    RANGS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    COULEURS = ['♠', '♥', '♦', '♣']  # Pique, Cœur, Carreau, Trèfle
    SYMBOLES = {'P': '♠', 'C': '♥', 'K': '♦', 'T': '♣'}

    def __init__(self, rang, couleur):
        self.rang = rang
        self.couleur = couleur

    def __repr__(self):
        return f"{self.rang}{self.couleur}"

def play_music():
    mixer.init()  # Initialiser le module de mixer
    mixer.music.load("sounds/casino.mp3")  # Charger le fichier audio
    mixer.music.play(-1)  # Jouer en boucle (-1 pour boucle infinie)

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
        # Logique de l'IA pour répondre à la mise
        force_main = random.randint(1, 100)

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

        # Chargement des images des cartes et jetons
        self.cartes_images = {}
        self.jetons_image = None
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

        try:
            jetons_path = "images/jetons.png"  # Image de jetons
            self.jetons_image = ImageTk.PhotoImage(Image.open(jetons_path).resize((40, 40)))
        except:
            self.jetons_image = None

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

    def afficher_jetons(self, x, y, nombre):
        if self.jetons_image:
            for i in range(nombre // 10):
                self.canvas.create_image(x + i * 10, y, image=self.jetons_image, anchor=tk.NW)

    def mettre_a_jour_jetons(self):
        self.label_humain.config(text=f"Vos jetons : {self.joueur_humain.tapis}")
        self.label_ia.config(text=f"Jetons IA : {self.joueur_ia.tapis}")
        self.label_pot.config(text=f"Pot : {self.partie.pot}")

        if self.joueur_humain.tapis <= 0:
            self.label_humain.config(text="Vous n'avez plus de jetons. Vous avez perdu.")
            self.bouton_miser.config(state=tk.DISABLED)
            self.bouton_suivre.config(state=tk.DISABLED)
            self.bouton_coucher.config(state=tk.DISABLED)
        elif self.joueur_ia.tapis <= 0:
            self.label_ia.config(text="L'IA n'a plus de jetons. Vous avez gagné.")
            self.bouton_miser.config(state=tk.DISABLED)
            self.bouton_suivre.config(state=tk.DISABLED)
            self.bouton_coucher.config(state=tk.DISABLED)

    def nouvelle_partie(self):
        self.partie.nouvelle_partie()
        self.partie.distribuer_cartes()
        self.canvas.delete("all")
        self.canvas.create_text(400, 50, text="Poker Texas Hold'em", font=("Arial", 24), fill="white")

        # Chargement et affichage de l'image de fond "table.png"
        table_image = Image.open("images/table.png").resize((800, 600))
        self.table_image_tk = ImageTk.PhotoImage(table_image)
        self.canvas.create_image(0, 0, image=self.table_image_tk, anchor=tk.NW)

        # Affichage des cartes sur la table avec l'image de fond
        self.afficher_cartes(self.joueur_humain, 200, 400)
        self.afficher_cartes(self.joueur_ia, 200, 150, face_cachee=True)
        self.partie.flop()
        self.afficher_cartes_communes()

        # Affichage des jetons
        self.afficher_jetons(150, 450, self.joueur_humain.tapis)
        self.afficher_jetons(600, 50, self.joueur_ia.tapis)

        self.mettre_a_jour_jetons()

        self.bouton_miser.config(state=tk.NORMAL)
        self.bouton_suivre.config(state=tk.NORMAL)
        self.bouton_coucher.config(state=tk.NORMAL)

    def miser(self):
        mise = simpledialog.askinteger("Mise", "Entrez votre mise (min 10) :", minvalue=10,
                                       maxvalue=self.joueur_humain.tapis)
        if mise:
            self.partie.ajouter_au_pot(self.joueur_humain.miser(mise))
            self.mettre_a_jour_jetons()
            messagebox.showinfo("Mise", f"Vous avez misé {mise} jetons.")

            # L'IA joue après le joueur
            ia_action = self.partie.ia_jouer()
            self.mettre_a_jour_jetons()
            messagebox.showinfo("Tour de l'IA", ia_action)
            if not self.joueur_ia.actif:
                self.afficher_cartes(self.joueur_ia, 200, 150)

    def suivre(self):
        mise = max(10, self.partie.mise_actuelle)
        self.partie.ajouter_au_pot(self.joueur_humain.miser(mise))
        self.mettre_a_jour_jetons()
        messagebox.showinfo("Suivi", f"Vous avez suivi la mise de {mise} jetons.")

        # IA joue après que le joueur suive
        ia_action = self.partie.ia_jouer()
        self.mettre_a_jour_jetons()
        messagebox.showinfo("Tour de l'IA", ia_action)
        if not self.joueur_ia.actif:
            self.afficher_cartes(self.joueur_ia, 200, 150)

    def coucher(self):
        if not self.joueur_ia.actif:  # Si l'IA est déjà inactive, le joueur gagne
            gagnant = self.joueur_humain
            perdant = self.joueur_ia
            messagebox.showinfo("Victoire", "Vous gagnez cette manche, l'IA s'était couchée.")
        elif not self.joueur_humain.actif:  # Si le joueur humain est déjà inactif, l'IA gagne
            gagnant = self.joueur_ia
            perdant = self.joueur_humain
            messagebox.showinfo("Défaite", "Vous vous êtes couché. L'IA gagne cette manche.")
        else:  # Sinon, c'est l'IA qui gagne
            gagnant = self.joueur_ia
            perdant = self.joueur_humain
            messagebox.showinfo("Défaite", "Vous vous êtes couché. L'IA gagne cette manche.")

        # Vérifier si le gagnant a encore des jetons
        if gagnant.tapis <= 0:
            messagebox.showinfo("Fin de la partie", f"{gagnant.nom} n'a plus de jetons. La partie est terminée.")
            self.partie.pot = 0  # Remise du pot
            self.mettre_a_jour_jetons()
            self.bouton_miser.config(state=tk.DISABLED)
            self.bouton_suivre.config(state=tk.DISABLED)
            self.bouton_coucher.config(state=tk.DISABLED)
            return

        # Transférer le pot au gagnant
        gagnant.tapis += self.partie.pot
        self.partie.pot = 0
        self.mettre_a_jour_jetons()

    def terminer_manche(self, gagnant):
        """Méthode pour terminer la manche avec un gagnant."""
        gagnant.tapis += self.partie.pot
        self.partie.pot = 0
        self.mettre_a_jour_jetons()
        messagebox.showinfo("Résultat", f"{gagnant.nom} gagne cette manche.")

# Exécution de l'application
root = tk.Tk()
app = PokerApp(root)
play_button = tk.Button(root, text="Jouer la musique", command=play_music)
play_button.pack(pady=20)

stop_button = tk.Button(root, text="Arrêter la musique", command=lambda: mixer.music.stop())
stop_button.pack(pady=20)
root.mainloop()
