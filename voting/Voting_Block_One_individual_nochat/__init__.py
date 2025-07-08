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
    """generate M data points"""
    table = []
    for _ in range(M):
        state = random.choice(C.STATES)
        group = {'state': state, 'players': {}}
        for pid in (1, 2, 3):
            qual = 'h' if random.random() < 0.30 else 'l'
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
# Triplet patterns (22 rows × 2 each = 44 triples)
# ================================================================
TRIPLE_ROWS: list[tuple[tuple[str, str, str], tuple[str, str, str]]] = [
    (('rh', 'bh', 'rl'), ('bh', 'rh', 'bl')),
    (('rh', 'bh', 'rh'), ('bh', 'rh', 'bh')),
    (('rh', 'bl', 'rh'), ('bh', 'rl', 'bh')),
    (('rh', 'bl', 'rl'), ('bh', 'rl', 'bl')),
    (('rl', 'bh', 'rl'), ('bl', 'rh', 'bl')),
    (('rl', 'bl', 'rl'), ('bl', 'rl', 'bl')),
    (('rh', 'b', 'r'),   ('bh', 'r', 'b')),
    (('rl', 'b', 'r'),   ('bl', 'r', 'b')),
    (('rh', 'bh', 'r'),  ('bh', 'rh', 'b')),
    (('rh', 'bl', 'r'),  ('bh', 'rl', 'b')),
    (('rl', 'bh', 'r'),  ('bl', 'rh', 'b')),
    (('rl', 'bl', 'r'),  ('bl', 'rl', 'b')),
    (('rh', 'b', 'rl'),  ('bh', 'r', 'bl')),
    (('rh', 'b', 'rh'),  ('bh', 'r', 'bh')),
    (('rl', 'b', 'rl'),  ('bl', 'r', 'bl')),
    (('rl', '', ''),     ('bl', '', '')),
    (('rh', '', ''),     ('bh', '', '')),
    (('r',   '', ''),    ('b',  '', '')),
    (('rh', 'b', ''),    ('bh', 'r', '')),
    (('rh', 'bl', ''),   ('bh', 'rl', '')),
    (('r',  'bh', ''),   ('b',  'rh', '')),
    (('r',  'bl', ''),   ('b',  'rl', '')),
]
ALL_TRIPLES: list[tuple[str, str, str]] = [t for pair in TRIPLE_ROWS for t in pair]


def expand_triplet(trip: tuple[str, str, str]) -> list[str]:
    patterns = []
    for i, tag in enumerate(trip):
        others = [trip[j] for j in range(3) if j != i]
        others.sort()
        others_disp = [(o if o else '0') for o in others]
        patterns.append(f"{tag}+{''.join(others_disp)}")
    return patterns




class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.session.vars['signal_table'] = build_signal_table(1000)
            self.session.vars['used_records'] = set()


class Group(BaseGroup):
    state   = models.StringField()

    def set_payoffs(self):
        for p in self.get_players():
            p.payoff_record = C.AMOUNT_CORRECT if p.vote == self.state else 0



