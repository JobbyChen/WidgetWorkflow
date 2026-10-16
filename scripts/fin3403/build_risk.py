"""sd-graph figures for the Risk and Return chapter, reused by the Exam 2 Review.
Conceptual graphs: no numbers on the axes unless the source prints them."""
import json, math, pathlib
G = pathlib.Path("/tmp/claude-0/-home-user-WidgetWorkflow/18e4fdac-d634-5a6b-a05e-3dc28e88a03b/scratchpad/fin/graphs")
AX = lambda x, y, **k: dict({"x": x, "y": y, "xmax": 110, "ymax": 110}, **k)

def samples(f, x0, x1, n):
    return [[round(x0 + (x1 - x0) * i / n, 2), round(f(x0 + (x1 - x0) * i / n), 2)] for i in range(n + 1)]

# 1. expected return rises with risk, concave
risk_curve = {
    "title": "Risk and Expected Return",
    "axes": AX("Risk", "Expected\nReturn"),
    "curves": [{"id": "RR", "label": "", "pts": samples(lambda x: 100 * (1 - math.exp(-x / 32)), 1, 104, 12), "curved": True}],
    "caption": "Expected return rises with risk: investors take on more uncertainty only for a higher expected return, so the line climbs as risk grows."}

# 2. two probability distributions, bars as rectangles
def bars(xs, hs, w, color="orange"):
    return [{"pts": [[x - w / 2, 0], [x - w / 2, h], [x + w / 2, h], [x + w / 2, 0]], "label": "", "color": color, "edge": True} for x, h in zip(xs, hs)]
histograms = {
    "title": "Two Distributions of Possible Returns",
    "link": False,
    "panels": [
        {"heading": "Security A", "axes": AX("Return", "Probability"), "areas": bars([30, 55, 80], [36, 100, 56], 12)},
        {"heading": "Security B", "axes": AX("Return", "Probability"), "areas": bars([10 + 11 * i for i in range(9)], [12, 28, 44, 60, 68, 56, 38, 22, 12], 10)}],
    "caption": "Security B's outcomes are spread over a far wider range than Security A's, so the risk of holding B is higher even if the two expect the same return."}

# 3. two volatile stocks
kA = [[2, 38], [30, 82], [60, 36], [100, 96]]
kB = [[2, 88], [35, 28], [52, 100], [100, 48]]
stocks = {
    "title": "Two Stocks Held Separately",
    "link": False,
    "panels": [
        {"heading": "Stock A", "axes": AX("Time", "Rate of\nReturn"), "curves": [{"id": "A", "label": "k_{A}", "pts": kA, "color": "orange", "ldy": 4}]},
        {"heading": "Stock B", "axes": AX("Time", "Rate of\nReturn"), "curves": [{"id": "B", "label": "k_{B}", "pts": kB, "color": "orange", "ldy": 4}]}],
    "caption": "Held on their own, each stock's return swings widely from period to period, and the two do not swing together."}

# 4. the portfolio of the two
pA = [[2, 12], [27, 72], [45, 22], [70, 98], [100, 34]]
pB = [[2, 82], [22, 50], [36, 8], [56, 72], [100, 22]]
portfolio = {
    "title": "The Same Two Stocks in One Portfolio",
    "axes": AX("Time", "Rate of\nReturn"),
    "curves": [{"id": "A", "label": "k_{A}", "pts": pA, "color": "grey", "ldy": 4},
               {"id": "B", "label": "k_{B}", "pts": pB, "color": "grey", "ldy": 4},
               {"id": "P", "label": "k_{PORTFOLIO}", "pts": [[2, 40], [100, 62]], "color": "orange", "at": 1, "ldy": 4}],
    "steps": ["Stock A and Stock B each have volatile returns, and they tend to move in opposite directions.",
              "Combined into one portfolio, their swings offset each other and the portfolio's return is far steadier."]}

