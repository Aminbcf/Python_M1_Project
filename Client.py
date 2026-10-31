from Paiment import Paiment
from Profile import Profile

class Client:
    
    
    
   def __init__(self , nom:str , solde:float , profile:Profile , pointfid = 0.0):
       self.nom = nom 
       self.solde = solde 
       self.profile = profile
       self.pointfid = pointfid
       if profile == Profile.visiteur:
          self.paiment = Paiment.comptant
       else :
           self.paiment = Paiment.badge 