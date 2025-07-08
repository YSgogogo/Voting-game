from otree.api import *
import random
from itertools import permutations

doc = """
Three-player voting experiment individual+nochat.
"""


class C(BaseConstants):
    NAME_IN_URL       = 'Voting_Block_One_individual_nochat'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS        = 20
    AMOUNT_CORRECT    = 6
    CHOICES           = [('R', 'RED Box'), ('B', 'BLUE Box')]
    STATES            = ['R', 'B']
    QUALITIES         = ['h', 'l']


# ------------------------------------------------------------------
#  build pre-generated signal table
# ------------------------------------------------------------------
def build_signal_table(M: int = 1000):
    """generate 1000 data"""
    table = []
    for _ in range(M):
        state = random.choice(C.STATES)
        group = {'state': state, 'players': {}}

        for pid in (1, 2, 3):
            qual = 'h' if random.random() < 0.30 else 'l'

            # 条件化信号概率
            if state == 'R':
                sig = 'r' if (qual == 'h' and random.random() < 8/9) or \
                             (qual == 'l' and random.random() < 5/9) else 'b'
            else:
                sig = 'r' if (qual == 'h' and random.random() < 1/9) or \
                             (qual == 'l' and random.random() < 4/9) else 'b'

            group['players'][pid] = {'qualities': qual, 'signals': sig}

        table.append(group)
    return table


# ================================================================
# Triplet patterns (6  × 2 = 12 )
# ================================================================
TRIPLE_ROWS: list[tuple[tuple[str, str, str], tuple[str, str, str]]] = [
    (('rh', 'bh', 'rl'), ('bh', 'rh', 'bl')),
    (('rh', 'bh', 'rh'), ('bh', 'rh', 'bh')),
    (('rh', 'bl', 'rh'), ('bh', 'rl', 'bh')),
    (('rh', 'bl', 'rl'), ('bh', 'rl', 'bl')),
    (('rl', 'bh', 'rl'), ('bl', 'rh', 'bl')),
    (('rl', 'bl', 'rl'), ('bl', 'rl', 'bl')),

    (('rh', 'b', 'r'), ('bh', 'r', 'b')),
    (('rl', 'b', 'r'), ('bl', 'r', 'b')),
    (('rh', 'bh', 'r'), ('bh', 'rh', 'b')),
    (('rh', 'bl', 'r'), ('bh', 'rl', 'b')),
    (('rl', 'bh', 'r'), ('bl', 'rh', 'b')),
    (('rl', 'bl', 'r'), ('bl', 'rl', 'b')),
    (('rh', 'b', 'rl'), ('bh', 'r', 'bl')),
    (('rh', 'b', 'rh'), ('bh', 'r', 'bh')),
    (('rl', 'b', 'rl'), ('bl', 'r', 'bl')),

    (('rl', '', ''), ('bl', '', '')),
    (('rh', '', ''), ('bh', '', '')),
    (('r', '', ''), ('b', '', '')),

    (('rh', 'b', ''), ('bh', 'r', '')),
    (('rh', 'bl', ''), ('bh', 'rl', '')),
    (('r', 'bh', ''), ('b', 'rh', '')),
    (('r', 'bl', ''), ('b', 'rl', '')),

]
ALL_TRIPLES: list[tuple[str, str, str]] = [t for pair in TRIPLE_ROWS for t in pair]


def expand_triplet(trip: tuple[str, str, str]) -> list[str]:
    patterns = []
    for tag in trip:
        others = sorted([t if t else '.' for t in trip if t != tag])
        tag_display = tag if tag else '.'
        patterns.append(f"{tag_display}+{''.join(others)}")
    return patterns

def data_matches_pattern(data_slots, required_pattern):
    """
    Correct interpretation:
    - required_pattern may contain up to 3 strings (e.g., ('rh', '', ''))
    - Only non-empty tags in required_pattern need to be checked.
    - If at least as many required tags as non-empty tags are found in data_slots, it's a match.
    """
    required_tags = [tag for tag in required_pattern if tag != '']
    data_tags = [slot[1] for slot in data_slots]

    # For each required tag, ensure at least one matching data_tag
    for req_tag in required_tags:
        matched = False
        for data_tag in data_tags:
            if req_tag == data_tag or (len(req_tag) == 1 and data_tag.startswith(req_tag)):
                matched = True
                break  # move to the next required tag
        if not matched:
            return False
    return True



class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.session.vars['signal_table'] = build_signal_table(1000)
            self.session.vars['used_records'] = set()


