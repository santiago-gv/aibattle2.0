"""
# Sistema de personatges per a combat estil Pokémon (singles 3v3).
# 
# Classe base abstracta Character amb tres subclasses especialitzades:
# - TankCharacter: Alta vida, baix dany, baixa velocitat
# - HybridCharacter: Stats equilibrats
# - OffensiveCharacter: Baixa vida, alt dany, alta velocitat
# 
# Accions disponibles: attack, super_attack, defend
# El canvi de personatge es gestiona a nivell d'agent/batalla.
"""

from abc import ABC, abstractmethod


class Character(ABC):
    """
    Classe base abstracta per a tots els tipus de personatges.
    Defineix la interfície comuna i comportament base.
    """

    # Constants de classe per a stats base (se sobreescriuen en subclasses)
    BASE_HEALTH = 100
    BASE_ATTACK_DAMAGE = 20
    BASE_SUPER_DAMAGE = 40
    BASE_SPEED = 10
    DEFEND_REDUCTION = 0.5  # Dany reduït al 50% si defensa

    def __init__(self, name: str):
        self.name = name
        self._max_health = self.BASE_HEALTH
        self.health = self._max_health
        self.is_defending = False
        self.cooldown = 3  # Torns fins a poder usar super_attack
        self._attack_damage = self.BASE_ATTACK_DAMAGE
        self._super_damage = self.BASE_SUPER_DAMAGE
        self._speed = self.BASE_SPEED

    @property
    @abstractmethod
    def char_type(self) -> str:
        # Retorna el tipus de personatge com a string per a l'estat Q.
        pass

    def attack(self, enemy: "Character") -> int:
        """
        Atac bàsic. Fa dany reduït si l'enemic defensa.
        Redueix cooldown en 1.
        """
        damage = self._attack_damage

        if enemy.is_defending:
            damage = int(damage * self.DEFEND_REDUCTION)
            # Arrodonir a desenes per a discretització neta
            damage = (damage // 10) * 10

        enemy.health = max(0, enemy.health - damage)
        self.cooldown -= 1
        return damage

    def super_attack(self, enemy: "Character") -> int:
        """
        Atac especial potent. Requereix cooldown <= 0.
        Reinicia cooldown a 3 després d'usar-lo.
        """
        damage = self._super_damage

        if enemy.is_defending:
            damage = int(damage * self.DEFEND_REDUCTION)
            damage = (damage // 10) * 10

        enemy.health = max(0, enemy.health - damage)
        self.cooldown = 3  # Reset cooldown
        return damage

    def defend(self) -> bool:
        """
        Activa defensa per a aquest torn. Redueix dany rebut.
        També redueix cooldown.
        """
        self.cooldown -= 1
        self.is_defending = True
        return True

    def reset_turn(self) -> None:
        # Reinicia l'estat de defensa al final del torn.
        self.is_defending = False

    def reset_for_battle(self) -> None:
        # Reinicia el personatge completament per a un nou episodi.
        self.health = self._max_health
        self.is_defending = False
        self.cooldown = 3

    def is_alive(self) -> bool:
        # Retorna True si el personatge té vida > 0.
        return self.health > 0

    # Getters
    def get_health(self) -> int:
        return self.health

    def get_max_health(self) -> int:
        return self._max_health

    def get_cooldown(self) -> int:
        return self.cooldown

    def get_speed(self) -> int:
        return self._speed

    def get_attack_damage(self) -> int:
        return self._attack_damage

    def get_super_damage(self) -> int:
        return self._super_damage

    def __repr__(self) -> str:
        return f"{self.char_type}({self.name}, HP={self.health}/{self._max_health})"


class TankCharacter(Character):
    """
    Personatge tipus Tank.
    - Alta vida (150)
    - Baix dany (15 / 30)
    - Baixa velocitat (6)
    """

    BASE_HEALTH = 150
    BASE_ATTACK_DAMAGE = 15
    BASE_SUPER_DAMAGE = 30
    BASE_SPEED = 6

    def __init__(self, name: str):
        super().__init__(name)
        self._max_health = self.BASE_HEALTH
        self.health = self._max_health
        self._attack_damage = self.BASE_ATTACK_DAMAGE
        self._super_damage = self.BASE_SUPER_DAMAGE
        self._speed = self.BASE_SPEED

    @property
    def char_type(self) -> str:
        return "tank"


class HybridCharacter(Character):
    """
    Personatge tipus Híbrid.
    - Vida mitjana (100)
    - Dany mitjà (20 / 40)
    - Velocitat mitjana (10)
    """

    BASE_HEALTH = 100
    BASE_ATTACK_DAMAGE = 20
    BASE_SUPER_DAMAGE = 40
    BASE_SPEED = 10

    def __init__(self, name: str):
        super().__init__(name)
        self._max_health = self.BASE_HEALTH
        self.health = self._max_health
        self._attack_damage = self.BASE_ATTACK_DAMAGE
        self._super_damage = self.BASE_SUPER_DAMAGE
        self._speed = self.BASE_SPEED

    @property
    def char_type(self) -> str:
        return "hybrid"


class OffensiveCharacter(Character):
    """
    Personatge tipus Ofensiu.
    - Baixa vida (70)
    - Alt dany (25 / 50)
    - Alta velocitat (14)
    """

    BASE_HEALTH = 70
    BASE_ATTACK_DAMAGE = 25
    BASE_SUPER_DAMAGE = 50
    BASE_SPEED = 14

    def __init__(self, name: str):
        super().__init__(name)
        self._max_health = self.BASE_HEALTH
        self.health = self._max_health
        self._attack_damage = self.BASE_ATTACK_DAMAGE
        self._super_damage = self.BASE_SUPER_DAMAGE
        self._speed = self.BASE_SPEED

    @property
    def char_type(self) -> str:
        return "offensive"


# Mapeig de tipus per facilitar creació
CHARACTER_TYPES = {
    "tank": TankCharacter,
    "hybrid": HybridCharacter,
    "offensive": OffensiveCharacter,
}


def create_character(char_type: str, name: str) -> Character:
    """
    Factory function per crear personatges per tipus.
    
    Args:
        char_type: "tank", "hybrid", o "offensive"
        name: Nom del personatge
    
    Returns:
        Instància del tipus de personatge corresponent
    """
    
    if char_type not in CHARACTER_TYPES:
        raise ValueError(f"Tipus de personatge desconegut: {char_type}. Usa: {list(CHARACTER_TYPES.keys())}")
    return CHARACTER_TYPES[char_type](name)