import pygame
import sys
from typing import Dict, List
from models.pokemon import Pokemon
from models.move import Move
from models.team import PokemonTeam
from battle.battle_engine import BattleEngine

# Inicialización de Pygame
pygame.init()
pygame.font.init()

# Configuración de la ventana
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pokémon Battle Simulator")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# Fuentes
title_font = pygame.font.SysFont('Arial', 48, bold=True)
main_font = pygame.font.SysFont('Arial', 32)
button_font = pygame.font.SysFont('Arial', 24)

class PyGameUI:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_state = "main_menu"
        self.battle_engine = None
        self.selected_move = None

    def show_main_menu(self):
        while self.current_state == "main_menu":
            self.screen.fill(WHITE)

            title_text = title_font.render("POKÉMON BATTLE SIMULATOR", True, BLUE)
            self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))

            new_game_btn = self.draw_button("New Battle", SCREEN_WIDTH//2, 300, 300, 60)
            instructions_btn = self.draw_button("Instructions", SCREEN_WIDTH//2, 400, 300, 60)
            quit_btn = self.draw_button("Exit", SCREEN_WIDTH//2, 500, 300, 60)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if new_game_btn.collidepoint(event.pos):
                        self.current_state = "team_builder"
                    elif instructions_btn.collidepoint(event.pos):
                        self.show_instructions_popup()
                    elif quit_btn.collidepoint(event.pos):
                        self.running = False
                        return

            self.clock.tick(60)

    def show_team_builder(self, api_client):
        team = PokemonTeam("Player's Team")
        input_text = ""
        input_active = True

        while self.current_state == "team_builder":
            self.screen.fill(WHITE)

            title_text = title_font.render("BUILD YOUR TEAM", True, BLUE)
            self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 50))

            team_text = main_font.render(f"Current Team: {', '.join(p.name for p in team.pokemon) or 'Empty'}", True, BLACK)
            self.screen.blit(team_text, (SCREEN_WIDTH//2 - team_text.get_width()//2, 150))

            input_box = pygame.Rect(SCREEN_WIDTH//2 - 200, 250, 400, 50)
            pygame.draw.rect(self.screen, GRAY if input_active else WHITE, input_box, 0)
            pygame.draw.rect(self.screen, BLACK, input_box, 2)

            text_surface = button_font.render(input_text, True, BLACK)
            self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 15))

            add_btn = self.draw_button("Add Pokemon", SCREEN_WIDTH//2, 350, 300, 60)
            done_btn = self.draw_button("Start Battle", SCREEN_WIDTH//2, 450, 300, 60)
            back_btn = self.draw_button("Back", SCREEN_WIDTH//2, 550, 300, 60)

            suggestions = button_font.render("Try: Pikachu, Charmander, Bulbasaur, Squirtle", True, BLACK)
            self.screen.blit(suggestions, (SCREEN_WIDTH//2 - suggestions.get_width()//2, 650))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        input_active = True
                    else:
                        input_active = False
                    if add_btn.collidepoint(event.pos) and input_text:
                        try:
                            pokemon = api_client.get_pokemon(input_text.lower())
                            if pokemon and len(team.pokemon) < 6:
                                team.add_pokemon(pokemon)
                                input_text = ""
                            else:
                                self.show_message("Invalid Pokémon or team full")
                        except Exception as e:
                            print(f"Error: {e}")
                    if done_btn.collidepoint(event.pos) and team.pokemon:
                        self.current_state = "battle"
                        return team
                    if back_btn.collidepoint(event.pos):
                        self.current_state = "main_menu"
                        return None
                if event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN:
                        if input_text:
                            try:
                                pokemon = api_client.get_pokemon(input_text.lower())
                                if pokemon and len(team.pokemon) < 6:
                                    team.add_pokemon(pokemon)
                                    input_text = ""
                            except Exception as e:
                                print(f"Error: {e}")
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            self.clock.tick(60)

    def show_battle(self, battle_engine: BattleEngine):
        self.battle_engine = battle_engine
        self.selected_move = None

        while self.current_state == "battle" and self.running:
            status = battle_engine.get_battle_status()
            self.screen.fill(WHITE)
            self.draw_battle_status(status)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if status["player_pokemon"].current_hp > 0:
                        for i, button in enumerate(self.move_buttons):
                            if button.collidepoint(event.pos):
                                self.selected_move = str(i + 1)
                                return
                    for i, button in enumerate(self.team_buttons):
                        if button.collidepoint(event.pos):
                            member = status["player_team"]["members"][i]
                            if not member["fainted"] and i != status["player_team"]["active_index"]:
                                self.selected_move = f"switch {i}"
                                return

            pygame.display.flip()
            self.clock.tick(60)

    def draw_battle_status(self, status: Dict):
        player_pokemon = status["player_pokemon"]
        ai_pokemon = status["ai_pokemon"]

        opponent_text = main_font.render(f"Opponent: {ai_pokemon.name}", True, BLACK)
        self.screen.blit(opponent_text, (50, 50))
        self.draw_hp_bar(ai_pokemon, 50, 100)

        player_text = main_font.render(f"Your: {player_pokemon.name}", True, BLACK)
        self.screen.blit(player_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT - 200))
        self.draw_hp_bar(player_pokemon, SCREEN_WIDTH - 450, SCREEN_HEIGHT - 150)

        if player_pokemon.current_hp > 0:
            move_text = main_font.render("Select a move:", True, BLACK)
            self.screen.blit(move_text, (50, SCREEN_HEIGHT - 200))

            self.move_buttons = []
            for i, move in enumerate(player_pokemon.moves):
                btn = self.draw_button(
                    f"{i+1}. {move.name} (PP: {move.current_pp}/{move.max_pp})",
                    200 + (i % 2) * 400,
                    SCREEN_HEIGHT - 150 + (i // 2) * 60,
                    350, 50
                )
                self.move_buttons.append(btn)

        team_text = main_font.render("Your Team:", True, BLACK)
        self.screen.blit(team_text, (SCREEN_WIDTH - 300, 50))

        self.team_buttons = []
        for i, member in enumerate(status["player_team"]["members"]):
            status_text = "FAINTED" if member["fainted"] else f"HP: {member['hp']}/{member['max_hp']}"
            btn = self.draw_button(
                f"{i+1}. {member['name']} - {status_text}",
                SCREEN_WIDTH - 200,
                100 + i * 60,
                300, 50,
                RED if member["fainted"] else GREEN
            )
            self.team_buttons.append(btn)

    def draw_hp_bar(self, pokemon: Pokemon, x: int, y: int):
        hp_percent = pokemon.current_hp / pokemon.stats["hp"]
        bar_width = 400 * hp_percent

        pygame.draw.rect(self.screen, RED, (x, y, 400, 30))
        pygame.draw.rect(self.screen, GREEN, (x, y, bar_width, 30))
        pygame.draw.rect(self.screen, BLACK, (x, y, 400, 30), 2)

        hp_text = button_font.render(f"{pokemon.current_hp}/{pokemon.stats['hp']}", True, BLACK)
        self.screen.blit(hp_text, (x + 200 - hp_text.get_width()//2, y + 5))

    def draw_button(self, text, x, y, width, height, color=BLUE):
        button_rect = pygame.Rect(x - width//2, y - height//2, width, height)
        pygame.draw.rect(self.screen, color, button_rect)
        pygame.draw.rect(self.screen, BLACK, button_rect, 2)

        text_surface = button_font.render(text, True, WHITE if color != YELLOW else BLACK)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

        return button_rect

    def show_instructions_popup(self):
        instructions = [
            "HOW TO PLAY:",
            "1. Build your team with 1-6 Pokémon",
            "2. Battle against an AI opponent",
            "3. During battle:",
            "   - Select moves by clicking buttons",
            "   - Switch Pokémon when needed",
            "4. Defeat all opponent Pokémon to win!"
        ]
        popup_width = 600
        popup_height = 400

        while True:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(180)
            s.fill(BLACK)
            self.screen.blit(s, (0, 0))

            popup_rect = pygame.Rect(
                SCREEN_WIDTH//2 - popup_width//2,
                SCREEN_HEIGHT//2 - popup_height//2,
                popup_width,
                popup_height
            )
            pygame.draw.rect(self.screen, WHITE, popup_rect)
            pygame.draw.rect(self.screen, BLUE, popup_rect, 3)

            for i, line in enumerate(instructions):
                text = button_font.render(line, True, BLACK)
                self.screen.blit(text, (
                    SCREEN_WIDTH//2 - text.get_width()//2,
                    SCREEN_HEIGHT//2 - popup_height//2 + 50 + i * 40
                ))

            ok_btn = self.draw_button("OK", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + popup_height//2 - 50, 200, 50)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ok_btn.collidepoint(event.pos):
                        return

            self.clock.tick(60)

    def show_message(self, message):
        popup_width = 500
        popup_height = 150
        while True:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(200)
            s.fill(BLACK)
            self.screen.blit(s, (0, 0))

            popup_rect = pygame.Rect(
                SCREEN_WIDTH//2 - popup_width//2,
                SCREEN_HEIGHT//2 - popup_height//2,
                popup_width,
                popup_height
            )
            pygame.draw.rect(self.screen, WHITE, popup_rect)
            pygame.draw.rect(self.screen, BLUE, popup_rect, 3)

            msg_text = main_font.render(message, True, BLACK)
            self.screen.blit(msg_text, (SCREEN_WIDTH//2 - msg_text.get_width()//2, SCREEN_HEIGHT//2 - 30))

            ok_btn = self.draw_button("OK", SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40, 100, 40)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if ok_btn.collidepoint(event.pos):
                        return

            self.clock.tick(60)