class Group(BaseGroup):
    state   = models.StringField()
    r_count = models.IntegerField()
    b_count = models.IntegerField()

    # 组内 r / b 信号计数（用于显示）
    def _count_signals(self):
        self.r_count = sum(1 for p in self.get_players() if p.signals == 'r')
        self.b_count = C.PLAYERS_PER_GROUP - self.r_count

    def set_payoffs(self):
        correct = sum(1 for p in self.get_players() if p.vote == self.state)
        payoff = correct * C.AMOUNT_CORRECT
        for p in self.get_players():
            p.payoff_record = payoff


class Player(BasePlayer):
    timeSpent = models.FloatField()
    vote            = models.StringField(widget=widgets.RadioSelect,
                                         choices=C.CHOICES)
    state     = models.StringField()
    signals   = models.CharField()
    qualities = models.StringField()
    payoff_record   = models.IntegerField(initial=0)
    selected_round  = models.IntegerField()
    r_count         = models.IntegerField()
    b_count         = models.IntegerField()
    current_pattern = models.StringField()

    num_failed_attempts1 = models.IntegerField(initial=0)
    failed_too_many1 = models.BooleanField(initial=False)
    num_failed_attempts2 = models.IntegerField(initial=0)
    failed_too_many2 = models.BooleanField(initial=False)
    num_failed_attempts3 = models.IntegerField(initial=0)
    failed_too_many3 = models.BooleanField(initial=False)
    quiz1 = models.IntegerField(
        label="If you observe a red signal, which state is more likely? ",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'RED'],
            [1, 'BLUE'],
            [2, 'Equally likely'],
        ]
    )
    quiz2 = models.IntegerField(
        label="Which of the following signal source is more informative?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'Strong source'],
            [1, 'Weak source'],
            [2, 'No difference'],
        ]
    )
    quiz3 = models.IntegerField(
        label="At the beginning of the each round, the probability that state is RED or Blue is 50%.",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'True'],
            [1, 'False'],
    ]
    )

    quiz4 = models.IntegerField(
        label="If I think BLUE is more likely, which state I should predict?  ",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'RED'],
            [1, 'BLUE'],
    ]
    )

    quiz5 = models.IntegerField(
        label="Strong source is less likely to be received than weak source.",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'True'],
            [1, 'False'],
    ]
    )
    quiz6 = models.IntegerField(
        label="I may have different group members in different rounds.",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'True'],
            [1, 'False'],
    ]
    )

    quiz7 = models.IntegerField(
        label="In a round, you and your group members have a same true state.  ",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'True'],
            [1, 'False'],
    ]
    )

    quiz8 = models.IntegerField(
        label="In the following example, who has the same signal as you?",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'Group member ID:2'],
            [1, 'Group member ID:1'],
            [2, 'No one has the same signal as me'],
    ]
    )


    quiz9 = models.IntegerField(
        label="In the following example, what is group member ID:2's signal source?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'Strong source'],
            [1, 'Weak source'],
            [2, 'I do not know'],
        ]
    )

    quiz10 = models.IntegerField(
        label="In the following example, suppose you guess correctly, Group member ID:1 guesses correctly, and Group member ID:2 guesses incorrectly, what is you payment in this block?",
        widget=widgets.RadioSelect,
        choices=[
            [0, '£ 0'],
            [1, '£ 6'],
            [2, '£ 12'],
        ]
    )

    quiz11 = models.IntegerField(
        label="In the following example, suppose you guess incorrectly, Group member ID:1 guesses correctly, and Group member ID:3 guesses correctly, what is you payment in this block?",
        widget=widgets.RadioSelect,
        choices=[
            [0, '£ 0'],
            [1, '£ 6'],
            [2, '£ 12'],
        ]
    )

def data_matches_pattern(data_slots, required_pattern):
    required_tags = [tag for tag in required_pattern if tag != '']
    data_tags = [slot[1] for slot in data_slots]

    for req_tag in required_tags:
        matched = False
        for data_tag in data_tags:
            if req_tag == data_tag or (len(req_tag)==1 and data_tag.startswith(req_tag)):
                matched = True
                data_tags.remove(data_tag)
                break
        if not matched:
            return False
    return True


