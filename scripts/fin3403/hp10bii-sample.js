/* HP 10bII+ interactive calculator widget — hp10bii.js
 *
 * Usage (place after loading hp10bii.css):
 *
 *   TVM example (annual convention, P/YR treated as 1, rate converted by hand):
 *   <div class="hp10bii" data-n="5" data-iyr="5" data-pv="-1000" data-pmt="0" data-solve="FV"></div>
 *
 *     data-solve      which register to solve for: N, I/YR, PV, PMT, FV
 *     data-order      entry order, default "N,I/YR,PV,PMT,FV" (the solved key is skipped automatically)
 *     data-beg="1"    annuity due — playback switches the calculator to BEGIN mode first
 *     data-iyr="5/12" a rate typed as an expression: keys 5 ÷ 12 = are played
 *     data-timeline="0" suppresses the timeline drawing
 *     data-period     word used for periods, default "year" (e.g. "month")
 *     data-note       extra sentence appended to the final step's caption
 *
 *   Cash-flow example:
 *   <div class="hp10bii-cf" data-cf="0,1000,2000,3000,6000" data-iyr="8" data-solve="NPV"></div>
 *   <div class="hp10bii-cf" data-cf="-425000,48000,49440,50923,52451,614025" data-solve="IRR"></div>
 *
 *   Key highlight (static picture of the calculator with keys glowing):
 *   <div class="hp10bii-keys" data-keys="PMT"></div>
 *   <div class="hp10bii-keys" data-keys="SHIFT_O,MAR"></div>
 */
