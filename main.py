import pygame
import sys
import random
import os

# Inicialización de Pygame
pygame.init()

# Configuraciones de pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Aventuras de Ciclista RPG")

# Configuración de rutas de assets
ASSETS_PATH = "assets/images/"

# Cargar imágenes con manejo de errores
def load_image(filename, size=None):
    try:
        image = pygame.image.load(os.path.join(ASSETS_PATH, filename)).convert_alpha()
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"No se pudo cargar la imagen {filename}: {e}")
        return pygame.Surface((50, 50), pygame.SRCALPHA)

# Clase del Ciclista
class Cyclist(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Cargar imagen del ciclista
        self.images = {
            'down': load_image('cyclist.png', (50, 50)),
            'up': load_image('cyclist.png', (50, 50)),
            'left': load_image('cyclist.png', (50, 50)),
            'right': load_image('cyclist.png', (50, 50))
        }
        self.image = self.images['down']
        self.rect = self.image.get_rect()
        
        # Estadísticas del ciclista
        self.energy = 100
        self.stamina = 100
        self.level = 1
        self.experience = 0
        self.coins = 0
        self.inventory = []

    def reset_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def move(self, dx, dy):
        # Reducir energía al moverse
        self.energy -= 0.5
        self.rect.x += dx * 5
        self.rect.y += dy * 5
        
        # Cambiar imagen según dirección
        if dx > 0:
            self.image = self.images['right']
        elif dx < 0:
            self.image = self.images['left']
        elif dy > 0:
            self.image = self.images['down']
        elif dy < 0:
            self.image = self.images['up']
        
        # Mantener al ciclista dentro de la pantalla
        self.rect.clamp_ip(screen.get_rect())

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= 100:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience = 0
        self.stamina += 10
        self.energy = min(self.energy + 20, 100)
        print(f"¡Nivel subido! Ahora eres nivel {self.level}")

    def add_to_inventory(self, item):
        self.inventory.append(item)
        print(f"Has recogido: {item}")

# Clase base de Obstáculos
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image_filename, obstacle_type):
        super().__init__()
        self.image = load_image(image_filename, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = obstacle_type

# Tipos específicos de Obstáculos
class Rock(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, 'rock.png', "rock")
        self.damage = 10

class EnergyBoost(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, 'energy_boost.png', "energy_boost")
        self.energy_amount = 20

class Coin(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, 'coin.png', "coin")
        self.value = 5

class SpecialItem(Obstacle):
    def __init__(self, x, y):
        super().__init__(x, y, 'special_item.png', "special_item")
        self.item_name = random.choice(["Casco Legendario", "Rueda Mágica", "Mapa de Atajos"])

# Clase de Nivel
class GameLevel:
    def __init__(self, background_image, start_pos, goal_pos, obstacles_config):
        self.background = load_image(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.goal = pygame.Rect(goal_pos[0], goal_pos[1], 50, 50)
        self.obstacles_config = obstacles_config
        self.obstacles = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

    def create_obstacles(self, cyclist):
        # Limpiar obstáculos anteriores
        self.obstacles.empty()
        self.all_sprites.empty()
        self.all_sprites.add(cyclist)

        # Crear obstáculos según la configuración
        for obstacle_class, count in self.obstacles_config:
            for _ in range(count):
                x = random.randint(0, SCREEN_WIDTH - 30)
                y = random.randint(0, SCREEN_HEIGHT - 30)
                obstacle = obstacle_class(x, y)
                self.obstacles.add(obstacle)
                self.all_sprites.add(obstacle)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.all_sprites.draw(screen)
        
        # Dibujar punto de meta
        pygame.draw.rect(screen, (0, 255, 0), self.goal)

# Configuración del juego
def main():
    clock = pygame.time.Clock()
    
    # Crear ciclista
    cyclist = Cyclist()

    # Definir niveles
    levels = [
        GameLevel(
            'background_level1.png', 
            (100, 100),  # Posición inicial
            (700, 500),  # Posición de meta
            [
                (Rock, 3),      
                (EnergyBoost, 2), 
                (Coin, 5),      
                (SpecialItem, 1)   
            ]
        ),
        GameLevel(
            'background_level2.png', 
            (50, 50),  # Posición inicial
            (750, 550),  # Posición de meta
            [
                (Rock, 5),      
                (EnergyBoost, 3), 
                (Coin, 7),      
                (SpecialItem, 2)   
            ]
        ),
        # Puedes añadir más niveles aquí
    ]

    # Variables de estado del juego
    current_level_index = 0
    current_level = levels[current_level_index]
    
    # Colocar ciclista en posición inicial
    cyclist.reset_position(*current_level.start_pos)
    current_level.create_obstacles(cyclist)

    # Bucle principal del juego
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Entrada de teclado para movimiento
        keys = pygame.key.get_pressed()
        movement = [0, 0]
        if keys[pygame.K_LEFT]:
            movement[0] -= 1
        if keys[pygame.K_RIGHT]:
            movement[0] += 1
        if keys[pygame.K_UP]:
            movement[1] -= 1
        if keys[pygame.K_DOWN]:
            movement[1] += 1
        
        if any(movement):
            cyclist.move(movement[0], movement[1])

        # Detección de colisiones con obstáculos
        hits = pygame.sprite.spritecollide(cyclist, current_level.obstacles, True)
        for hit in hits:
            if hit.type == "rock":
                cyclist.energy -= hit.damage
                print(f"¡Chocaste con una roca! Pierdes {hit.damage} de energía")
            
            elif hit.type == "energy_boost":
                cyclist.energy = min(cyclist.energy + hit.energy_amount, 100)
                print(f"¡Boost de energía! Recuperas {hit.energy_amount} de energía")
            
            elif hit.type == "coin":
                cyclist.coins += hit.value
                cyclist.gain_experience(5)
                print(f"¡Moneda recogida! +{hit.value} monedas")
            
            elif hit.type == "special_item":
                cyclist.add_to_inventory(hit.item_name)
                cyclist.gain_experience(20)

        # Comprobar si se alcanza la meta
        if current_level.goal.colliderect(cyclist.rect):
            current_level_index += 1
            
            # Comprobar si se han completado todos los niveles
            if current_level_index >= len(levels):
                print("¡Felicidades! Has completado todos los niveles.")
                running = False
                break
            
            # Cambiar al siguiente nivel
            current_level = levels[current_level_index]
            cyclist.reset_position(*current_level.start_pos)
            current_level.create_obstacles(cyclist)
            
            print(f"¡Nivel {current_level_index} completado!")

        # Dibujar
        current_level.draw(screen)
        
        # Mostrar estadísticas
        font = pygame.font.Font(None, 36)
        stats_text = f"Nivel: {cyclist.level} | Energía: {int(cyclist.energy)} | Exp: {cyclist.experience} | Monedas: {cyclist.coins} | Nivel del Juego: {current_level_index + 1}"
        text_surface = font.render(stats_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        # Actualizar pantalla
        pygame.display.flip()
        
        # Controlar FPS
        clock.tick(60)

        # Condición de fin de juego (sin energía)
        if cyclist.energy <= 0:
            print("¡Juego terminado! Te has quedado sin energía.")
            print(f"Estadísticas finales:")
            print(f"Nivel: {cyclist.level}")
            print(f"Monedas: {cyclist.coins}")
            print(f"Inventario: {cyclist.inventory}")
            running = False

    # Cerrar Pygame
    pygame.quit()
    sys.exit()

# Ejecutar el juego
if __name__ == "__main__":
    main()