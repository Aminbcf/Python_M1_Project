from Cafeteria import Cafeteria
from Client import Client
from Commande import Commande
from Produit import Produit
from Profile import Profile


# Produit
produit = Produit("BO1", "Café expresso", "boisson chaude", 1.20, 2)
assert produit.code == "BO1"
assert produit.prix == 1.20
assert produit.stock == 2
assert produit.disponible(1, "10:00")[0] is True
assert produit.disponible(0, "10:00")[0] is False
assert produit.disponible(3, "10:00")[0] is False
plat = Produit("PO1", "Sandwich", "plat", 4.00, 1)
assert plat.disponible(1, "11:30")[0] is True
assert plat.disponible(1, "14:00")[0] is False
assert plat.vendre(1, "11:30") is True
assert plat.stock == 0
assert plat.reapprovisionner(2) is True
assert plat.stock == 2
assert Produit("BO1", "Autre nom", "autre", 9.00, 1) == produit

# Client
client = Client("Test", 10.00, Profile.etudiant)
assert client.recharger(5.00) is True
assert client.solde == 15.00
assert client.recharger(4.99) is False
assert client.recharger(101.00) is False
assert client.peut_payer(15.00) is True
assert client.peut_payer(15.01) is False
assert client.debiter(5.00) is True
assert client.solde == 10.00
personnel = Client("Personnel", 0.00, Profile.personnel)
assert personnel.peut_payer(10.00) is True
assert personnel.peut_payer(10.01) is False
visiteur = Client("Visiteur", 0.00, Profile.visiteur)
assert visiteur.recharger(20.00) is False
assert visiteur.avantage_fidelite() == 0.00

# Commande
commande = Commande(client, "09:00")
assert commande.ajouter_ligne(produit, 2) is True
assert len(commande) == 2
assert produit in commande
assert commande.total() == 2.40
assert list(commande) == [(produit, 2)]

# Cafeteria and the O product codes
cafeteria = Cafeteria()
assert cafeteria.chercher_produit("BO1") is not None
assert cafeteria.chercher_produit("B01") is None
alice = cafeteria.clients[0]
cafe = cafeteria.chercher_produit("BO1")
stock_avant = cafe.stock
solde_avant = alice.solde
commande = Commande(alice, "09:00")
commande.ajouter_ligne(cafe, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is True
assert motif == ""
assert montant == 1.08
assert cafe.stock == stock_avant - 1
assert alice.solde == round(solde_avant - montant, 2)

produit_inconnu = Produit("SM1", "Smoothie mangue", "boisson froide", 3.00, 0)
commande = Commande(alice, "13:00")
commande.ajouter_ligne(produit_inconnu, 1)
acceptee, motif, montant = cafeteria.traiter_commande(commande)
assert acceptee is False
assert motif == "produit inconnu"
assert montant == 0.00
assert cafeteria.refus["produit inconnu"] == 1

print("Tous les tests sont reussis.")
