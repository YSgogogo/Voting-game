from otree.api import *
import random
import json

doc = """
Voting_high_diff Game
"""



class C(BaseConstants):
    NAME_IN_URL = 'Voting_high_diff'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 2
    AMOUNT_SHARED_IF_WIN = 15
    AMOUNT_SHARED_IF_LOSE = 2
    CHOICES = [
        ('R', 'RED Box'),
        ('B', 'BLUE Box')
    ]
    STATES = ['R', 'B']
    QUALITIES = ['h', 'l']
    MAJORITY_B = ['connect with voter who got B', 'connect with voter who got R', 'do not connect with anyone']
    MAJORITY_R = ['connect with voter who got R', 'connect with voter who got B', 'do not connect with anyone']
    MINORITY_R = ['connect with voter who got B', 'do not connect with anyone']
    MINORITY_B = ['connect with voter who got R', 'do not connect with anyone']
    ALL_R = ['connect with voter who got R', 'do not connect with anyone']
    ALL_B = ['connect with voter who got B', 'do not connect with anyone']



class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()



class Group(BaseGroup):
    state = models.StringField()
    r_count = models.IntegerField(initial=0)
    b_count = models.IntegerField(initial=0)
    chat_participants_record = models.StringField()
    def set_payoffs(self):
        votes = [p.vote for p in self.get_players()]
        majority_vote = self.state
        majority_vote_count = votes.count(majority_vote)

        if majority_vote_count > len(votes) / 2:
            payoff = C.AMOUNT_SHARED_IF_WIN
        else:
            payoff = C.AMOUNT_SHARED_IF_LOSE

        for p in self.get_players():
            p.payoff = payoff
            p.majority_vote_count = majority_vote_count

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

    def determine_chat_participants(self):
        rankings = [json.loads(p.updated_ranking) if p.updated_ranking else [] for p in self.get_players()]
        r_players = [p for p in self.get_players() if p.signals == 'r']
        b_players = [p for p in self.get_players() if p.signals == 'b']

        if self.r_count == 3:
            r_item1_first = [
                p.id_in_group
                for p in r_players
                if rankings[p.id_in_group - 1]
                and any('item1' == item for item in rankings[p.id_in_group - 1][0])
            ]

            if len(r_item1_first) == 0:
                chat_participants = []
            elif len(r_item1_first) == 1:
                chat_participants = []
            elif len(r_item1_first) == 2:
                chat_participants = r_item1_first
            else:
                chat_participants = random.sample(r_item1_first, 2)

        elif self.r_count == 2:
            b_player_ranking = rankings[[p.id_in_group - 1 for p in b_players][0]]

            if b_player_ranking[0] == ["item2"]:
                r_player_rankings = [rankings[p.id_in_group - 1] for p in r_players]
                if (
                        r_player_rankings[0] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item2"], ["item1"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                        and r_player_rankings[1] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item2"], ["item1"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                ):
                    chat_participants = [p.id_in_group for p in r_players]
                else:
                    chat_participants = []

            elif b_player_ranking[0] == ["item1"]:
                r_player_rankings = [rankings[p.id_in_group - 1] for p in r_players]
                if (
                        r_player_rankings[0] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                        and r_player_rankings[1] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                ):
                    chat_participants = [p.id_in_group for p in r_players]

                elif (
                        [["item3"], ["item2"], ["item1"]] in r_player_rankings
                        or [["item3"], ["item1"], ["item2"]] in r_player_rankings
                ):
                    if r_player_rankings[0] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [r_players[0].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[1] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [r_players[1].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[0] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [r_players[0].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[1] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [r_players[1].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[0] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [r_players[0].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[1] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [r_players[1].id_in_group, b_players[0].id_in_group]
                    else:
                        chat_participants = []

                elif (
                        [["item1"], ["item2"], ["item3"]] in r_player_rankings
                        or [["item1"], ["item3"], ["item2"]] in r_player_rankings
                ):
                    if r_player_rankings[0] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [r_players[0].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[1] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [r_players[1].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[0] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [r_players[0].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[1] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [r_players[1].id_in_group, b_players[0].id_in_group]
                    elif r_player_rankings[0] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [p.id_in_group for p in r_players]
                    elif r_player_rankings[1] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [p.id_in_group for p in r_players]
                    elif r_player_rankings[0] == [["item1"], ["item3"], ["item2"]]:
                        chat_participants = [p.id_in_group for p in r_players]
                    elif r_player_rankings[1] == [["item1"], ["item3"], ["item2"]]:
                        chat_participants = [p.id_in_group for p in r_players]
                    else:
                        chat_participants = []

                elif (
                        r_player_rankings[0] in [
                    [["item2"], ["item1"], ["item3"]],
                    [["item2"], ["item3"], ["item1"]]
                ]
                        and r_player_rankings[1] in [
                            [["item2"], ["item1"], ["item3"]],
                            [["item2"], ["item3"], ["item1"]]
                        ]
                ):
                    chosen_r_player = random.choice(r_players)
                    chat_participants = [chosen_r_player.id_in_group, b_players[0].id_in_group]
                else:
                    chat_participants = []

        elif self.r_count == 1:
            r_player_ranking = rankings[[p.id_in_group - 1 for p in r_players][0]]

            if r_player_ranking[0] == ["item2"]:
                b_player_rankings = [rankings[p.id_in_group - 1] for p in b_players]
                if (
                        b_player_rankings[0] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item2"], ["item1"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                        and b_player_rankings[1] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item2"], ["item1"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                ):
                    chat_participants = [p.id_in_group for p in b_players]
                else:
                    chat_participants = []

            elif r_player_ranking[0] == ["item1"]:
                b_player_rankings = [rankings[p.id_in_group - 1] for p in b_players]
                if (
                        b_player_rankings[0] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                        and b_player_rankings[1] in [
                    [["item1"], ["item2"], ["item3"]],
                    [["item1"], ["item3"], ["item2"]]
                ]
                ):
                    chat_participants = [p.id_in_group for p in b_players]

                elif (
                        [["item3"], ["item2"], ["item1"]] in b_player_rankings
                        or [["item3"], ["item1"], ["item2"]] in b_player_rankings
                ):
                    if b_player_rankings[0] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [b_players[0].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[1] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [b_players[1].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[0] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [b_players[0].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[1] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [b_players[1].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[0] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [b_players[0].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[1] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [b_players[1].id_in_group, r_players[0].id_in_group]
                    else:
                        chat_participants = []

                elif (
                        [["item1"], ["item2"], ["item3"]] in b_player_rankings
                        or [["item1"], ["item3"], ["item2"]] in b_player_rankings
                ):
                    if b_player_rankings[0] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [b_players[0].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[1] == [["item2"], ["item1"], ["item3"]]:
                        chat_participants = [b_players[1].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[0] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [b_players[0].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[1] == [["item2"], ["item3"], ["item1"]]:
                        chat_participants = [b_players[1].id_in_group, r_players[0].id_in_group]
                    elif b_player_rankings[0] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [p.id_in_group for p in b_players]
                    elif b_player_rankings[1] == [["item1"], ["item2"], ["item3"]]:
                        chat_participants = [p.id_in_group for p in b_players]
                    elif b_player_rankings[0] == [["item1"], ["item3"], ["item2"]]:
                        chat_participants = [p.id_in_group for p in b_players]
                    elif b_player_rankings[1] == [["item1"], ["item3"], ["item2"]]:
                        chat_participants = [p.id_in_group for p in b_players]
                    else:
                        chat_participants = []

                elif (
                        b_player_rankings[0] in [
                    [["item2"], ["item1"], ["item3"]],
                    [["item2"], ["item3"], ["item1"]]
                ]
                        and b_player_rankings[1] in [
                            [["item2"], ["item1"], ["item3"]],
                            [["item2"], ["item3"], ["item1"]]
                        ]
                ):
                    chosen_b_player = random.choice(b_players)
                    chat_participants = [chosen_b_player.id_in_group, r_players[0].id_in_group]
                else:
                    chat_participants = []

        elif self.r_count == 0:
            b_item1_first = [
                p.id_in_group
                for p in b_players
                if rankings[p.id_in_group - 1]
                and any('item1' == item for item in rankings[p.id_in_group - 1][0])
            ]
            if len(b_item1_first) == 0:
                chat_participants = []
            elif len(b_item1_first) == 1:
                chat_participants = []
            elif len(b_item1_first) == 2:
                chat_participants = b_item1_first
            else:
                chat_participants = random.sample(b_item1_first, 2)

        else:
            chat_participants = []

        self.chat_participants_record = json.dumps(chat_participants)

        return chat_participants



class Player(BasePlayer):
    timeSpent1 = models.FloatField()
    timeSpent2 = models.FloatField()
    timeSpent3 = models.FloatField()
    vote = models.StringField(widget=widgets.RadioSelect, choices=C.CHOICES)
    state = models.StringField()
    qualities = models.StringField()
    signals = models.CharField()
    majority_vote_count = models.IntegerField()
    selected_round = models.IntegerField()
    ranking = models.StringField()
    updated_ranking = models.StringField()
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
        label="Your can only see the ball (red ball or blue ball) that your group members got, but do not know where they got this ball: Right Box or Left Box.",
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
        label="If you got a red ball from right Box, which state will be more likely to be the true state?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
    ]
    )
    quiz5 = models.IntegerField(
        label="If you got a red ball from Right Box and a blue ball from Left box, which state will be more likely to be the true state?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
    ]
    )
    quiz6 = models.IntegerField(
        label="If you got a red ball from Right Box and a blue ball from Right box, which state will be more likely to be the true state?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
            [2, 'Equally likely'],
    ]
    )

    def chat_nickname(self):
        return 'Voter {}'.format(self.id_in_group)

    def chat_room(self):
        chat_participants = json.loads(self.group.chat_participants_record)
        if self.id_in_group in chat_participants:
            return '{}-{}'.format(C.NAME_IN_URL, self.group.pk)
        return None

    def get_ranking_options(self):
        if self.r_count == 0:
            return C.ALL_B
        elif self.r_count == 1:
            if self.signals == 'b':
                return C.MAJORITY_B
            else:  # signals == 'r'
                return C.MINORITY_R
        elif self.r_count == 2:
            if self.signals == 'r':
                return C.MAJORITY_R
            else:  # signals == 'b'
                return C.MINORITY_B
        else:  # r_count = 3
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
                        player.signals = 'r' if random.random() < 12 / 15 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 4 / 7 else 'b'
                else:  # 'B'
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 3 / 15 else 'b'
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



class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True



class Info(Page):
    form_model = 'player'
    form_fields = ['timeSpent1']
    @staticmethod
    def vars_for_template(player):
        if player.qualities == 'l':
            quality_display = "Right Box"
        else:
            quality_display = "Left Box"

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


class Ranking(Page):
    form_model = 'player'
    form_fields = ['ranking','timeSpent2']

    @staticmethod
    def vars_for_template(player):
        if player.qualities == 'l':
            quality_display = "Right Box"
        else:
            quality_display = "Left Box"

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

    def before_next_page(player, timeout_happened):

        current_ranking = json.loads(player.ranking) if player.ranking else []
        def adjust_ranking(ranking):
            updated_ranking = [None, None, None]

            if ranking[0] and len(ranking[0]) > 1:
                random.shuffle(ranking[0])
                updated_ranking[0] = [ranking[0][0]]
                updated_ranking[1] = [ranking[0][1]]
                if len(ranking[0]) > 2:
                    updated_ranking[2] = [ranking[0][2]]
                elif ranking[1]:
                    updated_ranking[2] = ranking[1]
            elif ranking[1] and len(ranking[1]) > 1:
                random.shuffle(ranking[1])
                updated_ranking[0] = ranking[0]
                updated_ranking[1] = [ranking[1][0]]
                updated_ranking[2] = [ranking[1][1]]
            else:
                updated_ranking = ranking

            return updated_ranking

        updated_ranking = adjust_ranking(current_ranking)
        player.updated_ranking = json.dumps(updated_ranking)



class ResultsWaitPage1(WaitPage):
    def after_all_players_arrive(self):
        self.group.determine_chat_participants()



class ResultsWaitPage1a(WaitPage):
    wait_for_all_groups = True



class Chat(Page):

    @staticmethod
    def vars_for_template(player):
        chat_participants_ids = json.loads(player.group.chat_participants_record)
        all_players = player.group.get_players()
        participants_info = []


        for participant in all_players:
            if participant.signals == 'r':
                player_signal_color = "red"
            else:  # b
                player_signal_color = "blue"

            player_signal_style = f"height: 1.2em; width: 1.2em; background-color: {player_signal_color}; border-radius: 50%; display: inline-block; vertical-align: middle; margin: 0 5px;"

            if participant.qualities == 'l':
                quality_representation = "Right Box"
            else:
                quality_representation = "Left Box"

            participants_info.append({
                'id_in_group': participant.id_in_group,
                'quality_representation': quality_representation,
                'player_signal_style': player_signal_style,
                'is_self': participant.id_in_group == player.id_in_group,
                'is_chat_participant': participant.id_in_group in chat_participants_ids
            })

        participants_info = sorted(participants_info, key=lambda x: not x['is_self'])

        return {
            'participants_info': participants_info
        }

    @staticmethod
    def is_displayed(player):
        chat_participants = json.loads(player.group.chat_participants_record)
        return player.id_in_group in chat_participants
    timeout_seconds = 60


class NonChat(Page):

    @staticmethod
    def vars_for_template(player):
        if player.qualities == 'l':
            quality_display = "Right Box"
        else:
            quality_display = "Left Box"

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

    @staticmethod
    def is_displayed(player):
        chat_participants = json.loads(player.group.chat_participants_record)
        return player.id_in_group not in chat_participants

    timeout_seconds = 60

class ResultsWaitPage2(WaitPage):
    wait_for_all_groups = True



class Voting(Page):

    form_model = 'player'
    form_fields = ['vote', 'timeSpent3']



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


page_sequence = [StartRoundWaitPage, Welcome, General_Instructions, Main_Instructions, Comprehension_Test, ResultsWaitPage, Info, Ranking, ResultsWaitPage1, ResultsWaitPage1a, Chat, NonChat, ResultsWaitPage2,  Voting, ResultsWaitPage3, ResultsWaitPage4, Results, Results_2, ResultsWaitPage5]
