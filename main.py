import pygame
import sys
import random
import os
import json

# Inicialización de Pygame
pygame.init()

# Configuraciones de pantalla
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bikepacking adventures RPG")

# Configuración de rutas
ASSETS_PATH = "assets/images/"
SAVE_FILE = "save_game.json"

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, image_filename, obstacle_type):
        super().__init__()
        self.image = load_image(image_filename, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = obstacle_type
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

# Clase de Gestión de Guardado
class SaveManager:
    @staticmethod
    def save_game(cyclist, current_level_index):
        """Guardar el progreso del juego"""
        save_data = {
            "cyclist": {
                "energy": cyclist.energy,
                "stamina": cyclist.stamina,
                "level": cyclist.level,
                "experience": cyclist.experience,
                "coins": cyclist.coins,
                "inventory": cyclist.inventory,
                "position": list(cyclist.rect.topleft)
            },
            "current_level_index": current_level_index
        }
        
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(save_data, f)
            print("Juego guardado exitosamente.")
            return True
        except Exception as e:
            print(f"Error al guardar el juego: {e}")
            return False

    @staticmethod
    def load_game():
        """Cargar el progreso del juego"""
        try:
            if not os.path.exists(SAVE_FILE):
                return None
            
            with open(SAVE_FILE, 'r') as f:
                save_data = json.load(f)
            print("Juego cargado exitosamente.")
            return save_data
        except Exception as e:
            print(f"Error al cargar el juego: {e}")
            return None

    @staticmethod
    def delete_save():
        """Eliminar archivo de guardado"""
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
                print("Archivo de guardado eliminado.")
        except Exception as e:
            print(f"Error al eliminar el archivo de guardado: {e}")

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

class Cyclist(pygame.sprite.Sprite):
    def __init__(self, load_data=None):
        super().__init__()
        
        self.images = {
            'down': load_image('cyclist.png', (50, 50)),
            'up': load_image('cyclist.png', (50, 50)),
            'left': load_image('cyclist.png', (50, 50)),
            'right': load_image('cyclist.png', (50, 50))
        }
        self.image = self.images['down']
        self.rect = self.image.get_rect()

        # Inicializar o cargar estadísticas
        if load_data:
            # Cargar datos guardados
            cyclist_data = load_data.get('cyclist', {})
            self.energy = cyclist_data.get('energy', 100)
            self.stamina = cyclist_data.get('stamina', 100)
            self.level = cyclist_data.get('level', 1)
            self.experience = cyclist_data.get('experience', 0)
            self.coins = cyclist_data.get('coins', 0)
            self.inventory = cyclist_data.get('inventory', [])
            
            # Establecer posición guardada
            start_pos = cyclist_data.get('position', [100, 100])
            self.rect.topleft = start_pos
        else:
            # Valores por defecto
            self.energy = 100
            self.stamina = 100
            self.level = 1
            self.experience = 0
            self.coins = 0
            self.inventory = []
            self.rect.topleft = (100, 100)

    def reset_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    # Resto de métodos igual que en la versión anterior
    def move(self, dx, dy):
        self.energy -= 0.5
        self.rect.x += dx * 5
        self.rect.y += dy * 5
        
        if dx > 0:
            self.image = self.images['right']
        elif dx < 0:
            self.image = self.images['left']
        elif dy > 0:
            self.image = self.images['down']
        elif dy < 0:
            self.image = self.images['up']
        
        self.rect.clamp_ip(screen.get_rect())

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= 10:
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


# Menú de Inicio
def start_menu():
    menu_font = pygame.font.Font(None, 50)
    
    # Títulos de las opciones
    new_game_text = menu_font.render("Nuevo Juego", True, (255, 255, 255))
    continue_game_text = menu_font.render("Continuar Juego", True, (255, 255, 255))
    quit_text = menu_font.render("Salir", True, (255, 255, 255))

    # Posiciones de los textos
    new_game_rect = new_game_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    continue_game_rect = continue_game_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))

    # Bucle del menú
    menu_running = True
    while menu_running:
        screen.fill((0, 0, 0))  # Fondo negro
        
        # Dibujar textos
        screen.blit(new_game_text, new_game_rect)
        screen.blit(continue_game_text, continue_game_rect)
        screen.blit(quit_text, quit_rect)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if new_game_rect.collidepoint(mouse_pos):
                    # Eliminar guardado anterior si existe
                    SaveManager.delete_save()
                    return None
                
                if continue_game_rect.collidepoint(mouse_pos):
                    # Intentar cargar juego guardado
                    saved_game = SaveManager.load_game()
                    return saved_game
                
                if quit_rect.collidepoint(mouse_pos):
                    return False

    return None

# Configuración del juego
def main():
    clock = pygame.time.Clock()
    
    # Mostrar menú de inicio
    start_result = start_menu()
    if start_result is False:
        pygame.quit()
        sys.exit()

    # Crear ciclista (con datos guardados o nuevo)
    cyclist = Cyclist(start_result)

    # Definir niveles (igual que en la versión anterior)
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
    ]

    # Variables de estado del juego
    current_level_index = start_result['current_level_index'] if start_result else 0
    current_level = levels[current_level_index]
    
    # Colocar ciclista en posición inicial
    cyclist.reset_position(*current_level.start_pos)
    current_level.create_obstacles(cyclist)

    # Variables de guardado automático
    last_save_time = pygame.time.get_ticks()
    AUTOSAVE_INTERVAL = 10000  # 10 segundos

    # Bucle principal del juego
    running = True
    while running:
        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Guardar antes de salir
                SaveManager.save_game(cyclist, current_level_index)
                running = False
            
            # Guardar con tecla de método abreviado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F5:
                    SaveManager.save_game(cyclist, current_level_index)

        # Autosave cada cierto tiempo
        current_time = pygame.time.get_ticks()
        if current_time - last_save_time > AUTOSAVE_INTERVAL:
            SaveManager.save_game(cyclist, current_level_index)
            last_save_time = current_time

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