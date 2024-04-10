from otree.api import *
import random

doc = """
Voting Game
"""

class C(BaseConstants):
    NAME_IN_URL = 'Voting'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    AMOUNT_SHARED_IF_A = 15  # Amount shared if option A wins
    AMOUNT_SHARED_IF_B = 2   # Amount shared if option B wins
    CHOICES = ['A', 'B']
    STATES = ['A', 'B']
    QUALITIES = ['h', 'l']

class Subsession(BaseSubsession):

    def creating_session(self):
        self.group_randomly()

class Group(BaseGroup):
    state = models.StringField()

    def set_payoffs(self):
        votes = [p.vote for p in self.get_players()]
        majority_vote = self.state
        majority_vote_count = votes.count(majority_vote)

        if majority_vote_count > len(votes) / 2:
            payoff = C.AMOUNT_SHARED_IF_A
        else:
            payoff = C.AMOUNT_SHARED_IF_B

        for p in self.get_players():
            p.payoff = payoff
            p.majority_vote_count = majority_vote_count

class Player(BasePlayer):
    vote = models.StringField(choices=C.CHOICES, label="Please choose A or B")
    state = models.StringField()
    qualities = models.StringField()
    signals = models.CharField()
    majority_vote_count = models.IntegerField()
    def chat_nickname(self):
        return 'Voter {}'.format(self.id_in_group)

    def chat_room(self):
        if self.id_in_group in [1, 3]:
            return '{}-{}'.format(C.NAME_IN_URL, self.group.pk)
        return None

class StartRoundWaitPage(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def after_all_players_arrive(subsession):
        subsession.group_randomly()
        for group in subsession.get_groups():
            chosen_state = random.choice(C.STATES)
            group.state = chosen_state
            for player in group.get_players():
                player.state = chosen_state

                qualities = random.choice(C.QUALITIES)
                player.qualities = qualities

                if player.state == 'A':
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 5 / 8 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 4 / 7 else 'b'
                else:  # 'B'
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 3 / 8 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 3 / 7 else 'b'


class Welcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class General_Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Main_Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1




class Info(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            quality=player.qualities,
            signal=player.signals
        )



class Chat(Page):

    @staticmethod
    def vars_for_template(player):
        return dict(
            state=player.state,
            quality=player.qualities,
            signal=player.signals
        )
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

page_sequence = [StartRoundWaitPage, Welcome, General_Instructions, Main_Instructions, Info, Chat, Voting, ResultsWaitPage, Results]
