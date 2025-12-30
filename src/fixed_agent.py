import random

# Agent simple amb comportament aleatori per a proves.
# Nota: Aquesta implementació no és compatible amb el sistema actual de batalla (Battle)
# que requereix gestió d'equips de 3 personatges.

class FixedAgent:
    """
    Agent 'Fixed' (o Dummy) per a proves bàsiques 1v1.
    Controla un únic personatge i pren decisions aleatòries.
    
    WARNING: No implementa la interfície completa requerida per Battle (get_state, update_q, etc).
    """

    def __init__(self, character):
        # Inicialitza l'agent amb un únic personatge.
        self.is_defending = False
        self.character = character

    def choose_action(self, enemy=None):
        # Tria una acció aleatòria respectant el cooldown del superatac.
        
        if self.character.get_cooldown() <= 0:
            # Si el cooldown està llest, inclou super_attack en les opcions.
            return random.choice(["super_attack", "attack", "defend"])
        else:
            # Si no, només ataca o defensa.
            return random.choice(["attack", "defend"])

        
