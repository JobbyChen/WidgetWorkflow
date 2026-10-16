"""sd-graph figures for the yield curves, capital structure, break-even and capital-rationing pictures."""
import json, math, pathlib, sys
sys.path.insert(0, "/home/user/WidgetWorkflow/scripts")
from curve_shapes import cross
G = pathlib.Path("/tmp/claude-0/-home-user-WidgetWorkflow/18e4fdac-d634-5a6b-a05e-3dc28e88a03b/scratchpad/fin/graphs")
AX = lambda x, y, **k: dict({"x": x, "y": y, "xmax": 110, "ymax": 110}, **k)
def samples(f, x0, x1, n):
    return [[round(x0 + (x1 - x0) * i / n, 2), round(f(x0 + (x1 - x0) * i / n), 2)] for i in range(n + 1)]

# ---- yield curves (Markets and Interest Rates)
yc = {
    "title": "Two Shapes of the Yield Curve",
    "link": False,
    "panels": [
        {"heading": "Traditional Yield Curve", "axes": AX("Time to Maturity\n(Years)", "Yield to\nMaturity"),
         "curves": [{"id": "T", "label": "", "pts": samples(lambda x: 92 * (1 - math.exp(-x / 28)), 1, 104, 14), "curved": True, "color": "orange"}]},
        {"heading": "Inverted Yield Curve", "axes": AX("Time to Maturity\n(Years)", "Yield to\nMaturity"),
         "curves": [{"id": "I", "label": "", "pts": samples(lambda x: 18 + 78 * math.exp(-x / 28), 1, 104, 14), "curved": True, "color": "orange"}]}],
    "caption": "A traditional yield curve slopes up: longer maturities pay more. An inverted curve slopes down, which can mean the market expects rates to fall."}

# ---- the moderate view of capital structure: cost of capital is lowest at a mix of the two
opt = 42
cost = {
    "title": "The Moderate View of Capital Structure",
    "axes": AX("", "Cost of\nCapital", bg=False),
    "curves": [{"id": "K", "label": "", "pts": [[0, 72], [opt, 40], [100, 92]], "color": "ink"}],
    "points": [{"q": 0, "p": 0, "dot": False, "ql": "100%\nEquity", "showP": False, "guides": False},
               {"q": 100, "p": 0, "dot": False, "ql": "100%\nDebt", "showP": False, "guides": False},
               {"q": opt, "p": 40, "color": "red", "label": "Optimal Capital\nStructure", "dx": 12, "dy": 22, "guides": False, "showP": False, "showQ": False, "at": 1}],
    "steps": ["Moving from all equity toward some debt lowers the cost of capital, because interest is tax-deductible; too much debt raises it again as bankruptcy and agency costs mount.",
              "The optimal capital structure is the mix where the cost of capital bottoms out, somewhere between all equity and all debt."]}

# ---- EBIT-EPS crossover
debt = [[22, 0], [100, 98]]; equity = [[0, 0], [100, 62]]
ip = cross(debt, equity)
assert 30 < ip[0] < 80, ip
ebit_eps = {
    "title": "EBIT-EPS Analysis: the Indifference Point",
    "axes": AX("EBIT", "EPS", bg=False),
    "curves": [{"id": "D", "label": "Debt Plan", "pts": debt, "color": "ink", "ldy": -4},
               {"id": "E", "label": "Equity Plan", "pts": equity, "color": "ink", "ldy": 10}],
    "points": [{"q": round(ip[0], 2), "p": round(ip[1], 2), "color": "orange", "label": "Indifference\nPoint", "dx": 12, "dy": 18, "guides": "q", "showP": False, "showQ": False, "at": 1}],
    "braces": [{"p": 0, "q1": 0, "q2": round(ip[0], 2), "label": "Equity: higher EPS", "below": True, "color": "ink", "at": 2},
               {"p": 0, "q1": round(ip[0], 2), "q2": 100, "label": "Debt: higher EPS", "below": True, "color": "ink", "at": 2}],
    "steps": ["Earnings per share rise with EBIT under either financing plan, but the debt plan's line is steeper: interest is a fixed charge, so each extra dollar of EBIT is spread over fewer shares.",
              "The two lines cross at the indifference point, the level of EBIT at which both plans give the same EPS.",
              "Below that EBIT the equity plan gives the higher EPS; above it the debt plan does."]}