# ------------------------------------------------------------------
# WaitPage – pattern assignment
# ------------------------------------------------------------------
class StartRoundWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def _pattern_match(slot_tag: str, pattern: str, others_tags: list[str]) -> bool:

        if '+' not in pattern:
            return slot_tag == pattern
        left, right = pattern.split('+')
        if slot_tag != left:
            return False
        required_tags = [right[i:i + 2] for i in range(0, len(right), 2)]
        temp_others = others_tags.copy()

        for req_tag in required_tags:
            if req_tag == '.':
                # Wildcard: match any, remove the first
                if temp_others:
                    temp_others.pop(0)
                else:
                    return False
            else:
                if req_tag in temp_others:
                    temp_others.remove(req_tag)
                else:
                    return False
        return True

    def _find_pattern(
        self,
        tag: str,
        others_tags: list[str],
        round_patterns: list[str],
    ) -> str:
        for pat in round_patterns:
            if self._pattern_match(tag, pat, others_tags):
                return pat
        return f"{tag}+{''.join(sorted(others_tags))}"

    def after_all_players_arrive(self):
        self.subsession.group_randomly()
        sv = self.session.vars

        if 'signal_table' not in sv:
            sv['signal_table'] = build_signal_table(1000)
            sv['used_records'] = set()

        if 'triple_order' not in sv:
            selected_triples = []
            block1 = TRIPLE_ROWS[:6]  # 1-6
            block2 = TRIPLE_ROWS[6:15]  # 7-15
            block3 = TRIPLE_ROWS[15:18]  # 16-18
            block4 = TRIPLE_ROWS[18:22]  # 19-22

            def pick_from_block(block, n):
                chosen = []
                unique_triples = [trip for pair in block for trip in pair]
                random.shuffle(unique_triples)
                for trip in unique_triples:
                    if len(chosen) < n and trip not in chosen:
                        chosen.append(trip)
                while len(chosen) < n:
                    chosen.append(random.choice(unique_triples))
                random.shuffle(chosen)
                return chosen

            selected_triples += pick_from_block(block1, 8)
            selected_triples += pick_from_block(block2, 8)
            selected_triples += pick_from_block(block3, 2)
            selected_triples += pick_from_block(block4, 2)

            sv['triple_order'] = selected_triples

        trip_this_round = sv['triple_order'][self.subsession.round_number - 1]
        round_patterns = expand_triplet(trip_this_round)
        sv['pair_patterns'] = round_patterns

        table = sv['signal_table']
        used_idx = sv['used_records']

        for g in self.subsession.get_groups():
            best_match = None
            for idx, rec in enumerate(table):
                if idx in used_idx:
                    continue
                slots = [(sid, info['signals'] + info['qualities']) for sid, info in rec['players'].items()]
                if data_matches_pattern(slots, trip_this_round):
                    best_match = (idx, slots, rec['state'])
                    break

            if not best_match:
                for idx, rec in enumerate(table):
                    if idx not in used_idx:
                        slots = [(sid, info['signals'] + info['qualities']) for sid, info in rec['players'].items()]
                        best_match = (idx, slots, rec['state'])
                        break

            idx, perm, state = best_match
            used_idx.add(idx)
            g.state = state
            players = g.get_players()
            for p, (sid, _) in zip(players, perm):
                info = rec['players'][sid]
                p.state = state
                p.signals = info['signals']
                p.qualities = info['qualities']

            assigned_patterns = set()
            default_pat = round_patterns[0]  # fallback

            for p in players:
                my_tag = p.signals + p.qualities
                others_tags = [q.signals + q.qualities for q in players if q != p]
                found = False
                for pat in round_patterns:
                    if pat in assigned_patterns:
                        continue  # ensure uniqueness
                    if self._pattern_match(my_tag, pat, others_tags):
                        p.current_pattern = pat
                        assigned_patterns.add(pat)
                        p.participant.vars.setdefault('patterns_seen_three', []).append(pat)
                        found = True
                        break
                if not found:
                    # fallback: assign any unused pattern
                    for pat in round_patterns:
                        if pat not in assigned_patterns:
                            p.current_pattern = pat
                            assigned_patterns.add(pat)
                            p.participant.vars.setdefault('patterns_seen_three', []).append(pat)
                            found = True
                            break
                if not found:
                    # final fallback if all patterns taken
                    p.current_pattern = default_pat
                    p.participant.vars.setdefault('patterns_seen_three', []).append(default_pat)

            g._count_signals()
            for p in players:
                p.r_count = g.r_count
                p.b_count = g.b_count

        sv['used_records'] = used_idx


