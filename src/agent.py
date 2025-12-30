"""
Agente Q-Learning para combate estilo Pokémon (singles 3v3).

El agente gestiona un equipo de 3 personajes y aprende:
- Cuándo atacar, defender, usar super_attack
- Cuándo cambiar de personaje (acción "switch")

Estado Q discretizado:
- Vida del personaje activo propio (0-10)
- Vida del personaje activo enemigo (0-10)
- Tipo del personaje activo propio (tank=0, hybrid=1, offensive=2)
- Tipo del personaje activo enemigo (tank=0, hybrid=1, offensive=2)
- Número de personajes vivos propios (1-3)
- Número de personajes vivos enemigos (1-3)
"""

import random
from typing import List, Tuple, Optional

# Mapeo de tipos de personaje a índices numéricos para el estado
TYPE_TO_INDEX = {"tank": 0, "hybrid": 1, "offensive": 2}


def discretize(health: int, max_health: int = 100) -> int:
    """
    Discretiza la vida en 11 niveles (0-10).
    Ajusta según la vida máxima del personaje para normalización.
    """
    ratio = health / max_health
    return max(0, min(10, int(ratio * 10)))


class QLearningAgent:
    """
    Agente Q-Learning que gestiona un equipo de 3 personajes.
    Aprende política óptima para combate singles estilo Pokémon.
    """

    def __init__(self, team: List):
        """
        Args:
            team: Lista de 3 objetos Character (subclases de Character)
        """
        if len(team) != 3:
            raise ValueError("El equipo debe tener exactamente 3 personajes")
        
        self.team = team
        self.active_index = 0  # Índice del personaje activo (0, 1, o 2)
        
        # Acciones base (switch se añade dinámicamente si hay personajes vivos en el banco)
        self.base_actions = ["attack", "defend", "super_attack"]
        
        self.q_table = {}
        
        # Hiperparámetros Q-Learning
        self.alpha = 0.1    # Tasa de aprendizaje
        self.gamma = 0.9    # Factor de descuento
        self.epsilon = 0.2  # Tasa de exploración (e-greedy)

    @property
    def character(self):
        # Retorna el personaje activo actual (compatibilidad con código anterior).
        return self.team[self.active_index]

    def get_alive_team(self) -> List:
        # Retorna lista de personajes vivos en el equipo.
        return [c for c in self.team if c.is_alive()]

    def get_bench(self) -> List[Tuple[int, any]]:
        # Retorna lista de (índice, personaje) vivos que NO están activos.
        return [(i, c) for i, c in enumerate(self.team) 
                if c.is_alive() and i != self.active_index]

    def count_alive(self) -> int:
        # Cuenta personajes vivos en el equipo.
        return sum(1 for c in self.team if c.is_alive())

    def has_switch_available(self) -> bool:
        # Retorna True si hay al menos un personaje vivo en el banco.
        return len(self.get_bench()) > 0

    def get_state(self, enemy_agent: "QLearningAgent") -> Tuple:
        """
        Genera el estado discretizado para Q-Learning.
        
        Returns:
            Tupla: (hp_propio, hp_enemigo, tipo_propio, tipo_enemigo, vivos_propios, vivos_enemigos)
        """
        my_char = self.character
        enemy_char = enemy_agent.character
        
        return (
            discretize(my_char.get_health(), my_char.get_max_health()),
            discretize(enemy_char.get_health(), enemy_char.get_max_health()),
            TYPE_TO_INDEX[my_char.char_type],
            TYPE_TO_INDEX[enemy_char.char_type],
            self.count_alive(),
            enemy_agent.count_alive()
        )

    def get_allowed_actions(self) -> List[str]:
        """
        Retorna las acciones permitidas según el estado actual.
        - super_attack: solo si cooldown <= 0
        - switch: solo si hay personajes vivos en el banco
        """
        allowed = ["attack", "defend"]
        
        if self.character.get_cooldown() <= 0:
            allowed.append("super_attack")
        
        if self.has_switch_available():
            allowed.append("switch")
        
        return allowed

    def choose_action(self, enemy_agent: "QLearningAgent") -> str:
        """
        Selecciona acción usando política ε-greedy.
        
        Args:
            enemy_agent: Agente enemigo (para obtener estado)
        
        Returns:
            Acción seleccionada: "attack", "defend", "super_attack", o "switch"
        """
        state = self.get_state(enemy_agent)
        allowed_actions = self.get_allowed_actions()
        
        # Exploración (ε)
        if random.random() < self.epsilon:
            return random.choice(allowed_actions)
        
        # Explotación: elegir acción con mayor Q-value entre las permitidas
        q_values = {a: self.q_table.get((state, a), 0.0) for a in allowed_actions}
        max_q = max(q_values.values())
        
        # Si hay empate, elegir aleatoriamente entre las mejores
        best_actions = [a for a, q in q_values.items() if q == max_q]
        return random.choice(best_actions)

    def choose_switch_target(self) -> Optional[int]:
        """
        Elige a qué personaje del banco cambiar.
        Por ahora, elige aleatoriamente entre los vivos del banco.
        
        Returns:
            Índice del personaje al que cambiar, o None si no hay opciones.
        """
        bench = self.get_bench()
        if not bench:
            return None
        # Selección aleatoria (podría mejorarse con otra Q-table o heurística)
        idx, _ = random.choice(bench)
        return idx

    def perform_switch(self, target_index: Optional[int] = None) -> bool:
        """
        Realiza el cambio de personaje.
        
        Args:
            target_index: Índice del personaje al que cambiar. Si None, elige automáticamente.
        
        Returns:
            True si el cambio fue exitoso, False si no había opciones.
        """
        if target_index is None:
            target_index = self.choose_switch_target()
        
        if target_index is None:
            return False
        
        if target_index < 0 or target_index >= len(self.team):
            return False
        
        if not self.team[target_index].is_alive():
            return False
        
        self.active_index = target_index
        return True

    def force_switch_if_fainted(self) -> bool:
        """
        Si el personaje activo está KO, fuerza un cambio al primer vivo disponible.
        
        Returns:
            True si se hizo cambio, False si no había a quién cambiar (derrota).
        """
        if self.character.is_alive():
            return True  # No hace falta cambio
        
        for i, c in enumerate(self.team):
            if c.is_alive():
                self.active_index = i
                return True
        
        return False  # Todos KO - derrota

    def update_q(self, state: Tuple, action: str, reward: float, next_state: Tuple) -> None:
        """
        Actualiza Q-table usando la ecuación de Q-Learning.
        
        Q(s,a) = Q(s,a) + α * [r + γ * max_a' Q(s',a') - Q(s,a)]
        """
        old_q = self.q_table.get((state, action), 0.0)
        
        # Para el max futuro, consideramos todas las acciones posibles en el siguiente estado
        # Nota: En estado terminal (derrota), future_q = 0
        future_actions = ["attack", "defend", "super_attack", "switch"]
        future_q = max(
            self.q_table.get((next_state, a), 0.0) for a in future_actions
        )
        
        new_q = old_q + self.alpha * (reward + self.gamma * future_q - old_q)
        self.q_table[(state, action)] = new_q

    def reset_for_episode(self) -> None:
        # Reinicia el agente y todo su equipo para un nuevo episodio.
        self.active_index = 0
        for c in self.team:
            c.reset_for_battle()

    def all_fainted(self) -> bool:
        # Retorna True si todos los personajes del equipo están KO.
        return all(not c.is_alive() for c in self.team)

    def setgamma(self, gamma: float) -> None:

        self.gamma = gamma

    def setalpha(self, alpha: float) -> None:
        self.alpha = alpha

    def setepsilon(self, epsilon: float) -> None:
  
        self.epsilon = epsilon



        
