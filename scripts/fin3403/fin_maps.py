#!/usr/bin/env python3
# Copied from the 2026-10-16 FIN3403 build area; paths are relative to a folder
# holding the unpacked "Finance P1"/"Finance P2" zips (S/fin). See CLAUDE.md.
"""Write S/fin/maps/<ChapterKey>.json for every FIN3403 chapter with calculator
screenshots. Every number here is read from the chapter's prose or the screenshot's
own register boxes (the alt texts repeat them); nothing is invented. `expect` is the
result the notes print, checked by test_hp.py against what the widget computes."""
import json, pathlib
MAPS = pathlib.Path(__file__).resolve().parent.parent / "maps"
MAPS.mkdir(exist_ok=True)

def tvm(expect, **kw):
    d = {"hp": "tvm"}; d.update(kw); d["expect"] = expect; return d
def cf(cfs, expect, **kw):
    d = {"hp": "cf", "cf": cfs}; d.update(kw); d["expect"] = expect; return d
def keys(k): return {"hp": "keys", "keys": k}
def amort(ranges, expect, **kw):
    d = {"hp": "amort", "n": 360, "iyr": 5, "pv": -300000, "pyr": 12, "ranges": ranges}; d.update(kw); d["expect"] = expect; return d
def keep(why): return {"keep": why}
def after(needle, widget, comment="below-referenced paragraph"):
    return {"after": needle, "widget": widget, "comment": comment}
def write(key, images, anchors=()):
    (MAPS / (key + ".json")).write_text(json.dumps({"images": images, "anchors": list(anchors)}, ensure_ascii=False, indent=1))

# ---------------------------------------------------------------- shared problems
fv100 = dict(n=1, iyr=7, pv=-100, pmt=0, pyr=1, solve="FV")                          # $100 for one year at 7%
pv100 = dict(n=1, iyr=7, fv=100, pmt=0, pyr=1, solve="PV", order="N,I/YR,PMT,FV,PV")
rate = dict(n=5, pv=-9000, pmt=0, fv=20000, pyr=1, solve="I/YR")                      # $9,000 -> $20,000 in 5 years
nper = dict(iyr=4.7, pv=-100, pmt=0, fv=500, pyr=12, period="month", solve="N")        # $100 -> $500 at 4.7% monthly
ann_fv = dict(n=3, iyr=7, pmt=-1000, pyr=1, solve="FV", order="N,I/YR,PMT,FV")        # $1,000 a year for 3 years at 7%
ann_pv = dict(n=3, iyr=7, pmt=-1000, pyr=1, solve="PV", order="N,I/YR,PMT,PV")
uneven = dict(iyr=8, pyr=1, solve="NPV")                                               # 1,000 / 2,000 / 3,000 / 6,000 at 8%
mortgage = dict(n=360, iyr=5, pv=-300000, pyr=12, period="month", solve="PMT", order="N,I/YR,PV,PMT")
bond = dict(n=10, pmt=110, fv=1000, pyr=1, solve="PV", order="N,I/YR,PMT,FV,PV")       # 10-year 11% annual-coupon bond
bond_semi = dict(n=20, iyr=12, pmt=55, fv=1000, pyr=2, period="half-year", solve="PV", order="N,I/YR,PMT,FV,PV")
ytm = dict(n=14, pv=-912.46, pmt=60, fv=1000, pyr=2, period="half-year", solve="I/YR")
zero = dict(n=8, pv=-492, pmt=0, fv=1000, pyr=1, solve="I/YR")
gm = dict(n=40, pv=-1141.04, pmt=41.25, fv=1000, pyr=2, period="half-year", solve="I/YR")
ibm = dict(n=7, pv=-594.05, pmt=0, fv=1000, pyr=1, solve="I/YR")
treas = dict(n=20, pv=-1453.75, pmt=38.75, fv=1000, pyr=2, period="half-year", solve="I/YR")
npv_cf = "-150000,50000x5"                                                             # $150,000 outlay, $50,000 for 5 years
full_cf = "-151000,49821x4,93321"                                                      # the chapter's capital budgeting example

