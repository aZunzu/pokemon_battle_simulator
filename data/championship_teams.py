"""
Championship teams for the Pokemon Battle Simulator
"""
import random
from models.team import PokemonTeam
from data.pokeapi import PokeAPIClient

class ChampionshipTeams:
    """Collection of pre-made teams for the AI to use."""

    def __init__(self, api_client: PokeAPIClient):
        """Initialize with an API client."""
        self.api_client = api_client
        self.teams = []

    def load_teams(self):
        """Load championship teams."""
        # This would be expanded with actual championship teams
        team_names = [
            ["Landorus-Therian", "amoonguss", "politoed", "aegislash-blade", "thundurus-Incarnate", "gardevoir"],
            ["gardevoir", "amoonguss", "heatran", "scrafty", "thundurus-Incarnate", "Landorus-Therian"],
            ["rotom-wash", "Landorus-Therian", "amoonguss", "salamence", "tyranitar", "aegislash-blade"],
            ["charizard", "conkeldurr", "sylveon", "aegislash-blade", "Landorus-Therian", "thundurus-Incarnate"],
            ["kangaskhan", "heatran", "Landorus-Therian", "thundurus-Incarnate", "amoonguss", "milotic"],
            ["excadrill", "gastrodon", "cresselia", "salamence", "rotom-heat", "tyranitar"],
            ["magikarp", "reshiram", "lugia", "rayquaza", "mewtwo", "arceus"]
        ]

        for names in team_names:
            team = PokemonTeam("Champion Team")
            for name in names:
                pokemon = self.api_client.get_pokemon(name)
                team.add_pokemon(pokemon)
            self.teams.append(team)

    def get_random_team(self) -> PokemonTeam:
        """Get a random championship team."""
        if not self.teams:
            self.load_teams()
        return random.choice(self.teams)