class Player(BasePlayer):
    timeSpent = models.FloatField()
    vote            = models.StringField(widget=widgets.RadioSelect,
                                         choices=C.CHOICES)
    state     = models.StringField()
    signals          = models.CharField(initial='')
    qualities        = models.StringField(initial='')
    payoff_record   = models.IntegerField(initial=0)
    selected_round  = models.IntegerField()
    current_pattern = models.StringField()

    num_failed_attempts1 = models.IntegerField(initial=0)
    failed_too_many1 = models.BooleanField(initial=False)
    num_failed_attempts2 = models.IntegerField(initial=0)
    failed_too_many2 = models.BooleanField(initial=False)
    num_failed_attempts3 = models.IntegerField(initial=0)
    failed_too_many3 = models.BooleanField(initial=False)
    quiz1 = models.IntegerField(
        label="At the beginning of each round, what is the probability that a signal source is a strong source?",
        widget=widgets.RadioSelect,
        choices=[
            [0, '30%'],
            [1, '50% '],
            [2, '100%'],
        ]
    )
    quiz2 = models.IntegerField(
        label="If the state is RED, which signal source contains more red signals?",
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
        label="If I see a red signal from a strong source, the state must be RED.  ",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'True'],
            [1, 'False'],
    ]
    )

    quiz5 = models.IntegerField(
        label="If I see a red signal from a weak source, the state must be RED.",
        widget = widgets.RadioSelect,
        choices = [
            [0, 'True'],
            [1, 'False'],
    ]
    )


    quiz7 = models.IntegerField(
        label="In the following example, what is group member ID:2's signal source? ",
        widget = widgets.RadioSelect,
        choices=[
            [0, 'Strong source'],
            [1, 'Weak source'],
            [2, 'I do not know'],
        ]
    )

    quiz8 = models.IntegerField(
        label="In the following example, what is group member ID:1's signal?",
        widget = widgets.RadioSelect,
        choices=[
            [0, 'Red signal'],
            [1, 'Blue signal'],
            [2, 'I do not know'],
        ]
    )


    quiz9 = models.IntegerField(
        label="In the following example, what is group member ID:3's signal source?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'Strong source'],
            [1, 'Weak source'],
            [2, 'I do not know'],
        ]
    )

    quiz10 = models.IntegerField(
        label="If the state is RED, you guess state BLUE, one of your group member guesses state RED, and another group member guesses state BLUE, what is your payment?",
        widget=widgets.RadioSelect,
        choices=[
            [0, '£ 0'],
            [1, '£ 2'],
            [2, '£ 6'],
        ]
    )

    quiz11 = models.IntegerField(
        label="If the state is BLUE, you guess state BLUE, one of your group member guesses state RED, and another group member guesses state BLUE, what is your payment?",
        widget=widgets.RadioSelect,
        choices=[
            [0, '£ 0'],
            [1, '£ 2'],
            [2, '£ 6'],
        ]
    )