bond_cases = tvm("1,000.0000", iyr=11, **bond,
                 alt=[{"label": "Case 1: at par (11%)"}, {"label": "Case 2: premium (10%)", "iyr": 10},
                      {"label": "Case 3: discount (12%)", "iyr": 12},
                      {"label": "Case 4: semi-annual (12%)", "n": 20, "iyr": 12, "pmt": 55, "pyr": 2, "period": "half-year"}],
                 alt_expect="1,000.0000|1,061.4457|943.4978|942.6504")
quote_cases = tvm("6.9357", **gm, alt=[{"label": "GM 8.25% of 2038"},
                                       {"label": "IBM zero coupon", "n": 7, "pv": -594.05, "pmt": 0, "pyr": 1, "period": "year"},
                                       {"label": "7.75% Treasury", "n": 20, "pv": -1453.75, "pmt": 38.75}],
                  alt_expect="6.9357|7.7236|2.5744")
ytm_cases = tvm("14.0021", **ytm, alt=[{"label": "Coupon bond ($912.46)"},
                                       {"label": "Zero-coupon bond ($492)", "n": 8, "pv": -492, "pmt": 0, "pyr": 1, "period": "year"}],
                alt_expect="14.0021|9.2709")
amort_cases = amort("1", "-299,639.5351", alt=[{"label": "Payment 1"}, {"label": "Payment 300", "ranges": "300"},
                                                {"label": "Payments 1–40", "ranges": "1-40"}, {"label": "Payments 321–360", "ranges": "321-360"}],
                    alt_expect="-299,639.5351|-85,339.6535|-284,345.6071|0.0250")

