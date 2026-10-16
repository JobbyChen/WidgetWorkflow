# Copied from the 2026-10-16 FIN3403 build area (S/fin); see CLAUDE.md.
"""Build engine/hp10bii.js from the sample's script plus the P/YR, AMORT, EFF%,
Nj, PI, chained-stage, alternatives and statistics support the FIN3403 notes need.
Every replacement asserts it matched exactly once."""
import pathlib, sys
S = pathlib.Path("/tmp/claude-0/-home-user-WidgetWorkflow/18e4fdac-d634-5a6b-a05e-3dc28e88a03b/scratchpad/fin")
src = (S / "hp10bii.js").read_text()
out = src

def rep(old, new, count=1):
    global out
    n = out.count(old)
    assert n == count, "expected %d match(es), found %d for: %r" % (count, n, old[:70])
    out = out.replace(old, new)

# ---- header -------------------------------------------------------------
rep("""/* HP 10bII+ interactive calculator widget — hp10bii.js
 *
 * Usage (place after loading hp10bii.css):
 *
 *   TVM example (annual convention, P/YR treated as 1, rate converted by hand):
 *   <div class="hp10bii" data-n="5" data-iyr="5" data-pv="-1000" data-pmt="0" data-solve="FV"></div>
 *""", """/* HP 10bII+ interactive calculator widget — hp10bii.js  (v2, FIN3403 edition)
 *
 * Usage (place after loading hp10bii.css):
 *
 *   TVM example:
 *   <div class="hp10bii" data-n="5" data-iyr="5" data-pv="-1000" data-pmt="0" data-solve="FV"></div>
 *
 *     data-pyr="12"   payments per year: playback presses 12 [orange] P/YR after C ALL and the
 *                     calculator divides I/YR by P/YR itself (the course's convention). Without it
 *                     P/YR is 1 and a sub-annual rate is typed as an expression (data-iyr="5/12").
 *     data-solve="EFF%"  with data-iyr and data-pyr: effective annual rate via [orange] EFF%
 *     data-then="+/-,FV|N=3,PMT=0|PV"  a second stage: keys that store the answer just found
 *                     (here +/- then FV), the registers to change, and the register to solve next
 *     data-tl-start="3"  the timeline's first tick is period 3 rather than 0
 *     data-alt='[{"label":"Machine 1"},{"label":"Machine 2","n":"6","pv":"4337"}]'
 *                     a row of buttons; each entry overrides the data-* attributes it names
 *""")
rep(""" *   <div class="hp10bii-keys" data-keys="SHIFT_O,MAR"></div>
 */
(function () {""", """ *   <div class="hp10bii-keys" data-keys="SHIFT_O,MAR"></div>
 *
 *   Amortization: <div class="hp10bii-amort" data-n="360" data-iyr="5" data-pv="-300000" data-pyr="12" data-ranges="1;300"></div>
 *     data-ranges     "1;300" two single payments, "1-40;321-360" two ranges (first INPUT last)
 *   Statistics: <div class="hp10bii-stat" data-values="0.2,0.0875,-0.063218"></div>  (Σ+ each, then x̄ and Sx)
 *   Cash flows: an entry "50000x5" is 50,000 followed by 5 [orange] Nj; data-solve="PI" with
 *     data-io="150000" adds the outlay back to the NPV and divides by it; data-pyr plays P/YR first.
 */
(function () {""")

# ---- engine state ---------------------------------------------------------
rep("""  function Engine() { this.clearAll(); this.beg = false; }
  Engine.prototype.clearAll = function () {
    this.R = { "N": 0, "I/YR": 0, "PV": 0, "PMT": 0, "FV": 0 }; this.touched = {};
    this.cfs = [];
    this.clearEntry();
    this.shO = false; this.shB = false;
  };
  Engine.prototype.clearEntry = function () {
    this.entry = ""; this.hasEntry = false; this.disp = 0; this.acc = null; this.op = null;
  };""", """  function Engine() { this.pyr = 1; this.clearAll(); this.beg = false; }
  Engine.prototype.clearAll = function () {
    this.R = { "N": 0, "I/YR": 0, "PV": 0, "PMT": 0, "FV": 0 }; this.touched = {};
    this.cfs = [];
    this.stat = [];
    this.inputVal = null; this.amort = null; this.amortLabel = ""; this.lcdText = null;
    this.clearEntry();
    this.shO = false; this.shB = false;
  };
  Engine.prototype.reset = function () { this.clearAll(); this.beg = false; this.pyr = 1; };
  Engine.prototype.clearEntry = function () {
    this.entry = ""; this.hasEntry = false; this.disp = 0; this.acc = null; this.op = null;
  };
  /* Amortization the way the 10bII+ does it: the payment and each period's interest are rounded to
     the display setting (four places), PRIN and INT carry the payment's sign, BAL carries PV's. */
  Engine.prototype.amortize = function (p1, p2) {
    var r = this.R["I/YR"] / this.pyr / 100, pm = Math.abs(Math.round(this.R.PMT * 1e4) / 1e4);
    var L = Math.abs(this.R.PV), P = 0, I = 0, k, i, p;
    var sp = this.R.PMT < 0 ? -1 : 1, sb = this.R.PV < 0 ? -1 : 1;
    for (k = 1; k <= p2; k++) {
      i = Math.round(L * r * 1e4) / 1e4; p = Math.round((pm - i) * 1e4) / 1e4;
      if (k >= p1) { P += p; I += i; }
      L = Math.round((L - p) * 1e4) / 1e4;
    }
    return { p1: p1, p2: p2, prin: sp * P, int: sp * I, bal: sb * L };
  };
  Engine.prototype.mean = function () { var s = 0; this.stat.forEach(function (v) { s += v; }); return this.stat.length ? s / this.stat.length : NaN; };
  Engine.prototype.sdev = function () {
    var n = this.stat.length; if (n < 2) return NaN;
    var m = this.mean(), s = 0; this.stat.forEach(function (v) { s += (v - m) * (v - m); }); return Math.sqrt(s / (n - 1));
  };""")
rep("""  Engine.prototype.displayText = function () {
    if (this.entry !== "") return fmtEntry(this.entry);
    return fmt(this.disp);
  };
  Engine.prototype.fvOf = function (n, i, pv, pmt) {
    var r = i / 100;""", """  Engine.prototype.displayText = function () {
    if (this.entry !== "") return fmtEntry(this.entry);
    if (this.lcdText !== null) return this.lcdText;
    return fmt(this.disp);
  };
  /* i is the rate per period, in percent */
  Engine.prototype.fvOf = function (n, i, pv, pmt) {
    var r = i / 100;""")
