import random

# Agante simple con comportamiento aleatorio para pruebas.
# Nota: Esta implementación no es compatible con el sistema actual de batalla (Battle)
# que requiere gestión de equipos de 3 personajes.

class FixedAgent:
    """
    Agente 'Fixed' (o Dummy) para pruebas básicas 1v1.
    Controla un único personaje y toma decisiones aleatorias.
    
    WARNING: No implementa la interfaz completa requerida por Battle (get_state, update_q, etc).
    """

    def __init__(self, character):
        # Inicializa el agente con un único personaje.
        self.is_defending = False
        self.character = character

    def choose_action(self, enemy=None):
        # Elige una acción aleatoria respetando el cooldown del superataque.
        
        if self.character.get_cooldown() <= 0:
            # Si el cooldown está listo, incluye super_attack en las opciones.
            return random.choice(["super_attack", "attack", "defend"])
        else:
            # Si no, solo ataca o defiende.
            return random.choice(["attack", "defend"])

        