# ---------------------------------------------------------------- Exam 2: Time Value of Money
P = "fin3403-exam2-tvm-"
images = {
    P + "01-hp10bii-calculator.png": keys("SHIFT_O,4,="),
    P + "02-calculator-buttons-diagram.png": keep("an annotated close-up whose legend (N = ..., P/YR = ...) is content the widget would lose"),
    P + "03-calculator-input-example.png": tvm("107.0000", occurrence=2, **fv100),   # first use explains the box convention and stays a picture
    P + "06-five-year-calculation.png": tvm("140.2552", n=5, iyr=7, pv=-100, pmt=0, pyr=1, solve="FV"),
    P + "07-quarterly-compounding.png": tvm("141.4778", n=20, iyr=7, pv=-100, pmt=0, pyr=4, period="quarter", solve="FV"),
    P + "08-monthly-compounding.png": tvm("141.7625", n=60, iyr=7, pv=-100, pmt=0, pyr=12, period="month", solve="FV"),
    P + "09-continuous-compounding-timeline-2.png": keep("a timeline for the continuous-compounding formula, which the calculator cannot do"),
    P + "11-present-value-calculation.png": tvm("93.4579", **pv100),
    P + "12-five-year-present-value.png": tvm("71.2986", n=5, iyr=7, fv=100, pmt=0, pyr=1, solve="PV", order="N,I/YR,PMT,FV,PV"),
    P + "13-fifteen-year-present-value.png": tvm("315.2417", n=15, iyr=8, fv=1000, pmt=0, pyr=1, solve="PV", order="N,I/YR,PMT,FV,PV"),
    P + "14-interest-rate-calculation.png": tvm("17.3161", **rate),
    P + "15-time-period-calculation.png": tvm("411.7245", **nper),
    P + "16-pmt-button-highlight.png": keys("PMT"),
    P + "17-ordinary-annuity-fv.png": tvm("3,214.9000", **ann_fv),
    P + "18-ordinary-annuity-pv.png": tvm("2,624.3160", **ann_pv),
    P + "19-alternative-calculation.png": tvm("2,624.3160", n=3, iyr=7, fv=3214.9, pyr=1, solve="PV", order="N,I/YR,FV,PV"),
    P + "20-ordinary-annuity-timeline-2.png": keep("a timeline showing where an ordinary annuity's PV and FV are measured"),
    P + "21-annuity-due-timeline.png": keep("a timeline showing where an annuity due's PV and FV are measured"),
    P + "22-calculator-beg-end.png": keys("SHIFT_O,MAR"),
    P + "23-ordinary-annuity-recap.png": tvm("2,624.3160", **ann_pv, alt=[{"label": "PV of the ordinary annuity"},
                                             {"label": "FV of the ordinary annuity", "solve": "FV", "order": "N,I/YR,PMT,FV"}],
                                             alt_expect="2,624.3160|3,214.9000"),
    P + "24-annuity-due-pv.png": tvm("2,808.0182", beg=1, **ann_pv),
    P + "25-annuity-due-fv.png": tvm("3,439.9430", beg=1, **ann_fv),
    P + "26-uneven-cash-flows-2.png": keep("the uneven cash-flow timeline"),
    P + "27-uneven-cash-flows-breakdown-2.png": keep("the four separate present values added up by hand"),
    P + "28-cfj-npv-keys.png": cf("0,1000,2000,3000,6000", "9,432.2794", **uneven),
    P + "29-deferred-annuity.png": keep("the deferred-annuity timeline"),
    P + "30-deferred-method1.png": keep("method 1: five present values added by hand"),
    P + "31-deferred-method2.png": tvm("56,961.4841", n=5, iyr=10, pmt=-20000, pyr=1, solve="PV", order="N,I/YR,PMT,PV",
                                       then="+/-,FV|N=3,PMT=0|PV", tl_start=3,
                                       note="That is the present value at time 0 of the annuity that starts in period 4."),
    P + "39-present-value-time-zero.png": cf("0,0,0,0,20000,20000,20000,20000,20000", "56,961.4841", iyr=10, pyr=1, solve="NPV",
                                             note="The four zeros are the periods with no cash flow; leaving them out would move the annuity to periods 1 to 5."),
    P + "32-deferred-future-value.png": tvm("383,208", n=5, iyr=10, pmt=-20000, pyr=1, solve="FV", order="N,I/YR,PMT,FV",
                                            then="+/-,PV|N=12,PMT=0|FV", tl_start=3,
                                            note="The lump sum at period 8 grows for 12 more periods to period 20."),
    P + "33-amortization-diagram.png": keep("the principal/interest-over-time diagram"),
    P + "34-house-payment-example-2.png": tvm("1,610.4649", **mortgage),
    P + "35-amort-keys-2.png": keys("FV,INPUT,="),
    P + "36-single-payment-breakdown.png": amort("1;300", "-85,339.6535"),
    P + "37-first-40-payments.png": amort("1-40", "-284,345.6071"),
    P + "38-last-40-payments.png": amort("321-360", "0.0250"),
}
compounding = tvm("140.2552", n=5, iyr=7, pv=-100, pmt=0, pyr=1, solve="FV",
                  alt=[{"label": "Annual"}, {"label": "Quarterly", "n": 20, "pyr": 4, "period": "quarter"},
                       {"label": "Monthly", "n": 60, "pyr": 12, "period": "month"}], alt_expect="140.2552|141.4778|141.7625")
annuities = tvm("3,214.9000", **ann_fv, alt=[{"label": "FV of annuity"}, {"label": "PV of annuity", "solve": "PV", "order": "N,I/YR,PMT,PV"},
                                             {"label": "PV of annuity due", "solve": "PV", "order": "N,I/YR,PMT,PV", "beg": 1},
                                             {"label": "FV of annuity due", "beg": 1}],
                alt_expect="3,214.9000|2,624.3160|2,808.0182|3,439.9430")
write("Exam2-TVM", images, [
    after("<td>Monthly</td><td>12</td><td>60</td>", compounding, "below the compounding-frequency table"),
    after("<td>FV of annuity due</td>", annuities, "below the annuity examples table"),
    after("<b>House payment example:</b>", tvm("1,610.4649", **mortgage)),
    after("<td>Last 40 (321–360)</td>", amort("1-40", "-284,345.6071", alt=[{"label": "First 40 payments"}, {"label": "Last 40 payments", "ranges": "321-360"}],
                                                   alt_expect="-284,345.6071|0.0250"), "below the amortization results table"),
])