rep("""  Engine.prototype.solveTVM = function (k) {
    var R = this.R, r = R["I/YR"] / 100, n = R.N, g = Math.pow(1 + r, n), a = this.beg ? (1 + r) : 1, x, self = this;
    if (k === "FV") x = this.fvOf(n, R["I/YR"], R.PV, R.PMT);""", """  Engine.prototype.solveTVM = function (k) {
    var R = this.R, pyr = this.pyr, ip = R["I/YR"] / pyr, r = ip / 100, n = R.N, g = Math.pow(1 + r, n), a = this.beg ? (1 + r) : 1, x, self = this;
    if (k === "FV") x = this.fvOf(n, ip, R.PV, R.PMT);""")
rep("""      x = (lo + hi) / 2;
    }
    return x;
  };
  Engine.prototype.expandCF""", """      x = (lo + hi) / 2 * pyr;   /* I/YR is reported as an annual rate: the per-period rate times P/YR */
    }
    return x;
  };
  Engine.prototype.expandCF""")

# ---- key presses ------------------------------------------------------------
rep("""    if (shO) {
      if (k === "C") { var beg = this.beg; this.clearAll(); this.beg = beg; ev.type = "clearall"; return ev; }
      if (k === "MAR") { this.beg = !this.beg; ev.type = "begend"; return ev; }""", """    if (this.lcdText !== null && !(shO && k === "FV") && k !== "=") this.lcdText = null;
    if (shO) {
      if (k === "C") { var beg = this.beg; this.clearAll(); this.beg = beg; ev.type = "clearall"; return ev; }
      if (k === "MAR") { this.beg = !this.beg; ev.type = "begend"; return ev; }
      if (k === "PMT") { var py = Math.max(1, Math.round(this.value())); this.pyr = py; this.disp = py; this.entry = ""; this.hasEntry = false; ev.type = "pyr"; ev.value = py; return ev; }
      if (k === "PV") { var ef = (Math.pow(1 + this.R["I/YR"] / this.pyr / 100, this.pyr) - 1) * 100; this.disp = ef; this.entry = ""; this.hasEntry = false; ev.type = "eff"; ev.value = ef; return ev; }
      if (k === "FV") {
        var q1, q2;
        if (this.amort && this.inputVal === null && !this.hasEntry) { q1 = this.amort.p2 + 1; q2 = q1 + (this.amort.p2 - this.amort.p1); }
        else { q1 = this.inputVal !== null ? Math.round(this.inputVal) : Math.round(this.value()); q2 = (this.inputVal !== null && this.hasEntry) ? Math.round(this.value()) : q1; }
        if (q2 < q1) { var tq = q1; q1 = q2; q2 = tq; }
        this.amort = this.amortize(q1, q2); this.amort.idx = -1; this.inputVal = null;
        this.entry = ""; this.hasEntry = false; this.lcdText = q1 + (q2 !== q1 ? " \\u2013 " + q2 : "") ; this.amortLabel = "PER";
        ev.type = "amort"; ev.value = this.amort; return ev;
      }
      if (k === "7") { var mu = this.mean(); this.disp = mu; this.entry = ""; this.hasEntry = false; ev.type = "mean"; ev.value = mu; return ev; }
      if (k === "8") { var sd = this.sdev(); this.disp = sd; this.entry = ""; this.hasEntry = false; ev.type = "sdev"; ev.value = sd; return ev; }""")
rep("""    if (k === "=") {
      var b = this.value(), res""", """    if (k === "=" && this.amort && this.op === null) {
      var am = this.amort; am.idx = (am.idx + 1) % 3;
      var lab = ["PRIN", "INT", "BAL"][am.idx], val = [am.prin, am.int, am.bal][am.idx];
      this.amortLabel = lab; this.lcdText = null; this.disp = val; this.entry = ""; this.hasEntry = false;
      ev.type = "amortval"; ev.label = lab; ev.value = val; ev.range = am; return ev;
    }
    if (k === "INPUT") { this.inputVal = this.value(); this.entry = ""; this.hasEntry = false; this.amort = null; this.amortLabel = ""; ev.type = "input"; ev.value = this.inputVal; return ev; }
    if (k === "SIGMA+") { var sv0 = this.value(); this.stat.push(sv0); this.disp = this.stat.length; this.entry = ""; this.hasEntry = false; ev.type = "sigma"; ev.value = sv0; ev.count = this.stat.length; return ev; }
    if (k === "=") {
      var b = this.value(), res""")
rep("""    if (k in this.R) {
      if (this.hasEntry) {""", """    if (k in this.R) {
      this.amort = null; this.amortLabel = "";
      if (this.hasEntry) {""")

# ---- LCD annunciators ----------------------------------------------------------
rep("""<span class="hp-ann" data-ann="pend">PEND</span></div>'""", """<span class="hp-ann" data-ann="pend">PEND</span><span class="hp-ann amort" data-ann="amort"></span></div>'""")
rep("""        this.ann.begin.classList.toggle("on", engine.beg);
        this.keyEl("SHIFT_O")""", """        this.ann.begin.classList.toggle("on", engine.beg);
        this.ann.input.classList.toggle("on", engine.inputVal !== null);
        this.ann.amort.textContent = engine.amortLabel ? "AMORT " + engine.amortLabel : "";
        this.ann.amort.classList.toggle("on", !!engine.amortLabel);
        this.keyEl("SHIFT_O")""")
rep("""    ["sho", "shb", "pend", "begin"].forEach""", """    ["sho", "shb", "pend", "begin", "input", "amort"].forEach""")

# ---- chips --------------------------------------------------------------------
rep("""        var fn = { "C": "C ALL", "MAR": "Beg/End", "PRC": "NPV", "CST": "IRR/YR", "CFj": "Nj" }[keys[i + 1]];""",
    """        var fn = { "C": "C ALL", "MAR": "Beg/End", "PRC": "NPV", "CST": "IRR/YR", "CFj": "Nj", "PMT": "P/YR", "PV": "EFF%", "FV": "AMORT", "7": "x\\u0304", "8": "Sx" }[keys[i + 1]];""")
rep("""  var LABEL = { "N": "N", "I/YR": "I/YR", "PV": "PV", "PMT": "PMT", "FV": "FV", "CFj": "CFj",""",
    """  var LABEL = { "N": "N", "I/YR": "I/YR", "PV": "PV", "PMT": "PMT", "FV": "FV", "CFj": "CFj", "SIGMA+": "\\u03a3+", "INPUT": "INPUT",""")

