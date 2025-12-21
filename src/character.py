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
        self.cooldown = 3

    def attack(self, enemy):
        damage = 20

        if enemy.is_defending:

            damage = damage // 2
            damage = (damage // 10) * 10


        enemy.health = max(0, enemy.health - damage)

        self.cooldown -= 1
        return damage

    def super_attack(self, enemy):
        damage = 40

        if enemy.is_defending:
            damage = damage // 2
            damage = (damage // 10) * 10

        enemy.health = max(0, enemy.health - damage)
        self.cooldown = 3

        return damage   

    def defend(self):

        self.cooldown -= 1
        self.is_defending = True
        return True

    def reset_turn(self):
        self.is_defending = False

    def get_health(self):
        return self.health
    
    def get_cooldown(self):
        return self.cooldown