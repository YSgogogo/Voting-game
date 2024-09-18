from otree.api import *
import random
import json


doc = """
Voting_real_treatment_2
"""


class C(BaseConstants):
    NAME_IN_URL = 'Voting_real_treatment_2'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 15
    AMOUNT_SHARED_IF_WIN = 15
    AMOUNT_SHARED_IF_LOSE = 2
    QUESTIONS = [
        ('cat', 'CAT'),
        ('dog', 'DOG')
    ]
    CHOICES = [
        ('R', 'RED Box'),
        ('B', 'BLUE Box')
    ]
    STATES = ['R', 'B']
    QUALITIES = ['h', 'l']
    MAJORITY_C_4 = ['send to a player who chose CAT', 'send to a player who chose DOG', 'do not send to anyone']
    MAJORITY_D_4 = ['send to a player who chose DOG', 'send to a player who chose CAT', 'do not send to anyone']
    MAJORITY_C_3 = ['send to a player who chose CAT', 'send to a player who chose DOG', 'do not send to anyone']
    MAJORITY_D_3 = ['send to a player who chose DOG', 'send to a player who chose CAT', 'do not send to anyone']
    MINORITY_C_1 = ['send to a player who chose DOG', 'do not send to anyone']
    MINORITY_D_1 = ['send to a player who chose CAT', 'do not send to anyone']
    MINORITY_C_2 = ['send to a player who chose CAT', 'send to a player who chose DOG', 'do not send to anyone']
    MINORITY_D_2 = ['send to a player who chose DOG', 'send to a player who chose CAT', 'do not send to anyone']
    ALL_C = ['send to a player who chose DOG', 'do not send to anyone']
    ALL_D = ['send to a player who chose CAT', 'do not send to anyone']


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()


class Group(BaseGroup):
    state = models.StringField()
    D_count = models.IntegerField(initial=0)
    C_count = models.IntegerField(initial=0)
    chosen_player_id = models.IntegerField()
    chosen_player_vote = models.StringField()
    def set_payoffs(self):
        chosen_player = random.choice(self.get_players())
        self.chosen_player_id = chosen_player.id_in_group
        self.chosen_player_vote = chosen_player.vote
        if chosen_player.vote == self.state:
            payoff = C.AMOUNT_SHARED_IF_WIN
        else:
            payoff = C.AMOUNT_SHARED_IF_LOSE
        for p in self.get_players():
            p.payoff = payoff

    def calculate_signals(self):
        D_count = 0
        C_count = 0
        for p in self.get_players():
            if p.question == 'cat':
                C_count += 1
            elif p.question == 'dog':
                D_count += 1
        self.D_count = D_count
        self.C_count = C_count


class Player(BasePlayer):
    timeSpent0 = models.FloatField()
    timeSpent1 = models.FloatField()
    timeSpent2 = models.FloatField()
    decision = models.StringField()
    info_from_whom = models.StringField()
    chosen_receiver = models.IntegerField(null=True)
    vote = models.StringField(widget=widgets.RadioSelect, choices=C.CHOICES)
    question = models.StringField(widget=widgets.RadioSelect, choices=C.QUESTIONS)
    state = models.StringField()
    qualities = models.StringField()
    signals = models.CharField()
    selected_round = models.IntegerField()
    D_count = models.IntegerField()
    C_count = models.IntegerField()

    def get_decision_options(self):
        if self.D_count == 0:
            return C.ALL_C
        elif self.D_count == 1:
            if self.question == 'cat':
                return C.MAJORITY_C_4
            else:  # signals == 'r'
                return C.MINORITY_D_1
        elif self.D_count == 2:
            if self.question == 'cat':
                return C.MAJORITY_C_3
            else:  # signals == 'r'
                return C.MINORITY_D_2
        elif self.D_count == 3:
            if self.question == 'cat':
                return C.MINORITY_C_2
            else:  # signals == 'r'
                return C.MAJORITY_D_3
        elif self.D_count == 4:
            if self.question == 'cat':
                return C.MINORITY_C_1
            else:  # signals == 'r'
                return C.MAJORITY_D_4
        else:  # D_count = 5
            return C.ALL_D


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

                if player.state == 'R':
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 7 / 8 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 4 / 7 else 'b'
                else:  # 'B'
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 1 / 7 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 3 / 7 else 'b'