# ---- timeline start offset -------------------------------------------------------
rep("""    var n = Math.max(1, Math.round(opts.n));
    var showAll = n <= 7, cols = showAll ? n + 1 : 6;""", """    var n = Math.max(1, Math.round(opts.n)), t0 = opts.start || 0;
    var showAll = n <= 7, cols = showAll ? n + 1 : 6;""")
rep("""      s += '<text x="' + x + '" y="' + (AX + 22) + '" font-size="12" text-anchor="middle" fill="#444" ' + FF + '>' + t + '</text>';""",
    """      s += '<text x="' + x + '" y="' + (AX + 22) + '" font-size="12" text-anchor="middle" fill="#444" ' + FF + '>' + (t + t0) + '</text>';""")

# ---- player: restart resets P/YR too --------------------------------------------------
rep("""    this.pos = -1; this.engine.clearAll(); this.engine.beg = false; this.view.render();
    this.caption.innerHTML = this.steps.intro || "";""", """    this.pos = -1; this.engine.reset(); this.view.render();
    this.caption.innerHTML = this.steps.intro || "";""")
rep("""    this.engine.clearAll(); this.engine.beg = false;
    var i, j, last = null;""", """    this.engine.reset();
    var i, j, last = null;""")
rep("""    else if (ev.type === "nj") msg = "Nj: repeat count set for the last cash flow.";""",
    """    else if (ev.type === "nj") msg = "Nj: repeat count set for the last cash flow.";
    else if (ev.type === "pyr") msg = "P/YR = " + ev.value + ": the calculator now counts " + ev.value + " period" + (ev.value === 1 ? "" : "s") + " a year and divides I/YR by " + ev.value + ".";
    else if (ev.type === "eff") msg = "EFF% = " + fmt(ev.value) + "%: the effective annual rate for " + plain(this.engine.R["I/YR"]) + "% compounded " + this.engine.pyr + " times a year.";
    else if (ev.type === "input") msg = "INPUT: " + fmt(ev.value) + " held as the first payment of the range.";
    else if (ev.type === "amort") msg = "AMORT for payment" + (ev.value.p2 !== ev.value.p1 ? "s " + ev.value.p1 + " to " + ev.value.p2 : " " + ev.value.p1) + ". Press = for PRIN, = again for INT, = again for BAL.";
    else if (ev.type === "amortval") msg = ev.label + " = " + fmt(ev.value);
    else if (ev.type === "sigma") msg = "\\u03a3+: " + ev.count + " value" + (ev.count === 1 ? "" : "s") + " entered.";
    else if (ev.type === "mean") msg = isFinite(ev.value) ? "x\\u0304 = " + fmt(ev.value, 5) : "Enter some values with \\u03a3+ first.";
    else if (ev.type === "sdev") msg = isFinite(ev.value) ? "Sx = " + fmt(ev.value, 5) : "Sx needs at least two values.";""")

# ---- TVM widget: P/YR, EFF%, then-stage, tl-start ---------------------------------------
rep("""    var spec = { "N": d.n, "I/YR": d.iyr, "PV": d.pv, "PMT": d.pmt, "FV": d.fv };
    var beg = d.beg === "1" || d.beg === "true";
    var period = d.period || "year";
    var periods = period + "s";
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var vals = {};
    order.forEach(function (k) { vals[k] = spec[k] === undefined ? 0 : evalSpec(spec[k]); });
""", """    var spec = { "N": d.n, "I/YR": d.iyr, "PV": d.pv, "PMT": d.pmt, "FV": d.fv };
    var beg = d.beg === "1" || d.beg === "true";
    var period = d.period || "year";
    var periods = period + "s";
    var pyr = d.pyr ? Math.max(1, Math.round(evalSpec(d.pyr))) : 0;   /* 0: no P/YR step is played */
    var eff = solve === "EFF%";
    if (eff) order = ["I/YR"];
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var vals = {};
    order.forEach(function (k) { vals[k] = spec[k] === undefined ? 0 : evalSpec(spec[k]); });
    /* a second stage: "store keys|REG=val,REG=val|SOLVE" */
    var then = null;
    if (d.then) {
      var tp = d.then.split("|");
      then = { store: tp[0].split(",").map(function (s) { return s.trim(); }).filter(Boolean),
               set: (tp[1] || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean).map(function (kv) { var p = kv.split("="); var kk = p[0].trim().toUpperCase(); return { k: kk === "I" ? "I/YR" : kk, s: p[1].trim() }; }),
               solve: (tp[2] || "FV").trim().toUpperCase() };
      if (then.solve === "I") then.solve = "I/YR";
    }
""")
rep("""    var tlHTML = "";
    if (d.timeline !== "0") {
      var n = vals.N || 1, flows = {}, pmtLabel = "";""", """    var tlHTML = "";
    if (d.timeline !== "0" && !eff) {
      var n = vals.N || 1, flows = {}, pmtLabel = "";""")
rep("""      var tl = timelineSVG({ n: solve === "N" ? 5 : n, flows: flows, pmtLabel: pmtLabel, unitLabel: solve === "N" ? "N = ?  (" + periods + ")" : periods });""",
    """      var tl = timelineSVG({ n: solve === "N" ? 5 : n, flows: flows, pmtLabel: pmtLabel, unitLabel: solve === "N" ? "N = ?  (" + periods + ")" : periods, start: d.tlStart ? parseInt(d.tlStart, 10) : 0 });""")