# ------------------------------------------------------------------
# WaitPage – pattern assignment
# ------------------------------------------------------------------
class StartRoundWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def _pattern_match(slot_tag, pattern, others_tags):
        if '+' not in pattern:
            left, right = pattern, ''
        else:
            left, right = pattern.split('+', 1)


        if left == '':
            own_ok = True
        elif len(left) == 1:
            own_ok = (slot_tag and slot_tag[0] == left)
        else:
            own_ok = (slot_tag == left)
        if not own_ok:
            return False

        if right:
            required = [right[i:i+2] for i in range(0, len(right), 2)]
            return sorted(required) == sorted(others_tags)
        return True

    def after_all_players_arrive(self):
        # 1. 随机分组
        self.subsession.group_randomly()

        sv = self.session.vars
        # 2. 初始化信号表 & 已用索引
        if 'signal_table' not in sv:
            sv['signal_table'] = build_signal_table(1000)
            sv['used_records'] = set()
        table = sv['signal_table']
        used_idx = sv['used_records']

        # 3. 生成 triple_order（首次执行）
        if 'triple_order' not in sv:
            section_slices = [
                (0, 6, 8), (6, 15, 8), (15, 18, 2), (18, 22, 2)
            ]
            picks: list[tuple[str,str,str]] = []
            for start, end, quota in section_slices:
                pairs = TRIPLE_ROWS[start:end]
                num_pairs = len(pairs)
                if quota <= num_pairs:
                    idxs = random.sample(range(start, end), quota)
                    picks.extend(random.choice(TRIPLE_ROWS[i]) for i in idxs)
                else:
                    row_picks = [random.choice(pair) for pair in pairs]
                    flat = [t for pair in pairs for t in pair]
                    remaining = [t for t in flat if t not in row_picks]
                    extras = random.sample(remaining, quota - num_pairs)
                    picks.extend(row_picks + extras)
            random.shuffle(picks)
            sv['triple_order'] = picks

        # 4. 本轮部分信息模板
        trip_this_round = sv['triple_order'][self.subsession.round_number - 1]
        round_patterns = expand_triplet(trip_this_round)
        sv['pair_patterns'] = round_patterns

        # 5. 对每个 group 进行匹配
        for g in self.subsession.get_groups():
            # 5.1 计算每位玩家的未见过 patterns
            needs: dict[int, list[str]] = {}
            for p in g.get_players():
                seen = p.participant.vars.get('patterns_seen_three', [])
                unseen = [pat for pat in round_patterns if pat not in seen]
                needs[p.id_in_subsession] = unseen or list(round_patterns)

            tags_template = list(trip_this_round)  # e.g. ['rh','b','']
            best_match = None

            # —— 5.2/5.3 简化：直接随机抽一条未用记录 ——
            unused = [i for i in range(len(table)) if i not in used_idx]
            idx = random.choice(unused)
            rec = table[idx]
            used_idx.add(idx)

            # 分配 state
            state = rec['state']
            g.state = state
            for p in g.get_players():
                p.state = state

            # 按原始顺序 tags_template 分配 pattern、signal 和 quality
            patterns = expand_triplet(tuple(tags_template))
            for p, tag, pat in zip(g.get_players(), tags_template, patterns):
                p.current_pattern = pat
                if tag == '':
                    p.signals, p.qualities = '', ''
                elif len(tag) == 1:
                    p.signals, p.qualities = tag, ''
                else:
                    p.signals, p.qualities = tag[0], tag[1]
                p.participant.vars.setdefault('patterns_seen_three', []).append(pat)

            # 存回 session.vars
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
        solutions1 = {"quiz1": 0, "quiz2": 0, "quiz3": 0,  "quiz4": 1, "quiz5": 1}
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
    form_fields = ['quiz7', 'quiz8', 'quiz9']

    @staticmethod
    def error_message(player: Player, values):
        solutions2 = {"quiz7": 2, "quiz8": 2, 'quiz9': 0}
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
        solutions3 = {"quiz10": 0, "quiz11": 2}
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
        # —— 自己的信息 ——
        if player.qualities == 'h':
            my_quality = 'strong source'
        elif player.qualities == 'l':
            my_quality = 'weak source'
        else:
            my_quality = 'unknown'

        if player.signals == 'r':
            my_signal_style = (
                'height:1.4em;width:1.4em;'
                'background-color:red;'
                'border-radius:50%;display:inline-block;'
                'vertical-align:middle;margin:0 0px;'
            )
        elif player.signals == 'b':
            my_signal_style = (
                'height:1.4em;width:1.4em;'
                'background-color:blue;'
                'border-radius:50%;display:inline-block;'
                'vertical-align:middle;margin:0 0px;'
            )
        else:
            my_signal_style = 'unknown'

        # —— 其他人 ——
        others = []
        for p in player.get_others_in_group():
            # 质量标签
            if p.qualities == 'h':
                qlabel = 'strong source'
            elif p.qualities == 'l':
                qlabel = 'weak source'
            else:
                qlabel = 'unknown'

            # 信号样式
            if p.signals in ('r', 'b'):
                color = 'red' if p.signals == 'r' else 'blue'
                sig_style = (
                    'height:1.4em;width:1.4em;'
                    f'background-color:{color};'
                    'border-radius:50%;display:inline-block;'
                    'vertical-align:middle;margin:0 0px;'
                )
            else:
                sig_style = 'unknown'

            others.append({
                'id': p.id_in_group,
                'quality_label': qlabel,
                'signal_style': sig_style,
            })

        return dict(
            my_quality=my_quality,
            my_signal_style=my_signal_style,
            my_id=player.id_in_group,
            other_urns=others,
        )


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
