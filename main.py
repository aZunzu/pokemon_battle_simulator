from ui.pygame_ui import PyGameUI
from data.pokeapi import PokeAPIClient
from data.championship_teams import ChampionshipTeams
from battle.battle_engine import BattleEngine

def main():
    ui = PyGameUI()
    api_client = PokeAPIClient()
    teams_data = ChampionshipTeams(api_client)

    while ui.running:
        if ui.current_state == "main_menu":
            ui.show_main_menu()
        elif ui.current_state == "team_builder":
            player_team = ui.show_team_builder(api_client)
            if player_team:
                ai_team = teams_data.get_random_team()
                battle = BattleEngine(player_team, ai_team)
                ui.current_state = "battle"
        elif ui.current_state == "battle":
            ui.show_battle(battle)
            if ui.selected_move:
                battle.process_turn(ui.selected_move)
                ui.selected_move = None

if __name__ == "__main__":
    main()