rep("""    var regsHTML = '<div class="hp-regs">' + ["N", "I/YR", "PV", "PMT", "FV"].map(function (k) { return '<div data-reg="' + k + '">' + k + "<b>—</b></div>"; }).join("") + "</div>";
    var side = sideShell(tlHTML + regsHTML);
    root.appendChild(side);

    /* build steps */
    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () {
      return "Press the orange shift key, then <b>C</b>. This runs <b>C ALL</b> and wipes every register (N, I/YR, PV, PMT, FV) left over from the previous problem. It does <i>not</i> change the BEGIN/END setting" +
        (beg ? ", which we'll set next." : ", so check that <b>BEGIN</b> is not showing on the display. If it is, press the orange shift key and <b>MAR</b> to get back to END mode.");
    } });""", """    var regNames = eff ? ["I/YR", "P/YR"] : (pyr ? ["N", "I/YR", "PV", "PMT", "FV", "P/YR"] : ["N", "I/YR", "PV", "PMT", "FV"]);
    var regsHTML = '<div class="hp-regs' + (regNames.length === 6 ? " hp-regs6" : "") + '">' + regNames.map(function (k) { return '<div data-reg="' + k + '">' + k + "<b>—</b></div>"; }).join("") + "</div>";
    var side = sideShell(tlHTML + regsHTML);
    root.appendChild(side);

    /* build steps */
    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () {
      return "Press the orange shift key, then <b>C</b>. This runs <b>C ALL</b> and wipes every register (N, I/YR, PV, PMT, FV) left over from the previous problem. It does <i>not</i> change the BEGIN/END setting" +
        (beg ? ", which we'll set next." : ", so check that <b>BEGIN</b> is not showing on the display. If it is, press the orange shift key and <b>MAR</b> to get back to END mode.");
    } });
    if (pyr) steps.push({ keys: numKeys(String(pyr)).concat(["SHIFT_O", "PMT"]), text: function () {
      return "Type " + pyr + ", press the orange shift key, then <b>PMT</b> to run <b>P/YR</b>. " +
        (pyr === 1 ? "Interest compounds once a year here, so P/YR is 1. Entering it every time is the habit that saves you when the last problem left it at 12." :
          "Interest compounds " + pyr + " times a year, so the calculator must count " + pyr + " periods per year: N is then in " + periods + ", and I/YR is still the annual rate because the calculator divides it by " + pyr + " for you.");
    } });""")
rep("""        if (k === "I/YR") {
          if (s.indexOf("/") >= 0) return typed""", """        if (k === "I/YR") {
          if (eff) return typed + "This is the quoted (nominal) annual rate, " + plain(v) + "%.";
          if (pyr > 1) return typed + "I/YR is always the <i>annual</i> rate. Do not divide it by " + pyr + ": with P/YR = " + pyr + " the calculator uses " + plain(v) + "% \\u00f7 " + pyr + " = " + fmt(v / pyr) + "% per " + period + " on its own.";
          if (s.indexOf("/") >= 0) return typed""")
rep("""    steps.push({ keys: [solve], text: function (evs) {
      var ev = evs[0], r = ev.value, res;
      if (!isFinite(r)) return "Press <b>" + solve + "</b>. The calculator can't find a solution with these inputs.";""", """    if (eff) steps.push({ keys: ["SHIFT_O", "PV"], text: function (evs) {
      var r = evs[evs.length - 1].value;
      return "Press the orange shift key, then <b>PV</b> to run <b>EFF%</b>: <span class='hp-res'>" + fmt(r) + "%</span>. That is the effective annual rate, (1 + " + plain(vals["I/YR"]) + "% \\u00f7 " + pyr + ")<sup>" + pyr + "</sup> \\u2212 1: what " + plain(vals["I/YR"]) + "% really costs when it compounds " + pyr + " times a year." + (d.note ? " " + d.note : "");
    } });
    else steps.push({ keys: [solve], text: function (evs) {
      var ev = evs[0], r = ev.value, res;
      if (!isFinite(r)) return "Press <b>" + solve + "</b>. The calculator can't find a solution with these inputs.";""")