# 5. portfolio risk against the number of stocks
n_at, market = 14, 30
f5 = lambda x: market + 72 * math.exp(-(x - 1) / 20)
risk_pts = samples(f5, 1, 106, 20)
at_n = f5(n_at)
diversify = {
    "title": "How Diversification Reduces Risk",
    "axes": AX("# of Stocks\nin Portfolio", "Portfolio\nRisk"),
    "curves": [{"id": "T", "label": "Total Portfolio\nRisk", "pts": risk_pts, "curved": True, "color": "orange", "ldx": 0, "ldy": 16, "dimAt": 1}],
    "hlines": [{"p": market, "label": "", "showP": False, "color": "ink", "thin": True}],
    "points": [{"q": n_at, "p": 0, "dot": False, "ql": "n", "showP": False, "guides": False}],
    "vbraces": [{"p1": market, "p2": round(at_n, 2), "q": n_at, "label": "Company-Unique\nRisk", "at": 1, "color": "ink", "ldy": 6},
                {"p1": 0, "p2": market, "q": n_at, "label": "Market\nRisk", "at": 2, "color": "ink"}],
    "steps": ["Total portfolio risk falls as stocks are added, quickly at first and then more slowly, until it levels off.",
              "The part that diversification removes is company-unique risk: the gap between the curve and the floor it falls toward.",
              "What is left at the floor is market risk, which no number of stocks can diversify away."]}

# 6. the security market line
def sml_p(b): return 25 + 0.6 * b
sml = {
    "title": "The Security Market Line",
    "axes": AX("Beta", "Required\nRate of\nReturn", ymax=122),
    "curves": [{"id": "SML", "label": "Security\nMarket Line", "pts": [[0, sml_p(0)], [104, sml_p(104)]], "color": "orange"}],
    "points": [{"q": 0, "p": sml_p(0), "pl": "k_{rf}", "showQ": False, "guides": False, "label": "U.S. Treasury Securities", "dx": 10, "dy": 16, "at": 1},
               {"q": 30, "p": sml_p(30), "showP": False, "showQ": False, "guides": False, "label": "Below-Average Risk\n(e.g. Utility Stocks)", "dx": 8, "dy": 20, "at": 2},
               {"q": 78, "p": sml_p(78), "pl": "k_{m}", "ql": "1", "label": "Market\nAverage", "dx": 10, "dy": 16, "at": 3},
               {"q": 95, "p": sml_p(95), "showP": False, "showQ": False, "guides": False, "label": "Above-Average Risk\n(e.g. Tech Stocks)", "dx": -118, "dy": -16, "at": 4}],
    "steps": ["The security market line plots the required rate of return against beta: a straight line, because the relationship is linear.",
              "At a beta of zero sits the risk-free rate, the return on U.S. Treasury securities.",
              "A stock with a beta below one carries below-average market risk and a below-average required return.",
              "At a beta of one is the market as a whole, with required return kₘ.",
              "A stock with a beta above one carries above-average market risk and a higher required return."]}

# 7. over-, correctly and underpriced against the SML
bj = 60
sml_priced = {
    "title": "Pricing a Stock Against the Security Market Line",
    "axes": AX("Beta", "Required\nRate of\nReturn", ymax=122),
    "curves": [{"id": "SML", "label": "Security\nMarket Line", "pts": [[0, sml_p(0)], [104, sml_p(104)]], "color": "orange", "ldx": -4, "ldy": -32}],
    "points": [{"q": 0, "p": sml_p(0), "pl": "k_{rf}", "dot": False, "showQ": False, "guides": False},
               {"q": bj, "p": sml_p(bj), "pl": "k_{j}¹", "ql": "β_{j}", "label": "Correctly\nPriced Stock", "dx": 10, "dy": 14, "at": 1},
               {"q": bj, "p": sml_p(bj) + 17, "pl": "k_{j}²", "guides": "p", "showQ": False, "label": "Underpriced Stock", "dx": -112, "dy": -7, "at": 2},
               {"q": bj, "p": sml_p(bj) - 22, "pl": "k_{j}³", "guides": "p", "showQ": False, "label": "Overpriced\nStock", "dx": 10, "dy": 16, "at": 3}],
    "steps": ["The security market line says what return a stock of beta βⱼ should offer.",
              "A stock whose expected return lies on the line is correctly priced: it pays exactly what its risk requires.",
              "A stock above the line pays more than its risk requires, so it is underpriced.",
              "A stock below the line pays less than its risk requires, so it is overpriced."]}

