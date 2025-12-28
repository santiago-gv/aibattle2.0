"""
Entrenamiento Q-Learning para combate 3v3 estilo Pokémon.

Dos agentes Q-Learning compiten con equipos de 3 personajes cada uno.
Tipos de personaje: Tank, Hybrid, Offensive.
Acciones: attack, defend, super_attack, switch.
"""

from src.character import TankCharacter, HybridCharacter, OffensiveCharacter
from src.agent import QLearningAgent
from src.battle import Battle


def create_team_a():
    """Crea el equipo del Agente A: Tank, Hybrid, Offensive."""
    return [
        HybridCharacter("Hybrid_A"),
        TankCharacter("Tank_A"),
        OffensiveCharacter("Offensive_A"),
    ]


def create_team_b():
    """Crea el equipo del Agente B: Offensive, Tank, Hybrid."""
    return [
        TankCharacter("Tank_B"),
        OffensiveCharacter("Offensive_B"),
        HybridCharacter("Hybrid_B"),
    ]


def main():
    # Crear equipos
    team_a = create_team_a()
    team_b = create_team_b()

    # Crear agentes con sus equipos
    agent_a = QLearningAgent(team_a)
    agent_b = QLearningAgent(team_b)
    agent_a.setalpha(0.05)
    agent_b.setalpha(0.2)

    # Crear batalla
    battle = Battle(agent_a, agent_b, initiative_mode="probabilistic")

    # Configuración de entrenamiento
    
    EPISODES = 10000
    PRINT_EVERY = 500

    # Contadores de victorias
    wins_a = 0
    wins_b = 0
    draws = 0

    print("=" * 60)
    print("ENTRENAMIENTO Q-LEARNING")
    print("=" * 60)
    print(f"\nEquipo A: {[c.char_type for c in team_a]}")
    print(f"Equipo B: {[c.char_type for c in team_b]}")
    print(f"\nEpisodios: {EPISODES}")
    print(f"Modo iniciativa: {battle._initiative_mode}")
    print("=" * 60)



    for episode in range(EPISODES):
        battle.reset_episode()
        
        # Ejecutar episodio hasta que termine
        max_turns = 100  # Límite de turnos para evitar bucles infinitos
        turn = 0
        while battle.step() and turn < max_turns:
            turn += 1

        # Contabilizar resultado
        winner = battle.get_winner()
        if winner == "A":
            wins_a += 1
        elif winner == "B":
            wins_b += 1
        else:
            draws += 1

        # Imprimir progreso periódicamente
        if episode % PRINT_EVERY == 0:
            print(f"\n{'='*60}")
            print(f"EPISODIO {episode}")
            print(f"{'='*60}")
            print(f"\nAcciones del episodio:")
            for log in battle.get_actions_log()[-10:]:  # Últimos 10 turnos
                print(f"  {log}")
            
            print(f"\nResultado: Ganador = {winner}")
            print(f"Marcador acumulado: A={wins_a} | B={wins_b} | Empates={draws}")
            
            # Winrate
            total = wins_a + wins_b + draws
            if total > 0:
                print(f"Winrate: A={100*wins_a/total:.1f}% | B={100*wins_b/total:.1f}%")

    # Resultados finales
    print("\n" + "=" * 60)
    print("RESULTADOS FINALES")
    print("=" * 60)
    print(f"\nVictorias Agente A: {wins_a}")
    print(f"Victorias Agente B: {wins_b}")
    print(f"Empates: {draws}")
    
    total = wins_a + wins_b + draws
    if total > 0:
        print(f"\nWinrate Final: A={100*wins_a/total:.1f}% | B={100*wins_b/total:.1f}%")

    # Mostrar tamaño de Q-tables
    print(f"\nEstados aprendidos Agente A: {len(agent_a.q_table)}")
    print(f"Estados aprendidos Agente B: {len(agent_b.q_table)}")

    # Mostrar algunos valores Q interesantes (top 10 por valor absoluto)
    print("\n" + "-" * 40)
    print("TOP 10 Q-VALUES (Agente A):")
    print("-" * 40)
    sorted_q_a = sorted(agent_a.q_table.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    for (state, action), value in sorted_q_a:
        print(f"  Estado {state}, Acción '{action}': {value:.2f}")

    print("\n" + "-" * 40)
    print("TOP 10 Q-VALUES (Agente B):")
    print("-" * 40)
    sorted_q_b = sorted(agent_b.q_table.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
    for (state, action), value in sorted_q_b:
        print(f"  Estado {state}, Acción '{action}': {value:.2f}")


if __name__ == "__main__":
    main()