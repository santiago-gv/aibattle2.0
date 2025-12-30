"""
Sistema de personajes para combate estilo Pokémon (singles 3v3).

Clase base abstracta Character con tres subclases especializadas:
- TankCharacter: Alta vida, bajo daño, baja velocidad
- HybridCharacter: Stats equilibrados
- OffensiveCharacter: Baja vida, alto daño, alta velocidad

Acciones disponibles: attack, super_attack, defend
El cambio de personaje se gestiona a nivel de agente/batalla.
"""

from abc import ABC, abstractmethod


class Character(ABC):
    """
    Clase base abstracta para todos los tipos de personajes.
    Define la interfaz común y comportamiento base.
    """

    # Constantes de clase para stats base (se sobrescriben en subclases)
    BASE_HEALTH = 100
    BASE_ATTACK_DAMAGE = 20
    BASE_SUPER_DAMAGE = 40
    BASE_SPEED = 10
    DEFEND_REDUCTION = 0.5  # Daño reducido al 50% si defiende

    def __init__(self, name: str):
        self.name = name
        self._max_health = self.BASE_HEALTH
        self.health = self._max_health
        self.is_defending = False
        self.cooldown = 3  # Turnos hasta poder usar super_attack
        self._attack_damage = self.BASE_ATTACK_DAMAGE
        self._super_damage = self.BASE_SUPER_DAMAGE
        self._speed = self.BASE_SPEED

    @property
    @abstractmethod
    def char_type(self) -> str:
        """Retorna el tipo de personaje como string para el estado Q."""
        pass

    def attack(self, enemy: "Character") -> int:
        """
        Ataque básico. Hace daño reducido si el enemigo defiende.
        Reduce cooldown en 1.
        """
        damage = self._attack_damage

        if enemy.is_defending:
            damage = int(damage * self.DEFEND_REDUCTION)
            # Redondear a decenas para discretización limpia
            damage = (damage // 10) * 10

        enemy.health = max(0, enemy.health - damage)
        self.cooldown -= 1
        return damage

    def super_attack(self, enemy: "Character") -> int:
        """
        Ataque especial potente. Requiere cooldown <= 0.
        Reinicia cooldown a 3 tras usarlo.
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
        Activa defensa para este turno. Reduce daño recibido.
        También reduce cooldown.
        """
        self.cooldown -= 1
        self.is_defending = True
        return True

    def reset_turn(self) -> None:
        """Reinicia el estado de defensa al final del turno."""
        self.is_defending = False

    def reset_for_battle(self) -> None:
        """Reinicia el personaje completamente para un nuevo episodio."""
        self.health = self._max_health
        self.is_defending = False
        self.cooldown = 3

    def is_alive(self) -> bool:
        """Retorna True si el personaje tiene vida > 0."""
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
    Personaje tipo Tanque.
    - Alta vida (150)
    - Bajo daño (15 / 30)
    - Baja velocidad (6)
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
    Personaje tipo Híbrido.
    - Vida media (100)
    - Daño medio (20 / 40)
    - Velocidad media (10)
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
    Personaje tipo Ofensivo.
    - Baja vida (70)
    - Alto daño (25 / 50)
    - Alta velocidad (14)
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


# Mapeo de tipos para facilitar creación
CHARACTER_TYPES = {
    "tank": TankCharacter,
    "hybrid": HybridCharacter,
    "offensive": OffensiveCharacter,
}


def create_character(char_type: str, name: str) -> Character:
    """
    Factory function para crear personajes por tipo.
    
    Args:
        char_type: "tank", "hybrid", o "offensive"
        name: Nombre del personaje
    
    Returns:
        Instancia del tipo de personaje correspondiente
    """
    
    if char_type not in CHARACTER_TYPES:
        raise ValueError(f"Tipo de personaje desconocido: {char_type}. Usa: {list(CHARACTER_TYPES.keys())}")
    return CHARACTER_TYPES[char_type](name)