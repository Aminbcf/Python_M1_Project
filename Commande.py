from decimal import Decimal

from Produit import Produit
from Client import Client
from Status import Status

class Commande:
    prochain_numero = 1

    def __init__(self, client: Client, heure: str, status: Status = Status.accepter):
        self.numero = Commande.prochain_numero
        Commande.prochain_numero += 1
        self.client = client
        self.heure = heure
        self.status = status
        self.lignes = []
        self.montant_paye = Decimal("0.00")
        self.remise = Decimal("0.00")
        self.avantage = Decimal("0.00")
        self.rappel_code: str | None = None

    def __repr__(self): # the !r is for formatting to use rpr representation
        return f"Commande({self.numero}, {self.client!r}, {self.heure!r} , {self.lignes!r} , {self.status!r})"

    def __str__(self):
        ticket = f"Commande {self.numero} - {self.client.nom}"
        if self.status == Status.anuller:
            ticket += " - ANNULÉE\n"
        else:
            ticket += "\n"
        for produit, quantite in self.lignes:
            sous_total = produit.prix * quantite
            ticket += f"{produit.nom} x {quantite} : {sous_total:.2f} EUR\n"
        ticket += f"Total : {self.total():.2f} EUR"
        return ticket

    def ajouter_ligne(self, produit, quantite: int) -> bool:
        if quantite <= 0:
            return False
        self.lignes.append((produit, quantite))
        return True

    def total(self) -> Decimal:
        total = Decimal("0.00")
        for produit, quantite in self.lignes:
            total += produit.prix * quantite
        return total.quantize(Decimal("0.01"))

    def __len__(self):
        nombre_articles = 0
        for _, quantite in self.lignes:
            nombre_articles += quantite
        return nombre_articles

    def __contains__(self, produit):
        for produit_ligne, _ in self.lignes:
            if produit == produit_ligne:
                return True
        return False

    def __iter__(self):
        return iter(self.lignes)