# ---------------------------------------------------------------- Exam 2: Risk and Return
write("Exam2-RiskAndReturn", {
    "fin3403-exam2-risk-return-01-expected-return-vs-risk-curve.png": keep("a conceptual risk-return chart"),
    "fin3403-exam2-risk-return-02-security-a-b-probability-histograms.png": keep("probability histograms"),
    "fin3403-exam2-risk-return-03-stock-a-b-individual-return-charts.png": keep("return charts"),
    "fin3403-exam2-risk-return-04-portfolio-combined-return-chart.png": keep("return chart"),
    "fin3403-exam2-risk-return-05-portfolio-risk-vs-number-of-stocks.png": keep("diversification chart"),
    "fin3403-exam2-risk-return-06-beta-best-fit-line-scatter-plot.png": keep("scatter plot"),
    "fin3403-exam2-risk-return-07-security-market-line-sml-diagram.png": keep("SML diagram"),
    "fin3403-exam2-risk-return-09-sml-overpriced-correctly-underpriced.png": keep("SML diagram"),
    "fin3403-exam2-risk-return-10-normal-curve-utility-stock-68-percent.png": keep("normal curve"),
    "fin3403-exam2-risk-return-11-normal-curve-tech-stock-68-percent.png": keep("normal curve"),
    "fin3403-exam2-risk-return-12-hp-10bii-calculator-sigma-plus-buttons.png":
        {"hp": "stat", "values": "0.2,0.0875,-0.063218,-0.02863,-0.042316,0.07716,0.02449,0.040837,0.096651,-0.03281,-0.007578",
         "expect": "0.07854"},
})

# ---------------------------------------------------------------- Exam 2: Bonds
P = "fin3403-exam2-bonds-"
write("Exam2-Bonds", {
    P + "02-case1-calculator-par-value.png": tvm("1,000.0000", iyr=11, **bond),
    P + "03-case2-calculator-premium.png": tvm("1,061.4457", iyr=10, **bond),
    P + "04-case3-calculator-discount.png": tvm("943.4978", iyr=12, **bond),
    P + "05-case4-calculator-semiannual.png": tvm("942.6504", **bond_semi),
    P + "06-ytm-calculator-912.png": tvm("14.0021", **ytm),
    P + "07-zero-coupon-calculator-492.png": tvm("9.2709", **zero),
    P + "08-gm-bond-ytm-calculator.png": tvm("6.9357", **gm),
    P + "09-ibm-zero-coupon-calculator.png": tvm("7.7236", **ibm),
    P + "10-treasury-bond-ytm-calculator.png": tvm("2.5744", **treas),
}, [
    after("<td>Semi-annual, discount (11% coupon, 12% rate)</td>", bond_cases, "below the calculator-inputs table"),
    after("PV=−912.46 → <b>YTM = 14%</b>", tvm("14.0021", **ytm)),
    after("PV=−492, P/YR=1 → <b>YTM = 9.27%</b>", tvm("9.2709", **zero)),
    after("PV=−1453.75 → <b>YTM = 2.57%</b>", quote_cases, "below the Treasury quote example"),
])

# ---------------------------------------------------------------- Exam 3: Cost of Capital
P = "fin3403-exam3-cost-of-capital-"
cost_debt = dict(n=20, pmt=40, fv=1000, pyr=2, period="half-year", solve="I/YR")
write("Exam3-CostOfCapital", {
    P + "01-calculator-ytm-8000.png": tvm("8.0000", pv=-1000, **cost_debt),
    P + "02-calculator-cost-of-debt-8-6045.png": tvm("8.6045", pv=-960, **cost_debt),
}, [after("<b>Bond with flotation example:</b>", tvm("8.6045", pv=-960, **cost_debt))])

