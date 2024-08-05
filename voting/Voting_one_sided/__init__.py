from otree.api import *
import random
import json


doc = """
Voting_one_sided
"""


class C(BaseConstants):
    NAME_IN_URL = 'Voting_one_sided'
    PLAYERS_PER_GROUP = 5
    NUM_ROUNDS = 2
    AMOUNT_SHARED_IF_WIN = 15
    AMOUNT_SHARED_IF_LOSE = 2
    CHOICES = [
        ('R', 'RED Box'),
        ('B', 'BLUE Box')
    ]
    STATES = ['R', 'B']
    QUALITIES = ['h', 'l']
    MAJORITY_B_4 = ['connect with voter who got B', 'connect with voter who got R', 'do not connect with anyone']
    MAJORITY_R_4 = ['connect with voter who got R', 'connect with voter who got B', 'do not connect with anyone']
    MAJORITY_B_3 = ['connect with voter who got B', 'connect with voter who got R', 'do not connect with anyone']
    MAJORITY_R_3 = ['connect with voter who got R', 'connect with voter who got B', 'do not connect with anyone']
    MINORITY_B_1 = ['connect with voter who got R', 'do not connect with anyone']
    MINORITY_R_1 = ['connect with voter who got B', 'do not connect with anyone']
    MINORITY_B_2 = ['connect with voter who got B', 'connect with voter who got R', 'do not connect with anyone']
    MINORITY_R_2 = ['connect with voter who got R', 'connect with voter who got B', 'do not connect with anyone']
    ALL_R = ['connect with voter who got R', 'do not connect with anyone']
    ALL_B = ['connect with voter who got B', 'do not connect with anyone']


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()


class Group(BaseGroup):
    state = models.StringField()
    r_count = models.IntegerField(initial=0)
    b_count = models.IntegerField(initial=0)
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
        r_count = 0
        b_count = 0
        for p in self.get_players():
            if p.signals == 'r':
                r_count += 1
            elif p.signals == 'b':
                b_count += 1
        self.r_count = r_count
        self.b_count = b_count

class Player(BasePlayer):
    timeSpent1 = models.FloatField()
    timeSpent2 = models.FloatField()
    decision = models.StringField()
    info_from_whom = models.StringField()
    vote = models.StringField(widget=widgets.RadioSelect, choices=C.CHOICES)
    state = models.StringField()
    qualities = models.StringField()
    signals = models.CharField()
    selected_round = models.IntegerField()
    r_count = models.IntegerField()
    b_count = models.IntegerField()
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    quiz1 = models.IntegerField(
        label="In the experiment, how many people in your group must vote correctly for you to earn £15?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'only myself.'],
            [1, 'myself and one other group member.'],
            [2, 'everyone in the group.'],
            [3, 'any two people in the group.'],
        ]
    )
    quiz2 = models.IntegerField(
        label="Your can only see the ball (red ball or blue ball) that your group members got, but do not know where they got this ball: Box A or Box B.",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'yes, the statement is correct.'],
            [1, 'no, the statement is wrong. '],
        ]
    )
    quiz3 = models.IntegerField(
        label="How should you perform the ranking task?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'I should drag the person I most want to communicate with to the first position; the order of the others does not matter.'],
            [1, 'I should rank exactly from the one I most want to communicate with to the one I least want to communicate with.'],
            [2, 'I can rank them randomly; the order does not matter.'],
    ]
    )
    quiz4 = models.IntegerField(
        label="If you got a red ball from Box B, which state will be more likely to be the true state?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
    ]
    )
    quiz5 = models.IntegerField(
        label="If you got a red ball from Box B and a blue ball from  Box A, which state will be more likely to be the true state?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
    ]
    )
    quiz6 = models.IntegerField(
        label="If you got a red ball from Box B and a blue ball from Box B, which state will be more likely to be the true state?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
            [2, 'Equally likely'],
    ]
    )

    def get_decision_options(self):
        if self.r_count == 0:
            return C.ALL_B
        elif self.r_count == 1:
            if self.signals == 'b':
                return C.MAJORITY_B_4
            else:  # signals == 'r'
                return C.MINORITY_R_1
        elif self.r_count == 2:
            if self.signals == 'b':
                return C.MAJORITY_B_3
            else:  # signals == 'r'
                return C.MINORITY_R_2
        elif self.r_count == 3:
            if self.signals == 'b':
                return C.MINORITY_B_2
            else:  # signals == 'r'
                return C.MAJORITY_R_3
        elif self.r_count == 4:
            if self.signals == 'b':
                return C.MINORITY_B_1
            else:  # signals == 'r'
                return C.MAJORITY_R_4
        else:  # r_count = 5
            return C.ALL_R


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

            group.calculate_signals()
            for player in group.get_players():
                player.r_count = group.r_count
                player.b_count = group.b_count


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


class Comprehension_Test(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5', 'quiz6']

    @staticmethod
    def error_message(player: Player, values):
        solutions = {"quiz1": 3, "quiz2": 0, "quiz3": 1, "quiz4": 0, "quiz5": 1, "quiz6": 2}
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.num_failed_attempts += 1
            if player.num_failed_attempts >= 100:
                player.failed_too_many = True
            else:
                return errors
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class ResultsWaitPage1(WaitPage):
    wait_for_all_groups = True


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

        player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"

        other_signals_info = []
        for p in player.group.get_players():
            if p.id_in_group != player.id_in_group:
                if p.signals == 'r':
                    signal_color = "red"
                else:  # 'b'
                    signal_color = "blue"

                other_signals_info.append({
                    'player_id': p.id_in_group,
                    'signal_style': f"height: 1.2em; width: 1.2em; background-color: {signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;",
                })

        return dict(
            quality=quality_display,
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
            if participant.decision == 'connect with voter who got B':
                eligible_players = [p for p in all_players if p.signals == 'b' and p.id_in_group != participant.id_in_group]
                if eligible_players:
                    chosen_receiver = random.choice(eligible_players)
                    chosen_receiver.info_from_whom += f",{participant.id_in_group}"
            elif participant.decision == 'connect with voter who got R':
                eligible_players = [p for p in all_players if p.signals == 'r' and p.id_in_group != participant.id_in_group]
                if eligible_players:
                    chosen_receiver = random.choice(eligible_players)
                    chosen_receiver.info_from_whom += f",{participant.id_in_group}"


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

            player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"

            if participant.qualities == 'l':
                quality_representation = "Box B"
            else:
                quality_representation = "Box A"

            box_info = quality_representation if participant.id_in_group in info_sources else 'Unknown'

            participants_info.append({
                'id_in_group': participant.id_in_group,
                'quality_representation': quality_representation,
                'player_signal_style': player_signal_style,
                'is_self': participant.id_in_group == player.id_in_group,
                'box_info': box_info
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


class Results(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number < C.NUM_ROUNDS


class Results_2(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS


page_sequence = [StartRoundWaitPage, Welcome, General_Instructions, Main_Instructions, Comprehension_Test, ResultsWaitPage1, Info_and_decision, ResultsWaitPage2, network_and_voting, ResultsWaitPage3, ResultsWaitPage4, ResultsWaitPage5, Results, Results_2]
