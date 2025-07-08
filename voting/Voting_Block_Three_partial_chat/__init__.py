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
    NAME_IN_URL       = 'Voting_Block_Three_partial_chat'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS        = 10
    AMOUNT_CORRECT    = 2
    CHOICES           = [('R', 'RED Box'), ('B', 'BLUE Box')]
    STATES            = ['R', 'B']
    QUALITIES         = ['h', 'l']


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
]
ALL_TRIPLES: list[tuple[str, str, str]] = [t for pair in TRIPLE_ROWS for t in pair]


def expand_triplet(trip: tuple[str, str, str]) -> list[str]:
    """
    ('rh','bh','rl') → ['rh+bhrl', 'bh+rhrl', 'rl+bhrh']
    """
    patterns = []
    for tag in trip:
        others = sorted([t for t in trip if t != tag])
        patterns.append(f"{tag}+{''.join(others)}")
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
    timeSpent1 = models.FloatField()
    timeSpent2 = models.FloatField()
    num_failed_attempts = models.IntegerField(initial=0)
    failed_too_many = models.BooleanField(initial=False)
    quiz1 = models.IntegerField(
        label="If the state is RED, you guess state RED, one of your group member guesses state BLUE, and another group member guesses state BLUE, what is your payment?",
        widget=widgets.RadioSelect,
        choices=[
            [0, '£ 0'],
            [1, '£ 2'],
            [2, '£ 6'],
        ]
    )

    quiz2 = models.IntegerField(
        label="In the following example, suppose you share your signal source with Group member ID:3, what he/she can observe?",
        widget=widgets.RadioSelect,
        choices=[
            [0, 'a strong source from Group member ID:2'],
            [1, 'a weak source from Group member ID:2'],
            [2, 'nothing from Group member ID:2'],
        ]
    )

    send_decision   = models.StringField()
    vote            = models.StringField(widget=widgets.RadioSelect,
                                         choices=C.CHOICES)
    state     = models.StringField()
    signals   = models.CharField()
    qualities = models.StringField()
    info_from_whom  = models.StringField(initial='')
    info_codes      = models.StringField(initial='')
    role_in_lottery = models.StringField(initial='none')
    payoff_record   = models.IntegerField(initial=0)
    selected_round  = models.IntegerField()

    # 显示用
    r_count        = models.IntegerField()
    b_count        = models.IntegerField()
    current_pattern = models.StringField()


    def send_decision_choices(player):
        others = [p.signals for p in player.group.get_players() if p != player]
        if others[0] == others[1]:
            col  = 'R' if others[0] == 'r' else 'B'
            opts = [f'share with a group member who got {col}',
                    'do not share with anyone']
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
    def _pattern_match(slot_tag: str, pattern: str, others_tags: list[str]) -> bool:
        if '+' not in pattern:
            return slot_tag == pattern
        left, right = pattern.split('+')
        if slot_tag != left:
            return False
        required_tags = [right[i:i + 2] for i in range(0, len(right), 2)]
        return sorted(required_tags) == sorted(others_tags)

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
        # ① random groups each round
        self.subsession.group_randomly()

        # ② retrieve signal table
        sv = self.session.vars
        if 'signal_table' not in sv:
            sv['signal_table'] = build_signal_table(1000)
            sv['used_records'] = set()
        table = sv['signal_table']
        used_idx = sv['used_records']

        # ───────────────────────────────────────────────────────────
        # ③ generate 10-round triplet schedule once,
        #    with first 6 rounds covering 6 rows, next 4 from remaining
        # ───────────────────────────────────────────────────────────
        if 'triple_order' not in sv:
            # first 6 rounds: pick one from each row, then shuffle
            row_picks = [random.choice(pair) for pair in TRIPLE_ROWS]
            random.shuffle(row_picks)
            # next 4 rounds: pick from remaining triples, then shuffle
            remaining = [t for t in ALL_TRIPLES if t not in row_picks]
            extra_picks = random.sample(remaining, C.NUM_ROUNDS - len(row_picks))
            random.shuffle(extra_picks)
            # combine: rounds 1–6 cover each row once, rounds 7–10 are extras
            sv['triple_order'] = row_picks + extra_picks

        # select this round's triplet and expand
        trip_this_round = sv['triple_order'][self.subsession.round_number - 1]
        round_patterns = expand_triplet(trip_this_round)
        sv['pair_patterns'] = round_patterns

        # ④ assignment logic (unchanged, but uses the single round_patterns)
        for g in self.subsession.get_groups():
            # 4.1 needs per player
            needs: dict[int, list[str]] = {}
            for p in g.get_players():
                seen = p.participant.vars.get('patterns_seen_three', [])
                not_seen = [pat for pat in round_patterns if pat not in seen]
                needs[p.id_in_subsession] = not_seen or round_patterns[:]

            # 4.2 tier search
            best_match = None
            for tier in [3, 2, 1, 0]:
                for idx, rec in enumerate(table):
                    if idx in used_idx:
                        continue
                    slots = [(sid, info['signals'] + info['qualities'])
                             for sid, info in rec['players'].items()]
                    pids = [p.id_in_subsession for p in g.get_players()]
                    for perm in permutations(slots, 3):
                        tag_map = {pid: slot_tag for pid, (_, slot_tag)
                                   in zip(pids, perm)}
                        match_count = 0
                        for pid, my_tag in tag_map.items():
                            others_tags = [t for qid, t in tag_map.items() if qid != pid]
                            if any(self._pattern_match(my_tag, pat, others_tags)
                                   for pat in needs[pid]):
                                match_count += 1
                        if match_count >= tier:
                            best_match = (idx, perm, rec['state'])
                            break
                    if best_match:
                        break
                if best_match:
                    break

            # 4.3 fallback
            if not best_match:
                for idx, rec in enumerate(table):
                    if idx not in used_idx:
                        slots = [(sid, info['signals'] + info['qualities'])
                                 for sid, info in rec['players'].items()]
                        best_match = (idx, tuple(slots), rec['state'])
                        break

            # 4.4 apply
            idx, perm, state = best_match  # type: ignore
            used_idx.add(idx)
            rec = table[idx]
            g.state = state
            players = g.get_players()
            for p, (sid, _) in zip(players, perm):
                info = rec['players'][sid]
                p.state     = state
                p.signals   = info['signals']
                p.qualities = info['qualities']

            # 4.5 record patterns_seen_three
            for p in players:
                my_tag = p.signals + p.qualities
                others_tags = [q.signals + q.qualities for q in players if q != p]
                matched = self._find_pattern(my_tag, others_tags, round_patterns)
                p.current_pattern = matched
                p.participant.vars.setdefault('patterns_seen_three', []).append(matched)

            # 4.6 counts for display
            g._count_signals()
            for p in players:
                p.r_count = g.r_count
                p.b_count = g.b_count

        # ⑤ persist used records
        sv['used_records'] = used_idx