# ---------------------------------------------------------------- Exam 3: Capital Budgeting
P = "fin3403-exam3-capbudget-"
mirr_fv = dict(n=5, iyr=12, pmt=50000, pyr=1, solve="FV", order="N,I/YR,PMT,FV")
write("Exam3-CapitalBudgeting", {
    P + "03-calculator-npv-180238-annuity-display.png": tvm("180,238.81", n=5, iyr=12, pmt=-50000, pyr=1, solve="PV", order="N,I/YR,PMT,PV"),
    P + "04-calculator-result-30238-npv-display.png": cf(npv_cf, "30,238.81", iyr=12, pyr=1, solve="NPV"),
    P + "06-calculator-result-120-pi-display.png": cf(npv_cf, "1.2016", iyr=12, pyr=1, solve="PI", io=150000),
    P + "07-hp10bii-calculator-irr-yr-button-location.png": keys("SHIFT_O,CST"),
    P + "09-calculator-result-198577-irr-display.png": cf(npv_cf, "19.8577", pyr=1, solve="IRR"),
    P + "11-calculator-result-317642-fv-display.png": tvm("317,642.3680", **mirr_fv),
    P + "12-calculator-result-161902-mirr-display.png": tvm("16.1902", n=5, pv=-150000, pmt=0, fv=317642.37, pyr=1, solve="I/YR", order="FV,PV,N,I/YR"),
    P + "13-cashflow-timeline-multiple-sign-changes.png": keep("a cash-flow timeline with three sign changes"),
    P + "15-calculator-result-200126-irr-example2.png": cf("-1000,200,300,400,400,500", "20.0126", solve="IRR"),
    P + "16-capital-rationing-bar-chart-irr-projects-vwxyz.png": keep("a bar chart"),
    P + "17-project-ab-size-disparity-cashflow-diagrams.png": keep("cash-flow diagrams with NPV, IRR and PI listed"),
    P + "18-project-cd-time-disparity-cashflow-diagrams.png": keep("cash-flow diagrams with NPV, IRR and PI listed"),
    P + "19-machine1-machine2-eaa-calculator-displays.png": tvm("1,264.45", n=3, iyr=12, pv=3037, pyr=1, solve="PMT", order="N,I/YR,PV,PMT",
                                                               alt=[{"label": "Machine 1"}, {"label": "Machine 2", "n": 6, "pv": 4337}], alt_expect="1,264.45|1,054.8699"),
    P + "21-cashflow-diagram-151000-49821-93321-summary.png": keep("the project's cash-flow summary diagram"),
    P + "22-calculator-result-4263206-npv-example.png": cf(full_cf, "42,632.06", iyr=14, solve="NPV"),
}, [
    after("<b>NPV = $30,238.81</b> → accept.", cf(npv_cf, "30,238.81", iyr=12, pyr=1, solve="NPV")),
    after("<b>IRR = 19.86%</b>", cf(npv_cf, "19.8577", pyr=1, solve="IRR")),
    after("<b>MIRR = 16.19%</b>", tvm("16.1902", **mirr_fv, then="+/-,FV|PV=-150000,PMT=0|I/YR",
                                      note="That is the MIRR: the rate at which the $150,000 outlay grows into the $317,642.37 the inflows are worth at the end."), "below the MIRR steps"),
    after("<b>NPV = $42,632.06 &gt; 0 → Accept the project.</b>", cf(full_cf, "42,632.06", iyr=14, solve="NPV")),
])

# ---------------------------------------------------------------- Exam 4: Exam 2 Review
P = "fin3403-exam4-exam2review-"
single_sums = tvm("107.0000", **fv100, alt=[{"label": "FV of $100"}, {"label": "PV of $100", "solve": "PV", "fv": 100, "pv": "", "order": "N,I/YR,PMT,FV,PV"},
                                            {"label": "Rate of return", "n": 5, "pv": -9000, "fv": 20000, "solve": "I/YR"},
                                            {"label": "Number of months", "iyr": 4.7, "fv": 500, "pyr": 12, "period": "month", "solve": "N"}],
                  alt_expect="107.0000|93.4579|17.3161|411.7245")
