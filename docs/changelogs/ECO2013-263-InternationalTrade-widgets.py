# -*- coding: utf-8 -*-
"""International Trade: the eight figures as widgets.

Built against the source artwork, figure by figure. The conventions below are
the printed ones, kept identical across all eight so a student reading the
chapter straight through sees the same picture mean the same thing:

  curves      D and S, always those two letters
  P axis      P* the no-trade price, Pw the world price, Pw+t with a tariff
  Q axis      Qd and Qs where the world price meets D and S
  guides      P* gets the horizontal leg only, Qd/Qs the vertical leg only
  shading     CS teal, PS orange, gains teal, deadweight loss red
  braces      exports above the world-price line, imports below it, inside
              the plot -- never under the axis except where the source puts
              them there (figure 8)
  numbers     every tick, quantity and surplus figure is the source's own

Symbolic panels use the house 110x110 with equilibrium at [50,50]; D is
p = 100 - q and S is p = q, so the world price at 75 or 25 meets them at
round quantities. No price tick is drawn on those, per rule 3.
"""

# ---- symbolic building blocks ---------------------------------------------

def D():  return {"id": "D", "label": "D", "pts": [[4, 96], [92, 8]], "ldx": 6, "ldy": -8}
def S():  return {"id": "S", "label": "S", "pts": [[8, 8], [100, 100]], "ldx": -20, "ldy": -10}

def EQ(both=False):
    """The no-trade equilibrium. `both` draws the full elbow, for a panel whose
    point is the autarky quantity; otherwise only the leg to P*."""
    p = {"q": 50, "p": 50, "pl": "P*"}
    if both:
        p["ql"] = "Qᴅ = Qꜱ"          # the full elbow is the default
    else:
        p["guides"] = "p"
        p["showQ"] = False
    return p

def QMARK(q, name, p):
    """Qd or Qs on the axis, at the price where the world price meets the curve.
    The brace draws the vertical guide, so this is the name alone -- two guides
    down the same line read as a double-struck rule."""
    return {"q": q, "p": p, "dot": False, "guides": False, "showP": False, "ql": name}

def PW(p, tag="World Price", color=None, tagdy=None):
    h = {"p": p, "label": "Pᵂ", "tag": tag}
    if tagdy is not None:
        h["tagdy"] = tagdy
    if color:
        h["color"] = color
    return h

CS_T, PS_T, REV = "teal", "orange", "navy"

W = {}

# --- 01  Exporter or importer? ---------------------------------------------
W["01"] = {
 "lede": "Compare the world price with the domestic no-trade price.",
 "scenarios": {
  "exp": {"label": "Domestic price below the world price",
   "title": "The country is a net exporter",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(75, tagdy=14)],
   "points": [EQ(), QMARK(25, "Qᴅ", 75), QMARK(75, "Qꜱ", 75)],
   "braces": [{"p": 75, "q1": 25, "q2": 75, "label": "Exports"}],
   "caption": "The world price sits above the price this market would reach on its own. Domestic producers supply more than domestic buyers want at that price, and the gap between the two is what the country exports."},
  "imp": {"label": "Domestic price above the world price",
   "title": "The country is a net importer",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(25)],
   "points": [EQ(), QMARK(25, "Qꜱ", 25), QMARK(75, "Qᴅ", 25)],
   "braces": [{"p": 25, "q1": 25, "q2": 75, "label": "Imports", "below": "in"}],
   "caption": "The world price sits below the price this market would reach on its own. Domestic buyers want more than domestic producers will supply at that price, and the gap between the two is what the country imports."}}}

# --- 02  Exports: surplus before and after trade ----------------------------
W["02"] = {
 "lede": "The same export market, with the world price and without it.",
 "scenarios": {
  "no": {"label": "No trade",
   "title": "Before trade: the market clears on its own",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "areas": [{"pts": [[0, 50], [0, 100], [50, 50]], "label": "CS", "color": CS_T, "lp": [13, 67]},
             {"pts": [[0, 50], [0, 0], [50, 50]], "label": "PS", "color": PS_T, "lp": [13, 33]}],
   "points": [EQ(both=True)],
   "caption": "Without trade the market settles where the curves cross, and the surplus splits between buyers and sellers in the usual way."},
  "yes": {"label": "With trade",
   "title": "After trade: the domestic price rises to the world price",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(75, tagdy=14)],
   "areas": [{"pts": [[0, 75], [0, 100], [25, 75]], "label": "CS", "color": CS_T, "lp": [6, 83]},
             {"pts": [[0, 75], [0, 0], [75, 75]], "label": "PS", "color": PS_T, "lp": [21, 36]}],
   "points": [EQ(), QMARK(25, "Qᴅ", 75), QMARK(75, "Qꜱ", 75)],
   "braces": [{"p": 75, "q1": 25, "q2": 75, "label": "Exports"}],
   "caption": "Every unit now sells at the world price, so buyers pay more and take less while sellers supply more. Consumer surplus shrinks, producer surplus grows by more than that, and total surplus rises."}}}