# ---- break-even: TR through the origin, TC from the fixed-cost intercept
def breakeven(F, v, price, title, high=False, q1=None):
    TR = [[0, 0], [100, price * 100]]
    TC = [[0, F], [100, F + v * 100]]
    bep = cross(TR, TC)
    assert 0 < bep[0] < 100 and abs(bep[1] - price * bep[0]) < 1e-6, bep
    qx = 100 if TR[1][1] <= 110 else 110 / price
    cfg = {
        "axes": AX("Quantity", "$", bg=False),
        "curves": [{"id": "TR", "label": "TR", "pts": TR, "color": "ink", "ldx": 6, "ldy": 2},
                   {"id": "TC", "label": "TC", "pts": TC, "color": "ink", "ldx": 6, "ldy": 12}],
        "points": [{"q": round(bep[0], 2), "p": round(bep[1], 2), "color": "orange", "guides": "q", "ql": "Break-Even\nPoint", "showP": False, "at": 1}],
        "vbraces": [{"p1": 0, "p2": F, "left": True, "label": "Fixed Costs", "color": "ink"}],
        "areas": [{"pts": [[0, 0], [0, F], [round(bep[0], 2), round(bep[1], 2)]], "label": "−", "color": "red", "at": 2},
                  {"pts": [[round(bep[0], 2), round(bep[1], 2)], [100, F + v * 100], [100, price * 100]], "label": "+", "color": "teal", "at": 2}],
        "braces": [{"p": 0, "q1": 0, "q2": round(bep[0], 2), "label": "Loss below the BEP", "below": True, "color": "ink", "at": 2},
                   {"p": 0, "q1": round(bep[0], 2), "q2": 100, "label": "Profit above the BEP", "below": True, "color": "ink", "at": 2}],
    }
    if q1 is not None:
        cfg["points"].append({"q": q1, "p": 0, "dot": False, "ql": "Q₁", "showP": False, "guides": False})
        cfg["vbraces"].append({"p1": F + v * q1, "p2": price * q1, "q": q1, "label": "EBIT", "color": "ink", "at": 2, "ldy": -14 if v else 0})
        cfg["braces"] = []
        for a in cfg["areas"]: a["label"] = ""      # the two-case figure carries no +/- signs in the source
    return cfg
be = breakeven(28, 0.46, 1.0, "Break-Even")
be.update({"title": "The Break-Even Point",
           "steps": ["Total revenue rises from the origin with every unit sold; total cost starts at the fixed costs and rises more slowly, at the variable cost per unit.",
                     "Where the two lines cross, revenue just covers cost: that is the break-even point, and operating income is zero.",
                     "Below the break-even quantity the firm loses money; above it, the growing gap between revenue and cost is its operating income."]})
low = breakeven(28, 0.46, 1.0, "Low", q1=84)
high = breakeven(55, 0.0, 1.0, "High", q1=84)
lev = {"title": "Low and High Operating Leverage",
       "scenarios": {"low": dict(label="Low Operating Leverage", **low), "high": dict(label="High Operating Leverage", **high)},
       "steps": ["Total revenue and total cost, with the fixed costs as the cost line's intercept.",
                 "The break-even point is where the lines cross.",
                 "At the same quantity Q₁, operating income (EBIT) is the gap between revenue and cost; with higher fixed costs the break-even point is further out and EBIT grows faster past it."]}
for sc in lev["scenarios"].values():
    sc.pop("title", None)

