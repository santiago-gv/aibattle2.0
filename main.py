"""
Entrenament Q-Learning per a combat 3v3 estil Pokémon.

Dos agents Q-Learning competeixen amb equips de 3 personatges cadascun.
Tipus de personatge: Tank, Hybrid, Offensive.
Accions: attack, defend, super_attack, switch.
"""

from src.character import TankCharacter, HybridCharacter, OffensiveCharacter
from src.agent import QLearningAgent
from src.battle import Battle


def create_team_a():
    # Crea l'equip de l'Agent A: Tank, Hybrid, Offensive.

    return [
        OffensiveCharacter("Offensive_A"),
        HybridCharacter("Hybrid_A"),
        TankCharacter("Tank_A"),

    ]


def create_team_b():
    # Crea l'equip de l'Agent B: Offensive, Tank, Hybrid.

    return [
        TankCharacter("Tank_B"),
        OffensiveCharacter("Offensive_B"),
        HybridCharacter("Hybrid_B"),
    ]



def main():
    # Crear equips
    team_a = create_team_a()
    team_b = create_team_b()

    # Crear agents amb els seus equips
    agent_a = QLearningAgent(team_a)
    agent_b = QLearningAgent(team_b)

    agent_a.setalpha(0.1)
    agent_b.setalpha(0.1)

    agent_a.setgamma(0.95)
    agent_b.setgamma(0.95)
    agent_a.setepsilon(0.05)
    agent_b.setepsilon(0.05)

    # Crear batalla
    battle = Battle(agent_a, agent_b, initiative_mode="probabilistic")

    # Configuració d'entrenament
    
    EPISODES = 100000
    PRINT_EVERY = 500

    # Comptadors de victòries
    wins_a = 0
    wins_b = 0
    draws = 0

    print("=" * 60)
    print("ENTRENAMENT Q-LEARNING")
    print("=" * 60)
    print(f"\nEquip A: {[c.char_type for c in team_a]}")
    print(f"Equip B: {[c.char_type for c in team_b]}")
    print(f"\nEpisodis: {EPISODES}")
    print(f"Mode iniciativa: {battle._initiative_mode}")
    print("=" * 60)



    for episode in range(EPISODES):
        battle.reset_episode()
        
        # Executar episodi fins que acabi
        max_turns = 100  # Límit de torns per evitar bucles infinits
        turn = 0
        while battle.step() and turn < max_turns:
            turn += 1

        # Comptabilitzar resultat
        winner = battle.get_winner()
        if winner == "A":
            wins_a += 1
        elif winner == "B":
            wins_b += 1
        else:
            draws += 1

        # Imprimir progrés periòdicament
        if episode % PRINT_EVERY == 0:
            print(f"\n{'='*60}")
            print(f"EPISODI {episode}")
            print(f"{'='*60}")
            print(f"\nAccions de l'episodi:")
            for log in battle.get_actions_log()[-10:]:  # Últims 10 torns
                print(f"  {log}")
            
            print(f"\nResultat: Guanyador = {winner}")
            print(f"Marcador acumulat: A={wins_a} | B={wins_b} | Empats={draws}")
            
            # Winrate
            total = wins_a + wins_b + draws
            if total > 0:
                print(f"Winrate: A={100*wins_a/total:.1f}% | B={100*wins_b/total:.1f}%")

    # Resultats finals
    print("\n" + "=" * 60)
    print("RESULTATS FINALS")
    print("=" * 60)
    print(f"\nVictòries Agent A: {wins_a}")
    print(f"Victòries Agent B: {wins_b}")
    print(f"Empats: {draws}")
    
    total = wins_a + wins_b + draws
    if total > 0:
        print(f"\nWinrate Final: A={100*wins_a/total:.1f}% | B={100*wins_b/total:.1f}%")

    # Mostrar mida de les Q-tables
    print(f"\nEstats apresos Agent A: {len(agent_a.q_table)}")
    print(f"Estats apresos Agent B: {len(agent_b.q_table)}")

    # Mostrar alguns valors Q interessants (top 10 per valor absolut)
    print("\n" + "-" * 40)
    print("TOP 10 Q-VALUES (Agent A):")
    print("-" * 40)
    sorted_q_a = sorted(agent_a.q_table.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    for (state, action), value in sorted_q_a:
        print(f"  Estat {state}, Acció '{action}': {value:.2f}")

    print("\n" + "-" * 40)
    print("TOP 10 Q-VALUES (Agent B):")
    print("-" * 40)
    sorted_q_b = sorted(agent_b.q_table.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    for (state, action), value in sorted_q_b:
        print(f"  Estat {state}, Acció '{action}': {value:.2f}")


if __name__ == "__main__":
    main()