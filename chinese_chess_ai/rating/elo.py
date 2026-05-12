from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


DEFAULT_RATING = 1500
K_FACTOR = 32


@dataclass
class RatingChange:
    player_rating: int
    opponent_rating: int
    player_new_rating: int
    opponent_new_rating: int
    player_delta: int
    opponent_delta: int


class EloSystem:
    def __init__(self, k_factor: int = K_FACTOR, default_rating: int = DEFAULT_RATING) -> None:
        self.k_factor = k_factor
        self.default_rating = default_rating
        self._ratings: Dict[str, int] = {}

    def get_rating(self, player_id: str) -> int:
        return self._ratings.get(player_id, self.default_rating)

    def set_rating(self, player_id: str, rating: int) -> None:
        self._ratings[player_id] = rating

    @staticmethod
    def expected_score(rating_a: int, rating_b: int) -> float:
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))

    def update_rating(self, player_rating: int, opponent_rating: int, score: float) -> int:
        expected = self.expected_score(player_rating, opponent_rating)
        return round(player_rating + self.k_factor * (score - expected))

    def record_game(self, winner_id: str, loser_id: str) -> RatingChange:
        r_winner = self.get_rating(winner_id)
        r_loser = self.get_rating(loser_id)
        new_winner = self.update_rating(r_winner, r_loser, 1.0)
        new_loser = self.update_rating(r_loser, r_winner, 0.0)
        self._ratings[winner_id] = new_winner
        self._ratings[loser_id] = new_loser
        return RatingChange(
            player_rating=r_winner,
            opponent_rating=r_loser,
            player_new_rating=new_winner,
            opponent_new_rating=new_loser,
            player_delta=new_winner - r_winner,
            opponent_delta=new_loser - r_loser,
        )

    def record_draw(self, player_a_id: str, player_b_id: str) -> RatingChange:
        r_a = self.get_rating(player_a_id)
        r_b = self.get_rating(player_b_id)
        new_a = self.update_rating(r_a, r_b, 0.5)
        new_b = self.update_rating(r_b, r_a, 0.5)
        self._ratings[player_a_id] = new_a
        self._ratings[player_b_id] = new_b
        return RatingChange(
            player_rating=r_a,
            opponent_rating=r_b,
            player_new_rating=new_a,
            opponent_new_rating=new_b,
            player_delta=new_a - r_a,
            opponent_delta=new_b - r_b,
        )