# 8. the normal curve with the one-standard-deviation band
mu, sd = 55, 17
bell = lambda x: 100 * math.exp(-((x - mu) / sd) ** 2 / 2)
bell_pts = samples(bell, 0, 110, 22)
band = [[mu - sd, 0]] + samples(bell, mu - sd, mu + sd, 10) + [[mu + sd, 0]]
def normal_points(lo, mid, hi):
    return [{"q": mu - sd, "p": 0, "dot": False, "ql": lo, "showP": False, "guides": False, "label": "−1σ", "dx": -8, "dy": -6},
            {"q": mu + sd, "p": 0, "dot": False, "ql": hi, "showP": False, "guides": False, "label": "+1σ", "dx": -8, "dy": -6},
            {"q": mu, "p": 100, "dot": False, "ql": mid, "showP": False, "guides": "q", "label": "μ", "dx": -14, "dy": -2}]
normal = {
    "title": "Two-Thirds of Outcomes Fall Within One Standard Deviation",
    "axes": AX("Return", "Probability", bg=False),
    "curves": [{"id": "N", "label": "", "pts": bell_pts, "curved": True}],
    "areas": [{"pts": band, "label": "68%", "color": "orange", "lp": [mu + 8, 42]}],
    "scenarios": {
        "utility": {"label": "Utility Stock", "points": normal_points("7.38%", "12.35%", "17.32%"),
                    "caption": "The shaded band is one standard deviation either side of the utility stock's mean, and about two-thirds of its returns land inside it."},
        "tech": {"label": "Tech Stock", "points": normal_points("3.31%", "15.6%", "27.89%"),
                 "caption": "The tech stock's band is the same two-thirds of outcomes, but its larger standard deviation stretches it from 3.31% all the way to 27.89%."}}}

R = "fin3403-exam2-risk-return-"
E = "fin3403-exam4-exam2review-"
risk = {R + "01-expected-return-vs-risk-curve.png": risk_curve,
        R + "02-security-a-b-probability-histograms.png": histograms,
        R + "03-stock-a-b-individual-return-charts.png": stocks,
        R + "04-portfolio-combined-return-chart.png": portfolio,
        R + "05-portfolio-risk-vs-number-of-stocks.png": diversify,
        R + "07-security-market-line-sml-diagram.png": sml,
        R + "09-sml-overpriced-correctly-underpriced.png": sml_priced,
        R + "10-normal-curve-utility-stock-68-percent.png": normal,
        R + "11-normal-curve-tech-stock-68-percent.png": {"keep": "the same figure for the tech stock is a button on the widget above"}}
review = {E + "22-risk-return-curve-expected-return-vs-risk.png": risk_curve,
          E + "23-diversification-portfolio-risk-chart-company-unique.png": diversify,
          E + "25-security-market-line-sml-capm-chart.png": sml,
          E + "27-sml-overpriced-correctly-priced-underpriced-stock.png": sml_priced}
# Concise: only where the Concise's own sentence or table introduces the figure
risk_anchors = [
    {"after": "perfect diversification possible.", "image": R + "05-portfolio-risk-vs-number-of-stocks.png", "comment": "below the diversification bullets"},
    {"after": "<td>Above the line</td><td><b>Underpriced</b></td>", "image": R + "09-sml-overpriced-correctly-underpriced.png", "comment": "below the SML pricing table"},
    {"after": "~68% of outcomes fall within ±1σ of the mean.", "image": R + "10-normal-curve-utility-stock-68-percent.png", "comment": "below the one-standard-deviation sentence"}]
review_anchors = [
    {"after": "Adding stocks reduces total risk until only market risk remains.", "image": E + "23-diversification-portfolio-risk-chart-company-unique.png", "comment": "below the diversification sentence"},
    {"after": "<td>Above the SML</td><td><b>Underpriced</b></td>", "image": E + "27-sml-overpriced-correctly-priced-underpriced-stock.png", "comment": "below the SML position table"}]
(G / "Exam2-RiskAndReturn.json").write_text(json.dumps({"images": risk, "anchors": risk_anchors}, ensure_ascii=False, indent=1))
(G / "Exam4-Exam2Review-graphs.json").write_text(json.dumps({"images": review, "anchors": review_anchors}, ensure_ascii=False, indent=1))
print("written")
