import random
from typing import Callable

from model.actions import Action
from model.cards import Card
from model.game_info import GameInfo, Winner
from model.state import State, BUST
from model.strategy import Strategy


class Deck:
    def __init__(self):
        self._deck = list(Card)

    def get_next_card(self) -> Card:
        return random.choice(self._deck)


class Game:
    def __init__(self, player_strategy: Strategy, dealer_strategy: Strategy, deck: Deck):
        self._player_strategy = player_strategy
        self._dealer_strategy = dealer_strategy
        self._deck = deck

    def _play_stage(self, initial_state: State, strategy: Strategy, log_action: Callable) -> State:
        taken_action = None
        state = initial_state

        while taken_action != Action.STICK and state != BUST:
            log_action(state)
            taken_action = strategy.make_decision_in(state)
            if taken_action == Action.HIT:
                state = state.move_with(self._deck.get_next_card())

        return state

    def play(self) -> GameInfo:
        game_info = GameInfo()

        player_cards = (self._deck.get_next_card(), self._deck.get_next_card())
        dealer_cards = (self._deck.get_next_card(), self._deck.get_next_card())

        player_state = self._play_stage(initial_state=State.from_deal(*player_cards, dealer_cards[0]),
                                        strategy=self._player_strategy,
                                        log_action=game_info.log_player)

        if player_state == BUST:
            game_info.set_winner(Winner.DEALER)
            return game_info

        dealer_state = self._play_stage(initial_state=State.from_deal(*dealer_cards, player_state.current_sum),
                                        strategy=self._dealer_strategy,
                                        log_action=game_info.log_dealer)

        if dealer_state == BUST:
            game_info.set_winner(Winner.PLAYER)
            return game_info

        if player_state.current_sum > dealer_state.current_sum:
            game_info.set_winner(Winner.PLAYER)
        elif player_state.current_sum == dealer_state.current_sum:
            game_info.set_winner(Winner.DRAW)
        else:
            game_info.set_winner(Winner.DEALER)

        return game_info