from otree.api import *
import random
from itertools import permutations

doc = """
Three-player voting experiment with sending decisions+partial chat.
"""

# ------------------------------------------------------------------
#  Constants
# ------------------------------------------------------------------
class C(BaseConstants):
    NAME_IN_URL       = 'Voting_try'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS        = 20
    AMOUNT_CORRECT    = 2
    CHOICES           = [('R', 'RED Box'), ('B', 'BLUE Box')]
    STATES            = ['R', 'B']
    QUALITIES         = ['h', 'l']


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
    # 按下标迭代， i=0,1,2 分别对应三位玩家
    for i, tag in enumerate(trip):
        # 分离出另外两个 slot（即便它们一样，也各保留一次）
        others = [trip[j] for j in range(3) if j != i]
        # 按字母顺序排序两个标签
        others.sort()
        # 把空字符串替换成 '0'
        others_disp = [(o if o else '0') for o in others]
        # 最终拼成 "tag+other1other2"
        patterns.append(f"{tag}+{''.join(others_disp)}")
    return patterns




class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.session.vars['signal_table'] = build_signal_table(1000)
            self.session.vars['used_records'] = set()


class Group(BaseGroup):
    state   = models.StringField()
    r_count = models.IntegerField()
    b_count = models.IntegerField()

    def _count_signals(self):
        self.r_count = sum(1 for p in self.get_players() if p.signals == 'r')
        self.b_count = C.PLAYERS_PER_GROUP - self.r_count

    def set_payoffs(self):
        correct = sum(1 for p in self.get_players() if p.vote == self.state)
        payoff = correct * C.AMOUNT_CORRECT
        for p in self.get_players():
            p.payoff_record = payoff


class Player(BasePlayer):
    timeSpent1       = models.FloatField()
    timeSpent2       = models.FloatField()
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many     = models.BooleanField(initial=False)
    quiz1            = models.IntegerField(
        label="In the following example, suppose you guess correctly, Group member ID:1 guesses correctly, and Group member ID:2 guesses incorrectly, what is your payment in this block?",
        widget=widgets.RadioSelect,
        choices=[[0, '£ 0'], [1, '£ 4'], [2, '£ 6']],
    )
    quiz2            = models.IntegerField(
        label="In the following example, suppose you share your information with Group member ID:3, what can he/she observe?",
        widget=widgets.RadioSelect,
        choices=[[0, 'only my signal'], [1, 'only my signal source'], [2, 'both of my signal and signal source']],
    )
    send_decision    = models.StringField()
    vote             = models.StringField(widget=widgets.RadioSelect, choices=C.CHOICES)
    state            = models.StringField()
    signals          = models.CharField(initial='')
    qualities        = models.StringField(initial='')
    info_from_whom   = models.StringField(initial='')
    info_codes       = models.StringField(initial='')
    role_in_lottery  = models.StringField(initial='none')
    payoff_record    = models.IntegerField(initial=0)
    selected_round   = models.IntegerField()
    # for display
    r_count          = models.IntegerField()
    b_count          = models.IntegerField()
    current_pattern  = models.StringField()

    def send_decision_choices(player):
        others = [p.signals for p in player.group.get_players() if p != player]
        if others[0] == others[1]:
            col = 'R' if others[0] == 'r' else 'B'
            opts = [f'share with a group member who got {col}', 'do not share with anyone']
        else:
            opts = ['share with a group member who got R',
                    'share with a group member who got B',
                    'do not share with anyone']
        random.shuffle(opts)
        return opts


# ------------------------------------------------------------------
# WaitPage – pattern assignment
# ------------------------------------------------------------------
class StartRoundWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def _pattern_match(slot_tag, pattern, others_tags):
        # 检查 slot_tag 是否符合部分信息 pattern
        if '+' not in pattern:
            left, right = pattern, ''
        else:
            left, right = pattern.split('+', 1)

        # 自身信息匹配
        if left == '':
            own_ok = True
        elif len(left) == 1:
            own_ok = (slot_tag and slot_tag[0] == left)
        else:
            own_ok = (slot_tag == left)
        if not own_ok:
            return False

        # 其他两位玩家信息匹配
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

            # 5.2 分层匹配：优先让更多玩家符合
            for tier in [3, 2, 1, 0]:
                if best_match:
                    break
                # 随机化遍历尚未使用的记录
                unused = [i for i in range(len(table)) if i not in used_idx]
                for idx in random.sample(unused, len(unused)):
                    rec = table[idx]
                    # 对模板做全排列
                    for perm in permutations(tags_template):
                        # 构造 pid -> tag
                        pids = [p.id_in_subsession for p in g.get_players()]
                        tag_map = dict(zip(pids, perm))
                        # 计算满足 pattern 的玩家数
                        match_count = 0
                        for pid, my_tag in tag_map.items():
                            others = [t for qid, t in tag_map.items() if qid != pid]
                            if any(self._pattern_match(my_tag, pat, others)
                                   for pat in needs[pid]):
                                match_count += 1
                        if match_count >= tier:
                            best_match = (idx, perm, rec['state'])
                            break
                    if best_match:
                        break

            # 5.3 后备：若无任何匹配，直接取第一个未用记录
            if not best_match:
                unused = [i for i in range(len(table)) if i not in used_idx]
                idx = unused[0]
                best_match = (idx, tuple(tags_template), table[idx]['state'])

            # 5.4 拆 best_match 并分配 state + pattern
            idx, perm, state = best_match
            used_idx.add(idx)
            g.state = state
            for p in g.get_players():
                p.state = state

            patterns = expand_triplet(tuple(perm))
            for p, tag, pat in zip(g.get_players(), perm, patterns):
                p.current_pattern = pat
                if tag == '':
                    p.signals, p.qualities = '', ''
                elif len(tag) == 1:
                    p.signals, p.qualities = tag, ''
                else:
                    p.signals, p.qualities = tag[0], tag[1]
                p.participant.vars.setdefault('patterns_seen_three', []).append(pat)

            # 5.5 更新信号计数并写入玩家
            g._count_signals()
            for p in g.get_players():
                p.r_count = g.r_count
                p.b_count = g.b_count

        # 6. 保存已用记录索引
        sv['used_records'] = used_idx


class ResultsWaitPage1(WaitPage):
    wait_for_all_groups = True

class Info_and_decision(Page):
    form_model  = 'player'
    form_fields = ['timeSpent1', 'send_decision']

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


class ResultsWaitPage4(WaitPage):
    wait_for_all_groups = True


page_sequence = [
    StartRoundWaitPage,
    ResultsWaitPage1,
    Info_and_decision,
]
