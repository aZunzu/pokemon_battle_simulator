"""
PokeAPI client for the Pokemon Battle Simulator
"""
from typing import Optional

import requests
from models.pokemon import Pokemon
from models.move import Move

class PokeAPIClient:
    """Client for fetching Pokemon data from PokeAPI."""

    BASE_URL = "https://pokeapi.co/api/v2/"

    def get_pokemon(self, name: str) -> Pokemon:
        """Get a Pokemon by name."""
        response = requests.get(f"{self.BASE_URL}pokemon/{name.lower()}")
        response.raise_for_status()
        data = response.json()

        # Get moves (limit to 4)
        moves = []
        for move_data in data["moves"][:4]:
            move = self.get_move(move_data["move"]["name"])
            if move:
                moves.append(move)

        # Create Pokemon
        pokemon = Pokemon(
            id=data["id"],
            name=data["name"],
            types=[t["type"]["name"] for t in data["types"]],
            stats={s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            moves=moves,
            sprite_url=data["sprites"]["front_default"]
        )
        return pokemon

    def get_move(self, name: str) -> Optional[Move]:
        """Get a move by name."""
        try:
            response = requests.get(f"{self.BASE_URL}move/{name.lower()}")
            response.raise_for_status()
            data = response.json()

            return Move(
                id=data["id"],
                name=data["name"],
                type_=data["type"]["name"],
                category=data["damage_class"]["name"],
                power=data["power"],
                accuracy=data["accuracy"],
                pp=data["pp"]
            )
        except:
            return None