# --- 03  Apples: a numerical export example --------------------------------
# Stated: autarky $3 and 80 units; world price $4; 40 demanded, 160 supplied,
# 120 exported. CS/PS/TS $80/$40/$120 then $20/$160/$180, a $60 gain.
APPLE_D = {"id": "D", "label": "D", "pts": [[0, 5], [180, 0.5]], "ldx": 6, "ldy": -8}
APPLE_S = {"id": "S", "label": "S", "pts": [[0, 2], [200, 4.5]], "ldx": -20, "ldy": -10}
W["03"] = {
 "lede": "The apple market, with the world price and without it.",
 "scenarios": {
  "no": {"label": "No trade (autarky)",
   "title": "Apples without trade",
   "axes": {"x": "Q", "y": "P", "xmax": 210, "ymax": 5.5, "money": True,
            "xticks": [80], "yticks": [2, 3, 5]},
   "curves": [APPLE_D, APPLE_S],
   "areas": [{"pts": [[0, 3], [0, 5], [80, 3]], "label": "CS", "color": CS_T, "lp": [22, 3.7]},
             {"pts": [[0, 3], [0, 2], [80, 3]], "label": "PS", "color": PS_T, "lp": [22, 2.65]}],
   "points": [{"q": 80, "p": 3}],
   "caption": "Without trade apples clear at $3 and 80 units. Consumer surplus is $80, producer surplus is $40, and total surplus is $120."},
  "yes": {"label": "With trade",
   "title": "Apples at the world price",
   "axes": {"x": "Q", "y": "P", "xmax": 210, "ymax": 5.5, "money": True,
            "xticks": [40, 160], "yticks": [2, 3, 5]},
   "curves": [APPLE_D, APPLE_S],
   "hlines": [{"p": 4, "label": "$4", "tag": "World Price", "tagdy": 14}],
   "areas": [{"pts": [[0, 4], [0, 5], [40, 4]], "label": "CS", "color": CS_T, "lp": [11, 4.4]},
             {"pts": [[0, 4], [0, 2], [160, 4]], "label": "PS", "color": PS_T, "lp": [10.67, 2.73]}],
   "points": [{"q": 80, "p": 3, "guides": "p", "showQ": False}],
   "braces": [{"p": 4, "q1": 40, "q2": 160, "label": "120 exported"}],
   "caption": "At the world price of $4 buyers take only 40 while sellers offer 160, and the 120-unit gap is exported. Consumer surplus falls to $20, producer surplus rises to $160, and total surplus is $180 — a $60 gain from trade."}}}

# --- 04  Imports: surplus before and after trade ---------------------------
W["04"] = {
 "lede": "The same import market, with the world price and without it.",
 "scenarios": {
  "no": {"label": "No trade",
   "title": "Before trade: the market clears on its own",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "areas": [{"pts": [[0, 50], [0, 100], [50, 50]], "label": "CS", "color": CS_T, "lp": [13, 67]},
             {"pts": [[0, 50], [0, 0], [50, 50]], "label": "PS", "color": PS_T, "lp": [13, 33]}],
   "points": [EQ(both=True)],
   "caption": "Without trade the market settles where the curves cross, and the surplus splits between buyers and sellers in the usual way."},
  "yes": {"label": "With trade",
   "title": "After trade: the domestic price falls to the world price",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(25)],
   "areas": [{"pts": [[0, 25], [0, 100], [75, 25]], "label": "CS", "color": CS_T, "lp": [32.5, 57.5]},
             {"pts": [[0, 25], [0, 0], [25, 25]], "label": "PS", "color": PS_T, "lp": [8, 15]}],
   "points": [EQ(), QMARK(25, "Qꜱ", 25), QMARK(75, "Qᴅ", 25)],
   "braces": [{"p": 25, "q1": 25, "q2": 75, "label": "Imports", "below": "in"}],
   "caption": "Every unit now sells at the world price, so buyers pay less and take more while sellers supply less. Producer surplus shrinks, consumer surplus grows by more than that, and total surplus rises."}}}