# ---- capital rationing by IRR
bars = [("V", 90), ("W", 72), ("X", 50), ("Y", 34), ("Z", 24)]
xs = [12 + 19 * i for i in range(5)]
cut = (xs[2] + xs[3]) / 2
irr_bars = {
    "title": "Ranking Projects by IRR Under a Limited Budget",
    "axes": AX("", "IRR", bg=False),
    "areas": [{"pts": [[x - 8, 0], [x - 8, h], [x + 8, h], [x + 8, 0]], "label": "", "color": "orange" if i < 3 else "grey", "edge": True} for i, (x, (nm, h)) in enumerate(zip(xs, bars))],
    "points": [{"q": x, "p": 0, "dot": False, "ql": nm, "showP": False, "guides": False} for x, (nm, h) in zip(xs, bars)] +
              [{"q": cut, "p": 104, "dot": False, "divider": True, "guides": "q", "showP": False, "showQ": False, "label": "Limited Capital\nBudget ($X)", "dx": -46, "dy": -4}],
    "moves": [{"from": [cut - 4, 96], "to": [cut - 30, 96], "color": "red", "offset": 0},
              {"from": [cut + 4, 96], "to": [cut + 30, 96], "color": "red", "offset": 0}],
    "caption": "Ranked by IRR, projects V, W and X fit inside the limited capital budget and are accepted; Y and Z fall past it and are rejected."}

out = {
 "Exam1-MarketsAndInterestRates": {"fin3403-exam1-markets-interest-rates-01-traditional-inverted-yield-curves.png": yc},
 "Exam4-CapitalStructure": {"fin3403-exam4-capital-structure-01-moderate-view-cost-of-capital-chart.png": cost,
                            "fin3403-exam4-capital-structure-02-ebit-eps-crossover-chart.png": ebit_eps},
 "Exam4-Leverage-graphs": {"fin3403-exam4-leverage-03-breakeven-chart-tr-tc-curves.png": be,
                           "fin3403-exam4-leverage-04-low-vs-high-operating-leverage-diagrams.png": lev},
 "Exam3-CapitalBudgeting": {"fin3403-exam3-capbudget-16-capital-rationing-bar-chart-irr-projects-vwxyz.png": irr_bars},
 "Exam4-Exam3Review": {"fin3403-exam4-review-08-capital-rationing-irr-bar-chart.png": irr_bars},
}
anchors = {
 "Exam1-MarketsAndInterestRates": [{"after": "<b>Yield curve:</b> Plots yield to maturity against time to maturity", "image": "fin3403-exam1-markets-interest-rates-01-traditional-inverted-yield-curves.png", "comment": "below the yield-curve definition"}],
 "Exam4-CapitalStructure": [{"after": "No formula exists; firms use industry-average benchmarks.", "image": "fin3403-exam4-capital-structure-01-moderate-view-cost-of-capital-chart.png", "comment": "below the moderate-view conclusion"},
                            {"after": "produce equal EPS. Above the indifference point, prefer debt; below it, prefer equity.", "image": "fin3403-exam4-capital-structure-02-ebit-eps-crossover-chart.png", "comment": "below the EBIT-EPS definition"}],
 "Exam4-Leverage-graphs": [{"after": "past break-even (double-edged sword).", "image": "fin3403-exam4-leverage-04-low-vs-high-operating-leverage-diagrams.png", "comment": "below the breakeven bullets"}],
 "Exam3-CapitalBudgeting": [{"after": "<b>Capital rationing</b>: allocating limited capital among competing projects.", "image": "fin3403-exam3-capbudget-16-capital-rationing-bar-chart-irr-projects-vwxyz.png", "comment": "below the capital-rationing definition"}],
 "Exam4-Exam3Review": [{"after": "<b>Capital rationing</b>: allocating limited capital across positive-NPV projects.", "image": "fin3403-exam4-review-08-capital-rationing-irr-bar-chart.png", "comment": "below the capital-rationing definition"}],
}
for k, v in out.items():
    (G / (k + ".json")).write_text(json.dumps({"images": v, "anchors": anchors.get(k, [])}, ensure_ascii=False, indent=1))
print("written", list(out))