write("Exam4-Exam2Review", {
    P + "01-future-value-timeline-100-at-7-percent.png": keep("timeline"),
    P + "02-calculator-fv-100-at-7-percent-result-107.png": tvm("107.0000", **fv100),
    P + "03-timeline-continuous-compounding-1000-to-1096633.png": keep("timeline for the continuous-compounding formula"),
    P + "04-present-value-timeline-pv-unknown-fv-100.png": keep("timeline"),
    P + "05-calculator-pv-result-93-4579.png": tvm("93.4579", **pv100),
    P + "06-calculator-rate-of-return-9000-to-20000-result-17-3161.png": tvm("17.3161", **rate),
    P + "07-calculator-n-100-to-500-result-411-7245.png": tvm("411.7245", **nper),
    P + "08-ordinary-annuity-timeline-end-mode-pv-fv.png": keep("timeline"),
    P + "09-calculator-fv-ordinary-annuity-1000-3yr-7pct-result-3214.png": tvm("3,214.9000", **ann_fv),
    P + "10-calculator-pv-ordinary-annuity-1000-3yr-7pct-result.png": tvm("2,624.3160", **ann_pv),
    P + "11-annuity-due-timeline-begin-mode-pv-fv.png": keep("timeline"),
    P + "12-uneven-cashflows-timeline-1000-2000-3000-6000.png": keep("the uneven cash-flow timeline"),
    P + "13-uneven-cashflows-npv-result-9432-2794.png": cf("0,1000,2000,3000,6000", "9,432.2794", **uneven),
    P + "14-amortized-loan-payment-principal-interest-diagram.png": keep("the principal/interest-over-time diagram"),
    P + "15-calculator-amortized-loan-360-5pct-300000-result.png": tvm("1,610.4649", **mortgage),
    P + "16-calculator-input-amort-equals-keys-identified.png": keys("FV,INPUT,="),
    P + "17-amort-first-payment-breakdown-prin-360-int-1250-bal.png": amort("1", "-299,639.5351"),
    P + "19-amort-first-40-payments-prin-15654-int-48764-bal-28.png": amort("1-40", "-284,345.6071"),
    P + "20-amort-last-40-payments-prin-59223-int-5195-bal-0025.png": amort("321-360", "0.0250"),
    P + "21-calculator-ear-5pct-monthly-result-5-1162.png": tvm("5.1162", iyr=5, pyr=12, solve="EFF%"),
    P + "22-risk-return-curve-expected-return-vs-risk.png": keep("chart"),
    P + "23-diversification-portfolio-risk-chart-company-unique.png": keep("chart"),
    P + "24-beta-scatter-plot-specific-stock-returns-vs-market-.png": keep("scatter plot"),
    P + "25-security-market-line-sml-capm-chart.png": keep("SML diagram"),
    P + "27-sml-overpriced-correctly-priced-underpriced-stock.png": keep("SML diagram"),
    P + "28-calculator-bond-par-value-10yr-11pct-result-1000.png": tvm("1,000.0000", iyr=11, **bond),
    P + "29-calculator-bond-premium-10yr-10pct-result-1061-44.png": tvm("1,061.4457", iyr=10, **bond),
    P + "30-calculator-bond-discount-10yr-12pct-result-943-49.png": tvm("943.4978", iyr=12, **bond),
    P + "31-calculator-ytm-912-46-12pct-7yr-semiannual-result.png": tvm("14.0021", **ytm),
    P + "32-calculator-zero-coupon-bond-492-8yr-result-9-2709.png": tvm("9.2709", **zero),
    P + "33-calculator-gm-bond-ytm-1141-04-8-25pct-result-6-9.png": tvm("6.9357", **gm),
    P + "34-calculator-ibm-zero-coupon-ytm-594-05-7yr-result-.png": tvm("7.7236", **ibm),
    P + "35-calculator-treasury-bond-ytm-1453-75-7-75pct-resu.png": tvm("2.5744", **treas),
}, [
    after("<td>$100 → $500 @ 4.7%/mo → N = 411.72 months</td>", single_sums, "below the single-sum summary table"),
    after("<td>$1,000/yr, 3 yrs, 7%: FV=$3,214.90; PV=$2,624.32</td>",
          tvm("3,214.9000", **ann_fv, alt=[{"label": "FV of the annuity"}, {"label": "PV of the annuity", "solve": "PV", "order": "N,I/YR,PMT,PV"}], alt_expect="3,214.9000|2,624.3160"),
          "below the annuities table"),
    after("$6,000 @ 8% → NPV = $9,432.28.", cf("0,1000,2000,3000,6000", "9,432.2794", **uneven)),
    after("<b>Setup example:</b> $300,000 mortgage", tvm("1,610.4649", **mortgage)),
    after("$59,223.29 (91.94%)", amort_cases, "below the amortization results table"),
    after("EAR = <b>5.1162%</b>", tvm("5.1162", iyr=5, pyr=12, solve="EFF%")),
    after("<td>I/YR=12% → PV=$943.50</td>", tvm("1,000.0000", iyr=11, **bond, alt=[{"label": "At par (11%)"}, {"label": "Premium (10%)", "iyr": 10}, {"label": "Discount (12%)", "iyr": 12}],
                                                   alt_expect="1,000.0000|1,061.4457|943.4978"), "below the bond pricing table"),
    after("<li>Example: $492 price, 8 yrs → <b>YTM = 9.27%</b></li>", ytm_cases, "below the zero-coupon example"),
    after("PV=−1453.75 → YTM=2.57% (\"Ask Yld\")</td>", quote_cases, "below the bond-quote table"),
])

