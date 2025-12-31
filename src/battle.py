"""
Sistema de batalla singles (3v3).

Cada agent té un equip de 3 personatges.
Només un personatge per equip està actiu a la vegada.
Accions: attack, defend, super_attack, switch.
Victòria: derrotar els 3 personatges de l'oponent.

"""

import random
from typing import Tuple, List


class Battle:
    
    """
    Gestiona combats singles 3v3 entre dos agents Q-Learning.
    """

    def __init__(self, agent_a, agent_b, initiative_mode: str = "probabilistic"):

        """
        Args:
            agent_a: Primer QLearningAgent amb equip de 3
            agent_b: Segon QLearningAgent amb equip de 3
            initiative_mode: "probabilistic" | "deterministic" | "alternate" | "simultaneous"
        """

        self.agent_a = agent_a
        self.agent_b = agent_b
        self.actions_log: List[str] = []
        self._initiative_toggle = 0
        self._initiative_mode = initiative_mode

    def _choose_order(self, a, b, action_a: str, action_b: str) -> Tuple[List, bool]:
        """
        Determina l'ordre d'execució segons velocitat i initiative_mode.
        
        Returns:
            (order_list, simultaneous_flag)
        """
        if self._initiative_mode == "simultaneous":
            return [("A", a, b, action_a), ("B", b, a, action_b)], True

        # Switches sempre tenen prioritat màxima
        a_switches = action_a == "switch"
        b_switches = action_b == "switch"
        
        if a_switches and not b_switches:
            return [("A", a, b, action_a), ("B", b, a, action_b)], False
        elif b_switches and not a_switches:
            return [("B", b, a, action_b), ("A", a, b, action_a)], False
        
        # Tots dos switch o cap: usar velocitat
        sa = a.character.get_speed()
        sb = b.character.get_speed()

        if self._initiative_mode == "probabilistic":
            total = sa + sb
            p_a = (sa / total) if total > 0 else 0.5
            first = "A" if random.random() < p_a else "B"
        
        if first == "A":
            return [("A", a, b, action_a), ("B", b, a, action_b)], False
        else:
            return [("B", b, a, action_b), ("A", a, b, action_a)], False

    def _execute_action(self, attacker, defender, action: str) -> int:
        # Executa una acció i retorna el dany infligit (0 per switch/defend).
        if action == "switch":
            attacker.perform_switch()
            return 0
        elif action == "defend":
            # Ja s'ha activat abans
            return 0
        elif action == "attack":
            return attacker.character.attack(defender.character)
        elif action == "super_attack":
            return attacker.character.super_attack(defender.character)
        return 0

    def step(self) -> bool:
        """
        Executa un torn complet de batalla.
        
        Returns:
            True si la batalla continua, False si ha acabat (un agent sense personatges vius).
        """
        a = self.agent_a
        b = self.agent_b
        turn_index = len(self.actions_log) + 1

        # Capturar estat abans d'actuar
        state_a = a.get_state(b)
        state_b = b.get_state(a)

        # Triar accions
        action_a = a.choose_action(b)
        action_b = b.choose_action(a)

        # Defenses s'activen abans de qualsevol atac
        if action_a == "defend":
            a.character.defend()
        if action_b == "defend":
            b.character.defend()

        # Determinar ordre d'execució
        order, simultaneous = self._choose_order(a, b, action_a, action_b)

        damage = {"A": 0, "B": 0}
        # Guardar els personatges que han triat les accions per al log
        char_a_at_action = a.character.char_type
        char_b_at_action = b.character.char_type

        if simultaneous:
            # Executar tots dos sense cancel·lar per KO
            for label, attacker, defender, action in order:
                dealt = self._execute_action(attacker, defender, action)
                damage[label] = dealt
        else:
            # Executar en ordre; cancel·lar si l'objectiu mor
            for label, attacker, defender, action in order:
                # Switch sempre es pot executar (fins i tot si el personatge actual està KO,
                # perquè pot ser que hagi mort en aquest mateix torn i el switch ja estava triat)
                if action == "switch":
                    # Només executar si hi ha algú a qui canviar
                    if attacker.has_switch_available():
                        attacker.perform_switch()
                    continue
                # Si l'atacant ja està KO, no pot actuar (per a atacs)
                if not attacker.character.is_alive():
                    continue
                # Si el defensor ja està KO, no ataquem (l'atac no té sentit)
                if not defender.character.is_alive():
                    continue
                dealt = self._execute_action(attacker, defender, action)
                damage[label] = dealt

        # Calcular recompenses
        reward_a = damage["A"] - damage["B"]
        reward_b = damage["B"] - damage["A"]

        # Comprovar KOs i forçar canvis
        a_char_fainted = not a.character.is_alive()
        b_char_fainted = not b.character.is_alive()

        # Bonus/penalització per KO de personatge
        if b_char_fainted:
            reward_a += 50  # Bonus per KO enemic
            reward_b -= 50
        if a_char_fainted:
            reward_b += 50
            reward_a -= 50

        # Forçar canvi si l'actiu ha mort
        if a_char_fainted:
            a.force_switch_if_fainted()
        if b_char_fainted:
            b.force_switch_if_fainted()

        # Comprovar victòria/derrota total
        a_all_fainted = a.all_fainted()
        b_all_fainted = b.all_fainted()

        if b_all_fainted and not a_all_fainted:
            reward_a += 100  # Victòria
            reward_b -= 100
        elif a_all_fainted and not b_all_fainted:
            reward_b += 100
            reward_a -= 100

        # Log del torn (usant els personatges que han triat les accions)
        # També mostrem el personatge actual si ha canviat (per switch o force_switch)
        char_a_final = a.character.char_type
        char_b_final = b.character.char_type
        
        log_entry = (
            f"Torn {turn_index}: "
            f"A[{char_a_at_action}]={action_a} (dany={damage['A']}), "
            f"B[{char_b_at_action}]={action_b} (dany={damage['B']}) | "
            f"HP_A={a.character.get_health()}, HP_B={b.character.get_health()} | "
            f"Vius: A={a.count_alive()}, B={b.count_alive()}"
        )
        
        # Afegir informació si el personatge actiu ha canviat
        changes = []
        if char_a_at_action != char_a_final:
            changes.append(f"A ara: {char_a_final}")
        if char_b_at_action != char_b_final:
            changes.append(f"B ara: {char_b_final}")
        if changes:
            log_entry += f" | {', '.join(changes)}"
        
        self.actions_log.append(log_entry)

        # Capturar estat després d'actuar
        next_state_a = a.get_state(b)
        next_state_b = b.get_state(a)

        # Actualitzar Q-tables
        a.update_q(state_a, action_a, reward_a, next_state_a)
        b.update_q(state_b, action_b, reward_b, next_state_b)

        # Reset estat de torn (defensa)
        a.character.reset_turn()
        b.character.reset_turn()

        # Retorna False si la batalla ha acabat
        return not (a_all_fainted or b_all_fainted)

    def reset_episode(self) -> None:
        # Reinicia la batalla per a un nou episodi.
        self.actions_log = []
        self.agent_a.reset_for_episode()
        self.agent_b.reset_for_episode()
        self._initiative_toggle = 0

    def get_actions_log(self) -> List[str]:
        # Retorna el log d'accions de l'episodi actual.
        return self.actions_log

    def get_winner(self) -> str:
        """
        Retorna el guanyador de l'episodi.
        
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