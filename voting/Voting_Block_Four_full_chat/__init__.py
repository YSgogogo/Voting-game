from otree.api import *
import random
from itertools import permutations

doc = """
Three-player voting experiment with send decisions + full chat.
"""


class C(BaseConstants):
    NAME_IN_URL       = 'Voting_Block_Four_full_chat'
    PLAYERS_PER_GROUP = 3
    NUM_ROUNDS        = 10
    AMOUNT_CORRECT    = 2
    CHOICES           = [('R', 'RED Box'), ('B', 'BLUE Box')]
    STATES            = ['R', 'B']
    QUALITIES         = ['h', 'l']


# ------------------------------------------------------------------
# build pre-generated signal table
# ------------------------------------------------------------------
def build_signal_table(M: int = 1000):
    """generate 1000 data"""
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


    r_count        = models.IntegerField()
    b_count        = models.IntegerField()
    current_pattern = models.StringField()

    def send_decision_choices(player):
        others = [p.signals for p in player.group.get_players() if p != player]
        if others[0] == others[1]:
            col  = 'R' if others[0] == 'r' else 'B'
            opts = [f'share with one of group members who got {col}',
                    'share with all group members',
                    'do not share with anyone']
        else:
            opts = ['share with a group member who got R',
                    'share with a group member who got B',
                    'share with all group members',
                    'do not share with anyone']
        random.shuffle(opts)
        return opts


class StartRoundWaitPage(WaitPage):

    wait_for_all_groups = True

    # -----------------------------------------------------------------
    # 1. Helper: pattern_match
    # -----------------------------------------------------------------
    @staticmethod
    def _pattern_match(slot_tag: str, pattern: str, others_tags: list[str]) -> bool:

        if '+' not in pattern:
            return slot_tag == pattern

        left, right = pattern.split('+')
        if slot_tag != left:
            return False

        required_tags = [right[i:i + 2] for i in range(0, len(right), 2)]
        return sorted(required_tags) == sorted(others_tags)

    # -----------------------------------------------------------------
    # 2. Helper:  find first satisfied pattern for a player
    # -----------------------------------------------------------------
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

    # -----------------------------------------------------------------
    # 3. Main: after_all_players_arrive
    # -----------------------------------------------------------------
    def after_all_players_arrive(self):


        self.subsession.group_randomly()


        sv = self.session.vars
        if 'signal_table' not in sv:
            sv['signal_table'] = build_signal_table(1000)
            sv['used_records'] = set()
        table: list          = sv['signal_table']
        used_idx: set[int]   = sv['used_records']

        pattern_rows: list[str] = [
            'rh+rlbl', 'bh+blrl',
            'rl+rhbl', 'bl+bhrl',
            'rh+rhbl', 'bh+bhrl',
            'rl+rlbl', 'bl+blrl',
            'rh+rlbh', 'bh+blrh',
            'rl+rhbh', 'bl+bhrh',
            'rh+rhbh', 'bh+bhrh',
            'rl+rlbh', 'bl+blrh',
            'bl+rhrh', 'rl+bhbh',
            'bl+rlrh', 'rl+blbh',
            'bl+rlrl', 'rl+blbl',
            'bh+rhrh', 'rh+bhbh',
            'bh+rlrh', 'rh+blbh',
            'bh+rlrl', 'rh+blbl',
        ]
        round_patterns = pattern_rows[:]
        random.shuffle(round_patterns)
        sv['pair_patterns'] = round_patterns

        # -----------------------------------------------------------------
        # ④ record
        # -----------------------------------------------------------------
        for g in self.subsession.get_groups():

            needs: dict[int, list[str]] = {}
            for p in g.get_players():
                seen = p.participant.vars.get('patterns_seen_four', [])
                need_list = [x for x in round_patterns if x not in seen]
                if not need_list:
                    need_list = round_patterns[:]
                needs[p.id_in_subsession] = need_list

            best_match: tuple[int, tuple, str] | None = None
            for tier in [3, 2, 1, 0]:
                for idx, rec in enumerate(table):
                    if idx in used_idx:
                        continue

                    slots = [(sid, info['signals'] + info['qualities'])
                             for sid, info in rec['players'].items()]
                    pids = [p.id_in_subsession for p in g.get_players()]

                    for perm in permutations(slots, 3):
                        tag_map = {pid: slot_tag
                                   for pid, (_, slot_tag) in zip(pids, perm)}

                        match_count = 0
                        for pid, my_tag in tag_map.items():
                            others_tags = [tag for pid2, tag in tag_map.items() if pid2 != pid]
                            need_list = needs[pid]
                            if any(self._pattern_match(my_tag, pat, others_tags) for pat in need_list):
                                match_count += 1

                        if match_count >= tier:
                            best_match = (idx, perm, rec['state'])
                            break
                    if best_match:
                        break
                if best_match:
                    break

            if not best_match:
                for idx, rec in enumerate(table):
                    if idx not in used_idx:
                        slots = [(sid, info['signals'] + info['qualities'])
                                 for sid, info in rec['players'].items()]
                        best_match = (idx, tuple(slots), rec['state'])
                        break

            idx, perm, state = best_match
            used_idx.add(idx)
            rec = table[idx]

            g.state = state
            players = g.get_players()
            for p, (sid, _) in zip(players, perm):
                info = rec['players'][sid]
                p.state     = state
                p.signals   = info['signals']
                p.qualities = info['qualities']

            for p in players:
                my_tag      = p.signals + p.qualities
                others_tags = [pl.signals + pl.qualities
                               for pl in players
                               if pl.id_in_subsession != p.id_in_subsession]
                matched = self._find_pattern(my_tag, others_tags, round_patterns)
                p.current_pattern = matched
                p.participant.vars.setdefault('patterns_seen_four', []).append(matched)

            g._count_signals()
            for p in players:
                p.r_count = g.r_count
                p.b_count = g.b_count

        sv['used_records'] = used_idx



class Main_Instructions(Page):
    @staticmethod
    def is_displayed(player):
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
                p.role_in_lottery = 'sender'

            for sender in ps:
                if 'do not share' in sender.send_decision:
                    continue

                if 'share with all group members' in sender.send_decision:
                    for rec in ps:
                        if rec != sender:
                            rec.info_from_whom += f',{sender.id_in_group}'

                else:
                    tgt = 'r' if 'got R' in sender.send_decision else 'b'
                    cand = [x for x in ps if x != sender and x.signals == tgt]
                    if cand:
                        rec = random.choice(cand)
                        rec.info_from_whom += f',{sender.id_in_group}'

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
    Main_Instructions,
    ResultsWaitPage1,
    Info_and_decision,
    ResultsWaitPage2,
    network_and_voting,
    ResultsWaitPage3,
    ResultsWaitPage4,
    ResultsWaitPage5,
    FinalResults,
]
