"""
# Agent Q-Learning per a combat (singles 3v3).
# 
# L'agent gestiona un equip de 3 personatges i aprèn:
# - Quan atacar, defensar, usar super_attack
# - Quan canviar de personatge (acció "switch")
# 
# Estat Q discretitzat:
# - Vida del personatge actiu propi (0-10)
# - Vida del personatge actiu enemic (0-10)
# - Tipus del personatge actiu propi (tank=0, hybrid=1, offensive=2)
# - Tipus del personatge actiu enemic (tank=0, hybrid=1, offensive=2)
# - Nombre de personatges vius propis (1-3)
# - Nombre de personatges vius enemics (1-3)
"""

import random
from typing import List, Tuple, Optional

# Mapeig de tipus de personatge a índexs numèrics per a l'estat
TYPE_TO_INDEX = {"tank": 0, "hybrid": 1, "offensive": 2}


def discretize(health: int, max_health: int = 100) -> int:
    """
    Discretitza la vida en 11 nivells (0-10).
    Ajusta segons la vida màxima del personatge per a normalització.
    """
    ratio = health / max_health
    return max(0, min(10, int(ratio * 10)))


class QLearningAgent:
    """
    Agent Q-Learning que gestiona un equip de 3 personatges.
    Aprèn política òptima per a combat singles estil.
    """

    def __init__(self, team: List):
        """
        Args:
            team: Llista de 3 objectes Character (subclasses de Character)
        """
        if len(team) != 3:
            raise ValueError("L'equip ha de tenir exactament 3 personatges")
        
        self.team = team
        self.active_index = 0  # Índex del personatge actiu (0, 1, o 2)
        
        # Accions base (switch s'afegeix dinàmicament si hi ha personatges vius a la banqueta)
        self.base_actions = ["attack", "defend", "super_attack"]
        
        self.q_table = {}
        
        # Hiperparàmetres Q-Learning
        self.alpha = 0.1    # Taxa d'aprenentatge
        self.gamma = 0.9    # Factor de descompte
        self.epsilon = 0.2  # Taxa d'exploració (e-greedy)

    @property
    def character(self):
        # Retorna el personatge actiu actual (compatibilitat amb codi anterior).
        return self.team[self.active_index]

    def get_alive_team(self) -> List:
        # Retorna llista de personatges vius a l'equip.
        return [c for c in self.team if c.is_alive()]

    def get_bench(self) -> List[Tuple[int, any]]:
        # Retorna llista de (índex, personatge) vius que NO estan actius.
        return [(i, c) for i, c in enumerate(self.team) 
                if c.is_alive() and i != self.active_index]

    def count_alive(self) -> int:
        # Compta personatges vius a l'equip.
        return sum(1 for c in self.team if c.is_alive())

    def has_switch_available(self) -> bool:
        # Retorna True si hi ha almenys un personatge viu a la banqueta.
        return len(self.get_bench()) > 0

    def get_state(self, enemy_agent: "QLearningAgent") -> Tuple:
        """
        Genera l'estat discretitzat per a Q-Learning.
        
        Returns:
            Tupla: (hp_propi, hp_enemic, tipus_propi, tipus_enemic, vius_propis, vius_enemics)
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
        Retorna les accions permeses segons l'estat actual.
        - super_attack: només si cooldown <= 0
        - switch: només si hi ha personatges vius a la banqueta
        """
        allowed = ["attack", "defend"]
        
        if self.character.get_cooldown() <= 0:
            allowed.append("super_attack")
        
        if self.has_switch_available():
            allowed.append("switch")
        
        return allowed

    def choose_action(self, enemy_agent: "QLearningAgent") -> str:
        """
        Selecciona acció usant política ε-greedy.
        
        Args:
            enemy_agent: Agent enemic (per obtenir estat)
        
        Returns:
            Acció seleccionada: "attack", "defend", "super_attack", o "switch"
        """
        state = self.get_state(enemy_agent)
        allowed_actions = self.get_allowed_actions()
        
        # Exploració (ε)
        if random.random() < self.epsilon:
            return random.choice(allowed_actions)
        
        # Explotació: triar acció amb major Q-value entre les permeses
        q_values = {a: self.q_table.get((state, a), 0.0) for a in allowed_actions}
        max_q = max(q_values.values())
        
        # Si hi ha empat, triar aleatòriament entre les millors
        best_actions = [a for a, q in q_values.items() if q == max_q]
        return random.choice(best_actions)

    def choose_switch_target(self) -> Optional[int]:
        """
        Tria a quin personatge de la banqueta canviar.
        Per ara, tria aleatòriament entre els vius de la banqueta.
        
        Returns:
            Índex del personatge al qual canviar, o None si no hi ha opcions.
        """
        bench = self.get_bench()
        if not bench:
            return None
        # Selecció aleatòria (podria millorar-se amb una altra Q-table o heurística)
        idx, _ = random.choice(bench)
        return idx

    def perform_switch(self, target_index: Optional[int] = None) -> bool:
        """
        Realitza el canvi de personatge.
        
        Args:
            target_index: Índex del personatge al qual canviar. Si és None, tria automàticament.
        
        Returns:
            True si el canvi ha estat exitós, False si no hi havia opcions.
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
        Si el personatge actiu està KO, força un canvi al primer viu disponible.
        
        Returns:
            True si s'ha fet canvi, False si no hi havia a qui canviar (derrota).
        """
        if self.character.is_alive():
            return True  # No cal canvi
        
        for i, c in enumerate(self.team):
            if c.is_alive():
                self.active_index = i
                return True
        
        return False  # Tots KO - derrota

    def update_q(self, state: Tuple, action: str, reward: float, next_state: Tuple) -> None:

        """
        Actualitza Q-table usant l'equació de Q-Learning.
        Q(s,a) = Q(s,a) + α * [r + γ * max_a' Q(s',a') - Q(s,a)]
        """

        old_q = self.q_table.get((state, action), 0.0)
        
        # Per al max futur, considerem totes les accions possibles en el següent estat
        # Nota: En estat terminal (derrota), future_q = 0

        future_actions = ["attack", "defend", "super_attack", "switch"]

        future_q = max(
            self.q_table.get((next_state, a), 0.0) for a in future_actions
        )

        new_q = old_q + self.alpha * (reward + self.gamma * future_q - old_q)
        self.q_table[(state, action)] = new_q

    def reset_for_episode(self) -> None:
        # Reinicia l'agent i tot el seu equip per a un nou episodi.
        self.active_index = 0
        for c in self.team:
            c.reset_for_battle()

    def all_fainted(self) -> bool:
        # Retorna True si tots els personatges de l'equip estan KO.
        return all(not c.is_alive() for c in self.team)

    def setgamma(self, gamma: float) -> None:

        self.gamma = gamma

    def setalpha(self, alpha: float) -> None:
        self.alpha = alpha

    def setepsilon(self, epsilon: float) -> None:
  
        self.epsilon = epsilon



        