class Welcome(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Overview(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class General_setting_of_the_experiment(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1




class Comprehension_Test1(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2', 'quiz3', 'quiz4', 'quiz5']

    @staticmethod
    def error_message(player: Player, values):
        solutions1 = {"quiz1": 0, "quiz2": 0, "quiz3": 0,  "quiz4": 1, "quiz5": 0}
        errors1 = {name: 'Wrong' for name in solutions1 if values[name] != solutions1[name]}
        if errors1:
            player.num_failed_attempts1 += 1
            if player.num_failed_attempts1 >= 100:
                player.failed_too_many1 = True
            else:
                return errors1
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Examples(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Comprehension_Test2(Page):
    form_model = 'player'
    form_fields = ['quiz6', 'quiz7', 'quiz8', 'quiz9']

    @staticmethod
    def error_message(player: Player, values):
        solutions2 = {"quiz6": 0, "quiz7": 0, "quiz8": 1, 'quiz9': 2}
        errors2 = {name: 'Wrong' for name in solutions2 if values[name] != solutions2[name]}
        if errors2:
            player.num_failed_attempts2 += 1
            if player.num_failed_attempts2 >= 100:
                player.failed_too_many2 = True
            else:
                return errors2
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


class Block_one_instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Comprehension_Test3(Page):
    form_model = 'player'
    form_fields = ['quiz10', 'quiz11']

    @staticmethod
    def error_message(player: Player, values):
        solutions3 = {"quiz10": 1, "quiz11": 0}
        errors3 = {name: 'Wrong' for name in solutions3 if values[name] != solutions3[name]}
        if errors3:
            player.num_failed_attempts3 += 1
            if player.num_failed_attempts3 >= 100:
                player.failed_too_many3 = True
            else:
                return errors3
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1



class ResultsWaitPage1(WaitPage):
    wait_for_all_groups = True


class network_and_voting(Page):
    form_model = 'player'
    form_fields = ['timeSpent', 'vote']

    @staticmethod
    def vars_for_template(player):

        pattern = player.current_pattern
        pattern_parts = pattern.split('+')

        g_players = player.group.get_players()
        tag_map = {p.id_in_group: p.signals + p.qualities for p in g_players}

        # 获得当前玩家的tag和其他玩家的tags
        my_tag = player.signals + player.qualities
        others_tags = [tag_map[p.id_in_group] for p in g_players if p != player]

        # 当前玩家能观察到所有tags，处理''为unknown
        visible_tags = [my_tag] + others_tags

        rows = []
        for gp, tag in zip(g_players, visible_tags):
            row = dict(
                id_in_group=gp.id_in_group,
                is_self=(gp == player),
                player_signal_style='',
                box_info='Unknown',
            )

            # 处理tag为空的情况：完全不可见
            if tag == '':
                row['player_signal_style'] = ''
                row['box_info'] = 'Unknown'
            else:
                # 如果tag不为空，则检查signal和quality
                signal = tag[0] if len(tag) >= 1 else ''
                quality = tag[1] if len(tag) == 2 else ''

                if signal in ['r', 'b']:
                    col = 'red' if signal == 'r' else 'blue'
                    row['player_signal_style'] = (
                        f'height:1.4em;width:1.4em;background-color:{col};'
                        'border-radius:50%;display:inline-block;'
                        'vertical-align:middle;margin:0 0px;'
                    )

                # 显示质量信息（若存在）
                if quality in ['h', 'l']:
                    row['box_info'] = 'Box A' if quality == 'h' else 'Box B'
                else:
                    row['box_info'] = 'Unknown'

            rows.append(row)

        # 确保自己排第一
        rows.sort(key=lambda d: not d['is_self'])

        return dict(participants_info=rows)


class ResultsWaitPage3(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class ResultsWaitPage4(WaitPage):
    wait_for_all_groups = True


class ResultsWaitPage5(WaitPage):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS

    def after_all_players_arrive(self):
        rnd = random.randint(1, C.NUM_ROUNDS)
        for p in self.group.get_players():
            p.selected_round = rnd
            p.payoff = p.in_round(rnd).payoff_record
            p.participant.vars[__name__] = [int(p.payoff), rnd]


class FinalResults(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == C.NUM_ROUNDS


# ------------------------------------------------------------------
#  Page sequence
# ------------------------------------------------------------------
page_sequence = [
    StartRoundWaitPage,
    Welcome,
    Overview,
    General_setting_of_the_experiment,
    Comprehension_Test1,
    Examples,
    Comprehension_Test2,
    Block_one_instructions,
    Comprehension_Test3,
    ResultsWaitPage1,
    network_and_voting,
    ResultsWaitPage3,
    ResultsWaitPage4,
    ResultsWaitPage5,
    FinalResults,
]