# --- 05  Avocados: a numerical import example ------------------------------
# Stated: autarky $3 and 40 units; world price $2; 60 demanded, 20 supplied,
# 40 imported. CS/PS/TS $40/$40/$80 then $90/$10/$100, a $20 gain.
AVO_D = {"id": "D", "label": "D", "pts": [[0, 5], [90, 0.5]], "ldx": 6, "ldy": -8}
AVO_S = {"id": "S", "label": "S", "pts": [[0, 1], [80, 5]], "ldx": -20, "ldy": -10}
W["05"] = {
 "lede": "The avocado market, with the world price and without it.",
 "scenarios": {
  "no": {"label": "No trade (autarky)",
   "title": "Avocados without trade",
   "axes": {"x": "Q", "y": "P", "xmax": 100, "ymax": 5.5, "money": True,
            "xticks": [40], "yticks": [1, 3, 5]},
   "curves": [AVO_D, AVO_S],
   "areas": [{"pts": [[0, 3], [0, 5], [40, 3]], "label": "CS", "color": CS_T, "lp": [11, 3.7]},
             {"pts": [[0, 3], [0, 1], [40, 3]], "label": "PS", "color": PS_T, "lp": [11, 2.3]}],
   "points": [{"q": 40, "p": 3}],
   "caption": "Without trade avocados clear at $3 and 40 units. Consumer surplus is $40, producer surplus is $40, and total surplus is $80."},
  "yes": {"label": "With trade",
   "title": "Avocados at the world price",
   "axes": {"x": "Q", "y": "P", "xmax": 100, "ymax": 5.5, "money": True,
            "xticks": [20, 60], "yticks": [1, 3, 5]},
   "curves": [AVO_D, AVO_S],
   "hlines": [{"p": 2, "label": "$2", "tag": "World Price"}],
   "areas": [{"pts": [[0, 2], [0, 5], [60, 2]], "label": "CS", "color": CS_T, "lp": [4.0, 3.5]},
             {"pts": [[0, 2], [0, 1], [20, 2]], "label": "PS", "color": PS_T, "lp": [3.33, 1.5]}],
   "points": [{"q": 40, "p": 3, "guides": "p", "showQ": False}],
   "braces": [{"p": 2, "q1": 20, "q2": 60, "label": "40 imported", "below": "in"}],
   "caption": "At the world price of $2 buyers take 60 while sellers offer only 20, and the 40-unit gap is imported. Consumer surplus rises to $90, producer surplus falls to $10, and total surplus is $100 — a $20 gain from trade."}}}

# --- 06  The gains from trade ----------------------------------------------
W["06"] = {
 "lede": "Trade adds the same wedge of surplus either way round.",
 "scenarios": {
  "exp": {"label": "A net exporter",
   "title": "Gains from trade in an export market",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(75, tagdy=14)],
   "areas": [{"pts": [[50, 50], [25, 75], [75, 75]], "label": "Gain", "color": CS_T, "lp": [50, 63]}],
   "points": [EQ(), QMARK(25, "Qᴅ", 75), QMARK(75, "Qꜱ", 75)],
   "braces": [{"p": 75, "q1": 25, "q2": 75, "label": "Exports"}],
   "caption": "Consumers lose and producers gain, but the producers' gain is larger, and the shaded wedge is what society is left with on balance."},
  "imp": {"label": "A net importer",
   "title": "Gains from trade in an import market",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(25)],
   "areas": [{"pts": [[50, 50], [25, 25], [75, 25]], "label": "Gain", "color": CS_T, "lp": [43.33, 35.0]}],
   "points": [EQ(), QMARK(25, "Qꜱ", 25), QMARK(75, "Qᴅ", 25)],
   "braces": [{"p": 25, "q1": 25, "q2": 75, "label": "Imports", "below": "in"}],
   "caption": "Producers lose and consumers gain, but the consumers' gain is larger, and the shaded wedge is what society is left with on balance."}}}