rep("""      else if (solve === "I/YR") t += "This is the rate per " + period + " implied by the other four values.";
      if (d.note) t += " " + d.note;
      return t;
    } });
    steps.intro = "Press <b>Play</b> to step through the keystrokes" + (beg ? " for this annuity due." : ".");
""", """      else if (solve === "I/YR") t += (pyr > 1 ? "This is an annual rate: the rate per " + period + " times " + pyr + "." : "This is the rate per " + period + " implied by the other four values.");
      if (d.note && !then) t += " " + d.note;
      if (then) t += " That answer is the input to the next step.";
      return t;
    } });
    if (then) {
      var storeReg = then.store[then.store.length - 1];
      steps.push({ keys: then.store.slice(), text: function (evs) {
        var ev = evs[evs.length - 1];
        return "The answer is still on the display, so there is nothing to retype: " + (then.store[0] === "+/-" ? "press <b>+/\\u2212</b> to flip its sign, then " : "press ") + "<b>" + storeReg + "</b> to store it as " + FULLNAME[storeReg] + " of the next calculation (" + fmt(ev.value) + "). The other registers keep their values.";
      } });
      then.set.forEach(function (e) {
        steps.push({ keys: numKeys(e.s).concat([e.k]), text: function () {
          var v = evalSpec(e.s);
          if (e.k === "PMT" && v === 0) return "Type 0, then press <b>PMT</b>. The second calculation is a single sum, so the payment that drove the first one has to be cleared out.";
          if (e.k === "N") return "Type " + specText(e.s) + ", then press <b>N</b>: " + plain(v) + " " + (v === 1 ? period : periods) + " separate the amount just stored from where it is being moved to.";
          return "Type " + specText(e.s) + ", then press <b>" + e.k + "</b>.";
        } });
      });
      steps.push({ keys: [then.solve], text: function (evs) {
        var r = evs[0].value;
        var t = "Press <b>" + then.solve + "</b>: <span class='hp-res'>" + fmt(r) + "</span>. ";
        var first = fmt(Math.abs(engine.R[storeReg])), nset = engine.R.N;
        if (then.solve === "PV") t += "That is the " + first + " found first, discounted " + plain(nset) + " more " + (nset === 1 ? period : periods) + " back to the start of the timeline" + (r < 0 ? "; the minus sign only says it is the amount paid out today." : ".");
        else if (then.solve === "FV") t += "That is the " + first + " found first, compounded " + plain(nset) + " more " + (nset === 1 ? period : periods) + " forward to the end of the timeline" + (r < 0 ? "; the minus sign only marks the direction of the cash flow." : ".");
        else if (then.solve === "I/YR") t = "Press <b>I/YR</b>: <span class='hp-res'>" + fmt(r) + "%</span>. That is the annual rate at which the present value just entered grows into the future value stored a moment ago.";
        if (d.note) t += " " + d.note;
        return t;
      } });
    }
    steps.intro = "Press <b>Play</b> to step through the keystrokes" + (beg ? " for this annuity due." : ".");
""")
rep("""    var refresh = function (ev) {
      ["N", "I/YR", "PV", "PMT", "FV"].forEach(function (k) {
        var cell = regEls[k], b = cell.querySelector("b");
        var touched = !!engine.touched[k];
        b.textContent = touched ? fmt(engine.R[k]) : "—";
        cell.classList.toggle("hp-stored", !!(ev && ev.type === "store" && ev.reg === k));
        cell.classList.toggle("hp-solved", !!(ev && ev.type === "solve" && ev.reg === k));
      });
    };
    new Player(root, engine, view, steps, side, refresh);
  }""", """    var refresh = function (ev) {
      regNames.forEach(function (k) {
        var cell = regEls[k], b = cell.querySelector("b");
        if (k === "P/YR") {
          b.textContent = ev && ev.type === "eff" ? fmt(ev.value) + "%" : String(engine.pyr);
          cell.classList.toggle("hp-stored", !!(ev && ev.type === "pyr"));
          cell.classList.toggle("hp-solved", !!(ev && ev.type === "eff"));
          if (eff) cell.firstChild.textContent = ev && ev.type === "eff" ? "EFF%" : "P/YR";
          return;
        }
        var touched = !!engine.touched[k];
        b.textContent = touched ? fmt(engine.R[k]) : "—";
        cell.classList.toggle("hp-stored", !!(ev && ev.type === "store" && ev.reg === k));
        cell.classList.toggle("hp-solved", !!(ev && ev.type === "solve" && ev.reg === k));
      });
    };
    new Player(root, engine, view, steps, side, refresh);
  }

  /* ------------------------------------------------------------------ */
  /* Amortization widget                                                   */
  /* ------------------------------------------------------------------ */
  function initAmort(root) {
    var d = root.dataset;
    var pyr = d.pyr ? Math.max(1, Math.round(evalSpec(d.pyr))) : 1;
    var period = d.period || (pyr === 12 ? "month" : pyr === 4 ? "quarter" : "year");
    var ranges = (d.ranges || "1").split(";").map(function (s) { s = s.trim(); var m = s.match(/^(\\d+)\\s*[-\\u2013]\\s*(\\d+)$/); return m ? [parseInt(m[1], 10), parseInt(m[2], 10)] : [parseInt(s, 10), parseInt(s, 10)]; });
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);
    var regNames = ["N", "I/YR", "PV", "PMT", "FV", "P/YR"];
    var regsHTML = '<div class="hp-regs hp-regs6">' + regNames.map(function (k) { return '<div data-reg="' + k + '">' + k + "<b>—</b></div>"; }).join("") + "</div>" +
      '<div class="hp-regs hp-regs3">' + ["PRIN", "INT", "BAL"].map(function (k) { return '<div data-out="' + k + '">' + k + "<b>—</b></div>"; }).join("") + "</div>";
    var side = sideShell(regsHTML);
    root.appendChild(side);
    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () { return "Press the orange shift key, then <b>C</b> to run <b>C ALL</b>, so nothing from the last problem is left in the registers."; } });
    var setup = numKeys(String(pyr)).concat(["SHIFT_O", "PMT"]).concat(numKeys(d.n)).concat(["N"]).concat(numKeys(d.iyr)).concat(["I/YR"]).concat(numKeys(d.pv)).concat(["PV"]);
    if (d.fv !== undefined) setup = setup.concat(numKeys(d.fv)).concat(["FV"]);
    setup.push("PMT");
    steps.push({ keys: setup, text: function (evs) {
      var r = evs[evs.length - 1].value;
      return "Put the loan back in: " + pyr + " P/YR, " + plain(evalSpec(d.n)) + " N, " + plain(evalSpec(d.iyr)) + " I/YR, " + specText(d.pv) + " PV" + (d.fv !== undefined ? ", " + specText(d.fv) + " FV" : "") + ", then press <b>PMT</b>. The display shows the payment, <span class='hp-res'>" + fmt(r) + "</span>, and the amortization keys work from exactly these five registers.";
    } });
    ranges.forEach(function (rg) {
      var single = rg[0] === rg[1];
      var keys = numKeys(String(rg[0])).concat(["INPUT"]);
      if (!single) keys = keys.concat(numKeys(String(rg[1])));
      keys = keys.concat(["SHIFT_O", "FV"]);
      steps.push({ keys: keys, text: function () {
        return (single ? "Type " + rg[0] + ", press <b>INPUT</b>, then the orange shift key and <b>FV</b> to run <b>AMORT</b>. "
          : "Type " + rg[0] + ", press <b>INPUT</b>, type " + rg[1] + ", then the orange shift key and <b>FV</b> to run <b>AMORT</b>. ") +
          "The display shows the range of payments it is about to break down" + (single ? " (" + period + " " + rg[0] + " alone)" : " (" + periods(period) + " " + rg[0] + " to " + rg[1] + ")") + ". Nothing has been calculated yet: the three answers come out one <b>=</b> at a time.";
      } });
      steps.push({ keys: ["="], text: function (evs) { return "Press <b>=</b>: <b>PRIN</b> shows in the display, <span class='hp-res'>" + fmt(evs[0].value) + "</span>. That is how much of " + (single ? "this payment" : "these " + (rg[1] - rg[0] + 1) + " payments") + " goes toward paying down the principal."; } });
      steps.push({ keys: ["="], text: function (evs) { return "Press <b>=</b> again: <b>INT</b>, <span class='hp-res'>" + fmt(evs[0].value) + "</span>. That is the interest paid" + (single ? " with this payment." : " over the same payments."); } });
      steps.push({ keys: ["="], text: function (evs) { return "Press <b>=</b> a third time: <b>BAL</b>, <span class='hp-res'>" + fmt(evs[0].value) + "</span>. That is the balance still owed after payment " + rg[1] + (evs[0].value < 0 ? " (negative because it is money you still owe)." : ".") + (d.note && rg === ranges[ranges.length - 1] ? " " + d.note : ""); } });
    });
    steps.intro = "Press <b>Play</b> to step through the keystrokes.";
    var regEls = {}, outEls = {};
    side.querySelectorAll("[data-reg]").forEach(function (e) { regEls[e.getAttribute("data-reg")] = e; });
    side.querySelectorAll("[data-out]").forEach(function (e) { outEls[e.getAttribute("data-out")] = e; });
    var refresh = function (ev) {
      regNames.forEach(function (k) {
        var cell = regEls[k], b = cell.querySelector("b");
        if (k === "P/YR") { b.textContent = String(engine.pyr); cell.classList.toggle("hp-stored", !!(ev && ev.type === "pyr")); return; }
        b.textContent = engine.touched[k] ? fmt(engine.R[k]) : "—";
        cell.classList.toggle("hp-stored", !!(ev && ev.type === "store" && ev.reg === k));
        cell.classList.toggle("hp-solved", !!(ev && ev.type === "solve" && ev.reg === k));
      });
      var am = engine.amort;
      ["PRIN", "INT", "BAL"].forEach(function (k, i) {
        var cell = outEls[k], shown = am && am.idx >= i;
        cell.querySelector("b").textContent = shown ? fmt([am.prin, am.int, am.bal][i]) : "—";
        cell.classList.toggle("hp-solved", !!(ev && ev.type === "amortval" && ev.label === k));
      });
    };
    new Player(root, engine, view, steps, side, refresh);
  }
  function periods(p) { return p + "s"; }

  /* ------------------------------------------------------------------ */
  /* Statistics widget (Σ+, x̄, Sx)                                        */
  /* ------------------------------------------------------------------ */
  function initStat(root) {
    var d = root.dataset;
    var vals = (d.values || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);
    var regsHTML = '<div class="hp-regs hp-regs3">' + [["n", "n"], ["MEAN", "x\\u0304"], ["SD", "Sx"]].map(function (k) { return '<div data-out="' + k[0] + '">' + k[1] + "<b>—</b></div>"; }).join("") + "</div>";
    var side = sideShell(regsHTML);
    root.appendChild(side);
    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () { return "Press the orange shift key, then <b>C</b> to run <b>C ALL</b>. The statistics registers are cleared along with everything else, so no value from an earlier list is counted in this one."; } });
    vals.forEach(function (s, i) {
      steps.push({ keys: numKeys(s).concat(["SIGMA+"]), text: function (evs) {
        var ev = evs[evs.length - 1];
        return "Type " + specText(s) + ", then press <b>\\u03a3+</b>. " + (ev.value < 0 ? "A negative return is typed as its digits followed by +/\\u2212, before \\u03a3+. " : "") + "The display shows <b>" + ev.count + "</b>: the number of values entered so far" + (i === vals.length - 1 ? ", which is all of them." : ".");
      } });
    });
    steps.push({ keys: ["SHIFT_O", "7"], text: function (evs) { return "Press the orange shift key, then <b>7</b> for <b>x\\u0304</b>: <span class='hp-res'>" + fmt(evs[evs.length - 1].value, 5) + "</span>, the average of the " + vals.length + " values, which is the expected return."; } });
    steps.push({ keys: ["SHIFT_O", "8"], text: function (evs) { return "Press the orange shift key, then <b>8</b> for <b>Sx</b>: <span class='hp-res'>" + fmt(evs[evs.length - 1].value, 5) + "</span>, the standard deviation of the values around that average." + (d.note ? " " + d.note : ""); } });
    steps.intro = "Press <b>Play</b> to step through the keystrokes.";
    var outEls = {};
    side.querySelectorAll("[data-out]").forEach(function (e) { outEls[e.getAttribute("data-out")] = e; });
    var refresh = function (ev) {
      outEls.n.querySelector("b").textContent = engine.stat.length ? String(engine.stat.length) : "—";
      outEls.n.classList.toggle("hp-stored", !!(ev && ev.type === "sigma"));
      outEls.MEAN.querySelector("b").textContent = ev && ev.type === "mean" ? fmt(ev.value, 5) : (ev && ev.type === "sdev" ? fmt(engine.mean(), 5) : "—");
      outEls.MEAN.classList.toggle("hp-solved", !!(ev && ev.type === "mean"));
      outEls.SD.querySelector("b").textContent = ev && ev.type === "sdev" ? fmt(ev.value, 5) : "—";
      outEls.SD.classList.toggle("hp-solved", !!(ev && ev.type === "sdev"));
    };
    new Player(root, engine, view, steps, side, refresh);
  }""")

