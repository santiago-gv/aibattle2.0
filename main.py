from src.character import Character
from src.agent import QLearningAgent
from src.battle import Battle

char_a = Character("Agente A", speed=30)
char_b = Character("Agente B", speed=9)

agent_a = QLearningAgent(char_a)
agent_b = QLearningAgent(char_b)

battle = Battle(agent_a, agent_b, initiative_mode="probabilistic")  # try "simultaneous" or "alternate"

EPISODES = 1000
wins_a = 0
wins_b = 0
draws = 0
for episode in range(EPISODES):
    battle.reset_episode()
    while char_a.get_health() > 0 and char_b.get_health() > 0:
        battle.step()

    # contabilizar resultado del episodio
    if char_a.get_health() <= 0 and char_b.get_health() <= 0:
        draws += 1
    elif char_a.get_health() > 0:
        wins_a += 1
    else:
        wins_b += 1

    if episode % 100 == 0:
        print(f"\nAcciones del episodio {episode}:")
        for log in battle.get_actions_log():
            print(log)
        print(f"\nEpisodio {episode}: Vida A = {char_a.get_health()}, Vida B = {char_b.get_health()}")
        print(f"Marcador hasta episodio {episode}: A={wins_a} | B={wins_b} | Empates={draws}")

print("\nQ-TABLE A:")
for k, v in agent_a.q_table.items():
    print(k, "->", round(v, 2))
print("\nQ-TABLE B:")
for k, v in agent_b.q_table.items():
    print(k, "->", round(v, 2))

print(f"\nResultados finales tras {EPISODES} episodios:")
print(f"Victorias A: {wins_a}")
print(f"Victorias B: {wins_b}")
print(f"Empates: {draws}")