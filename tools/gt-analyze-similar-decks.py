#!/usr/bin/python3

import re
import sys

# 96.4578  GW_GT_DEF_107: Battlemaster Krellus, Alpha Scimitar, Silv...
# Arena.Guild.<:-(nick)*(name)-:>: Battlemaster Krellus, Alpha Scimitar, Silv...
DECK_FMT = re.compile("^(?P<prefix>(?P<points>\s*[0-9.]+\s+)?(?P<deck_name>.+?): )(?P<cards>.*)$")
CARD_FMT = re.compile("^(?P<name>.+?)(?P<level>-\d)?\s*(?:\s+#(?P<count>\d+))?$")

class NameCount:
    def __init__(self, name, count):
        self.name = name
        self.count = count
    def __str__(self):
        return "{} #{}".format(self.name, self.count)
    def __repr__(self):
        return self.__str__()

class Deck:
    def __init__(self, name, cards, points):
        self.name = name
        self.cards = cards
        self.points = points
        self.name2card = dict([(c.name, c) for c in cards])
    def __str__(self):
        if self.points is None:
            return "({}) {}".format(self.name, str(self.cards))
        else:
            return "({}) [ {:^3.2f} ] {}".format(self.name, self.points, str(self.cards))
    def __repr__(self):
        return self.__str__()
    def cardsCount(self):
        count = 0
        for card in self.cards:
            count += card.count
        return count
    def similarity_points(self, that):
        denominator = self.cardsCount() * that.cardsCount()
        if not denominator:
            return 0
        value = 0
        def calc_value(x1, x2, scale):
            res = 0
            for name in x1.name2card.keys():
                if name not in x2.name2card:
                    continue
                card1 = x1.name2card[name]
                card2 = x2.name2card[name]
                x_count = min(card1.count, card2.count)
                res += x_count * scale
            return res
        value += calc_value(self, that, that.cardsCount())
        value += calc_value(that, self, self.cardsCount())
        return value / float(2.0 * denominator)

class CmpResult:
    def __init__(self, deck_pair, points):
        self.deck_pair = deck_pair
        self.points = points

fname = sys.argv[1]
decks = {}
with open(fname, 'r') as f:
    for line in f:
        line = line.rstrip()
        m = DECK_FMT.match(line)
        if not m:
            continue
        deck_name = m.group('deck_name')
        points = float(m.group('points')) if m.group('points') else None
        cards = []
        for card in m.group('cards').split(', '):
            m = CARD_FMT.match(card)
            if not m:
                raise Exception("bad card: " + card)
            name = m.group('name')
            count = int(m.group('count') or 1)
            cards.append(NameCount(name, count))
        decks[deck_name] = Deck(deck_name, cards, points)

deck_names = list(decks.keys())
deck_names.sort()

results = []

def show_result(r):
    n1, n2 = r.deck_pair
    d1, d2 = map(lambda n: decks[n], (n1, n2))
    print("{:<8.3f}\n\t{}\n\t{}".format(r.points, d1, d2))

for i in range(0, len(deck_names)-1):
    for j in range(i+1, len(deck_names)):
        n1, n2 = (deck_names[i], deck_names[j])
        d1, d2 = map(lambda n: decks[n], (n1, n2))
        if None not in (d1.points, d2.points) and (d1.points < d2.points):
            n1, n2 = (n2, n1)
            d1, d2 = (d2, d1)
        sim_points = d1.similarity_points(d2)
        res = CmpResult((n1, n2), sim_points)
        results.append(res)

results.sort(key = lambda x: -int(x.points*1000))
for r in results[1:max(int(len(results)/30), 1)]:
    show_result(r)
