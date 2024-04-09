from otree.api import *
import random

doc = """
Voting Game
"""

class C(BaseConstants):
    NAME_IN_URL = 'Voting'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    AMOUNT_SHARED_IF_A = cu(100)
    AMOUNT_SHARED_IF_B = cu(20)
    CHOICES = ['A', 'B']
    STATES = ['A', 'B']
    CATEGORIES = ['h', 'l']
    REWARDS = ['r', 'b']


class Subsession(BaseSubsession):
    def creating_session(self):
        for group in self.get_groups():
            group.state = random.choice(C.STATES)


class Group(BaseGroup):
    state = models.StringField()

    def set_categories_and_rewards(self):
        for player in self.get_players():
            player.category = random.choice(C.CATEGORIES)
            # A状态下的分配
            if self.state == 'A':
                if player.category == 'h':
                    player.reward = random.choices(C.REWARDS, weights=(5, 3), k=1)[0]
                else:
                    player.reward = random.choices(C.REWARDS, weights=(4, 3), k=1)[0]
            # B状态下的分配
            else:
                if player.category == 'h':
                    player.reward = random.choices(C.REWARDS, weights=(3, 5), k=1)[0]
                else:
                    player.reward = random.choices(C.REWARDS, weights=(3, 4), k=1)[0]

    def set_payoffs(self):
        # 根据状态投票的结果分配payoff
        votes = [p.vote for p in self.get_players()]
        if self.state == 'A' and votes.count('A') >= 2 or self.state == 'B' and votes.count('B') >= 2:
            payoff = C.AMOUNT_SHARED_IF_A
        else:
            payoff = C.AMOUNT_SHARED_IF_B
        for p in self.get_players():
            p.payoff = payoff


class Player(BasePlayer):
    vote = models.StringField(choices=C.CHOICES, label="Please choose A or B")
    category = models.StringField()
    reward = models.StringField()

class Info(Page):

    @staticmethod
    def vars_for_template(player: Player):
        return {
            'state': player.group.state,
            'category': player.category,
            'reward': player.reward
        }


class Chat(Page):
    @staticmethod
    def is_displayed(player):
        return player.id_in_group in [1, 3]
    timeout_seconds = 120

class Voting(Page):
    form_model = 'player'
    form_fields = ['vote']

class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()

class Results(Page):
    pass

page_sequence = [Info, Chat, Voting, ResultsWaitPage, Results]