# --- 07  A tariff, before and after ----------------------------------------
W["07"] = {
 "lede": "A tariff raises the price importers must charge.",
 "scenarios": {
  "free": {"label": "Free trade",
   "title": "Imports at the world price",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(25)],
   "areas": [{"pts": [[0, 25], [0, 100], [75, 25]], "label": "CS", "color": CS_T, "lp": [32.5, 57.5]},
             {"pts": [[0, 25], [0, 0], [25, 25]], "label": "PS", "color": PS_T, "lp": [8, 15]}],
   "points": [EQ(), QMARK(25, "Qꜱ", 25), QMARK(75, "Qᴅ", 25)],
   "braces": [{"p": 25, "q1": 25, "q2": 75, "label": "Imports", "below": "in"}],
   "caption": "At the world price the country buys the gap between what it wants and what it makes from abroad."},
  "tar": {"label": "With a tariff",
   "title": "The tariff raises the effective world price",
   "axes": {"xmax": 110, "ymax": 110},
   "curves": [D(), S()],
   "hlines": [PW(25, tag="World Price", color="grey"),
              {"p": 40, "label": "Pᵂ+t", "tag": "World Price + Tariff"}],
   "areas": [{"pts": [[0, 40], [0, 100], [60, 40]], "label": "CS", "color": CS_T, "lp": [17, 62]},
             {"pts": [[0, 40], [0, 0], [40, 40]], "label": "PS", "color": PS_T, "lp": [12.0, 18.67]},
             {"pts": [[40, 25], [60, 25], [60, 40], [40, 40]], "label": "", "color": REV},
             {"pts": [[25, 25], [40, 40], [40, 25]], "label": "DWL", "color": "red", "lp": [37.5, 30.5]},
             {"pts": [[60, 40], [75, 25], [60, 25]], "label": "DWL", "color": "red", "lp": [62.5, 30.5]}],
   "points": [EQ(), QMARK(40, "Qꜱ", 40), QMARK(60, "Qᴅ", 40)],
   "braces": [{"p": 25, "q1": 40, "q2": 60, "label": "Imports", "below": "in"}],
   "caption": "The price rises by the tariff, so domestic production rises, domestic consumption falls and imports shrink. The government collects the navy rectangle between the two price lines, and the two red wedges are surplus that nobody gets at all."}}}

# --- 08  A tariff: a numerical example --------------------------------------
# Stated: world price $2, tariff $0.50, imports 40 then 20, consumption 60 then
# 50, production 20 then 30. CS/PS $90/$10 then $62.50/$22.50, revenue $10,
# total surplus $100 then $95, deadweight loss $5.
W["08"] = {
 "title": "A $0.50 tariff on avocados",
 "lede": "The world price is $2. Step through what the tariff does.",
 "axes": {"x": "Q", "y": "P", "xmax": 90, "ymax": 5.5, "money": True,
          "xticks": [20, 30, 50, 60], "yticks": [1, 2, 2.5, 5]},
 "curves": [AVO_D, AVO_S],
 "hlines": [{"p": 2, "color": "grey"},
            {"p": 2.5, "at": 1}],
 "areas": [{"pts": [[0, 2], [0, 5], [60, 2]], "label": "CS", "color": CS_T, "lp": [16, 2.9], "until": 1},
           {"pts": [[0, 2], [0, 1], [20, 2]], "label": "PS", "color": PS_T, "lp": [3.33, 1.5], "until": 1},
           {"pts": [[0, 2.5], [0, 5], [50, 2.5]], "label": "CS", "color": CS_T, "lp": [13, 3.25], "at": 1},
           {"pts": [[0, 1], [0, 2.5], [30, 2.5]], "label": "PS", "color": PS_T, "lp": [3.0, 1.7], "at": 1},
           {"pts": [[30, 2], [50, 2], [50, 2.5], [30, 2.5]], "label": "", "color": REV, "at": 2},
           {"pts": [[20, 2], [30, 2.5], [30, 2]], "label": "", "color": "red", "at": 3},
           {"pts": [[50, 2.5], [60, 2], [50, 2]], "label": "", "color": "red", "at": 3}],
 # the quantities traded at each price, as dashed drops to the axis; the
 # numbers themselves are already ticks, so these add the guide and nothing else
 "points": [{"q": 20, "p": 2, "dot": False, "guides": "q", "showQ": False, "until": 1},
            {"q": 60, "p": 2, "dot": False, "guides": "q", "showQ": False, "until": 1},
            {"q": 30, "p": 2.5, "dot": False, "guides": "q", "showQ": False, "at": 1},
            {"q": 50, "p": 2.5, "dot": False, "guides": "q", "showQ": False, "at": 1}],
 "braces": [{"p": 2, "q1": 20, "q2": 60, "label": "40 imported", "below": True, "until": 1},
            {"p": 2.5, "q1": 30, "q2": 50, "label": "20 imported", "below": True, "at": 1}],
 "steps": ["At the world price of $2 the country supplies 20 units, demands 60, and imports the 40-unit difference. Consumer surplus is $90, producer surplus is $10, and total surplus is $100.",
           "The $0.50 tariff raises the price buyers pay to $2.50. Domestic supply rises to 30, demand falls to 50, and imports drop to 20. Consumer surplus falls to $62.50 while producer surplus rises to $22.50.",
           "The government collects $0.50 on each of the 20 imported units, which is $10 of tariff revenue — the navy rectangle between the two price lines.",
           "The two red triangles are surplus that nobody receives: $5 in all. Total surplus falls from $100 to $95, and that $5 is the deadweight loss the tariff creates."]}