(function () {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* Keyboard definition (matches the HP 10bII+ faceplate)               */
  /* up = blue label above the key, dn = orange label printed on the key */
  /* ------------------------------------------------------------------ */
  var KEYS = [
    { id: "N", main: "N", up: "AccInt", dn: "xP/YR" },
    { id: "I/YR", main: "I/YR", up: "YTM", dn: "NOM%" },
    { id: "PV", main: "PV", up: "PRICE", dn: "EFF%" },
    { id: "PMT", main: "PMT", up: "CPN%", dn: "P/YR" },
    { id: "FV", main: "FV", up: "CALL", dn: "AMORT" },

    { id: "INPUT", main: "INPUT", up: "D.MY/M.DY", dn: "DATE" },
    { id: "MU", main: "MU", up: "360/Act", dn: "ΔDAYS" },
    { id: "CST", main: "CST", up: "Semi/Ann", dn: "IRR/YR" },
    { id: "PRC", main: "PRC", up: "SetDate", dn: "NPV" },
    { id: "MAR", main: "MAR", up: "MatDate", dn: "Beg/End" },

    { bracket: "BREAKEVEN", cls: "hp-br1" },
    { id: "K", main: "K", up: "UNITS", dn: "SWAP" },
    { id: "%", main: "%", up: "SP", dn: "%CHG" },
    { id: "CFj", main: "CF<sub style='font-size:8px'>j</sub>", up: "VC", dn: "Nj" },
    { id: "SIGMA+", main: "Σ+", up: "FC", dn: "Σ−" },
    { id: "BKSP", main: "<span class='hp-arrow'>←</span>", up: "PROFIT", dn: "RND" },

    { bracket: "DEPRECIATION", cls: "hp-br2" },
    { id: "+/-", main: "+/−", up: "SL", dn: "E" },
    { id: "RCL", main: "RCL", up: "SOYD", dn: "STO" },
    { id: "STO", main: "→M", up: "DB", dn: "C STAT" },
    { id: "RM", main: "RM", up: "HYP", dn: "(" },
    { id: "M+", main: "M+", up: "INV", dn: ")" },

    { id: "SHIFT_B", main: "<span class='hp-arrow'>↱</span>", up: "", dn: "", shift: "b" },
    { id: "7", main: "7", up: "Σx²", dn: "x̄,ȳ" },
    { id: "8", main: "8", up: "Σy²", dn: "sx,sy" },
    { id: "9", main: "9", up: "Σxy", dn: "σx,σy" },
    { id: "/", main: "÷", up: "SIN", dn: "1/x" },

    { id: "SHIFT_O", main: "<span class='hp-arrow'>↱</span>", up: "", dn: "", shift: "o" },
    { id: "4", main: "4", up: "n", dn: "x̂,r" },
    { id: "5", main: "5", up: "Σx", dn: "ŷ,m" },
    { id: "6", main: "6", up: "Σy", dn: "x̄w,b" },
    { id: "*", main: "×", up: "COS", dn: "yˣ" },

    { id: "C", main: "C", up: "C MEM", dn: "C ALL" },
    { id: "1", main: "1", up: "REGR", dn: "eˣ" },
    { id: "2", main: "2", up: "df,t⇄P", dn: "LN" },
    { id: "3", main: "3", up: "Z⇄P", dn: "n!" },
    { id: "-", main: "−", up: "TAN", dn: "√x" },

    { id: "ON", main: "ON", up: "Alg/Chain", dn: "OFF" },
    { id: "0", main: "0", up: "ₙPᵣ", dn: "π" },
    { id: ".", main: "•", up: "ₙCᵣ", dn: "·/,", },
    { id: "=", main: "=", up: "RAND", dn: "DISP" },
    { id: "+", main: "+", up: "Rad/Deg", dn: "x²" }
  ];

  var LABEL = { "N": "N", "I/YR": "I/YR", "PV": "PV", "PMT": "PMT", "FV": "FV", "CFj": "CFj",
    "MAR": "MAR", "PRC": "PRC", "CST": "CST", "C": "C", "+/-": "+/−", "/": "÷", "*": "×",
    "-": "−", "+": "+", "=": "=", "BKSP": "←" };
  var FULLNAME = { "N": "the number of periods", "I/YR": "the interest rate per period", "PV": "the present value",
    "PMT": "the periodic payment", "FV": "the future value" };

  /* ------------------------------------------------------------------ */
  /* Number formatting                                                    */
  /* ------------------------------------------------------------------ */
  function fmt(x, d) {
    if (d === undefined) d = 4;
    if (!isFinite(x)) return "Error";
    var r = Math.round(x * Math.pow(10, d)) / Math.pow(10, d);
    if (Object.is(r, -0)) r = 0;
    return r.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  }
  function fmtEntry(e) {
    var neg = e.charAt(0) === "-";
    if (neg) e = e.slice(1);
    var parts = e.split(".");
    var ip = parts[0].replace(/^0+(?=\d)/, "") || "0";
    ip = ip.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return (neg ? "-" : "") + ip + (parts.length > 1 ? "." + parts[1] : "");
  }
  function money(x) { var a = Math.abs(x), s = fmt(a, Math.abs(a - Math.round(a)) < 1e-9 ? 0 : 2); return (x < 0 ? "−$" : "$") + s; }
  function plain(x) { var s = fmt(Math.abs(x), 4).replace(/\.?0+$/, ""); return (x < 0 ? "−" : "") + s; }

  /* ------------------------------------------------------------------ */
  /* Calculator engine (P/YR = 1; rates converted by hand as in the guide) */
  /* ------------------------------------------------------------------ */
  function Engine() { this.clearAll(); this.beg = false; }
  Engine.prototype.clearAll = function () {
    this.R = { "N": 0, "I/YR": 0, "PV": 0, "PMT": 0, "FV": 0 }; this.touched = {};
    this.cfs = [];
    this.clearEntry();
    this.shO = false; this.shB = false;
  };
  Engine.prototype.clearEntry = function () {
    this.entry = ""; this.hasEntry = false; this.disp = 0; this.acc = null; this.op = null;
  };
  Engine.prototype.value = function () { return this.hasEntry && this.entry !== "" ? (parseFloat(this.entry) || 0) : this.disp; };
  Engine.prototype.displayText = function () {
    if (this.entry !== "") return fmtEntry(this.entry);
    return fmt(this.disp);
  };
  Engine.prototype.fvOf = function (n, i, pv, pmt) {
    var r = i / 100;
    if (r === 0) return -(pv + pmt * n);
    var g = Math.pow(1 + r, n), a = this.beg ? (1 + r) : 1;
    return -(pv * g + pmt * a * (g - 1) / r);
  };
  Engine.prototype.solveTVM = function (k) {
    var R = this.R, r = R["I/YR"] / 100, n = R.N, g = Math.pow(1 + r, n), a = this.beg ? (1 + r) : 1, x, self = this;
    if (k === "FV") x = this.fvOf(n, R["I/YR"], R.PV, R.PMT);
    else if (k === "PV") x = r === 0 ? -(R.FV + R.PMT * n) : -(R.FV + R.PMT * a * (g - 1) / r) / g;
    else if (k === "PMT") x = r === 0 ? -(R.PV + R.FV) / n : -(R.PV * g + R.FV) / (a * (g - 1) / r);
    else if (k === "N") {
      if (r === 0) x = -(R.PV + R.FV) / R.PMT;
      else { var p = R.PMT * a / r; x = Math.log((p - R.FV) / (p + R.PV)) / Math.log(1 + r); }
    } else if (k === "I/YR") {
      var f = function (i) { return self.fvOf(n, i, R.PV, R.PMT) - R.FV; };
      var lo = -99, hi = 1000, flo = f(lo), fhi = f(hi);
      if (isNaN(flo) || isNaN(fhi) || (flo < 0) === (fhi < 0)) return NaN;
      for (var t = 0; t < 300; t++) {
        var mid = (lo + hi) / 2, fm = f(mid);
        if ((fm < 0) === (flo < 0)) { lo = mid; flo = fm; } else hi = mid;
      }
      x = (lo + hi) / 2;
    }
    return x;
  };
  Engine.prototype.expandCF = function () {
    var out = [];
    this.cfs.forEach(function (c, idx) { var reps = idx === 0 ? 1 : (c.n || 1); for (var j = 0; j < reps; j++) out.push(c.amt); });
    return out;
  };
  Engine.prototype.npv = function (i) {
    var r = i / 100, cf = this.expandCF(), s = 0;
    for (var t = 0; t < cf.length; t++) s += cf[t] / Math.pow(1 + r, t);
    return s;
  };
  Engine.prototype.irr = function () {
    var self = this, f = function (i) { return self.npv(i); };
    var lo = -99.9, hi = 1000, flo = f(lo), fhi = f(hi);
    if (isNaN(flo) || isNaN(fhi) || (flo < 0) === (fhi < 0)) return NaN;
    for (var t = 0; t < 300; t++) {
      var mid = (lo + hi) / 2, fm = f(mid);
      if ((fm < 0) === (flo < 0)) { lo = mid; flo = fm; } else hi = mid;
    }
    return (lo + hi) / 2;
  };
  Engine.prototype.apply = function (a, op, b) {
    if (op === "+") return a + b; if (op === "-") return a - b; if (op === "*") return a * b; if (op === "/") return b === 0 ? NaN : a / b;
    return b;
  };

  /* press() returns an event object describing what happened */
  Engine.prototype.press = function (k) {
    var ev = { key: k };
    var shO = this.shO, shB = this.shB;
    if (k === "SHIFT_O") { this.shO = !this.shO; this.shB = false; return ev; }
    if (k === "SHIFT_B") { this.shB = !this.shB; this.shO = false; return ev; }
    this.shO = false; this.shB = false;

    if (shO) {
      if (k === "C") { var beg = this.beg; this.clearAll(); this.beg = beg; ev.type = "clearall"; return ev; }
      if (k === "MAR") { this.beg = !this.beg; ev.type = "begend"; return ev; }
      if (k === "PRC") { var v = this.npv(this.R["I/YR"]); this.entry = ""; this.hasEntry = false; this.disp = v; ev.type = "npv"; ev.value = v; return ev; }
      if (k === "CST") { var irr = this.irr(); this.entry = ""; this.hasEntry = false; this.disp = irr; ev.type = "irr"; ev.value = irr; return ev; }
      if (k === "CFj") { if (this.cfs.length > 1) { this.cfs[this.cfs.length - 1].n = Math.max(1, Math.round(this.value())); } this.entry = ""; this.hasEntry = false; ev.type = "nj"; return ev; }
      ev.type = "unused"; return ev;
    }
    if (shB) { ev.type = "unused"; return ev; }

    if (/^[0-9]$/.test(k)) {
      if (!this.hasEntry) { this.entry = ""; }
      if (this.entry.replace(/[-.]/g, "").length >= 12) return ev;
      this.entry += k; this.hasEntry = true; ev.type = "digit"; return ev;
    }
    if (k === ".") {
      if (!this.hasEntry) this.entry = "";
      if (this.entry.indexOf(".") < 0) { this.entry = (this.entry === "" || this.entry === "-" ? this.entry + "0" : this.entry) + "."; }
      this.hasEntry = true; ev.type = "digit"; return ev;
    }
    if (k === "+/-") {
      if (this.entry !== "") { this.entry = this.entry.charAt(0) === "-" ? this.entry.slice(1) : "-" + this.entry; }
      else { this.disp = -this.disp; this.entry = ""; }
      this.hasEntry = true; ev.type = "sign"; return ev;
    }
    if (k === "BKSP") { if (this.entry !== "") { this.entry = this.entry.slice(0, -1); if (this.entry === "" || this.entry === "-") { this.entry = ""; this.disp = 0; } } ev.type = "digit"; return ev; }
    if (k === "C") { this.clearEntry(); ev.type = "clear"; return ev; }
    if (k === "+" || k === "-" || k === "*" || k === "/") {
      var cur = this.value();
      this.acc = (this.op !== null && this.acc !== null) ? this.apply(this.acc, this.op, cur) : cur;
      this.op = k; this.disp = this.acc; this.entry = ""; this.hasEntry = false; ev.type = "op"; return ev;
    }
    if (k === "=") {
      var b = this.value(), res = (this.op !== null && this.acc !== null) ? this.apply(this.acc, this.op, b) : b;
      this.disp = res; this.entry = ""; this.hasEntry = true; this.op = null; this.acc = null; ev.type = "equals"; ev.value = res; return ev;
    }
    if (k in this.R) {
      if (this.hasEntry) { var sv = this.value(); this.R[k] = sv; this.touched[k] = true; this.disp = sv; this.entry = ""; this.hasEntry = false; ev.type = "store"; ev.reg = k; ev.value = sv; return ev; }
      var sol = this.solveTVM(k); this.R[k] = isFinite(sol) ? sol : 0; this.touched[k] = true; this.disp = sol; this.entry = ""; ev.type = "solve"; ev.reg = k; ev.value = sol; return ev;
    }
    if (k === "CFj") { var a = this.value(); this.cfs.push({ amt: a, n: 1 }); this.disp = a; this.entry = ""; this.hasEntry = false; ev.type = "cf"; ev.index = this.cfs.length - 1; ev.value = a; return ev; }
    ev.type = "unused"; return ev;
  };

  /* ------------------------------------------------------------------ */
  /* DOM: calculator                                                      */
  /* ------------------------------------------------------------------ */
  function buildCalc(container, engine, interactive) {
    var calc = document.createElement("div");
    calc.className = "hp-calc";
    var html = '<div class="hp-bezel"><div class="hp-brand"><div>HP 10bII+<small>Financial Calculator</small></div></div>' +
      '<div class="hp-lcd" aria-live="polite">' +
      '<div class="hp-lcd-top"><span class="hp-ann sh-o" data-ann="sho">⬆ SHIFT</span><span class="hp-ann sh-b" data-ann="shb">⬆ SHIFT</span><span class="hp-ann" data-ann="pend">PEND</span></div>' +
      '<div class="hp-lcd-num" data-lcd>0.0000</div>' +
      '<div class="hp-lcd-bot"><span class="hp-ann" data-ann="begin">BEGIN</span><span class="hp-ann" data-ann="input">INPUT</span></div>' +
      '</div></div><div class="hp-keys">';
    KEYS.forEach(function (k) {
      if (k.bracket) { html += '<div class="hp-bracket ' + k.cls + '">' + k.bracket + '</div>'; return; }
      var cls = k.shift === "b" ? " hp-shift-b" : k.shift === "o" ? " hp-shift-o" : "";
      var title = k.shift === "b" ? "Blue shift" : k.shift === "o" ? "Orange shift" : k.id;
      html += '<div class="hp-k"><div class="hp-up">' + (k.up || "&nbsp;") + '</div>' +
        '<button type="button" data-key="' + k.id + '" class="' + cls.trim() + '" aria-label="' + title + '"' + (interactive ? "" : " tabindex='-1'") + '>' +
        '<span>' + k.main + '</span>' + (k.dn ? '<span class="hp-dn">' + k.dn + '</span>' : "") + '</button></div>';
    });
    html += "</div>";
    calc.innerHTML = html;
    container.appendChild(calc);
    var view = {
      el: calc,
      lcd: calc.querySelector("[data-lcd]"),
      ann: {},
      keyEl: function (id) { return calc.querySelector('[data-key="' + id + '"]'); },
      render: function () {
        if (!engine) return;
        this.lcd.textContent = engine.displayText();
        this.ann.sho.classList.toggle("on", engine.shO);
        this.ann.shb.classList.toggle("on", engine.shB);
        this.ann.pend.classList.toggle("on", engine.op !== null);
        this.ann.begin.classList.toggle("on", engine.beg);
        this.keyEl("SHIFT_O").classList.toggle("hp-on", engine.shO);
        this.keyEl("SHIFT_B").classList.toggle("hp-on", engine.shB);
      },
      flash: function (id, ms) {
        var b = this.keyEl(id); if (!b) return;
        b.classList.add("hp-lit");
        setTimeout(function () { b.classList.remove("hp-lit"); }, ms || 420);
      }
    };
    ["sho", "shb", "pend", "begin"].forEach(function (a) { view.ann[a] = calc.querySelector('[data-ann="' + a + '"]'); });
    return view;
  }

  /* ------------------------------------------------------------------ */
  /* Keystroke helpers                                                    */
  /* ------------------------------------------------------------------ */
  function numKeys(spec) {
    spec = String(spec).trim();
    var m = spec.match(/^(-?[\d.]+)\s*\/\s*([\d.]+)$/);
    if (m) return numKeys(m[1]).concat(["/"], numKeys(m[2]), ["="]);
    var neg = spec.charAt(0) === "-"; if (neg) spec = spec.slice(1);
    var keys = spec.split("");
    if (neg) keys.push("+/-");
    return keys;
  }
  function evalSpec(spec) {
    spec = String(spec).trim();
    var m = spec.match(/^(-?[\d.]+)\s*\/\s*([\d.]+)$/);
    if (m) return parseFloat(m[1]) / parseFloat(m[2]);
    return parseFloat(spec);
  }
  function specText(spec) {
    spec = String(spec).trim();
    var m = spec.match(/^(-?[\d.]+)\s*\/\s*([\d.]+)$/);
    if (m) return plain(parseFloat(m[1])) + " ÷ " + plain(parseFloat(m[2])) + " =";
    var v = parseFloat(spec);
    return plain(Math.abs(v)) + (v < 0 ? ", then +/−" : "");
  }
  function chip(k) {
    if (k === "SHIFT_O") return '<kbd class="o" title="Orange shift"></kbd>';
    if (k === "SHIFT_B") return '<kbd class="b" title="Blue shift"></kbd>';
    return "<kbd>" + (LABEL[k] || k) + "</kbd>";
  }
  function chipsFor(keys) {
    var out = "", i;
    for (i = 0; i < keys.length; i++) {
      var k = keys[i];
      if ((k === "SHIFT_O") && i + 1 < keys.length) {
        var fn = { "C": "C ALL", "MAR": "Beg/End", "PRC": "NPV", "CST": "IRR/YR", "CFj": "Nj" }[keys[i + 1]];
        if (fn) { out += chip(k) + '<kbd class="fn">' + fn + "</kbd>"; i++; continue; }
      }
      out += chip(k);
    }
    return out;
  }

  /* ------------------------------------------------------------------ */
  /* Timeline SVG                                                          */
  /* ------------------------------------------------------------------ */
  function timelineSVG(opts) {
    // opts: { n, flows: {0: label, 1: label, ...}, pmtLabel, unitLabel, stagger }
    var n = Math.max(1, Math.round(opts.n));
    var showAll = n <= 7, cols = showAll ? n + 1 : 6;
    var W = 520, H = 104, x0 = 40, x1 = W - 40, step = (x1 - x0) / (cols - 1), AX = 64;
    var s = '<svg class="hp-tl" viewBox="0 0 ' + W + ' ' + H + '" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Timeline of cash flows">';
    s += '<line x1="' + (x0 - 16) + '" y1="' + AX + '" x2="' + (x1 + 16) + '" y2="' + AX + '" stroke="#444" stroke-width="1.4"/>';
    var slots = [];
    if (showAll) { for (var t = 0; t <= n; t++) slots.push(t); }
    else { slots = [0, 1, 2, "…", n - 1, n]; }
    var FF = 'font-family="Helvetica Neue, Arial, sans-serif"';
    slots.forEach(function (t, i) {
      var x = x0 + i * step;
      if (t === "…") { s += '<text x="' + x + '" y="' + (AX + 4) + '" font-size="15" text-anchor="middle" fill="#444">…</text>'; return; }
      s += '<line x1="' + x + '" y1="' + (AX - 6) + '" x2="' + x + '" y2="' + (AX + 6) + '" stroke="#444" stroke-width="1.4"/>';
      s += '<text x="' + x + '" y="' + (AX + 22) + '" font-size="12" text-anchor="middle" fill="#444" ' + FF + '>' + t + '</text>';
      var lab = opts.flows[t];
      if (lab) {
        var q = lab.indexOf("?") >= 0, col = q ? "#c45d12" : "#1f2a3a";
        var y = opts.stagger && (i % 2 === 1) ? AX - 34 : AX - 16;
        var anchor = "middle"; if (i === 0 && !opts.stagger) anchor = "start"; if (i === slots.length - 1 && !opts.stagger) anchor = "end";
        if (i === 0 && opts.stagger) anchor = "start";
        var lx = anchor === "start" ? x - 10 : anchor === "end" ? x + 10 : x;
        s += '<text x="' + lx + '" y="' + y + '" font-size="12.5" font-weight="' + (q ? "700" : "500") + '" text-anchor="' + anchor + '" fill="' + col + '" ' + FF + '>' + lab + '</text>';
      }
    });
    if (opts.pmtLabel) s += '<text x="' + (W / 2) + '" y="14" font-size="11.5" text-anchor="middle" fill="#666" ' + FF + '>' + opts.pmtLabel + '</text>';
    if (opts.unitLabel) s += '<text x="' + (W / 2) + '" y="' + (AX + 38) + '" font-size="11" text-anchor="middle" fill="#888" ' + FF + '>' + opts.unitLabel + '</text>';
    s += "</svg>";
    return s;
  }

  /* ------------------------------------------------------------------ */
  /* Shared player                                                         */
  /* ------------------------------------------------------------------ */
  function Player(root, engine, view, steps, side, onAfterStep) {
    this.root = root; this.engine = engine; this.view = view; this.steps = steps; this.side = side;
    this.pos = -1; this.timer = null; this.playing = false; this.animating = false; this.onAfterStep = onAfterStep;
    var self = this;
    this.strip = side.querySelector(".hp-strip");
    this.caption = side.querySelector(".hp-caption");
    this.prog = side.querySelector(".hp-prog");
    this.playBtn = side.querySelector(".hp-play");
    this.strip.innerHTML = steps.map(function (st, i) { return '<span class="hp-grp" data-i="' + i + '" role="button" tabindex="0" title="Jump to this step">' + chipsFor(st.keys) + "</span>"; }).join("");
    this.strip.addEventListener("click", function (e) { var g = e.target.closest(".hp-grp"); if (g) { self.stop(); self.goTo(+g.getAttribute("data-i")); } });
    this.strip.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { var g = e.target.closest(".hp-grp"); if (g) { e.preventDefault(); self.stop(); self.goTo(+g.getAttribute("data-i")); } } });
    side.querySelector(".hp-next").addEventListener("click", function () { self.stop(); self.next(); });
    side.querySelector(".hp-prev").addEventListener("click", function () { self.stop(); if (self.pos > 0) self.goTo(self.pos - 1); else self.restart(); });
    side.querySelector(".hp-reset").addEventListener("click", function () { self.stop(); self.restart(); });
    this.playBtn.addEventListener("click", function () {
      if (self.playing) { self.stop(); return; }
      if (self.pos >= self.steps.length - 1) self.pos = -1;
      self.playing = true;
      self.playBtn.textContent = "Pause";
      self.next();
    });
    view.el.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-key]"); if (!b) return;
      self.stop(); self.userKey(b.getAttribute("data-key"));
    });
    this.restart();
  }
  Player.prototype.stop = function () { this.playing = false; if (this.timer) { clearTimeout(this.timer); this.timer = null; } this.playBtn.textContent = "Play"; };
  /* Reading time for a caption: a base pause plus time proportional to its length (about 200 words a minute). */
  Player.prototype.readingDelay = function (html) {
    var words = html.replace(/<[^>]+>/g, " ").trim().split(/\s+/).filter(Boolean).length;
    return Math.min(20000, Math.max(3000, 1800 + words * 300));
  };
  Player.prototype.scheduleNext = function () {
    var self = this;
    if (!this.playing) return;
    if (this.pos >= this.steps.length - 1) { this.stop(); return; }
    this.timer = setTimeout(function () { self.timer = null; if (self.playing) self.next(); }, this.readingDelay(this.caption.innerHTML));
  };
  Player.prototype.restart = function () {
    this.pos = -1; this.engine.clearAll(); this.engine.beg = false; this.view.render();
    this.caption.innerHTML = this.steps.intro || "";
    this.prog.textContent = "";
    this.markStrip();
    this.onAfterStep(null, -1);
  };
  Player.prototype.markStrip = function () {
    var pos = this.pos;
    Array.prototype.forEach.call(this.strip.children, function (g, i) { g.classList.toggle("cur", i === pos); g.classList.toggle("done", i < pos); });
  };
  Player.prototype.next = function () { if (this.pos < this.steps.length - 1) this.goTo(this.pos + 1); else this.stop(); };
  Player.prototype.goTo = function (n) {
    var self = this;
    if (this.animating) return;
    this.engine.clearAll(); this.engine.beg = false;
    var i, j, last = null;
    for (i = 0; i < n; i++) for (j = 0; j < this.steps[i].keys.length; j++) last = this.engine.press(this.steps[i].keys[j]);
    this.pos = n; this.markStrip();
    this.view.render();
    var keys = this.steps[n].keys, idx = 0, evs = [];
    this.animating = true;
    this.caption.innerHTML = "";
    var tick = function () {
      if (idx >= keys.length) {
        self.animating = false;
        self.caption.innerHTML = self.steps[n].text(evs);
        self.prog.textContent = "Step " + (n + 1) + " of " + self.steps.length;
        self.onAfterStep(evs[evs.length - 1], n);
        self.scheduleNext();
        return;
      }
      var k = keys[idx++];
      evs.push(self.engine.press(k));
      self.view.flash(k, 720);
      self.view.render();
      setTimeout(tick, 660);
    };
    tick();
  };
  Player.prototype.userKey = function (k) {
    var ev = this.engine.press(k);
    this.view.flash(k, 200); this.view.render();
    this.pos = -1; this.markStrip(); this.prog.textContent = "";
    var msg;
    if (ev.type === "store") msg = "Stored " + fmt(ev.value) + " in " + ev.reg + ".";
    else if (ev.type === "solve") msg = isFinite(ev.value) ? ev.reg + " = " + fmt(ev.value) : "No solution with these inputs — check the signs of PV, PMT and FV.";
    else if (ev.type === "clearall") msg = "C ALL: all registers cleared. BEGIN/END mode is unchanged.";
    else if (ev.type === "begend") msg = this.engine.beg ? "BEGIN mode: payments at the start of each period." : "END mode: payments at the end of each period.";
    else if (ev.type === "cf") msg = "CF" + ev.index + " = " + fmt(ev.value) + " added to the cash-flow list.";
    else if (ev.type === "npv") msg = "NPV = " + fmt(ev.value) + " at " + plain(this.engine.R["I/YR"]) + "%.";
    else if (ev.type === "irr") msg = isFinite(ev.value) ? "IRR/YR = " + fmt(ev.value) + "%" : "No IRR found — the list needs at least one sign change.";
    else if (ev.type === "nj") msg = "Nj: repeat count set for the last cash flow.";
    else if (ev.type === "unused") msg = "That function isn't needed in this course.";
    else msg = "";
    if (msg) this.caption.innerHTML = '<span style="color:#666">' + msg + "</span>";
    this.onAfterStep(ev, -1);
  };

  function sideShell(extra) {
    var d = document.createElement("div");
    d.className = "hp-side";
    d.innerHTML = extra +
      '<div class="hp-strip"></div><div class="hp-caption"></div>' +
      '<div class="hp-controls"><button type="button" class="hp-play">Play</button><button type="button" class="hp-prev" aria-label="Previous step">‹ Back</button><button type="button" class="hp-next" aria-label="Next step">Next ›</button><button type="button" class="hp-reset">Restart</button><span class="hp-prog"></span></div>' +
      '<div class="hp-hint">Click any step to jump to it, or press the keys on the calculator yourself.</div>';
    return d;
  }

  /* ------------------------------------------------------------------ */
  /* TVM widget                                                            */
  /* ------------------------------------------------------------------ */
  function initTVM(root) {
    var d = root.dataset;
    var solve = (d.solve || "FV").toUpperCase(); if (solve === "I") solve = "I/YR";
    var order = (d.order || "N,I/YR,PV,PMT,FV").split(",").map(function (s) { return s.trim().toUpperCase() === "I" ? "I/YR" : s.trim().toUpperCase(); }).filter(function (k) { return k !== solve; });
    var spec = { "N": d.n, "I/YR": d.iyr, "PV": d.pv, "PMT": d.pmt, "FV": d.fv };
    var beg = d.beg === "1" || d.beg === "true";
    var period = d.period || "year";
    var periods = period + "s";
    var engine = new Engine();
    root.classList.add("hp-widget");
    var view = buildCalc(root, engine, true);

    var vals = {};
    order.forEach(function (k) { vals[k] = spec[k] === undefined ? 0 : evalSpec(spec[k]); });

    /* timeline */
    var tlHTML = "";
    if (d.timeline !== "0") {
      var n = vals.N || 1, flows = {}, pmtLabel = "";
      var pvv = vals.PV, fvv = vals.FV, pmtv = vals.PMT;
      if (solve === "PV") flows[0] = "PV = ?"; else if (pvv) flows[0] = "PV = " + money(pvv);
      if (solve === "FV") flows[Math.round(n)] = "FV = ?"; else if (fvv) flows[Math.round(n)] = (flows[Math.round(n)] ? flows[Math.round(n)] + " + " : "") + "FV = " + money(fvv);
      if (solve === "PMT") pmtLabel = "PMT = ? each " + period + (beg ? " (beginning)" : " (end)");
      else if (pmtv) pmtLabel = "PMT = " + money(pmtv) + " every " + period + (beg ? ", paid at the beginning of the " + period : ", paid at the end of the " + period);
      if (solve === "N") { flows[Math.round(n)] = undefined; }
      var tl = timelineSVG({ n: solve === "N" ? 5 : n, flows: flows, pmtLabel: pmtLabel, unitLabel: solve === "N" ? "N = ?  (" + periods + ")" : periods });
      tlHTML = tl;
    }
    var regsHTML = '<div class="hp-regs">' + ["N", "I/YR", "PV", "PMT", "FV"].map(function (k) { return '<div data-reg="' + k + '">' + k + "<b>—</b></div>"; }).join("") + "</div>";
    var side = sideShell(tlHTML + regsHTML);
    root.appendChild(side);

    /* build steps */
    var steps = [];
    steps.push({ keys: ["SHIFT_O", "C"], text: function () {
      return "Press the orange shift key, then <b>C</b>. This runs <b>C ALL</b> and wipes every register (N, I/YR, PV, PMT, FV) left over from the previous problem. It does <i>not</i> change the BEGIN/END setting" +
        (beg ? ", which we'll set next." : ", so check that <b>BEGIN</b> is not showing on the display. If it is, press the orange shift key and <b>MAR</b> to get back to END mode.");
    } });
    if (beg) steps.push({ keys: ["SHIFT_O", "MAR"], text: function () {
      return "Press the orange shift key, then <b>MAR</b> to run <b>Beg/End</b>. <b>BEGIN</b> now appears on the display: the calculator will treat each payment as arriving at the <i>start</i> of the period, which is what an annuity due needs.";
    } });
    order.forEach(function (k) {
      var s = spec[k] === undefined ? "0" : String(spec[k]);
      var v = vals[k];
      steps.push({ keys: numKeys(s).concat([k]), text: function (evs) {
        var last = evs[evs.length - 1], stored = fmt(last.value);
        var typed = "Type " + specText(s) + ", then press <b>" + k + "</b>. ";
        if (k === "N") return typed + "The calculator now holds " + plain(v) + " as the number of " + periods + (period !== "year" ? " (the years have been converted to " + periods + ")" : "") + ".";
        if (k === "I/YR") {
          if (s.indexOf("/") >= 0) return typed + "The annual rate has to be converted to a rate per " + period + " before it goes into I/YR. Letting the calculator do the division and pressing <b>=</b> leaves the result on the display, so pressing I/YR stores " + stored + "%.";
          return typed + "Interest goes in as a percentage (" + plain(v) + "), not as a decimal (" + plain(v / 100) + ").";
        }
        if (k === "PV") {
          if (v < 0) return typed + "Money that leaves your pocket today is a cash <i>outflow</i>, so the present value carries a minus sign. (Type the digits first, then +/−.)";
          if (v === 0) return typed + "Nothing changes hands at time 0 in this problem. Entering the zero explicitly is safer than trusting whatever was left in the register.";
          return typed + "The present value is entered as a positive amount because it is money received today.";
        }
        if (k === "PMT") {
          if (v === 0) return typed + "This is a lump-sum problem, so there is no periodic payment. A leftover PMT from an earlier problem is the single most common cause of a wrong answer, so always enter the 0.";
          if (v < 0) return typed + "Each deposit is money leaving your pocket, so the payment is negative.";
          return typed + "Each payment is money coming in to you, so it is positive.";
        }
        if (k === "FV") {
          if (v === 0) return typed + "There is no lump sum at the end of this annuity, so the future value is zero.";
          if (v > 0) return typed + "The amount received in the future is a cash inflow, so it is positive.";
          return typed + "This future amount is a cash outflow, so it is negative.";
        }
        return typed;
      } });
    });
    steps.push({ keys: [solve], text: function (evs) {
      var ev = evs[0], r = ev.value, res;
      if (!isFinite(r)) return "Press <b>" + solve + "</b>. The calculator can't find a solution with these inputs.";
      if (solve === "I/YR") res = '<span class="hp-res">' + fmt(r) + "%</span>";
      else if (solve === "N") res = '<span class="hp-res">' + fmt(r) + "</span> " + periods;
      else res = '<span class="hp-res">' + fmt(r) + "</span>";
      var t = "Press <b>" + solve + "</b> <i>without</i> typing a number first. With the other four values stored, the calculator solves for " + FULLNAME[solve] + ": " + res + ". ";
      if (solve === "PV" && r < 0) t += "It shows as a negative number because it is the amount you would pay out today.";
      else if (solve === "FV" && r > 0) t += "It is positive because it is money flowing back to you.";
      else if (solve === "FV" && r < 0) t += "It is negative because it is money you will owe at the end.";
      else if (solve === "PMT") t += (r < 0 ? "It is negative because each payment is money you pay out." : "It is positive because each payment is money you receive.");
      else if (solve === "I/YR") t += "This is the rate per " + period + " implied by the other four values.";
      if (d.note) t += " " + d.note;
      return t;
    } });
    steps.intro = "Press <b>Play</b> to step through the keystrokes" + (beg ? " for this annuity due." : ".");

    var regEls = {};
    side.querySelectorAll("[data-reg]").forEach(function (e) { regEls[e.getAttribute("data-reg")] = e; });
    var refresh = function (ev) {
      ["N", "I/YR", "PV", "PMT", "FV"].forEach(function (k) {
        var cell = regEls[k], b = cell.querySelector("b");
        var touched = !!engine.touched[k];
        b.textContent = touched ? fmt(engine.R[k]) : "—";
        cell.classList.toggle("hp-stored", !!(ev && ev.type === "store" && ev.reg === k));
        cell.classList.toggle("hp-solved", !!(ev && ev.type === "solve" && ev.reg === k));
      });
    };
    new Player(root, engine, view, steps, side, refresh);
  }

  /* ------------------------------------------------------------------ */
  /* Cash-flow widget                                                      */
  /* ------------------------------------------------------------------ */
  function initCF(root) {
    var d = root.dataset;
    var cfs = (d.cf || "0").split(",").map(function (s) { return s.trim(); });
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
    if (solve === "NPV") {
      steps.push({ keys: numKeys(iyr).concat(["I/YR"]), text: function () {
        return "Type " + specText(iyr) + ", then press <b>I/YR</b>. This is the discount rate the NPV function will use for every cash flow in the list.";
      } });
      steps.push({ keys: ["SHIFT_O", "PRC"], text: function (evs) {
        var r = evs[evs.length - 1].value;
        return "Press the orange shift key, then <b>PRC</b> to run <b>NPV</b>: <span class='hp-res'>" + fmt(r) + "</span>. Every cash flow has been discounted back to time 0 at " + plain(evalSpec(iyr)) + "% and added up (including CF0)." + (d.note ? " " + d.note : "");
      } });
    } else {
      steps.push({ keys: ["SHIFT_O", "CST"], text: function (evs) {
        var r = evs[evs.length - 1].value;
        if (!isFinite(r)) return "Press the orange shift key, then <b>CST</b> to run <b>IRR/YR</b>. No rate satisfies these cash flows.";
        return "Press the orange shift key, then <b>CST</b> to run <b>IRR/YR</b>: <span class='hp-res'>" + fmt(r) + "%</span>. This is the discount rate at which the NPV of the whole list is exactly zero. No I/YR is needed, because the rate is what you are solving for." + (d.note ? " " + d.note : "");
      } });
    }
    steps.intro = "Press <b>Play</b> to step through the keystrokes.";

    var cells = {};
    side.querySelectorAll("[data-cf]").forEach(function (e) { cells[e.getAttribute("data-cf")] = e; });
    var refresh = function (ev) {
      cfs.forEach(function (c, i) {
        var cell = cells[i], has = engine.cfs.length > i;
        cell.querySelector("b").textContent = has ? fmt(engine.cfs[i].amt, 2) : "—";
        cell.classList.toggle("hp-stored", !!(ev && ev.type === "cf" && ev.index === i));
      });
      if (cells.I) { cells.I.querySelector("b").textContent = engine.touched["I/YR"] ? fmt(engine.R["I/YR"]) : "—"; cells.I.classList.toggle("hp-stored", !!(ev && ev.type === "store" && ev.reg === "I/YR")); }
      var res = cells.RES, isRes = ev && (ev.type === "npv" || ev.type === "irr");
      if (isRes) res.querySelector("b").textContent = fmt(ev.value) + (ev.type === "irr" ? "%" : "");
      else if (!ev || ev.type === "clearall") res.querySelector("b").textContent = "—";
      res.classList.toggle("hp-solved", !!isRes);
    };
    new Player(root, engine, view, steps, side, refresh);
  }

  /* ------------------------------------------------------------------ */
  /* Key highlight widget (static)                                          */
  /* ------------------------------------------------------------------ */
  function initKeys(root) {
    var keys = (root.dataset.keys || "").split(",").map(function (s) { return s.trim(); }).filter(Boolean);
    root.classList.add("hp-widget", "hp-hl-only", "hp-static");
    var view = buildCalc(root, null, false);
    var eng = new Engine();
    view.lcd.textContent = root.dataset.display || "0.0000";
    if (root.dataset.begin === "1") view.ann.begin.classList.add("on");
    keys.forEach(function (k) { var b = view.keyEl(k); if (b) b.classList.add("hp-glow"); });
    view.el.setAttribute("aria-label", "HP 10bII+ calculator with " + keys.map(function (k) { return LABEL[k] || k; }).join(", ") + " highlighted");
  }

  /* ------------------------------------------------------------------ */
  function init() {
    document.querySelectorAll(".hp10bii:not([data-hp-ready])").forEach(function (el) { el.setAttribute("data-hp-ready", "1"); try { initTVM(el); } catch (e) { console.error("hp10bii", e); } });
    document.querySelectorAll(".hp10bii-cf:not([data-hp-ready])").forEach(function (el) { el.setAttribute("data-hp-ready", "1"); try { initCF(el); } catch (e) { console.error("hp10bii-cf", e); } });
    document.querySelectorAll(".hp10bii-keys:not([data-hp-ready])").forEach(function (el) { el.setAttribute("data-hp-ready", "1"); try { initKeys(el); } catch (e) { console.error("hp10bii-keys", e); } });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  window.HP10bII = { init: init, Engine: Engine };
})();

