class Produit:
    HEURE_DEBUT_PLATS = "11:30"
    HEURE_FIN_PLATS = "14:00"

    def __init__(self, code: str, nom: str, categorie: str,prix: float, stock: int):
        self.code = code
        self.nom = nom
        self.categorie = categorie
        self.prix = round(prix, 2)
        self.stock = stock

    def __repr__(self):
        return f"Produit({self.code!r}, {self.nom!r}, {self.categorie!r}, " \
               f"{self.prix!r}, {self.stock!r})"

    def __str__(self):
        return f"{self.code} - {self.nom} ({self.prix:.2f} EUR)"

    def __eq__(self, other):
        if not isinstance(other, Produit):
            return NotImplemented
        return self.code == other.code

    def __lt__(self, other):
        if not isinstance(other, Produit):
            return NotImplemented
        return self.prix < other.prix

    def disponible(self, quantite: int, heure: str) -> bool:
        if quantite <= 0:
            return False
        if quantite > self.stock:
            return False
        if self.categorie == "plat":
            if heure < self.HEURE_DEBUT_PLATS:
                return False
            if heure >= self.HEURE_FIN_PLATS:
                return False
        return True

    def vendre(self, quantite: int, heure: str) -> bool:
        if not self.disponible(quantite, heure):
            return False
        self.stock -= quantite
        return True

    def reapprovisionner(self, quantite: int) -> bool:
        if quantite <= 0:
            return False
        self.stock += quantite
        return True