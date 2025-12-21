class Battle:
    def __init__(self, learning_agent, fixed_agent):
        self.learning_agent = learning_agent
        self.fixed_agent = fixed_agent

    def step(self):
        learning_agent = self.learning_agent
        fixed_agent = self.fixed_agent.character

        # ACCION/STEP DEL AGENTE Q-LEARNING
        state = learning_agent.get_state(fixed_agent)
        action = learning_agent.choose_action(fixed_agent)
        reward = 0

        if action == "attack":
            damage = learning_agent.character.attack(fixed_agent)
            reward += damage
        elif action == "defend":
            learning_agent.character.defend()

        # SI EL ENEMIGO MUERE
        if fixed_agent.get_health() <= 0:
            fixed_agent.health = 0
            reward += 100
            next_state = learning_agent.get_state(fixed_agent)
            learning_agent.update_q(state, action, reward, next_state)
            learning_agent.character.reset_turn()
            fixed_agent.reset_turn()
            return
        

        # ACCION/STEP DEL AGENTE FIJO
        if learning_agent.character.get_health() > 0:
            action_fa = self.fixed_agent.choose_action()
            if action_fa == "attack":
                learning_agent.character.health = max(0, learning_agent.character.health - fixed_agent.attack(learning_agent.character))
            elif action_fa == "defend":
                fixed_agent.defend()

        # Terminamos de calcular reward restandole al reward de ahora (daño infligido) el daño recibido
        reward -= max(0, 100 - learning_agent.character.get_health())

        # actualizamos Q-table
        next_state = learning_agent.get_state(fixed_agent)
        learning_agent.update_q(state, action, reward, next_state)

        # reseteamos estados de defensa
        learning_agent.character.reset_turn()
        fixed_agent.reset_turn()

    def reset_episode(self):
        for c in [self.learning_agent.character, self.fixed_agent.character]:
            c.health = 100
            c.attack_bonus = 0
            c.reset_turn()