class Welcome(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1



class ResultsWaitPage0(WaitPage):
    wait_for_all_groups = True


class question_answering(Page):
    form_model = 'player'
    form_fields = ['timeSpent0','question']


class ResultsWaitPage1(WaitPage):
    wait_for_all_groups = True
    @staticmethod
    def after_all_players_arrive(subsession):
        for group in subsession.get_groups():
            group.calculate_signals()
            for player in group.get_players():
                player.D_count = group.D_count
                player.C_count = group.C_count

class Info_and_decision(Page):
    form_model = 'player'
    form_fields = ['timeSpent1','decision']
    @staticmethod
    def vars_for_template(player):
        if player.qualities == 'l':
            quality_display = "Box B"
        else:
            quality_display = "Box A"

        if player.signals == 'r':
            player_signal_color = "red"
        else:  # 'b'
            player_signal_color = "blue"

        if player.question == 'cat':
            p_question = "CAT"
        else:
            p_question = "DOG"

        player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"
        p_self_question = p_question

        other_signals_info = []
        for p in player.group.get_players():
            if p.id_in_group != player.id_in_group:
                if p.question == 'cat':
                    p_question = "CAT"
                else:
                    p_question = "DOG"

                other_signals_info.append({
                    'player_id': p.id_in_group,
                    'other_p_question': p_question,
                })

        return dict(
            quality=quality_display,
            player_question=p_self_question,
            player_signal_style=player_signal_style,
            other_signals_info=other_signals_info,
        )


class ResultsWaitPage2(WaitPage):
    wait_for_all_groups = True


class ResultsWaitPage2(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        all_players = self.subsession.get_players()

        for player in all_players:
            player.info_from_whom = str(player.id_in_group)


        for participant in all_players:
            if participant.decision == 'send to a player who chose CAT':
                eligible_players = [p for p in all_players if p.question == 'cat' and p.id_in_group != participant.id_in_group]
                if eligible_players:
                    chosen_receiver = random.choice(eligible_players)
                    chosen_receiver.info_from_whom += f",{participant.id_in_group}"
                    participant.chosen_receiver = chosen_receiver.id_in_group
            elif participant.decision == 'send to a player who chose DOG':
                eligible_players = [p for p in all_players if p.question == 'dog' and p.id_in_group != participant.id_in_group]
                if eligible_players:
                    chosen_receiver = random.choice(eligible_players)
                    chosen_receiver.info_from_whom += f",{participant.id_in_group}"
                    participant.chosen_receiver = chosen_receiver.id_in_group


class network_and_voting(Page):
    form_model = 'player'
    form_fields = ['timeSpent2','vote']

    @staticmethod
    def vars_for_template(player):
        all_players = player.group.get_players()
        participants_info = []

        info_sources = set(map(int, player.info_from_whom.split(',')))

        for participant in all_players:
            if participant.signals == 'r':
                player_signal_color = "red"
            else:  # b
                player_signal_color = "blue"

            if participant.question == 'cat':
                p_question = "CAT"
            else:
                p_question = "DOG"

            player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"
            player_question_answering = p_question
            all_info = participant.info_from_whom

            if participant.qualities == 'l':
                quality_representation = "Box B"
            else:
                quality_representation = "Box A"

            box_info = quality_representation if participant.id_in_group in info_sources else 'Unknown'
            ball_info = player_signal_style if participant.id_in_group in info_sources else 'Unknown'

            participants_info.append({
                'id_in_group': participant.id_in_group,
                'quality_representation': quality_representation,
                'player_signal_style': player_signal_style,
                'is_self': participant.id_in_group == player.id_in_group,
                'ball_info': ball_info,
                'box_info': box_info,
                'all_info': all_info,
                'player_question_answering': player_question_answering,
            })

        participants_info = sorted(participants_info, key=lambda x: not x['is_self'])

        return {
            'participants_info': participants_info
        }

class ResultsWaitPage3(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()


class ResultsWaitPage4(WaitPage):
    wait_for_all_groups = True


class ResultsWaitPage5(WaitPage):
    def is_displayed(player:Player):
        return player.round_number==C.NUM_ROUNDS

    def after_all_players_arrive(self):
        selected_round = random.randint(1, C.NUM_ROUNDS)
        for player in self.group.get_players():
            player_in_selected_round = player.in_round(selected_round)
            player.selected_round = selected_round
            player.payoff = player_in_selected_round.payoff

            player.participant.vars[__name__] = [int(player.payoff), int(selected_round)]


page_sequence = [StartRoundWaitPage, Welcome, ResultsWaitPage0, question_answering, ResultsWaitPage1, Info_and_decision, ResultsWaitPage2, network_and_voting, ResultsWaitPage3, ResultsWaitPage4, ResultsWaitPage5]
