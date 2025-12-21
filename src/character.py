"""
Funciones del personaje:

-Tiene vida (health) por default 100
-Puede atacar o defender tantas veces como quiera
-El ataque hace 10 de daño base, pero si el enemigo está defendiendo, hace la mitad
-Si defiendes, te quitan la mitad del daño Y ACUMULAS 5 DE DAÑO EXTRA PARA TU PRÓXIMO ATAQUE
-Por lo que puedes defender varias veces para acumular más daño, al atacar, se resetea el bonus (lo gastas)
"""

class Character:
    def __init__(self, name, health=100):
        self.name = name
        self.health = health
        self.is_defending = False
        self.attack_bonus = 0  

    def attack(self, enemy):
        damage = 10 + self.attack_bonus
        if enemy.is_defending:
            damage = damage // 2

        enemy.health = max(0, enemy.health - damage)
        self.attack_bonus = 0  # reset bonus después de atacar
        return damage

    def defend(self):
        self.is_defending = True
        self.attack_bonus += 5  # acumula daño para próximo ataque
        return True

    def reset_turn(self):
        self.is_defending = False

    def get_health(self):
        return self.health
