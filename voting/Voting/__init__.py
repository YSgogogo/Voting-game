from otree.api import *
import random
import json

doc = """
Voting Game
"""


class C(BaseConstants):
    NAME_IN_URL = 'Voting'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS = 10
    AMOUNT_SHARED_IF_WIN = 15
    AMOUNT_SHARED_IF_LOSE = 2
    CHOICES = ['R', 'B']
    STATES = ['R', 'B']
    QUALITIES = ['h', 'l']
    MAJORITY_B = ['link with B', 'link with R', 'do not want to chat']
    MAJORITY_R = ['link with R', 'link with B', 'do not want to chat']
    MINORITY_R = ['link with B', 'do not want to chat']
    MINORITY_B = ['link with R', 'do not want to chat']
    ALL_R = ['link with R', 'do not want to chat']
    ALL_B = ['link with B', 'do not want to chat']



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
        rankings = [json.loads(p.ranking) if p.ranking else [] for p in self.get_players()]
        r_players = [p for p in self.get_players() if p.signals == 'r']
        b_players = [p for p in self.get_players() if p.signals == 'b']

        if self.r_count == 3:
            r_item1_first = [p.id_in_group for p in r_players if rankings[p.id_in_group - 1] and any('item1' == item for item in rankings[p.id_in_group - 1][0])]
            if len(r_item1_first) == 0:
                chat_participants = []
            elif len(r_item1_first) == 1:
                chat_participants = []
            elif len(r_item1_first) == 2:
                chat_participants = r_item1_first
            else:
                chat_participants = random.sample(r_item1_first, 2)

        elif self.r_count == 0:
            b_item1_first = [p.id_in_group for p in b_players if rankings[p.id_in_group - 1] and any('item1' == item for item in rankings[p.id_in_group - 1][0])]
            if len(b_item1_first) == 0:
                chat_participants = []
            elif len(b_item1_first) == 1:
                chat_participants = []
            elif len(b_item1_first) == 2:
                chat_participants = b_item1_first
            else:
                chat_participants = random.sample(b_item1_first, 2)

        else:
            chat_participants = [1, 2]

        self.chat_participants_record = json.dumps(chat_participants)

        return chat_participants



class Player(BasePlayer):
    vote = models.StringField(choices=C.CHOICES, label="Please vote for R or vote for B")
    state = models.StringField()
    qualities = models.StringField()
    signals = models.CharField()
    majority_vote_count = models.IntegerField()
    selected_round = models.IntegerField()
    ranking = models.StringField()
    r_count = models.IntegerField()
    b_count = models.IntegerField()
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
                        player.signals = 'r' if random.random() < 5 / 8 else 'b'
                    else:  # 'l'
                        player.signals = 'r' if random.random() < 4 / 7 else 'b'
                else:  # 'B'
                    if player.qualities == 'h':
                        player.signals = 'r' if random.random() < 3 / 8 else 'b'
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



class Info(Page):
    @staticmethod
    def vars_for_template(player):
        return dict(
            quality=player.qualities,
            signal=player.signals
        )



class Ranking(Page):

    form_model = 'player'
    form_fields = ['ranking']



class ResultsWaitPage1(WaitPage):
    def after_all_players_arrive(self):
        self.group.determine_chat_participants()



class Chat(Page):

    @staticmethod
    def vars_for_template(player):
        chat_participants_ids = json.loads(player.group.chat_participants_record)
        participants_info = []

        for participant_id in chat_participants_ids:
            participant = next(p for p in player.group.get_players() if p.id_in_group == participant_id)
            participants_info.append({
                'id_in_group': participant.id_in_group,
                'quality': participant.qualities,
                'signal': participant.signals,
                'is_self': participant.id_in_group == player.id_in_group
            })

        participants_info = sorted(participants_info, key=lambda x: not x['is_self'])

        return {
            'state': player.state,
            'participants_info': participants_info
        }

    @staticmethod
    def is_displayed(player):
        chat_participants = json.loads(player.group.chat_participants_record)
        return player.id_in_group in chat_participants
    timeout_seconds = 120



class ResultsWaitPage2(WaitPage):
    wait_for_all_groups = True



class Voting(Page):

    form_model = 'player'
    form_fields = ['vote']



class ResultsWaitPage3(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_payoffs()



class ResultsWaitPage4(WaitPage):
    wait_for_all_groups = True
    def is_displayed(player:Player):
        return player.round_number==C.NUM_ROUNDS



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
    pass



page_sequence = [StartRoundWaitPage, Welcome, General_Instructions, Main_Instructions, Info, Ranking, ResultsWaitPage1, Chat, ResultsWaitPage2,  Voting, ResultsWaitPage3, Results, ResultsWaitPage4, ResultsWaitPage5]
