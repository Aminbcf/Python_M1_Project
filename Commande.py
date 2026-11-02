class Commande:
    prochain_numero = 1

    def __init__(self, client, heure: str):
        self.numero = Commande.prochain_numero
        Commande.prochain_numero += 1
        self.client = client
        self.heure = heure
        self.lignes = []

    def __repr__(self):
        return f"Commande({self.numero}, {self.client!r}, {self.heure!r})"

    def __str__(self):
        ticket = f"Commande {self.numero} - {self.client.nom}\n"
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

    def total(self) -> float:
        total = 0
        for produit, quantite in self.lignes:
            total += produit.prix * quantite
        return round(total, 2)

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