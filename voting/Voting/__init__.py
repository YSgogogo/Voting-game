from otree.api import *

doc = """
Voting Game
"""

class C(BaseConstants):
    NAME_IN_URL = 'Voting'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    AMOUNT_SHARED_IF_A = cu(100)  # Amount shared if option A wins
    AMOUNT_SHARED_IF_B = cu(20)   # Amount shared if option B wins
    CHOICES = ['A', 'B']  # Voting options

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    def set_payoffs(self):
        votes = [p.vote for p in self.get_players()]
        if votes.count('A') >= 2:
            payoff = C.AMOUNT_SHARED_IF_A
        else:
            payoff = C.AMOUNT_SHARED_IF_B
        for p in self.get_players():
            p.payoff = payoff

class Player(BasePlayer):
    vote = models.StringField(choices=C.CHOICES, label="Please choose A or B")

    def chat_nickname(self):
        return 'Voter {}'.format(self.id_in_group)

    def chat_room(self):
        if self.id_in_group in [1, 3]:
            return '{}-{}'.format(C.NAME_IN_URL, self.group.pk)
        return None

# PAGES
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

page_sequence = [Chat, Voting, ResultsWaitPage, Results]