class Block_three_instructions(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1


class Comprehension_Test(Page):
    form_model = 'player'
    form_fields = ['quiz1', 'quiz2']

    @staticmethod
    def error_message(player: Player, values):
        solutions = {"quiz1": 1, "quiz2": 1}
        errors = {name: 'Wrong' for name in solutions if values[name] != solutions[name]}
        if errors:
            player.num_failed_attempts += 1
            if player.num_failed_attempts >= 100:
                player.failed_too_many3 = True
            else:
                return errors
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1



class ResultsWaitPage1(WaitPage):
    wait_for_all_groups = True


class Info_and_decision(Page):
    form_model  = 'player'
    form_fields = ['timeSpent1', 'send_decision']

    @staticmethod
    def vars_for_template(player):
        my_quality = 'strong source' if player.qualities == 'h' else 'weak source'

        col = 'red' if player.signals == 'r' else 'blue'
        my_signal  = (
            f'height:1.4em;width:1.4em;background-color:{col};'
            'border-radius:50%;display:inline-block;'
            'vertical-align:middle;margin:0 0px;')

        others   = []
        for p in player.group.get_players():
            if p == player:
                continue

            quality = ('strong source' if p.qualities == 'h' else 'weak source') \
                    if str(p.id_in_group) in player.info_from_whom.split(',') \
                    else 'Unknown jar'
            col = 'red' if p.signals == 'r' else 'blue'
            signal = (
                f'height:1.4em;width:1.4em;background-color:{col};'
                'border-radius:50%;display:inline-block;'
                'vertical-align:middle;margin:0 0px;')

            others.append(dict(id=p.id_in_group, signal = signal, quality_label=quality))
        return dict( my_quality=my_quality, my_signal = my_signal,
                    my_id=player.id_in_group, other_urns=others)


class ResultsWaitPage2(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        for g in self.subsession.get_groups():
            ps = g.get_players()


            for p in ps:
                p.info_from_whom = str(p.id_in_group)
                p.role_in_lottery = 'none'

            chosen = random.choice(ps)
            role   = random.choice(['sender'])
            chosen.role_in_lottery = role


            if role == 'sender' and 'do not share' not in chosen.send_decision:
                tgt  = 'r' if 'got R' in chosen.send_decision else 'b'
                cand = [x for x in ps if x != chosen and x.signals == tgt]
                if cand:
                    rec = random.choice(cand)
                    rec.info_from_whom += f',{chosen.id_in_group}'


            for p in ps:
                codes = []
                for src_id in map(int, p.info_from_whom.split(',')):
                    src = next(x for x in ps if x.id_in_group == src_id)
                    sig = 'R' if src.signals == 'r' else 'B'
                    codes.append(f'{sig}{src.qualities}')
                p.info_codes = ','.join(codes)


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
            all_info = participant.info_from_whom

            if participant.qualities == 'l':
                quality_representation = "weak"
            else:
                quality_representation = "strong"

            box_info = quality_representation if participant.id_in_group in info_sources else 'Unknown'

            participants_info.append({
                'id_in_group': participant.id_in_group,
                'quality_representation': quality_representation,
                'player_signal_style': player_signal_style,
                'is_self': participant.id_in_group == player.id_in_group,
                'box_info': box_info,
                'all_info': all_info
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
    Block_three_instructions,
    Comprehension_Test,
    ResultsWaitPage1,
    Info_and_decision,
    ResultsWaitPage2,
    network_and_voting,
    ResultsWaitPage3,
    ResultsWaitPage4,
    ResultsWaitPage5,
    FinalResults,
]