# ---------------------------------------------------------------- Exam 4: Exam 3 Review
P = "fin3403-exam4-review-"
write("Exam4-Exam3Review", {
    P + "01-single-holding-period-calculator-186.png": tvm("186.6071", n=1, iyr=12, fv=209, pmt=0, pyr=1, solve="PV", order="N,I/YR,PMT,FV,PV"),
    P + "03-npv-calculator-30238.png": cf(npv_cf, "30,238.81", iyr=12, pyr=1, solve="NPV"),
    P + "05-pi-calculator-1-20.png": cf(npv_cf, "1.2016", iyr=12, solve="PI", io=150000),
    P + "07-irr-calculator-19-8577.png": cf(npv_cf, "19.8577", pyr=1, solve="IRR"),
    P + "08-capital-rationing-irr-bar-chart.png": keep("a bar chart"),
    P + "09-size-disparity-project-a-b-timelines.png": keep("cash-flow timelines with NPV, IRR and PI listed"),
    P + "10-time-disparity-project-c-d-timelines.png": keep("cash-flow timelines with NPV, IRR and PI listed"),
    P + "11-eaa-project-a-b-calculators-2.png": tvm("1,264.45", n=3, iyr=12, pv=3037, pyr=1, solve="PMT", order="N,I/YR,PV,PMT",
                                                   alt=[{"label": "Project A"}, {"label": "Project B", "n": 6, "pv": 4337}], alt_expect="1,264.45|1,054.8699"),
    P + "13-capital-budgeting-example-cashflow-summary.png": keep("the project's cash-flow summary diagram"),
    P + "14-capital-budgeting-example-npv-42632.png": cf(full_cf, "42,632.06", iyr=14, solve="NPV"),
}, [
    after("12% → NPV = $30,238.81 → accept.", cf(npv_cf, "30,238.81", iyr=12, pyr=1, solve="NPV")),
    after("same project → IRR = 19.86% &gt; 12% → accept.", cf(npv_cf, "19.8577", pyr=1, solve="IRR")),
    after("<p>NPV = <b>$42,632.06</b> &gt; 0", cf(full_cf, "42,632.06", iyr=14, solve="NPV")),
])
print("maps written:", sorted(p.name for p in MAPS.glob("*.json")))
