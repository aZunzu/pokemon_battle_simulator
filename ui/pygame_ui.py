import pygame
import sys
from typing import Dict
from models.pokemon import Pokemon

class PyGameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pokémon Battle Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)

        # Colores
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)

        # Sprites básicos (usaremos rectángulos + texto)
        self.player_sprite = pygame.Rect(100, 400, 100, 100)
        self.enemy_sprite = pygame.Rect(600, 100, 100, 100)

    def show_main_menu(self):
        running = True
        while running:
            self.screen.fill(self.WHITE)

            title = self.font.render("POKÉMON BATTLE SIMULATOR", True, self.BLUE)
            self.screen.blit(title, (200, 100))

            start_btn = pygame.Rect(300, 250, 200, 50)
            pygame.draw.rect(self.screen, self.GREEN, start_btn)
            start_text = self.font.render("Start Battle", True, self.BLACK)
            self.screen.blit(start_text, (350, 265))

            quit_btn = pygame.Rect(300, 350, 200, 50)
            pygame.draw.rect(self.screen, self.RED, quit_btn)
            quit_text = self.font.render("Quit", True, self.WHITE)
            self.screen.blit(quit_text, (375, 365))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_btn.collidepoint(event.pos):
                        return "start"
                    if quit_btn.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            self.clock.tick(60)

    def show_battle(self, player_pokemon: Pokemon, enemy_pokemon: Pokemon):
        running = True
        while running:
            self.screen.fill(self.WHITE)

            # Dibuja Pokémon del jugador
            pygame.draw.rect(self.screen, self.BLUE, self.player_sprite)
            player_text = self.font.render(player_pokemon.name, True, self.BLACK)
            self.screen.blit(player_text, (100, 380))

            # Dibuja Pokémon enemigo
            pygame.draw.rect(self.screen, self.RED, self.enemy_sprite)
            enemy_text = self.font.render(enemy_pokemon.name, True, self.BLACK)
            self.screen.blit(enemy_text, (600, 80))

            # Barra de HP
            self.draw_hp_bar(player_pokemon, 100, 520)
            self.draw_hp_bar(enemy_pokemon, 600, 220)

            # Movimientos
            for i, move in enumerate(player_pokemon.moves[:4]):
                move_btn = pygame.Rect(400, 400 + i*60, 200, 50)
                pygame.draw.rect(self.screen, self.GREEN, move_btn, 2)
                move_text = self.font.render(f"{i+1}. {move.name}", True, self.BLACK)
                self.screen.blit(move_text, (410, 415 + i*60))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(4):
                        if pygame.Rect(400, 400 + i*60, 200, 50).collidepoint(event.pos):
                            return i  # Devuelve el índice del movimiento seleccionado

            self.clock.tick(60)

    def draw_hp_bar(self, pokemon: Pokemon, x: int, y: int):
        hp_percent = pokemon.current_hp / pokemon.stats["hp"]
        bar_width = 200 * hp_percent
        pygame.draw.rect(self.screen, self.RED, (x, y, 200, 20))
        pygame.draw.rect(self.screen, self.GREEN, (x, y, bar_width, 20))
        hp_text = self.font.render(f"HP: {pokemon.current_hp}/{pokemon.stats['hp']}", True, self.BLACK)
        self.screen.blit(hp_text, (x, y + 25))