# ---- CF widget: Nj, P/YR, PI ----------------------------------------------------------------
rep("""    var cfs = (d.cf || "0").split(",").map(function (s) { return s.trim(); });
    var solve = (d.solve || "NPV").toUpperCase();
    var iyr = d.iyr;
    var period = d.period || "year";
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var tlHTML = "";
    if (d.timeline !== "0") {
      var flows = {};
      cfs.forEach(function (c, i) { var v = evalSpec(c); if (v !== 0 || i === 0) flows[i] = money(v); });
      tlHTML = timelineSVG({ n: cfs.length - 1, flows: flows, unitLabel: period + "s", stagger: true });
    }
    var regsHTML = '<div class="hp-regs hp-cf">' + cfs.map(function (c, i) { return '<div data-cf="' + i + '">CF' + i + "<b>—</b></div>"; }).join("") +
      (solve === "NPV" ? '<div data-cf="I">I/YR<b>—</b></div>' : "") +
      '<div data-cf="RES">' + (solve === "NPV" ? "NPV" : "IRR/YR") + "<b>—</b></div></div>";
    var side = sideShell(tlHTML + regsHTML);
    root.appendChild(side);

    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () {
      return "Press the orange shift key, then <b>C</b> to run <b>C ALL</b>. This matters even more for cash-flow problems: <b>CF<sub>j</sub></b> keeps <i>adding</i> to whatever list is already in memory, so an old list would quietly corrupt this answer.";
    } });
    cfs.forEach(function (c, i) {
      var v = evalSpec(c);
      steps.push({ keys: numKeys(c).concat(["CFj"]), text: function () {
        var typed = "Type " + specText(c) + ", then press <b>CF<sub>j</sub></b>. ";
        if (i === 0) {
          if (v === 0) return typed + "The first entry is always <b>CF0</b>, the cash flow at time 0. It is zero here because we only want the present value of the future cash flows, not a net present value after paying a price.";
          if (v < 0) return typed + "The first entry is always <b>CF0</b>, the cash flow at time 0. The purchase price is money paid out, so it goes in as a negative number.";
          return typed + "The first entry is always <b>CF0</b>, the cash flow at time 0.";
        }
        return typed + "This becomes <b>CF" + i + "</b>, the cash flow at the end of " + period + " " + i + "." + (i === cfs.length - 1 ? " That is the last one in the list." : "");
      } });
    });
    if (solve === "NPV") {""", """    /* an entry "50000x5" is 50,000 entered once and repeated with Nj = 5 */
    var cfs = [], reps = [];
    (d.cf || "0").split(",").forEach(function (s) { var m = s.trim().match(/^(.*?)\\s*[x\\u00d7]\\s*(\\d+)$/); cfs.push(m ? m[1].trim() : s.trim()); reps.push(m ? Math.max(1, parseInt(m[2], 10)) : 1); });
    var solve = (d.solve || "NPV").toUpperCase();
    var pi = solve === "PI"; if (pi) solve = "NPV";
    var io = d.io !== undefined ? d.io : null;
    var iyr = d.iyr;
    var period = d.period || "year";
    var pyr = d.pyr ? Math.max(1, Math.round(evalSpec(d.pyr))) : 0;
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var tlHTML = "";
    var nTotal = 0; cfs.forEach(function (c, i) { nTotal += i === 0 ? 1 : reps[i]; }); nTotal -= 1;
    if (d.timeline !== "0") {
      var flows = {}, t = 0;
      cfs.forEach(function (c, i) { var v = evalSpec(c), k = i === 0 ? 1 : reps[i]; for (var j = 0; j < k; j++) { if (v !== 0 || t === 0) flows[t] = money(v); t++; } });
      tlHTML = timelineSVG({ n: nTotal, flows: flows, unitLabel: period + "s", stagger: true });
    }
    var regsHTML = '<div class="hp-regs hp-cf">' + cfs.map(function (c, i) { return '<div data-cf="' + i + '">CF' + i + (reps[i] > 1 ? " <small>\\u00d7" + reps[i] + "</small>" : "") + "<b>—</b></div>"; }).join("") +
      (solve === "NPV" ? '<div data-cf="I">I/YR<b>—</b></div>' : "") +
      '<div data-cf="RES">' + (solve === "NPV" ? "NPV" : "IRR/YR") + "<b>—</b></div>" + (pi ? '<div data-cf="PI">PI<b>—</b></div>' : "") + "</div>";
    var side = sideShell(tlHTML + regsHTML);
    root.appendChild(side);

    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () {
      return "Press the orange shift key, then <b>C</b> to run <b>C ALL</b>. This matters even more for cash-flow problems: <b>CF<sub>j</sub></b> keeps <i>adding</i> to whatever list is already in memory, so an old list would quietly corrupt this answer.";
    } });
    if (pyr) steps.push({ keys: numKeys(String(pyr)).concat(["SHIFT_O", "PMT"]), text: function () {
      return "Type " + pyr + ", press the orange shift key, then <b>PMT</b> to run <b>P/YR</b>. The cash flows are " + (pyr === 1 ? "annual, so P/YR must be 1: the NPV and IRR/YR functions use P/YR too, and a 12 left over from a mortgage problem would be wrong here." : "one per " + period + ", so P/YR is " + pyr + ".");
    } });
    cfs.forEach(function (c, i) {
      var v = evalSpec(c);
      steps.push({ keys: numKeys(c).concat(["CFj"]), text: function () {
        var typed = "Type " + specText(c) + ", then press <b>CF<sub>j</sub></b>. ";
        if (i === 0) {
          if (v === 0) return typed + "The first entry is always <b>CF0</b>, the cash flow at time 0. It is zero here because we only want the present value of the future cash flows, not a net present value after paying a price.";
          if (v < 0) return typed + "The first entry is always <b>CF0</b>, the cash flow at time 0. The initial outlay is money paid out, so it goes in as a negative number.";
          return typed + "The first entry is always <b>CF0</b>, the cash flow at time 0.";
        }
        return typed + "This becomes <b>CF" + i + "</b>, the " + (reps[i] > 1 ? "cash flow for each of the next " + reps[i] + " " + period + "s." : "cash flow at the end of " + period + " " + i + ".") + (i === cfs.length - 1 && reps[i] === 1 ? " That is the last one in the list." : "");
      } });
      if (reps[i] > 1) steps.push({ keys: numKeys(String(reps[i])).concat(["SHIFT_O", "CFj"]), text: function () {
        return "Type " + reps[i] + ", press the orange shift key, then <b>CF<sub>j</sub></b> to run <b>N<sub>j</sub></b>. That tells the calculator CF" + i + " repeats " + reps[i] + " times in a row, instead of entering it " + reps[i] + " times." + (i === cfs.length - 1 ? " That completes the list." : "");
      } });
    });
    if (solve === "NPV") {""")
