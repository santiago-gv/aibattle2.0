"""
Sistema de batalla singles estilo Pokémon (3v3).

Cada agente tiene un equipo de 3 personajes.
Solo un personaje por equipo está activo a la vez.
Acciones: attack, defend, super_attack, switch.
Victoria: derrotar a los 3 personajes del oponente.
"""

import random
from typing import Tuple, List


class Battle:
    
    """
    Gestiona combates singles 3v3 entre dos agentes Q-Learning.
    """

    def __init__(self, agent_a, agent_b, initiative_mode: str = "probabilistic"):

        """
        Args:
            agent_a: Primer QLearningAgent con equipo de 3
            agent_b: Segundo QLearningAgent con equipo de 3
            initiative_mode: "probabilistic" | "deterministic" | "alternate" | "simultaneous"
        """

        self.agent_a = agent_a
        self.agent_b = agent_b
        self.actions_log: List[str] = []
        self._initiative_toggle = 0
        self._initiative_mode = initiative_mode

    def _choose_order(self, a, b, action_a: str, action_b: str) -> Tuple[List, bool]:
        """
        Determina el orden de ejecución según velocidad e initiative_mode.
        
        Returns:
            (order_list, simultaneous_flag)
        """
        if self._initiative_mode == "simultaneous":
            return [("A", a, b, action_a), ("B", b, a, action_b)], True

        # Switches siempre tienen prioridad máxima (como en Pokémon)
        a_switches = action_a == "switch"
        b_switches = action_b == "switch"
        
        if a_switches and not b_switches:
            return [("A", a, b, action_a), ("B", b, a, action_b)], False
        elif b_switches and not a_switches:
            return [("B", b, a, action_b), ("A", a, b, action_a)], False
        
        # Ambos switch o ninguno: usar velocidad
        sa = a.character.get_speed()
        sb = b.character.get_speed()

        if self._initiative_mode == "probabilistic":
            total = sa + sb
            p_a = (sa / total) if total > 0 else 0.5
            first = "A" if random.random() < p_a else "B"
        elif self._initiative_mode == "alternate":
            first = "A" if (self._initiative_toggle % 2 == 0) else "B"
            self._initiative_toggle += 1
        else:  # deterministic
            first = "A" if sa >= sb else "B"

        if first == "A":
            return [("A", a, b, action_a), ("B", b, a, action_b)], False
        else:
            return [("B", b, a, action_b), ("A", a, b, action_a)], False

    def _execute_action(self, attacker, defender, action: str) -> int:
        # Ejecuta una acción y retorna el daño infligido (0 para switch/defend).
        if action == "switch":
            attacker.perform_switch()
            return 0
        elif action == "defend":
            # Ya se activó antes
            return 0
        elif action == "attack":
            return attacker.character.attack(defender.character)
        elif action == "super_attack":
            return attacker.character.super_attack(defender.character)
        return 0

    def step(self) -> bool:
        """
        Ejecuta un turno completo de batalla.
        
        Returns:
            True si la batalla continúa, False si terminó (un agente sin personajes vivos).
        """
        a = self.agent_a
        b = self.agent_b
        turn_index = len(self.actions_log) + 1

        # Capturar estado antes de actuar
        state_a = a.get_state(b)
        state_b = b.get_state(a)

        # Elegir acciones
        action_a = a.choose_action(b)
        action_b = b.choose_action(a)

        # Defensas se activan antes de cualquier ataque
        if action_a == "defend":
            a.character.defend()
        if action_b == "defend":
            b.character.defend()

        # Determinar orden de ejecución
        order, simultaneous = self._choose_order(a, b, action_a, action_b)

        damage = {"A": 0, "B": 0}
        # Guardar los personajes que eligieron las acciones para el log
        char_a_at_action = a.character.char_type
        char_b_at_action = b.character.char_type

        if simultaneous:
            # Ejecutar ambos sin cancelar por KO
            for label, attacker, defender, action in order:
                dealt = self._execute_action(attacker, defender, action)
                damage[label] = dealt
        else:
            # Ejecutar en orden; cancelar si el objetivo muere
            for label, attacker, defender, action in order:
                # Switch siempre se puede ejecutar (incluso si el personaje actual está KO,
                # porque puede que haya muerto en este mismo turno y el switch ya estaba elegido)
                if action == "switch":
                    # Solo ejecutar si hay alguien a quien cambiar
                    if attacker.has_switch_available():
                        attacker.perform_switch()
                    continue
                # Si el atacante ya está KO, no puede actuar (para ataques)
                if not attacker.character.is_alive():
                    continue
                # Si el defensor ya está KO, no atacamos (el ataque no tiene sentido)
                if not defender.character.is_alive():
                    continue
                dealt = self._execute_action(attacker, defender, action)
                damage[label] = dealt

        # Calcular recompensas
        reward_a = damage["A"] - damage["B"]
        reward_b = damage["B"] - damage["A"]

        # Comprobar KOs y forzar cambios
        a_char_fainted = not a.character.is_alive()
        b_char_fainted = not b.character.is_alive()

        # Bonus/penalización por KO de personaje
        if b_char_fainted:
            reward_a += 50  # Bonus por KO enemigo
            reward_b -= 50
        if a_char_fainted:
            reward_b += 50
            reward_a -= 50

        # Forzar cambio si el activo murió
        if a_char_fainted:
            a.force_switch_if_fainted()
        if b_char_fainted:
            b.force_switch_if_fainted()

        # Comprobar victoria/derrota total
        a_all_fainted = a.all_fainted()
        b_all_fainted = b.all_fainted()

        if b_all_fainted and not a_all_fainted:
            reward_a += 100  # Victoria
            reward_b -= 100
        elif a_all_fainted and not b_all_fainted:
            reward_b += 100
            reward_a -= 100

        # Log del turno (usando los personajes que eligieron las acciones)
        # También mostramos el personaje actual si cambió (por switch o force_switch)
        char_a_final = a.character.char_type
        char_b_final = b.character.char_type
        
        log_entry = (
            f"Torn {turn_index}: "
            f"A[{char_a_at_action}]={action_a} (dany={damage['A']}), "
            f"B[{char_b_at_action}]={action_b} (dany={damage['B']}) | "
            f"HP_A={a.character.get_health()}, HP_B={b.character.get_health()} | "
            f"Vivos: A={a.count_alive()}, B={b.count_alive()}"
        )
        
        # Añadir información si el personaje activo cambió
        changes = []
        if char_a_at_action != char_a_final:
            changes.append(f"A ahora: {char_a_final}")
        if char_b_at_action != char_b_final:
            changes.append(f"B ahora: {char_b_final}")
        if changes:
            log_entry += f" | {', '.join(changes)}"
        
        self.actions_log.append(log_entry)

        # Capturar estado después de actuar
        next_state_a = a.get_state(b)
        next_state_b = b.get_state(a)

        # Actualizar Q-tables
        a.update_q(state_a, action_a, reward_a, next_state_a)
        b.update_q(state_b, action_b, reward_b, next_state_b)

        # Reset estado de turno (defensa)
        a.character.reset_turn()
        b.character.reset_turn()

        # Retorna False si la batalla terminó
        return not (a_all_fainted or b_all_fainted)

    def reset_episode(self) -> None:
        # Reinicia la batalla para un nuevo episodio.
        self.actions_log = []
        self.agent_a.reset_for_episode()
        self.agent_b.reset_for_episode()
        self._initiative_toggle = 0

    def get_actions_log(self) -> List[str]:
        # Retorna el log de acciones del episodio actual.
        return self.actions_log

    def get_winner(self) -> str:
        """
        Retorna el ganador del episodio.
        
        Returns:
            "A", "B", o "draw"
        """
        a_alive = not self.agent_a.all_fainted()
        b_alive = not self.agent_b.all_fainted()
        
        if a_alive and not b_alive:
            return "A"
        elif b_alive and not a_alive:
            return "B"
        else:
            return "draw"