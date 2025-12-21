from src.character import Character
from src.agent import QLearningAgent
from src.fixed_agent import FixedAgent
from src.battle import Battle


agent_char = Character("Agente Inteligente")
fixed_char = Character("Enemigo")

learning_agent = QLearningAgent(agent_char)
fixed_agent = FixedAgent(fixed_char)

battle = Battle(learning_agent, fixed_agent)

EPISODES = 1000

for episode in range(EPISODES):
    
    battle.reset_episode()
    turn = 0

    while agent_char.get_health() > 0 and fixed_char.get_health() > 0:
        battle.step()
        turn += 1
        
    if episode % 100 == 0:

        # Mostrar les accions realitzades a l'episodi
        print(f"\nAccions de l'episodi {episode}:")
        for log in battle.get_actions_log():
            print(log)
        print(f"\nEpisodio {episode}: Vida Agente Inteligente = {agent_char.get_health()}, Vida Enemigo = {fixed_char.get_health()}")

print("\nQ-TABLE APRENDIDA:")
for e1, e2 in learning_agent.q_table.items():
    print(e1, "->", round(e2, 2))