rep("""        return "Press the orange shift key, then <b>PRC</b> to run <b>NPV</b>: <span class='hp-res'>" + fmt(r) + "</span>. Every cash flow has been discounted back to time 0 at " + plain(evalSpec(iyr)) + "% and added up (including CF0)." + (d.note ? " " + d.note : "");
      } });
    } else {""", """        return "Press the orange shift key, then <b>PRC</b> to run <b>NPV</b>: <span class='hp-res'>" + fmt(r) + "</span>. Every cash flow has been discounted back to time 0 at " + plain(evalSpec(iyr)) + "% and added up (including CF0)." + (d.note && !pi ? " " + d.note : "");
      } });
      if (pi) {
        steps.push({ keys: ["+"].concat(numKeys(io)).concat(["="]), text: function (evs) {
          return "Press <b>+</b>, type " + specText(io) + ", then <b>=</b>: " + fmt(evs[evs.length - 1].value) + ". Adding the initial outlay back to the NPV leaves the present value of the cash inflows alone.";
        } });
        steps.push({ keys: ["/"].concat(numKeys(io)).concat(["="]), text: function (evs) {
          return "Press <b>\\u00f7</b>, type " + specText(io) + ", then <b>=</b>: <span class='hp-res'>" + fmt(evs[evs.length - 1].value) + "</span>. Dividing by the initial outlay gives the profitability index, the present value of inflows per dollar invested." + (d.note ? " " + d.note : "");
        } });
      }
    } else {""")
rep("""      var res = cells.RES, isRes = ev && (ev.type === "npv" || ev.type === "irr");
      if (isRes) res.querySelector("b").textContent = fmt(ev.value) + (ev.type === "irr" ? "%" : "");
      else if (!ev || ev.type === "clearall") res.querySelector("b").textContent = "—";
      res.classList.toggle("hp-solved", !!isRes);
    };""", """      var res = cells.RES, isRes = ev && (ev.type === "npv" || ev.type === "irr");
      if (isRes) res.querySelector("b").textContent = fmt(ev.value) + (ev.type === "irr" ? "%" : "");
      else if (!ev || ev.type === "clearall") res.querySelector("b").textContent = "—";
      res.classList.toggle("hp-solved", !!isRes);
      if (cells.PI) {
        var last = ev && ev.type === "equals" && engine.op === null;
        if (!ev || ev.type === "clearall") cells.PI.querySelector("b").textContent = "—";
        else if (last && cells.PI.getAttribute("data-step") === "div") cells.PI.querySelector("b").textContent = fmt(ev.value);
        cells.PI.classList.toggle("hp-solved", !!(last && cells.PI.getAttribute("data-step") === "div"));
      }
    };""")
