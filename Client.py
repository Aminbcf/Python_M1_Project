from Paiment import Paiment
from Profile import Profile


class Client:
    MIN_RECHARGE = 5.00
    MAX_RECHARGE = 100.00
    MAX_SOLDE = 150.00
    DECOUVERT_MAX = -10.00
    SEUIL_POINTS = 30
    AVANTAGE_POINTS = 2.00

    def __init__(self, nom: str, solde: float, profile: Profile,
                 pointfid: int = 0):
        self.nom = nom
        self.solde = round(solde, 2)
        self.profile = profile
        self.pointfid = pointfid
        if profile == Profile.visiteur:
            self.paiment = Paiment.comptant
        else:
            self.paiment = Paiment.badge

    def __repr__(self):
        return f"Client({self.nom!r}, {self.solde!r}, Profile.{self.profile.name})"

    def __str__(self):
        return f"{self.nom} ({self.profile.value})"

    def recharger(self, montant: float) -> bool:
        if self.paiment == Paiment.comptant:
            return False
        if montant < self.MIN_RECHARGE or montant > self.MAX_RECHARGE:
            return False
        if self.solde + montant > self.MAX_SOLDE:
            return False
        self.solde = round(self.solde + montant, 2)
        return True

    def peut_payer(self, montant: float) -> bool:
        if montant < 0:
            return False
        if self.paiment == Paiment.comptant:
            return True
        if self.profile == Profile.personnel:
            return self.solde - montant >= self.DECOUVERT_MAX
        return self.solde >= montant

    def debiter(self, montant: float) -> bool:
        if not self.peut_payer(montant):
            return False
        if self.paiment == Paiment.badge:
            self.solde = round(self.solde - montant, 2)
        return True

    def avantage_fidelite(self) -> float:
        if self.paiment != Paiment.badge:
            return 0.00
        if self.pointfid < self.SEUIL_POINTS:
            return 0.00
        return self.AVANTAGE_POINTS

    def ajouter_points(self, montant_paye: float) -> None:
        if self.paiment == Paiment.badge:
            self.pointfid += int(montant_paye)

    def utiliser_avantage_fidelite(self) -> None:
        if self.avantage_fidelite() == 0:
            return
        self.pointfid -= self.SEUIL_POINTS
            
            
        