# the PI cell needs to know whether the last "=" closed the division: mark it from the step text
rep("""        steps.push({ keys: ["/"].concat(numKeys(io)).concat(["="]), text: function (evs) {
          return "Press <b>\\u00f7</b>""", """        steps.push({ keys: ["/"].concat(numKeys(io)).concat(["="]), text: function (evs) {
          side.querySelector('[data-cf="PI"]').setAttribute("data-step", "div");
          return "Press <b>\\u00f7</b>""")
rep("""        steps.push({ keys: ["+"].concat(numKeys(io)).concat(["="]), text: function (evs) {
          return "Press <b>+</b>""", """        steps.push({ keys: ["+"].concat(numKeys(io)).concat(["="]), text: function (evs) {
          side.querySelector('[data-cf="PI"]').setAttribute("data-step", "add");
          return "Press <b>+</b>""")

# ---- init: alternatives and the new widget kinds ------------------------------------------
rep("""  function init() {
    document.querySelectorAll(".hp10bii:not([data-hp-ready])").forEach(function (el) { el.setAttribute("data-hp-ready", "1"); try { initTVM(el); } catch (e) { console.error("hp10bii", e); } });
    document.querySelectorAll(".hp10bii-cf:not([data-hp-ready])").forEach(function (el) { el.setAttribute("data-hp-ready", "1"); try { initCF(el); } catch (e) { console.error("hp10bii-cf", e); } });
    document.querySelectorAll(".hp10bii-keys:not([data-hp-ready])").forEach(function (el) { el.setAttribute("data-hp-ready", "1"); try { initKeys(el); } catch (e) { console.error("hp10bii-keys", e); } });
  }""", """  var KINDS = { "hp10bii": initTVM, "hp10bii-cf": initCF, "hp10bii-keys": initKeys, "hp10bii-amort": initAmort, "hp10bii-stat": initStat };

  /* data-alt: a row of buttons, each re-initialising the widget with its own overrides */
  function initAlts(el, kind) {
    var alts;
    try { alts = JSON.parse(el.getAttribute("data-alt")); } catch (e) { console.error("hp data-alt", e); return false; }
    if (!alts || !alts.length) return false;
    var base = {};
    Array.prototype.forEach.call(el.attributes, function (a) { if (a.name.indexOf("data-") === 0 && a.name !== "data-alt" && a.name !== "data-hp-ready") base[a.name] = a.value; });
    var bar = document.createElement("div");
    bar.className = "hp-alts";
    bar.setAttribute("role", "tablist");
    el.parentNode.insertBefore(bar, el);
    var show = function (i) {
      Array.prototype.forEach.call(el.attributes, function (a) { if (a.name.indexOf("data-") === 0 && a.name !== "data-alt") el.removeAttribute(a.name); });
      Object.keys(base).forEach(function (k) { el.setAttribute(k, base[k]); });
      Object.keys(alts[i]).forEach(function (k) { if (k !== "label") el.setAttribute("data-" + k.replace(/[A-Z]/g, function (c) { return "-" + c.toLowerCase(); }), String(alts[i][k])); });
      el.innerHTML = ""; el.className = kind;
      el.setAttribute("data-hp-ready", "1");
      try { KINDS[kind](el); } catch (e) { console.error(kind, e); }
      Array.prototype.forEach.call(bar.children, function (b, j) { b.classList.toggle("cur", j === i); b.setAttribute("aria-selected", j === i ? "true" : "false"); });
    };
    alts.forEach(function (a, i) {
      var b = document.createElement("button"); b.type = "button"; b.textContent = a.label || ("Case " + (i + 1)); b.setAttribute("role", "tab");
      b.addEventListener("click", function () { show(i); });
      bar.appendChild(b);
    });
    show(0);
    return true;
  }

  function init() {
    Object.keys(KINDS).forEach(function (kind) {
      document.querySelectorAll("." + kind + ":not([data-hp-ready])").forEach(function (el) {
        el.setAttribute("data-hp-ready", "1");
        if (el.hasAttribute("data-alt") && initAlts(el, kind)) return;
        try { KINDS[kind](el); } catch (e) { console.error(kind, e); }
      });
    });
  }""")

# the noscript fallback image must not be counted as content when the widget builds
rep("""    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var vals = {};""", """    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var vals = {};""")

pathlib.Path("/home/user/WidgetWorkflow/engine/hp10bii.js").write_text(out)
css = (S / "hp10bii.css").read_text()
assert "hp-regs6" not in css
css = css.replace("/* HP 10bII+ interactive calculator widget — hp10bii.css */", "/* HP 10bII+ interactive calculator widget — hp10bii.css  (v2, FIN3403 edition) */")
css += """
/* ---------- v2 additions: P/YR cell, amortization outputs, alternatives, AMORT annunciator ---------- */
.hp-regs.hp-regs6 { grid-template-columns: repeat(6, 1fr); }
.hp-regs.hp-regs3 { grid-template-columns: repeat(3, 1fr); }
.hp-regs small { font-size: 9.5px; color: #888; }
.hp-lcd-top .hp-ann.amort { margin-left: auto; color: var(--hp-lcd-ink); letter-spacing: .3px; }
.hp-alts { display: flex; flex-wrap: wrap; gap: 6px; margin: 22px 0 -12px; font-family: "Helvetica Neue", Arial, sans-serif; }
.hp-alts button {
  appearance: none; font: inherit; font-size: 13px; padding: 5px 12px; border-radius: 6px;
  border: 1px solid #b9b9b4; background: #fff; color: #222; cursor: pointer; min-height: 32px;
}
.hp-alts button:hover { background: #f3f3f0; }
.hp-alts button.cur { background: #1f2a3a; border-color: #1f2a3a; color: #fff; font-weight: 700; }
.hp-alts button:focus-visible { outline: 2px solid #2b6cb0; outline-offset: 1px; }
.hp-widget noscript { display: none; }
/* a long keystroke group (the amortization setup) wraps inside its own chip row rather than widening the page */
.hp-strip .hp-grp { flex-wrap: wrap; max-width: 100%; }
@media (max-width: 640px) {
  .hp-regs.hp-regs6, .hp-regs.hp-regs3 { grid-template-columns: repeat(auto-fill, minmax(92px, 1fr)); }
  .hp-alts button { padding: 8px 12px; min-height: 44px; }
}
"""
pathlib.Path("/home/user/WidgetWorkflow/engine/hp10bii.css").write_text(css)
print("ok", len(out), len(css))
