/* ===== sd-graph.js v2.56 — data-driven supply & demand widgets =====
   Markup:  <div class="sdg"><script type="application/json">{ ...config... }<\/script></div>
   Top-level config:
     title, lede, caption         heading / intro / static caption (caption used only when there are no steps)
     steps: [caption, ...]        index 0 = start state; elements use `at`/`until` (step indices) to appear/vanish
     scenarios: {key:{label, ...overrides}}   one button per scenario; overrides merge over the base config
     panels: [panelCfg, panelCfg]  two side-by-side graphs (two-market). Otherwise the panel keys live at top level.
   Panel config:
     heading                      title above the panel (two-market only)
     axes: {x, y, xmax, ymax, xticks[], yticks[], money, cents, pct, k, grid, bg:false}
        x, y = axis titles, default 'Q' and 'P'. A word or two fits; they are never wrapped.
     curves[]: {id, label, pts:[[q,p],...], color, at, until, from, arrowP, shiftArrow, curved, thin, leader, dashed, lstart, ldx, ldy}
     areas[]:  {pts:[[q,p],...], label, boxed, color, edge, lp, ldx, ldy, at, until}   a shaded polygon under the curves (CS, PS, deadweight loss)
        label wraps on \n; boxed:true gives it a white box so it can be read over the curves crossing its shape
        lstart = put the curve label at the first point instead of the last; ldx/ldy nudge it
        label:"" draws no label at all (a lone PPF needs none); omitting label falls back to the id
        from   = id of the curve this one shifts away from (animated shift + arrow); arrowP = price height of arrow
        shiftArrow:false = animate and dim as usual but draw no shift arrow. Use it whenever the
                 widget already shows per-row arrows (table.arrows), which say the same thing once per row.
        curved = smooth through 3+ points (conceptual, non-linear look)
     points[]: {id, q, p, label, boxed, marker, pl, ql, color, at, until, hiAt, dx, dy, guides:false|'p'|'q', showP:false, showQ:false, dot:false}
        boxed: true   the label goes in a white box with its own border, so it can be read over the curves it sits on
        hiAt: n   re-marks the point from step n on, whenever it arrived -- for the corners of a shape a later step draws
        marker = "1"/"2" numbered circle;  pl/ql = symbolic axis labels ("P₁","Q₁") instead of numbers
     moves[]:  {from:[q,p], to:[q,p], at, until, color, offset}  arrow between two points, drawn `offset` px beside the curve (default 14; negative = other side)
     calcs[]:  "CS = 1/2 x 80 x ($5 - $3) = $80" | {text, at, until}   the working, under the plot
     hlines[]: {p, label, tag, tagdy, tagq, control, showP:false, color, at, until}   horizontal price line across the plot
                 `control:true` declares a ceiling/floor/world price -- drawn the same, but the
                 checks read it: no dot may sit on it, and it is not a disequilibrium price
     braces[]: {p, q1, q2, label, at, until, below:true|'in'|'axis', color}  curly brace spanning a gap at price p
     vbraces[]:{p1, p2, q, label, at, until, left, side, color}   the same brace turned upright, spanning a
        price gap. left:true is the mirror of a brace's below:true: it sits outside the P axis, clear of the
        plot and the tick numbers, with its label running up the axis, and widens the left margin to fit.
        Without left it sits inside the plot at quantity q, opening right unless side:'left'.
     table:    {cols[], series[], rows[[price,q,...]], arrows}    schedule beside the graph; arrows draws row shift arrows
     matrix:   {rows:{player,labels[]}, cols:{player,labels[]}, cells[[[aPayoff,bPayoff],...],...], marks[]}
        A payoff matrix instead of a plot. A mark names {row|col|cell}, optionally who:'a'|'b' for one
        player's line inside it, and pick:true for the one a comparison lands on. Marks take at/until.
     plays:    {rowhead, cols[], years[{label, cells[[move,amount],...], at, until}], total:{label,cells[]}, arrows[{from:[y,c], to:[y,c]}]}
     amort:    {amount, rate, term, terms:[15,30], rateMin, rateMax, rateStep, compare:[4,10], hideCompare}
        An amortization explorer: the engine computes the schedule and redraws. Rate and term change
        the curve; the year slider reads the split off it. The one widget here that is a model, not
        a drawing -- a share of a payment is a function of three inputs and no table can hold it.
        The same game played year after year: one row a year, a running total underneath, and an
        arrow carrying one year's move into the next year's answer. Years, total and arrows take at/until.
   Colors: 'ink' (default, black-navy), 'red' (shifted/new), 'teal', 'orange', 'grey'
   Presets (symbolic graphs, P₁/P₂/Q₁/Q₂, no numbers) — a few keys expand into a full config:
     {"preset":"shift", "shift":"D"|"S", "dir":"right"|"left", "good":"pasta", "event":"The price of pizza rises.", "why":"...", "static":true}
     {"preset":"double", "demand":"right"|"left", "supply":"right"|"left", "dD":40, "dS":15, "note":"...", "static":true}
     {"preset":"double", "demand":"right", "supply":"left", "compare":true}   two panels: larger supply shift vs larger demand shift
     Presets can be combined with title/lede/caption/steps overrides and with scenarios (each scenario gives its own shift/dir).
*/
(function () {
  var NS = 'http://www.w3.org/2000/svg';
  var C = {ink: 'var(--ink)', red: 'var(--red)', teal: 'var(--teal)', orange: 'var(--orange)', grey: 'var(--grey)', navy: 'var(--navy)'};
  function col(c) { return C[c || 'ink']; }
  function el(tag, a, text) { var e = document.createElementNS(NS, tag); for (var k in a) if (a[k] != null) e.setAttribute(k, a[k]); if (text != null) e.textContent = text; return e; }
  // A word subscript -- S_{Market}, d_{Firm} = MR -- set smaller and lighter
  // than the label it hangs off. Small capitals were the nearest thing the
  // text could do on its own and they render at full weight, so the subscript
  // read as capitals rather than as a subscript.
  function setLabel(node, str, x) {
    var parts = String(str).split(/_\{([^}]*)\}/), dy = 0;
    parts.forEach(function (part, i) {
      if (part === '') return;
      var sub = i % 2 === 1, a = {};
      if (x != null && i === 0) a.x = x;
      if (sub) { a.class = 'sub'; a.dy = 3 - dy; dy = 3; }
      else if (dy) { a.dy = -dy; dy = 0; }
      node.appendChild(el('tspan', a, part));
    });
    return node;
  }

// Measured in Chromium, per character (v2.45): ten copies of each between
  // two H's, so the side bearings cancel. Weights 700 and 800 at 12, 13 and
  // 14px agree to 0.0002em, so one table serves every label drawn here.
  // An average per *case* was the model at v2.44 and it was 20% narrow for
  // "S + Quota" -- a Q, a W or a + is half again an average capital -- so
  // the margin sized to that label cut it to "S + Quo". The third wrong
  // width model in three tries, and the first measured per character.
  // scripts/em_widths.py holds this table and prints it with --js; it is
  // pasted here, never retyped, and test_check_file.py fails on a drift.
  var EMW = {
      ' ':.201,'!':.241,'"':.436,'#':.738,'$':.601,'%':.792,'&':.683,
      '\'':.251,'(':.412,')':.412,'*':.475,'+':.6,',':.25,'-':.458,'.':.25,
      '/':.367,0:.684,1:.349,2:.6,3:.591,4:.673,5:.586,6:.6,7:.61,8:.597,
      9:.633,':':.25,';':.25,'=':.6,'?':.526,A:.755,B:.69,C:.704,D:.737,
      E:.644,F:.639,G:.793,H:.738,I:.272,J:.625,K:.672,L:.628,M:.881,N:.748,
      O:.812,P:.68,Q:.812,R:.678,S:.641,T:.66,U:.724,V:.745,W:.931,X:.711,
      Y:.719,Z:.625,'[':.394,']':.394,a:.555,b:.632,c:.518,d:.632,e:.589,
      f:.433,g:.628,h:.594,i:.245,j:.245,k:.568,l:.245,m:.905,n:.594,o:.616,
      p:.632,q:.632,r:.408,s:.491,t:.434,u:.594,v:.603,w:.78,x:.568,y:.589,
      z:.506,'²':.307,'³':.329,'¹':.195,'×':.6,'÷':.6,'ˢ':.381,'ᵂ':.694,
      'ᵈ':.479,'ᶜ':.413,'ᶠ':.377,'₀':.438,'₁':.438,'₂':.438,'₃':.438,
      '₄':.438,'₅':.438,'ₐ':.457,'→':.837,'−':.6,'≤':.837,'≥':.837};
  function emw(t) {
    var w = 0;
    String(t).split('').forEach(function (c) {
      // Anything unmeasured takes the widest of its class, so it is
      // over-counted rather than clipped.
      w += EMW[c] != null ? EMW[c]
         : /[A-Z]/.test(c) ? 1.102 : /[a-z]/.test(c) ? 1.041
         : /[0-9]/.test(c) ? 0.695 : 1.001;
    });
    return w;
  }
  function h(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  // pct is money's opposite number (v2.35): the income-distribution chapter
  // plots a cumulative percent against a cumulative percent, and every value
  // on both axes carries a % in the source.
  function fmtP(v, ax) { if (ax.pct) return v + '%'; if (!ax.money) return String(v); if (ax.cents) return '$' + Number(v).toFixed(2); return '$' + (Number.isInteger(v) ? v : v.toFixed(2)); }
  // pct:true is both axes; pct:'y' is the price axis alone, for a figure that
  // plots a percentage against something that is not one -- a share of the
  // payment against the year of the loan (v2.50).
  function fmtQ(v, ax) { if (ax.pct === true) return v + '%'; if (ax.k && v >= 1000) return (v / 1000) + 'k'; return v.toLocaleString('en-US'); }
  function merge(a, b) { var o = {}; for (var k in a) o[k] = a[k]; for (var k2 in b) o[k2] = b[k2]; return o; }

  // ---------- one SVG panel ----------
  function buildPanel(cfg) {
    // A one-line Q title is a letter or two and sits beside the tick row. A
    // wrapped one is a name that runs back across it, so it goes *below* the
    // ticks and the panel grows to hold it (v2.35) -- the same trade a
    // below-axis brace makes. The income-distribution chapter writes
    // "Cumulative % of Households" under its Q axis and the ticks are
    // percentages all the way along it.
    var ax = cfg.axes, W = 372;
    var xtitle = String(ax.x || 'Q').split('\n');
    var below = (cfg.braces || []).some(function (b) { return b.below === true; });
    var H = (below || xtitle.length > 1) ? 268 : 250;
    // A brace outside the P axis needs margin to sit in, the way a brace below
    // the Q axis needs the extra panel height above.
    var vleft = (cfg.vbraces || []).some(function (b) { return b.left; });
    // The left margin was a fixed 40/54/62, so a price-axis label wider than
    // that ran off the left of the viewBox and was simply cut in half --
    // "P* = ATC" rendered as "= ATC", with nothing reporting it. It is sized
    // to the widest label the axis actually carries now. Subscripts are set
    // at .72em, so they count for less, the same way check_file measures them.
    function axw(t) {
      t = String(t); var subs = 0;
      var plain = t.replace(/_\{([^}]*)\}/g, function (m, inner) { subs += emw(inner); return ''; });
      return 10.5 * (emw(plain) + 0.72 * subs);
    }
    var widest = 0;
    (ax.yticks || []).forEach(function (v) { widest = Math.max(widest, axw(fmtP(v, ax))); });
    (cfg.points || []).forEach(function (pt) {
      if (pt.showP === false) return;
      widest = Math.max(widest, axw(pt.pl != null ? pt.pl : fmtP(pt.p, ax)));
    });
    // A price line writes on the same axis (v2.43). Counting only the points
    // cut `P_{WORLD}` down to `WORLD` in the trade chapter -- the same defect
    // v2.27 and v2.28 fixed for the other two margins, in the one place left
    // that writes there.
    (cfg.hlines || []).forEach(function (l) {
      if (l.showP === false || (ax.yticks || []).indexOf(l.p) >= 0) return;
      widest = Math.max(widest, axw(l.label != null ? l.label : fmtP(l.p, ax)));
    });
    // A one-line price-axis title is a letter or two and sits just inside the
    // axis, where it has always sat. A wrapped one is a name -- "Wage /
    // Rate (W)" -- and the labor chapter puts that name clear to the left of
    // the axis, not pressed against it (v2.34). So it is anchored the other
    // way, and the margin carries it the same as a price label.
    var ytitle = String(ax.y || 'P').split('\n');
    var ytw = 0;
    if (ytitle.length > 1) {
      ytitle.forEach(function (rw) { ytw = Math.max(ytw, 14 * emw(rw)); });
    }
    var left = Math.max(ax.cents ? 62 : (ax.yticks && ax.yticks.length ? 54 : 40),
                        Math.ceil(widest) + 12,
                        Math.ceil(ytw) + 22) + (vleft ? 30 : 0);
    // And the same on the right, for the curve labels. A curve drawn out to
    // the edge of the plot puts its name past the edge of the panel, where it
    // is simply cut off: "D = MB = MSB" rendered as "D = M" with every check
    // passing, because a label's width was measured against the other labels
    // and never against the panel holding them. The margin was a fixed 36,
    // which fits "MC" and nothing longer. Curve labels are 13px at weight 800,
    // which measures about .70em a character.
    function labelChars(c) {
      var rows = String(c.label == null ? c.id : c.label).split('\n'), n = 0;
      rows.forEach(function (rw) {
        var subs = 0;
        var plain = rw.replace(/_\{([^}]*)\}/g, function (m, inner) { subs += emw(inner); return ''; });
        n = Math.max(n, emw(plain) + 0.72 * subs);
      });
      return n;
    }
    var right = 36;
    // Widening the margin narrows the plot, which pulls the anchors left
    // again, so this settles rather than solving in one go.
    for (var pass = 0; pass < 6; pass++) {
      var pw = W - left - right, want = 36;
      (cfg.curves || []).forEach(function (c) {
        var pts = c.pts || [];
        if (!pts.length || c.label === '') return;
        var lp = c.lstart ? pts[0] : pts[pts.length - 1];
        var endsAt = left + (lp[0] / ax.xmax) * pw + (c.ldx || 6);
        var overflow = endsAt + 13 * labelChars(c) + 4 - W;
        if (overflow > 0) want = Math.max(want, right + overflow);
      });
      if (want <= right + 0.01) break;
      right = want;
    }
    right = Math.min(right, W - left - 120);   // never starve the plot

    var O = {x: left, y: 205}, PW = W - left - right, PH = 178;
    var X = function (q) { return O.x + (q / ax.xmax) * PW; }, Y = function (p) { return O.y - (p / ax.ymax) * PH; };
    var svg = el('svg', {viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': cfg.heading || cfg.title || 'Supply and demand graph'});
    var g = el('g', {}); svg.appendChild(g);
    var parts = [], byId = {};
    function reg(node, spec) { node.classList.add('fade'); parts.push({node: node, spec: spec}); if (spec.id) byId[spec.id] = {node: node, spec: spec}; return node; }

    if (ax.bg !== false) g.appendChild(el('rect', {class: 'plotbg', x: O.x, y: 14, width: PW + 14, height: O.y - 14}));
    if (ax.grid) {
      (ax.xticks || []).forEach(function (q) { g.appendChild(el('line', {class: 'grid', x1: X(q), y1: 14, x2: X(q), y2: O.y})); });
      (ax.yticks || []).forEach(function (p) { g.appendChild(el('line', {class: 'grid', x1: O.x, y1: Y(p), x2: O.x + PW + 14, y2: Y(p)})); });
    }
    g.appendChild(el('path', {class: 'ax', d: 'M' + O.x + ' 14 L' + O.x + ' ' + O.y + ' L' + (O.x + PW + 14) + ' ' + O.y}));
    (ax.xticks || []).forEach(function (q) { g.appendChild(el('text', {class: 'tk', x: X(q), y: O.y + 15, 'text-anchor': 'middle'}, fmtQ(q, ax))); });
    (ax.yticks || []).forEach(function (p) { g.appendChild(el('text', {class: 'tk', x: O.x - 6, y: Y(p) + 4, 'text-anchor': 'end'}, fmtP(p, ax))); });
    // Axis titles. P and Q fit anywhere, but a PPF names its axes with words, so
    // the x title is anchored to the right edge instead of running off it, and the
    // y title sits in the headroom above the plot instead of inside its top-left
    // corner. Keep axis titles to a word or two: nothing here can wrap them.
    // Axis titles wrap on \n (v2.33). "Amount of Employment (L)" is 23
    // characters at 14px/800 -- two thirds of the panel on one line, and the
    // labor chapter stacks it on two, as it stacks "Wage Rate (W)". Both
    // stack downward from where a one-line title sits, so nothing already
    // drawn moves; a title tall enough to leave the panel is check_file's to
    // report, the same as any other label.
    function axisTitle(text, x, y, anchor) {
      var t = el('text', {class: 'axlbl', x: x, y: y, 'text-anchor': anchor});
      String(text).split('\n').forEach(function (rw, i) {
        t.appendChild(el('tspan', {x: x, dy: i ? 15 : 0}, rw));
      });
      return t;
    }
    g.appendChild(axisTitle(ax.x || 'Q', O.x + PW + 34,
                            O.y + (xtitle.length > 1 ? 36 : 16), 'end'));
    // A wrapped title drops below the topmost tick rather than standing
    // beside it (v2.35), which is where the source puts it and what keeps the
    // margin down to the title's own width: side by side, "100%" and
    // "Cumulative / % of Income" cost 40px of plot between them.
    g.appendChild(axisTitle(ax.y || 'P', ytitle.length > 1 ? O.x - 12 : O.x - 2,
                            ytitle.length > 1 ? 52 : 11,
                            ytitle.length > 1 ? 'end' : 'start'));

    // Surplus and deadweight loss ARE areas, and before v2.11 the engine drew
    // none: "area fills of any kind" was on the list of things it does not do,
    // which left an entire chapter unconvertible. A polygon is enough. These
    // graphs draw demand and supply as straight lines, so every region the
    // chapter needs -- consumer surplus, producer surplus, total surplus, a
    // deadweight wedge -- has straight edges and is named by its corners.
    // The fill is drawn here, after the axes and before the curves, so a wash
    // never hides a line. Its *name* is not: an area label goes in with the
    // curves drawn under it (v2.46), because a wash is not a background and a
    // curve run through a label strikes it through. Boxed, it masks what
    // passes beneath, which is what the printed figure gets for free by
    // filling its deadweight wedges solid black. (Ian, 2026-09-30: "have the
    // CS, DWL and the grey box be on top".)
    var areaLabels = [];
    (cfg.areas || []).forEach(function (a) {
      var cc = col(a.color), grp = el('g', {class: 'area-g'});
      // edge:true outlines the polygon in its own colour. Two pieces of one
      // surplus -- the triangle and rectangle a trapezoid splits into -- are
      // the same wash and read as a single blob without a line between them.
      // The stroke goes in a style attribute because the sheet sets
      // stroke:none on .area, and a rule beats a presentation attribute.
      grp.appendChild(el('polygon', {class: 'area', fill: cc,
        style: a.edge ? 'stroke:' + cc + ';stroke-width:1.6;stroke-opacity:1' : null,
        points: a.pts.map(function (p) { return X(p[0]) + ',' + Y(p[1]); }).join(' ')}));
      if (a.label) {
        var lgrp = el('g', {class: 'area-g'});
        // The centroid keeps a label inside its own shape, which is right for
        // the triangles this draws. A thin wedge has no room for one, so `lp`
        // places it by hand instead -- outside the shape if that is what fits.
        var n = a.pts.length,
            lp = a.lp || [a.pts.reduce(function (t, p) { return t + p[0]; }, 0) / n,
                          a.pts.reduce(function (t, p) { return t + p[1]; }, 0) / n];
        // Wraps on \n and takes `boxed`, the way a point's label does
        // (v2.41). Set on one line, "Tariff Revenue" is wider than the
        // rectangle it names and crosses both curves; a wash is not a
        // background, so the box is what lets it be read there.
        var arows = String(a.label).split('\n'),
            ax0 = X(lp[0]) + (a.ldx || 0),
            ay0 = Y(lp[1]) + (a.ldy || 0) - (arows.length - 1) * 5;
        if (a.boxed) {
          // 5.3px a character until v2.46, which is an average and so too
          // narrow for a word of wide letters: "Importers" hung out of both
          // sides of its own box. The box was a little short for its
          // descenders too, so the p sat on the bottom border.
          var aw = 0;
          arows.forEach(function (rw) { aw = Math.max(aw, 10 * emw(rw)); });
          lgrp.appendChild(el('rect', {class: 'lblbox', x: ax0 - aw / 2 - 4,
            y: ay0 - 9, width: aw + 8, height: 11 * arows.length + 3,
            stroke: cc}));
        }
        var at = el('text', {class: 'arlbl', x: ax0, y: ay0,
                             'text-anchor': 'middle', fill: cc});
        arows.forEach(function (rw, i) {
          at.appendChild(el('tspan', {x: ax0, dy: i ? 10 : 0}, rw));
        });
        lgrp.appendChild(at);
        areaLabels.push({node: lgrp, spec: a});
      }
      g.appendChild(reg(grp, a));
    });

    function arrow(x1, y1, x2, y2, c, cls) {
      var dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len,
          // The head was a fixed 7x3.6 however long the arrow was, so a short
          // movement arrow -- two firms sliding a few units along one cost
          // curve -- came out almost entirely head. It scales with length now,
          // down to 55% for the shortest, and is a shade smaller throughout.
          k = Math.max(0.55, Math.min(1, len / 46)), hh = 6.2 * k, ww = 3.1 * k,
          bx = x2 - ux * hh, by = y2 - uy * hh;
      return el('path', {class: 'arrow ' + (cls || ''), stroke: c, d: 'M' + x1 + ' ' + y1 + ' L' + x2 + ' ' + y2 + ' M' + (bx - uy * ww) + ' ' + (by + ux * ww) + ' L' + x2 + ' ' + y2 + ' L' + (bx + uy * ww) + ' ' + (by - ux * ww)});
    }
    function pathD(pts, curved) {
      var P = pts.map(function (p) { return [X(p[0]), Y(p[1])]; });
      if (!curved || P.length < 3) return P.map(function (p, i) { return (i ? 'L' : 'M') + p[0] + ' ' + p[1]; }).join(' ');
      var d = 'M' + P[0][0] + ' ' + P[0][1];
      for (var i = 0; i < P.length - 1; i++) {
        var p0 = P[i - 1] || P[i], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2] || p2;
        d += ' C' + (p1[0] + (p2[0] - p0[0]) / 6) + ' ' + (p1[1] + (p2[1] - p0[1]) / 6) + ' ' + (p2[0] - (p3[0] - p1[0]) / 6) + ' ' + (p2[1] - (p3[1] - p1[1]) / 6) + ' ' + p2[0] + ' ' + p2[1];
      }
      return d;
    }
    // Where does the *drawn* curve sit? For a curved pair the spline bows away
    // from the polyline through its points, so a shift arrow whose ends were
    // computed from the polyline was inset from the wrong place and landed on
    // the curve. Sample the same Catmull-Rom the renderer draws.
    function samplePx(pts, curved) {
      var P = pts.map(function (q) { return [X(q[0]), Y(q[1])]; });
      if (!curved || P.length < 3) return P;
      var out = [P[0]], N = 24;
      for (var i = 0; i < P.length - 1; i++) {
        var p0 = P[i - 1] || P[i], p1 = P[i], p2 = P[i + 1], p3 = P[i + 2] || p2;
        var c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
        var c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
        for (var k = 1; k <= N; k++) {
          var t = k / N, u = 1 - t;
          out.push([u * u * u * p1[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * p2[0],
                    u * u * u * p1[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * p2[1]]);
        }
      }
      return out;
    }
    function xAtPx(pts, curved, y) {
      var S = samplePx(pts, curved);
      for (var i = 0; i < S.length - 1; i++) {
        var a = S[i], b = S[i + 1];
        if ((y - a[1]) * (y - b[1]) <= 0 && a[1] !== b[1])
          return a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]);
      }
      var f = S[0], l = S[S.length - 1];
      return f[1] === l[1] ? f[0] : f[0] + (y - f[1]) * (l[0] - f[0]) / (l[1] - f[1]);
    }
    // The drawn curve's direction where it crosses height y, as |dx|,|dy| of a
    // unit vector -- what a horizontal arrow's clearance from it depends on.
    function dirAtPx(pts, curved, y) {
      var S = samplePx(pts, curved);
      for (var i = 0; i < S.length - 1; i++) {
        var a = S[i], b = S[i + 1];
        if ((y - a[1]) * (y - b[1]) <= 0 && a[1] !== b[1]) {
          var dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy);
          return [Math.abs(dx) / l, Math.abs(dy) / l];
        }
      }
      return [0, 1];
    }
    // How far each end of a shift arrow stands off its curve (v2.56). A fixed
    // 11px along the arrow is 11px from a steep curve but only 5.7px from one
    // at 31 degrees -- every symbolic preset -- which left 2.7px of white
    // between the head and the line it points at once both strokes were drawn.
    // So the inset is solved for the slope: the tail, the tip and both barbs
    // clear their curve by ARROW_GAP, edge to edge, at the thickest either line
    // is ever drawn (3.6px curve and 3.4px arrow on the step they arrive).
    // Never less than the old 11. Two curves close together get the smallest
    // head the engine draws (55%, which arrow() picks for a short arrow), and
    // only where even that leaves under 10px of arrow does the old 11 stand.
    var ARROW_GAP = 3.5, ARROW_REACH = ARROW_GAP + 1.8 + 1.7;
    function shiftInsets(src, c, yA, x0, x1) {
      var u0 = dirAtPx(src.pts, src.curved, yA), u1 = dirAtPx(c.pts, c.curved, yA),
          sy0 = Math.max(u0[1], 0.1), sy1 = Math.max(u1[1], 0.1), span = Math.abs(x1 - x0);
      var d0 = Math.max(11, Math.min(40, ARROW_REACH / sy0));
      // the barbs reach hh back and ww out: 6.2 x 3.1 at full size
      function head(hh, ww) { return Math.max(11, Math.min(40, Math.max(ARROW_REACH / sy1, (ARROW_REACH + ww * u1[0]) / sy1 - hh))); }
      var d1 = head(6.2, 3.1);
      if (span - d0 - d1 >= 14) return [d0, d1];
      d1 = head(3.4, 1.7);
      return span - d0 - d1 >= 10 ? [d0, d1] : [11, 11];
    }
    function qAt(pts, p) {
      for (var i = 0; i < pts.length - 1; i++) { var a = pts[i], b = pts[i + 1]; if ((p - a[1]) * (p - b[1]) <= 0 && a[1] !== b[1]) return a[0] + (p - a[1]) * (b[0] - a[0]) / (b[1] - a[1]); }
      var a2 = pts[0], b2 = pts[pts.length - 1]; return a2[0] + (p - a2[1]) * (b2[0] - a2[0]) / (b2[1] - a2[1]);
    }

    (cfg.curves || []).forEach(function (c) {
      var cc = col(c.color), grp = el('g', {class: 'curve-g'});
      // `leader` is the hairline that runs from a boxed label to the curve it
      // names (v2.37). It is thinner than `thin`, which is the weight of a
      // line that is part of the drawing -- a line of equality, or the curve a
      // shift moved away from. A leader is not part of the drawing; it is
      // pointing at it, and at `thin` it reads as another curve.
      var path = el('path', {class: 'curve' + (c.leader ? ' leader' : c.thin ? ' thin' : ''),
                             d: pathD(c.pts, c.curved), stroke: cc});
      if (c.dashed) path.setAttribute('stroke-dasharray', '6 4');
      grp.appendChild(path);
      var last = c.pts[c.pts.length - 1], up = last[1] > c.pts[0][1], lp = c.lstart ? c.pts[0] : last;
      // label:"" draws nothing. A lone frontier needs no name -- the axis titles
      // already say what it is -- but the id is still needed by table.series, and
      // falling back to it parked "PPF" on the curve. Omitting label still uses the id.
      // A curve label may carry newlines, like a brace label. "Labor Demand"
      // on one line is wider than the right-hand margin it is anchored in and
      // runs off the plot; the artwork sets it on two lines.
      var ctext = c.label != null ? c.label : (c.id || ''),
          crows = String(ctext).split('\n'),
          clx = X(lp[0]) + (c.ldx || 6), cly = Y(lp[1]) + (c.ldy || (up ? 2 : 6)),
          cnode = el('text', {class: 'clbl', x: clx, y: cly, fill: cc});
      crows.forEach(function (row, ri) {
        var line = el('tspan', {x: clx, dy: ri ? 14 : 0});
        setLabel(line, row);
        cnode.appendChild(line);
      });
      grp.appendChild(cnode);
      if (c.from && byId[c.from]) {
        var src = byId[c.from].spec, ap = c.arrowP != null ? c.arrowP : (c.pts[0][1] + last[1]) / 2;
        var yA = Y(ap);
        var x0 = xAtPx(src.pts, src.curved, yA), x1 = xAtPx(c.pts, c.curved, yA), s = Math.sign(x1 - x0);
        grp.dataset.dx = x1 - x0; grp.dataset.dy = 0; grp.classList.add('move');
        // shiftArrow:false keeps the slide and the dimming but drops the arrow, for
        // widgets whose per-row arrows already show the shift once per schedule row.
        // The insets are measured off the drawn curves, so the arrow clears
        // both of them however far the spline bows and whatever its slope.
        if (c.shiftArrow !== false) {
          var ins = shiftInsets(src, c, yA, x0, x1);
          g.appendChild(reg(arrow(x0 + s * ins[0], yA, x1 - s * ins[1], yA, cc, 'shift'), {at: c.at || 0, until: c.until}));
        }
      }
      g.appendChild(grp); reg(grp, c);
    });

    (cfg.hlines || []).forEach(function (l) {
      var cc = col(l.color || 'red'), grp = el('g', {});
      grp.appendChild(el('line', {class: 'hline', stroke: cc, x1: O.x, y1: Y(l.p), x2: O.x + PW + 8, y2: Y(l.p)}));
      // showP:false drops the price from the axis, as it does on a point
      // (v2.42). A line named only by its tag -- "World Price + Tariff" --
      // has nothing to write there, and without this it wrote its own
      // coordinate, which on a symbolic panel is a number out of thin air.
      if (l.showP !== false && (ax.yticks || []).indexOf(l.p) < 0)
        grp.appendChild(setLabel(el('text', {class: 'tk strong', x: O.x - 6, y: Y(l.p) + 4, 'text-anchor': 'end', fill: cc}), l.label || fmtP(l.p, ax)));
      // `label` names the line's price on the P axis; `tag` names the line
      // itself, at its right-hand end, the way the printed artwork writes
      // "World Price" beside the line rather than only on the axis.
      // tagdy nudges it off the line: above by default, below where the
      // curve that climbs to the right-hand corner is already there.
      // tagq anchors the name over a chosen quantity instead of the line's
      // right-hand end, for a panel where a curve runs through that corner.
      if (l.tag) grp.appendChild(setLabel(el('text', {class: 'tag',
        x: l.tagq != null ? X(l.tagq) : O.x + PW + 6,
        y: Y(l.p) + (l.tagdy != null ? l.tagdy : -6),
        'text-anchor': l.tagq != null ? 'middle' : 'end', fill: cc}), l.tag));
      g.appendChild(grp); reg(grp, l);
    });

    // The area names, held back from their fills so the curves and the price
    // lines draw underneath them (v2.46). Still before the points and braces:
    // a marked reading is never covered by a name.
    areaLabels.forEach(function (al) { g.appendChild(reg(al.node, al.spec)); });

    (cfg.braces || []).forEach(function (b) {
      var cc = col(b.color || 'red'), grp = el('g', {});
      // Four positions, all of them in the artwork. "axis" keeps the drop
      // guides running from the price line but sets the bracket down by the Q
      // axis with its label above -- the tariff figures are drawn that way,
      // where the space just under the price line is taken by the revenue
      // rectangle, while the import figures hug the line with "in".
      var inplot = b.below === 'in', out = b.below === true, atax = b.below === 'axis';
      var x1 = X(Math.min(b.q1, b.q2)), x2 = X(Math.max(b.q1, b.q2)),
          y = out ? O.y + 22 : atax ? O.y - 12 : Y(b.p) + (inplot ? 8 : -8),
          dir = (out || inplot) ? 1 : -1, m = (x1 + x2) / 2;
      // Each half of the curl needs about 2*hh of run. Over a short span a
      // fixed hh makes the segments overlap and the brace reads as a scribble,
      // so it shrinks with the span it has to cover.
      var hh = Math.max(2.5, Math.min(7, (x2 - x1) / 4));
      var d = 'M' + x1 + ' ' + y + ' Q' + x1 + ' ' + (y + dir * hh) + ' ' + (x1 + hh) + ' ' + (y + dir * hh) + ' L' + (m - hh) + ' ' + (y + dir * hh) + ' Q' + m + ' ' + (y + dir * hh) + ' ' + m + ' ' + (y + dir * 2 * hh) +
              ' Q' + m + ' ' + (y + dir * hh) + ' ' + (m + hh) + ' ' + (y + dir * hh) + ' L' + (x2 - hh) + ' ' + (y + dir * hh) + ' Q' + x2 + ' ' + (y + dir * hh) + ' ' + x2 + ' ' + y;
      grp.appendChild(el('path', {class: 'brace', stroke: cc, d: d}));
      // A brace label may carry newlines. The artwork wraps its longer ones
      // -- "Shortage (187.5 units)" goes on two lines -- and on one line the
      // text is wider than the gap between the curves it has to sit in.
      var rows = String(b.label).split('\n'),
          ly = y + dir * 2 * hh + ((out || inplot) ? 12 : -4);
      if (dir < 0) ly -= (rows.length - 1) * 13;   // grow upward, away from the line
      var txt = el('text', {class: 'tag', x: m, y: ly, 'text-anchor': 'middle', fill: cc});
      rows.forEach(function (row, ri) {
        txt.appendChild(el('tspan', {x: m, dy: ri ? 13 : 0}, row));
      });
      grp.appendChild(txt);
      if (!out) { [b.q1, b.q2].forEach(function (q) { grp.appendChild(el('line', {class: 'guide', stroke: cc, x1: X(q), y1: Y(b.p), x2: X(q), y2: O.y})); }); }
      g.appendChild(grp); reg(grp, b);
    });

    // The brace turned upright, spanning a price gap. left:true mirrors the
    // horizontal brace's below:true -- outside the P axis, clear of the plot and
    // the tick numbers, label running up the axis because horizontal text does
    // not fit in the margin.
    (cfg.vbraces || []).forEach(function (b) {
      var cc = col(b.color || 'red'), grp = el('g', {});
      var y1 = Y(Math.max(b.p1, b.p2)), y2 = Y(Math.min(b.p1, b.p2));
      // Just outside the widest price-axis label, rather than a fixed 32px
      // in from the axis (v2.33): the labor chapter's CWD brace spans two
      // wages named W_{Alaska} and W_{Hawaii} and was drawn straight through
      // both. The clearance was then measured off the widest label *and*
      // kept a 32px floor, so on a panel that writes nothing on its price
      // axis -- the real estate chapter's equity diagrams -- the brace stood
      // 32px out in empty space, a long way from the gap it was measuring
      // (v2.51). It is 12px clear of whatever is there, which is nothing
      // when nothing is there.
      var x = b.left ? O.x - 12 - widest : X(b.q);
      var dir = (b.left || b.side === 'left') ? -1 : 1, m = (y1 + y2) / 2;
      var hh = Math.max(2.5, Math.min(7, (y2 - y1) / 4));
      var d = 'M' + x + ' ' + y1 +
              ' Q' + (x + dir * hh) + ' ' + y1 + ' ' + (x + dir * hh) + ' ' + (y1 + hh) +
              ' L' + (x + dir * hh) + ' ' + (m - hh) +
              ' Q' + (x + dir * hh) + ' ' + m + ' ' + (x + dir * 2 * hh) + ' ' + m +
              ' Q' + (x + dir * hh) + ' ' + m + ' ' + (x + dir * hh) + ' ' + (m + hh) +
              ' L' + (x + dir * hh) + ' ' + (y2 - hh) +
              ' Q' + (x + dir * hh) + ' ' + y2 + ' ' + x + ' ' + y2;
      grp.appendChild(el('path', {class: 'brace', stroke: cc, d: d}));
      if (b.left) {
        var lx = x + dir * (2 * hh + 8);
        grp.appendChild(el('text', {class: 'tag', x: lx, y: m, 'text-anchor': 'middle',
          transform: 'rotate(-90 ' + lx + ' ' + m + ')', fill: cc}, b.label));
      } else {
        // Wraps on \n, the way a horizontal brace (v2.17) and a curve label
        // (v2.19) already do. Without it the externalities chapter's
        // "Marginal External Cost" had to be one 22-character run, which fits
        // nowhere inside a plot -- the source sets it on three lines for
        // exactly that reason. The block is centred on the brace's middle.
        // ldx/ldy nudge it, as they do every other label in the schema. It
        // was centred on the brace and nothing else, so on a panel where the
        // gap being measured is barely taller than the label -- the external
        // benefit figures -- there was no position that cleared the curves
        // either side of it. The source does not centre these either.
        var vrows = String(b.label).split('\n'),
            vlx = x + dir * (2 * hh + 6) + (b.ldx || 0),
            vtxt = el('text', {class: 'tag vin', x: vlx,
                               y: m + 4 - (vrows.length - 1) * 6.5 + (b.ldy || 0),
                               'text-anchor': dir > 0 ? 'start' : 'end', fill: cc});
        vrows.forEach(function (row, ri) {
          var vline = el('tspan', {x: vlx, dy: ri ? 13 : 0});
          setLabel(vline, row);
          vtxt.appendChild(vline);
        });
        grp.appendChild(vtxt);
      }
      g.appendChild(grp); reg(grp, b);
    });

    (cfg.moves || []).forEach(function (m) {
      var x1 = X(m.from[0]), y1 = Y(m.from[1]), x2 = X(m.to[0]), y2 = Y(m.to[1]);
      var off = m.offset != null ? m.offset : 14, len = Math.hypot(x2 - x1, y2 - y1), nx = -(y2 - y1) / len * off, ny = (x2 - x1) / len * off;
      var a = arrow(x1 + nx, y1 + ny, x2 + nx, y2 + ny, col(m.color), 'mv');
      g.appendChild(a); reg(a, m);
    });

    (cfg.points || []).forEach(function (p) {
      var cc = col(p.color), grp = el('g', {class: 'ptg'});
      // guides: the dashed elbow from the P axis across to the point and down
      // to the Q axis. "p" draws only the leg to the price axis and "q" only
      // the leg to the quantity axis, because the printed artwork rarely wants
      // both: a world-price quantity gets a vertical guide only (the price line
      // is already drawn through it), and an equilibrium under trade gets a
      // horizontal guide only (its quantity is not the point being made).
      if (p.guides !== false) {
        var hleg = 'M' + O.x + ' ' + Y(p.p) + ' L' + X(p.q) + ' ' + Y(p.p),
            vleg = 'M' + X(p.q) + ' ' + Y(p.p) + ' L' + X(p.q) + ' ' + O.y,
            gd = p.guides === 'p' ? hleg : p.guides === 'q' ? vleg : hleg + ' L' + X(p.q) + ' ' + O.y;
        grp.appendChild(el('path', {class: 'guide', stroke: cc, d: gd}));
      }
      // dot:false keeps the axis labels and drops the marker. A quantity
      // marked by a vertical line wants its name on the axis in the same tick
      // style as every other number there, and nothing drawn on the line
      // itself. Without this the only way to get that label was a curve label,
      // which is 13px at weight 800 and reads as a chunky block next to the
      // 10.5px ticks it sits among.
      if (p.dot !== false) {
        grp.appendChild(el('circle', {class: 'halo', cx: X(p.q), cy: Y(p.p), r: p.marker ? 10.5 : 8.5}));
        grp.appendChild(el('circle', {class: 'pt' + (p.marker ? ' mk' : ''), cx: X(p.q), cy: Y(p.p), r: p.marker ? 6 : 4.2, stroke: cc}));
        if (p.marker) grp.appendChild(el('text', {class: 'mktxt', x: X(p.q), y: Y(p.p) + 2.6, 'text-anchor': 'middle'}, p.marker));
      }
      // Wraps on \n and runs through setLabel, the way curve labels, braces
      // and axis labels already do (v2.34). The labor chapter names the two
      // halves of its supply curve in the source's own words -- "Income
      // Effect > Substitution Effect" over "W↑ ⇒ LS↓" -- which is two lines
      // in the source for the good reason that one does not fit.
      if (p.label) {
        var lrows = String(p.label).split('\n');
        var lx = X(p.q) + (p.dx != null ? p.dx : 9);
        var lrh = p.boxed ? 11.5 : 13;
        var ly = Y(p.p) + (p.dy != null ? p.dy : -9) - (lrows.length - 1) * lrh / 2;
        // boxed:true puts the label in a white box with its own border, so it
        // can be read over the curves it sits on (v2.36). Three Lorenz curves
        // converge on one corner and there is no gap between them wide enough
        // for a horizontal label -- the source boxes each year and runs a
        // short leader to its curve, and this is what draws that box. The
        // width is estimated the same way check_file measures a label, so the
        // two never disagree about where the box is.
        if (p.boxed) {
          var bw = 0;
          lrows.forEach(function (rw) {
            var bs = 0;
            var bp = rw.replace(/_\{([^}]*)\}/g, function (m, inner) { bs += inner.length; return ''; });
            bw = Math.max(bw, 5.9 * (bp.length + 0.72 * bs));
          });
          grp.appendChild(el('rect', {class: 'lblbox', x: lx - 4.5, y: ly - 9,
            width: bw + 9, height: 11.5 * lrows.length + 2, stroke: cc}));
        }
        var lt = el('text', {class: 'tag' + (p.boxed ? ' boxed' : ''),
                             x: lx, y: ly, fill: cc});
        lrows.forEach(function (rw, i) {
          var ts = el('tspan', {x: lx, dy: i ? lrh : 0});
          setLabel(ts, rw); lt.appendChild(ts);
        });
        grp.appendChild(lt);
      }
      // A price line only suppresses the point's own label while the two are
      // on screen together. Ignoring the step windows here silently dropped
      // $600 from step 1 of the generator figure, because a ceiling appearing
      // at step 3 sits at that price -- leaving a dashed guide running to a
      // blank axis three steps before the line existed.
      function shares(a, b) {
        var a0 = a.at || 0, a1 = a.until, b0 = b.at || 0, b1 = b.until;
        return Math.max(a0, b0) < Math.min(a1 == null ? 1e9 : a1, b1 == null ? 1e9 : b1);
      }
      var pl = p.pl || ((p.showP !== false && (ax.yticks || []).indexOf(p.p) < 0 && !(cfg.hlines || []).some(function (l) { return l.p === p.p && shares(l, p); })) ? fmtP(p.p, ax) : null);
      var ql = p.ql || ((p.showQ !== false && (ax.xticks || []).indexOf(p.q) < 0) ? fmtQ(p.q, ax) : null);
      // through setLabel like the curve labels and tags: a point's axis label
      // printed _{1} verbatim, braces and all, when it was written that way
      if (pl) grp.appendChild(setLabel(el('text', {class: 'tk strong', x: O.x - 6, y: Y(p.p) + 4, 'text-anchor': 'end', fill: cc}), pl));
      if (ql) grp.appendChild(setLabel(el('text', {class: 'tk strong', x: X(p.q), y: O.y + 15, 'text-anchor': 'middle', fill: cc}), ql));
      grp.addEventListener('mouseenter', function () { grp.classList.add('hi'); });
      grp.addEventListener('mouseleave', function () { grp.classList.remove('hi'); });
      g.appendChild(grp); reg(grp, p);
    });

    var rowHooks = [];
    if (cfg.table) {
      var t = cfg.table;
      t.rows.forEach(function (row) {
        var dots = [], p = row[0];
        (t.series || []).forEach(function (sid, si) {
          var sc = byId[sid] && byId[sid].spec, q = row[si + 1];
          var dot = el('circle', {class: 'pt sched', cx: X(q), cy: Y(p), r: 3.8, stroke: col(sc && sc.color)});
          g.appendChild(dot); reg(dot, {at: (sc && sc.at) || 0}); dots.push(dot);
          if (t.arrows && si > 0) { var q0 = row[si], s = Math.sign(q - q0); g.appendChild(reg(arrow(X(q0) + s * 6, Y(p), X(q) - s * 6, Y(p), col('ink'), 'row'), {at: (sc && sc.at) || 0})); }
        });
        rowHooks.push(dots);
      });
    }
    return {svg: svg, parts: parts, byId: byId, rowHooks: rowHooks, cfg: cfg};
  }

  // ---------- widget ----------
  function Widget(host, cfg) { this.host = host; this.cfg = cfg; this.step = 0; this.build(); }
  Widget.prototype.build = function () {
    var cfg = this.cfg, self = this, host = this.host; host.innerHTML = '';
    if (cfg.title) host.appendChild(h('h4', null, cfg.title));
    if (cfg.lede) host.appendChild(h('p', 'sdg-lede', cfg.lede));
    if (cfg.scenarios) {
      var sc = h('div', 'sdg-scen'); sc.setAttribute('role', 'group');
      Object.keys(cfg.scenarios).forEach(function (k) {
        var b = h('button', null, cfg.scenarios[k].label); b.type = 'button';
        b.setAttribute('aria-pressed', k === cfg.activeScenario ? 'true' : 'false');
        b.addEventListener('click', function () { host.dispatchEvent(new CustomEvent('sdg-scenario', {detail: k})); });
        sc.appendChild(b);
      });
      host.appendChild(sc);
    }
    // A payoff matrix is a grid of numbers, not a plot, so it is built as
    // HTML the way the schedule table is -- and it takes at/until marks like
    // anything else, which is the whole reason it is a widget: the chapter
    // walks the reader through the matrix one comparison at a time, and a
    // picture of the finished grid cannot do that. (v2.39)
    this.mparts = [];
    if (cfg.matrix) { this.panels = []; this.buildMatrix(); return this.finish(); }
    if (cfg.plays) { this.panels = []; this.buildPlays(); return this.finish(); }
    if (cfg.amort) { this.panels = []; this.buildAmort(); return this.finish(); }
    var panels = cfg.panels || [cfg];
    this.panels = panels.map(buildPanel);
    var body = h('div', 'sdg-body' + (cfg.table ? ' has-table' : '') + (panels.length > 1 ? ' two' : ''));
    this.panels.forEach(function (pn, i) {
      var fig = h('figure');
      if (pn.cfg.heading) fig.appendChild(h('figcaption', null, pn.cfg.heading));
      fig.appendChild(pn.svg); body.appendChild(fig);
      if (i === 0 && panels.length > 1 && cfg.link !== false) { var a = h('div', 'sdg-between'); a.innerHTML = '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M4 20 H26 M18 11 L28 20 L18 29" /></svg>'; body.appendChild(a); }
    });
    if (cfg.table) {
      var t = cfg.table, ax = cfg.axes, tbl = h('table', 'sdg-table'), thead = h('thead'), tr = h('tr');
      t.cols.forEach(function (c) { tr.appendChild(h('th', null, c)); }); thead.appendChild(tr); tbl.appendChild(thead);
      var tbody = h('tbody'), hooks = this.panels[0].rowHooks;
      t.rows.forEach(function (row, ri) {
        var r = h('tr');
        row.forEach(function (v, i) { r.appendChild(h('td', null, i === 0 ? fmtP(v, ax) : fmtQ(v, ax))); });
        r.addEventListener('mouseenter', function () { r.classList.add('hi'); hooks[ri].forEach(function (d) { d.classList.add('hi'); }); });
        r.addEventListener('mouseleave', function () { r.classList.remove('hi'); hooks[ri].forEach(function (d) { d.classList.remove('hi'); }); });
        tbody.appendChild(r);
      });
      tbl.appendChild(tbody); var wrap = h('div', 'sdg-tablewrap'); wrap.appendChild(tbl); body.insertBefore(wrap, body.firstChild);
    }
    // The plot and its working share a row when the widget is wide enough for
    // both, and the working wraps underneath when it is not. Set under the
    // plot unconditionally it costs five or six lines of height on a page
    // where vertical space is the scarce thing.
    var main = h('div', 'sdg-main' + (cfg.calcs && cfg.calcs.length ? ' has-calc' : ''));
    main.appendChild(body);
    host.appendChild(main);
    // finish() puts the working inside this row, and it is a different
    // function: reached through the local, it threw "main is not defined" and
    // took the step controls down with it, so every calcs widget in the
    // government-intervention file was dead on arrival with check_file and
    // render_widgets both passing. mobile_check is what saw it, because it is
    // the one that drives the buttons. (v2.45)
    this.main = main;
    return this.finish();
  };

  // The payoff matrix. Two players, two strategies each, and four cells
  // carrying both players' payoffs -- laid out as the printed matrix is, with
  // each player's name outside its own strategy labels.
  Widget.prototype.buildMatrix = function () {
    var self = this, m = this.cfg.matrix, host = this.host;
    var rl = m.rows.labels, cl = m.cols.labels;
    var tbl = h('table', 'sdg-mx'), tb = h('tbody');
    var r0 = h('tr');
    r0.appendChild(h('td', 'mx-pad')); r0.appendChild(h('td', 'mx-pad'));
    var pc = h('td', 'mx-player', m.cols.player); pc.colSpan = cl.length;
    r0.appendChild(pc); tb.appendChild(r0);
    var r1 = h('tr');
    r1.appendChild(h('td', 'mx-pad')); r1.appendChild(h('td', 'mx-pad'));
    cl.forEach(function (c) { r1.appendChild(h('td', 'mx-head', c)); });
    tb.appendChild(r1);
    this.cells = []; this.rowHeads = []; this.colHeads = [];
    [].slice.call(r1.querySelectorAll('.mx-head')).forEach(function (td) {
      self.colHeads.push(td);
    });
    rl.forEach(function (rlab, i) {
      var tr = h('tr'), row = [];
      if (i === 0) {
        var pr = h('td', 'mx-player mx-rowp', m.rows.player);
        pr.rowSpan = rl.length; tr.appendChild(pr);
      }
      var rh = h('td', 'mx-head', rlab);
      self.rowHeads.push(rh); tr.appendChild(rh);
      cl.forEach(function (_, j) {
        var td = h('td', 'mx-cell'), pair = m.cells[i][j], lns = {};
        ['a', 'b'].forEach(function (who, k) {
          var ln = h('div', 'ln ln-' + who, pair[k]);
          td.appendChild(ln); lns[who] = ln;
        });
        tr.appendChild(td); row.push({td: td, lns: lns});
      });
      tb.appendChild(tr); self.cells.push(row);
    });
    tbl.appendChild(tb);
    var wrap = h('div', 'sdg-mxwrap'); wrap.appendChild(tbl);
    host.appendChild(wrap);
    // A mark names a row, a column or one cell, and optionally one player's
    // line inside it; `pick` is the one the comparison lands on. `given` is
    // the move being held fixed -- the row or column the comparison is
    // conditioned on. Without it the two lit payoffs read as arbitrary cells:
    // the argument is "if B complies, A does better cheating", and the "if"
    // half was nowhere on the drawing. (v2.40)
    (m.marks || []).forEach(function (mk) {
      var targets = [];
      if (mk.given) {
        var head = mk.row != null ? self.rowHeads[mk.row]
                 : mk.col != null ? self.colHeads[mk.col] : null;
        if (head) self.mparts.push({node: head, spec: mk, cls: 'given'});
      }
      self.cells.forEach(function (row, i) {
        row.forEach(function (cell, j) {
          var hit = mk.cell ? (mk.cell[0] === i && mk.cell[1] === j)
                  : mk.row != null ? mk.row === i
                  : mk.col != null ? mk.col === j : false;
          if (hit) targets.push(mk.who ? cell.lns[mk.who] : cell.td);
        });
      });
      targets.forEach(function (n) {
        self.mparts.push({node: n, spec: mk, cls: mk.pick ? 'pick' : 'on'});
      });
    });
  };

  // The same game played year after year (v2.48): one row a year, a running
  // total underneath, and a red arrow carrying one year's move into the next
  // year's answer -- which is the whole of tit-for-tat, and the one thing the
  // printed table has to state all at once. A year at a time, the reader sees
  // the cheating year pay and the answer arrive the year after.
  Widget.prototype.buildPlays = function () {
    var self = this, pl = this.cfg.plays, host = this.host;
    var tbl = h('table', 'sdg-plays'), tb = h('tbody');
    var hr = h('tr', 'pl-headrow');
    hr.appendChild(h('th', 'pl-corner', pl.rowhead || ''));
    (pl.cols || []).forEach(function (c) { hr.appendChild(h('th', 'pl-col', c)); });
    tb.appendChild(hr);
    self.playCells = [];
    (pl.years || []).forEach(function (y) {
      var tr = h('tr', 'pl-row'), row = [];
      tr.appendChild(h('td', 'pl-year', y.label));
      (y.cells || []).forEach(function (c) {
        var td = h('td', 'pl-cell');
        td.appendChild(h('i', 'pl-move', c[0]));
        td.appendChild(h('span', 'pl-amt', '(' + c[1] + ')'));
        tr.appendChild(td); row.push(td);
      });
      tb.appendChild(tr); self.playCells.push(row);
      self.mparts.push({node: tr, spec: y, cls: 'shown'});
    });
    if (pl.total) {
      var tr = h('tr', 'pl-row pl-totalrow');
      tr.appendChild(h('td', 'pl-year', pl.total.label || 'Total'));
      (pl.total.cells || []).forEach(function (c) { tr.appendChild(h('td', 'pl-total', c)); });
      tb.appendChild(tr);
      self.mparts.push({node: tr, spec: pl.total, cls: 'shown'});
    }
    tbl.appendChild(tb);
    var wrap = h('div', 'sdg-playswrap');
    wrap.appendChild(tbl);
    // The arrows are drawn over the table rather than in it, because each one
    // runs from inside one cell to inside another a row down: there is no cell
    // to put it in. So they are measured off the laid-out table -- after the
    // web font arrives, and again whenever the table changes size.
    var svg = el('svg', {class: 'pl-arrows'});
    wrap.appendChild(svg);
    host.appendChild(wrap);
    self.playArrows = (pl.arrows || []).map(function (a) {
      var path = el('path', {class: 'arrow pl-arrow', stroke: col(a.color || 'red')});
      svg.appendChild(path);
      self.mparts.push({node: path, spec: a, cls: 'shown'});
      return {spec: a, path: path};
    });
    function place() {
      var box = wrap.getBoundingClientRect();
      if (!box.width) return;
      svg.setAttribute('viewBox', '0 0 ' + box.width + ' ' + box.height);
      svg.setAttribute('width', box.width);
      svg.setAttribute('height', box.height);
      self.playArrows.forEach(function (ar) {
        var f = (self.playCells[ar.spec.from[0]] || [])[ar.spec.from[1]],
            t = (self.playCells[ar.spec.to[0]] || [])[ar.spec.to[1]];
        if (!f || !t) return;
        // An arrow runs from where one cell's writing ends to where the
        // other's begins, measured off the text rather than set at some
        // fraction of the cell: a fraction lands on the closing bracket at
        // one end and on the move at the other, and it lands somewhere
        // different again the moment an amount is a character longer.
        var fb = f.getBoundingClientRect(), tb2 = t.getBoundingClientRect(),
            rightwards = ar.spec.from[1] < ar.spec.to[1],
            fs = textSpan(f), ts = textSpan(t), gap = 7,
            x1 = (rightwards ? fs.r + gap : fs.l - gap),
            x2 = (rightwards ? ts.l - gap : ts.r + gap),
            y1 = fb.top + fb.height / 2 - box.top,
            y2 = tb2.top + tb2.height / 2 - box.top;
        // Where the writing leaves no room between the columns -- a narrow
        // screen -- the arrow straddles the border they share instead.
        if ((rightwards ? x2 - x1 : x1 - x2) < 12) {
          var mid = rightwards ? (fb.right + tb2.left) / 2 : (tb2.right + fb.left) / 2;
          x1 = mid - (rightwards ? 9 : -9);
          x2 = mid + (rightwards ? 9 : -9);
        }
        ar.path.setAttribute('d', headed(x1 - box.left, y1, x2 - box.left, y2));
      });
    }
    self.placePlays = place;
    place();
    if (window.ResizeObserver) { new ResizeObserver(place).observe(wrap); }
    if (document.fonts && document.fonts.ready) { document.fonts.ready.then(place); }
  };

  // How far the writing inside a cell actually reaches. The cell is mostly
  // padding by design -- the channel the arrows run in -- so its own edges say
  // nothing about where the text stops.
  function textSpan(cell) {
    var l = Infinity, r = -Infinity;
    [].slice.call(cell.children).forEach(function (k) {
      var b = k.getBoundingClientRect();
      if (!b.width) return;
      l = Math.min(l, b.left); r = Math.max(r, b.right);
    });
    if (l === Infinity) { var cb = cell.getBoundingClientRect(); return {l: cb.left, r: cb.right}; }
    return {l: l, r: r};
  }

  // An arrow between two pixel points, head scaled to its length the way the
  // plot's own arrows are (v2.26).
  function headed(x1, y1, x2, y2) {
    var dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy) || 1,
        ux = dx / len, uy = dy / len,
        k = Math.max(0.55, Math.min(1, len / 46)), hh = 6.2 * k, ww = 3.1 * k,
        bx = x2 - ux * hh, by = y2 - uy * hh;
    return 'M' + x1 + ' ' + y1 + ' L' + x2 + ' ' + y2 +
           ' M' + (bx - uy * ww) + ' ' + (by + ux * ww) + ' L' + x2 + ' ' + y2 +
           ' L' + (bx + uy * ww) + ' ' + (by - ux * ww);
  }

  // ---------------------------------------------------------------- amort --
  // An amortization explorer (v2.50). Every other widget here draws data the
  // config states; this one is a model, because the share of a payment that
  // is interest is a function of three inputs -- amount, rate, term -- and a
  // precomputed track can hold one of them at a time, not all three. The
  // config states the loan; the engine works out the schedule.
  //
  // Interest orange and principal teal, the two colours this set already uses
  // for "what the other side gets" and "what you keep", and the split the
  // printed figure shades.
  var AW = 372, AH = 236, AM = {l: 40, r: 14, t: 14, b: 34};

  function schedule(amount, apr, years) {
    var r = apr / 1200, n = Math.round(years * 12),
        pmt = r === 0 ? amount / n : amount * r / (1 - Math.pow(1 + r, -n)),
        rows = [{bal: amount, cumInt: 0, cumPrin: 0, share: r === 0 ? 0 : amount * r / pmt}],
        bal = amount, ci = 0, cp = 0;
    for (var m = 1; m <= n; m++) {
      var it = bal * r, pr = pmt - it;
      bal = Math.max(0, bal - pr); ci += it; cp += pr;
      rows.push({bal: bal, cumInt: ci, cumPrin: cp, share: it / pmt});
    }
    return {pmt: pmt, n: n, rows: rows};
  }

  function money(x) {
    var v = Math.round(x);
    return '$' + Math.abs(v).toLocaleString('en-US');
  }
  function pctTxt(x, d) { return (x * 100).toFixed(d == null ? 0 : d) + '%'; }
  function yearTxt(m) {
    if (m === 0) return 'start';
    return (m / 12) + (m === 12 ? ' year' : ' years');
  }

  Widget.prototype.buildAmort = function () {
    var self = this, a = this.cfg.amort, host = this.host,
        state = {apr: a.rate != null ? a.rate : 7,
                 years: a.term != null ? a.term : 30,
                 amount: a.amount != null ? a.amount : 300000,
                 month: 0, compare: false},
        terms = a.terms || [15, 30],
        cmp = a.compare || [4, 10];

    var svg = el('svg', {viewBox: '0 0 ' + AW + ' ' + AH, role: 'img',
      'aria-label': 'The share of each payment that goes to interest and to principal over the life of the loan'});
    var plot = h('div', 'am-plot'); plot.appendChild(svg); host.appendChild(plot);

    var CWp = AW - AM.l - AM.r, CHp = AH - AM.t - AM.b;
    function xOf(m, n) { return AM.l + CWp * m / n; }
    function yOf(sh) { return AM.t + CHp * (1 - sh); }
    function boundary(sch) {
      var d = '', i;
      for (i = 0; i <= sch.n; i++) {
        d += (i ? 'L' : 'M') + xOf(i, sch.n).toFixed(1) + ' ' +
             yOf(i === 0 ? sch.rows[1].share : sch.rows[i].share).toFixed(1);
      }
      return d;
    }

    // The controls, in the order the question is usually asked: what rate,
    // over how long, and then where in the loan are we.
    var ctl = h('div', 'am-ctl');
    function row(labelText, node, outNode) {
      var r = h('div', 'am-row');
      r.appendChild(h('span', 'am-lab', labelText));
      r.appendChild(node);
      if (outNode) r.appendChild(outNode);
      ctl.appendChild(r);
      return r;
    }
    var rateIn = h('input'), rateOut = h('span', 'am-out'),
        yearIn = h('input'), yearOut = h('span', 'am-out'),
        seg = h('div', 'am-seg');
    rateIn.type = 'range'; rateIn.className = 'am-range';
    rateIn.min = a.rateMin != null ? a.rateMin : 1;
    rateIn.max = a.rateMax != null ? a.rateMax : 15;
    rateIn.step = a.rateStep != null ? a.rateStep : 0.25;
    rateIn.value = state.apr;
    rateIn.setAttribute('aria-label', 'Interest rate');
    // Whole years (Ian, 2026-09-30). The schedule is indexed by month, so the
    // reading is still taken from a month -- but always the first of a year,
    // and every way in snaps to one: the slider, the arrow keys and a drag
    // across the figure. A chart that answers "14.3 years" is answering a
    // question nobody asked of a figure whose own ticks are 0, 15 and 30.
    yearIn.type = 'range'; yearIn.className = 'am-range';
    yearIn.min = 0; yearIn.step = 1; yearIn.value = 0;
    yearIn.setAttribute('aria-label', 'Year of the loan');
    row('Interest rate', rateIn, rateOut);
    var termBtns = terms.map(function (t) {
      var b = h('button', null, t + ' yrs'); b.type = 'button';
      // Keep the year when the term changes, clamped into the new one: what
      // the toggle is for is "year 13 of a 30-year loan against year 13 of a
      // 15-year one", and resetting to the start throws that comparison away.
      b.addEventListener('click', function () { state.years = t; redraw(); });
      seg.appendChild(b); return {btn: b, term: t};
    });
    row('Loan term', seg);
    row('Year', yearIn, yearOut);
    host.appendChild(ctl);

    var cards = h('div', 'am-cards');
    function card(cls, name) {
      var c = h('div', 'am-card' + (cls ? ' ' + cls : '')), v = h('b');
      c.appendChild(h('span', null, name)); c.appendChild(v);
      cards.appendChild(c); return {box: c, val: v};
    }
    var cInt = card('c-orange', 'Interest share of the payment'),
        cPrin = card('c-teal', 'Principal share of the payment'),
        cPmt = card('', 'Monthly payment'),
        cCum = card('', 'Interest paid so far'),
        cBal = card('wide', 'Remaining balance');
    var balPct = h('span', 'am-balpct'), bar = h('div', 'am-bar'), barFill = h('i');
    bar.appendChild(barFill);
    cBal.box.appendChild(balPct); cBal.box.appendChild(bar);
    host.appendChild(cards);

    var note = h('p', 'am-note'); note.setAttribute('aria-live', 'polite');
    host.appendChild(note);

    if (!a.hideCompare && cmp.length) {
      var lab = h('label', 'am-check'), box = h('input');
      box.type = 'checkbox';
      lab.appendChild(box);
      lab.appendChild(h('span', null, 'Show ' + cmp.join('% and ') + '% alongside'));
      box.addEventListener('change', function () { state.compare = box.checked; redraw(); });
      host.appendChild(lab);
    }

    var sch;

    function drawPlot() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var bp = boundary(sch);
      svg.appendChild(el('path', {class: 'am-area am-prin', d: bp + ' L' + (AW - AM.r) + ' ' + yOf(1) + ' L' + AM.l + ' ' + yOf(1) + ' Z'}));
      svg.appendChild(el('path', {class: 'am-area am-int', d: bp + ' L' + (AW - AM.r) + ' ' + yOf(0) + ' L' + AM.l + ' ' + yOf(0) + ' Z'}));
      [0.25, 0.5, 0.75].forEach(function (gv) {
        svg.appendChild(el('line', {class: 'am-grid', x1: AM.l, x2: AW - AM.r, y1: yOf(gv), y2: yOf(gv)}));
      });
      // The comparison curves go under the one the controls are set to, so
      // the reader's own loan stays the dominant line -- but their names go
      // over everything, or the curve being dragged past a label rubs it out.
      // (Ian, 2026-09-30; the same order the area names take since v2.46.)
      var cmpLabels = [];
      if (state.compare) {
        cmp.forEach(function (ap, i) {
          var c = schedule(state.amount, ap, state.years);
          svg.appendChild(el('path', {class: 'am-cmp', d: boundary(c)}));
          var lm = Math.round(c.n * (i === 0 ? 0.14 : 0.6));
          cmpLabels.push(el('text', {class: 'am-cmplbl', x: xOf(lm, c.n) + 4,
            y: yOf(c.rows[lm].share) - 5}, ap + '%'));
        });
      }
      svg.appendChild(el('path', {class: 'am-line', d: bp}));
      svg.appendChild(el('path', {class: 'ax', d: 'M' + AM.l + ' ' + AM.t + ' L' + AM.l + ' ' + (AH - AM.b) + ' L' + (AW - AM.r) + ' ' + (AH - AM.b)}));
      [0, 0.25, 0.5, 0.75, 1].forEach(function (gv) {
        svg.appendChild(el('text', {class: 'tk', x: AM.l - 6, y: yOf(gv) + 3.6, 'text-anchor': 'end'}, pctTxt(gv)));
      });
      var stepY = state.years <= 15 ? 3 : 5;
      for (var y = 0; y <= state.years; y += stepY) {
        svg.appendChild(el('text', {class: 'tk', x: xOf(y * 12, sch.n), y: AH - AM.b + 14, 'text-anchor': 'middle'}, String(y)));
      }
      svg.appendChild(el('text', {class: 'axlbl', x: AW - AM.r, y: AH - 4, 'text-anchor': 'end'}, 'Year'));
      // The cursor's line goes on before the names, and its dot and chip
      // after them: a dashed line is part of the drawing and a name is what
      // the drawing is called, so the line passes behind "Interest" the same
      // way the curves do. (Ian, 2026-09-30.) The chip is the exception --
      // it is the reading, and it has to be on top of everything.
      cLine = el('line', {class: 'am-cline'});
      svg.appendChild(cLine);
      svg.appendChild(el('text', {class: 'am-areatext am-t-prin', x: AM.l + CWp * 0.74, y: AM.t + 22, 'text-anchor': 'middle'}, 'Principal'));
      svg.appendChild(el('text', {class: 'am-areatext am-t-int', x: AM.l + CWp * 0.26, y: AH - AM.b - 18, 'text-anchor': 'middle'}, 'Interest'));
      cmpLabels.forEach(function (n) { svg.appendChild(n); });
      cursor = el('g', {class: 'am-cursor'});
      cDot = el('circle', {class: 'am-cdot', r: 4.6});
      // The reading travels with the point (v2.52). Otherwise the year and
      // the share are down in the cards and the eye has to leave the curve
      // to read what it is pointing at.
      cChip = el('rect', {class: 'am-chip', rx: 4, ry: 4, height: 18});
      cChipT = el('text', {class: 'am-chiptxt', 'text-anchor': 'middle'});
      cursor.appendChild(cDot);
      cursor.appendChild(cChip); cursor.appendChild(cChipT);
      svg.appendChild(cursor);
    }

    var cursor, cLine, cDot, cChip, cChipT;

    function update() {
      var m = Math.min(sch.n, Math.max(0, state.month)),
          r = sch.rows[m], share = m === 0 ? sch.rows[1].share : r.share,
          x = xOf(m, sch.n), y = yOf(share);
      cLine.setAttribute('x1', x); cLine.setAttribute('x2', x);
      cLine.setAttribute('y1', AM.t); cLine.setAttribute('y2', AH - AM.b);
      cDot.setAttribute('cx', x); cDot.setAttribute('cy', y);
      // Measured off the character table rather than counted (v2.45), so the
      // chip fits the words rather than roughly fitting them, and clamped to
      // the plot at both ends -- it flips below the point near the top.
      var tag = 'Yr ' + (m % 12 ? (m / 12).toFixed(1) : String(m / 12)) +
                ': ' + pctTxt(share) + ' interest',
          tw = 11 * emw(tag) + 14,
          cx = Math.min(AW - AM.r - tw / 2, Math.max(AM.l + tw / 2, x)),
          cy = y - 28;
      if (cy < AM.t + 2) cy = y + 12;
      cChip.setAttribute('x', cx - tw / 2); cChip.setAttribute('y', cy);
      cChip.setAttribute('width', tw);
      cChipT.setAttribute('x', cx); cChipT.setAttribute('y', cy + 12.5);
      cChipT.textContent = tag;
      cInt.val.textContent = pctTxt(share, 1);
      cPrin.val.textContent = pctTxt(1 - share, 1);
      cPmt.val.textContent = money(sch.pmt);
      cCum.val.textContent = money(r.cumInt);
      cBal.val.textContent = money(r.bal);
      balPct.textContent = pctTxt(r.bal / state.amount) + ' of the original ' + money(state.amount);
      barFill.style.width = (100 * r.bal / state.amount).toFixed(1) + '%';
      yearOut.textContent = yearTxt(m);
      yearIn.value = m / 12;
      var cross = null, k;
      for (k = 1; k <= sch.n; k++) { if (sch.rows[k].share < 0.5) { cross = k; break; } }
      var t = m === 0
        ? 'The very first payment is ' + pctTxt(share) + ' interest, and only ' + pctTxt(1 - share) + ' of it comes off the balance.'
        : 'After ' + yearTxt(m) + ' you have paid ' + money(r.cumInt) +
          ' in interest and ' + money(r.cumPrin) + ' of principal, so ' + pctTxt(r.bal / state.amount) + ' of the loan is still owed.';
      t += cross
        ? ' Principal does not become the larger half of the payment until year ' + Math.ceil(cross / 12) + '.'
        : ' Interest stays the larger half of every payment for the whole term.';
      note.textContent = t;
    }

    function redraw() {
      sch = schedule(state.amount, state.apr, state.years);
      yearIn.max = state.years;
      state.month = Math.min(Math.round(state.month / 12) * 12, sch.n);
      rateOut.textContent = (Math.round(state.apr * 100) / 100) + '%';
      termBtns.forEach(function (tb) {
        tb.btn.setAttribute('aria-pressed', String(tb.term === state.years));
      });
      drawPlot();
      update();
    }

    rateIn.addEventListener('input', function () {
      state.apr = parseFloat(rateIn.value); redraw();
    });
    yearIn.addEventListener('input', function () {
      state.month = Math.round(parseFloat(yearIn.value)) * 12; update();
    });

    // Drag across the figure itself, and walk it a month at a time with the
    // arrow keys: the reading the widget exists for is "what about year 12",
    // and reaching for a slider under the plot is a worse way to ask it than
    // pointing at the year. (Ian, 2026-09-30, from the example.)
    function fromX(clientX) {
      var r = svg.getBoundingClientRect();
      if (!r.width) return;
      var frac = ((clientX - r.left) / r.width * AW - AM.l) / CWp;
      state.month = Math.round(Math.min(1, Math.max(0, frac)) * state.years) * 12;
      update();
    }
    // A mouse reads the figure by moving over it, with nothing held down --
    // there is no reason to make someone click to ask what year 12 looks
    // like. A finger has no hover, so touch still needs the drag. (Ian,
    // 2026-09-30; the example does the same.)
    var dragging = false;
    svg.setAttribute('tabindex', '0');
    svg.addEventListener('pointerdown', function (e) {
      dragging = true; svg.setPointerCapture(e.pointerId); fromX(e.clientX);
      e.preventDefault();
    });
    svg.addEventListener('pointermove', function (e) {
      if (dragging || e.pointerType === 'mouse') fromX(e.clientX);
    });
    svg.addEventListener('pointerup', function (e) {
      dragging = false;
      if (svg.hasPointerCapture(e.pointerId)) svg.releasePointerCapture(e.pointerId);
    });
    svg.addEventListener('pointercancel', function () { dragging = false; });
    svg.addEventListener('keydown', function (e) {
      var d = e.key === 'ArrowRight' || e.key === 'ArrowUp' ? 1
            : e.key === 'ArrowLeft' || e.key === 'ArrowDown' ? -1
            : e.key === 'PageUp' ? 5 : e.key === 'PageDown' ? -5
            : e.key === 'Home' ? -state.years : e.key === 'End' ? state.years : 0;
      if (!d) return;
      state.month = Math.min(sch.n, Math.max(0, state.month + d * 12));
      update(); e.preventDefault();
    });
    redraw();
  };

  Widget.prototype.finish = function () {
    var cfg = this.cfg, self = this, host = this.host;

    // calcs: the working, set beside the plot the way the artwork prints it
    // beneath each diagram -- a reader who only sees "CS = $80" cannot get
    // there themselves. Each line's closing "= result" is set apart, which is
    // the red underline in the source. Lines take at/until like anything else,
    // so a walkthrough can add the arithmetic as it reaches it.
    self.calcs = [];
    if (cfg.calcs && cfg.calcs.length) {
      var cbox = h('div', 'sdg-calc');
      cfg.calcs.forEach(function (c) {
        var spec = (typeof c === 'string') ? {text: c} : c,
            line = h('div', 'sdg-calcline'), t = spec.text || '', cut = t.lastIndexOf(' = ');
        if (cut > 0) {
          line.appendChild(document.createTextNode(t.slice(0, cut + 3)));
          line.appendChild(h('span', 'res', t.slice(cut + 3)));
        } else { line.textContent = t; }
        cbox.appendChild(line);
        self.calcs.push({node: line, spec: spec});
      });
      (this.main || host).appendChild(cbox);
    }

    if (cfg.steps && cfg.steps.length > 1) {
      var ctrl = h('div', 'sdg-ctrl'), prev = h('button', null, 'Back'), next = h('button', null, 'Next step'), reset = h('button', null, 'Start over'), lbl = h('span', 'sdg-step');
      prev.type = next.type = reset.type = 'button';
      [prev, next, reset, lbl].forEach(function (x) { ctrl.appendChild(x); }); host.appendChild(ctrl);
      var cap = h('p', 'sdg-cap'); cap.setAttribute('aria-live', 'polite'); host.appendChild(cap);
      this.ui = {prev: prev, next: next, lbl: lbl, cap: cap};
      var n = cfg.steps.length;
      prev.addEventListener('click', function () { if (self.step > 0) { self.step--; self.render(); } });
      next.addEventListener('click', function () { if (self.step < n - 1) { self.step++; self.render(); } });
      reset.addEventListener('click', function () { self.step = 0; self.render(); });
    } else if (cfg.caption) host.appendChild(h('p', 'sdg-cap', cfg.caption));
    this.render();
  };
  Widget.prototype.render = function () {
    var s = this.step, cfg = this.cfg;
    (this.mparts || []).forEach(function (mp) {
      var at = mp.spec.at || 0, until = mp.spec.until;
      mp.node.classList.toggle(mp.cls, s >= at && (until == null || s < until));
    });
    this.panels.forEach(function (pn) {
      pn.parts.forEach(function (pt) {
        var at = pt.spec.at || 0, until = pt.spec.until, on = s >= at && (until == null || s < until);
        pt.node.classList.toggle('off', !on);
        // Which element is this step's? Without that, a walkthrough that leaves
        // earlier points on screen gives no clue which one the caption means.
        // What this step brought in is highlighted; what an earlier step
        // brought in stays, but steps back.
        // hiAt re-marks a point from that step on, whenever it arrived. A
        // deadweight-loss wedge has three corners that come in over two steps,
        // and on the step that shades it all three are its corners -- ringing
        // only the last one drawn says the other two belong to something else.
        var hz = pt.spec.hiAt, held = hz != null && s >= hz;
        pt.node.classList.toggle('new', on && s > 0 && (at === s || held));
        pt.node.classList.toggle('prior', on && at > 0 && at < s && !held);
        if (pt.node.dataset.dx != null) pt.node.style.transform = on ? 'translate(0,0)' : 'translate(' + (-pt.node.dataset.dx) + 'px,0)';
      });
      (pn.cfg.curves || []).forEach(function (c) { if (c.from && pn.byId[c.from]) pn.byId[c.from].node.classList.toggle('dim', s >= (c.at || 0)); });
      // dimAt fades a curve from that step on, so a label can be read over it.
      // The externalities figures name the gap between two cost curves at the
      // quantity it is measured at, and the curve above runs right through the
      // only place that label fits.
      (pn.cfg.curves || []).forEach(function (c) {
        if (c.dimAt != null && pn.byId[c.id]) pn.byId[c.id].node.classList.toggle('faint', s >= c.dimAt);
      });
    });
    (this.calcs || []).forEach(function (c) {
      var at = c.spec.at || 0, until = c.spec.until;
      // display, not opacity: an invisible line that still takes its height
      // leaves a gap the reader has to wonder about
      c.node.classList.toggle('hide', !(s >= at && (until == null || s < until)));
    });
    if (this.ui) {
      var n = cfg.steps.length;
      this.ui.cap.textContent = cfg.steps[s];
      this.ui.lbl.textContent = 'Step ' + (s + 1) + ' of ' + n;
      this.ui.prev.disabled = s === 0; this.ui.next.disabled = s === n - 1;
    }
  };


  // ---------- presets: symbolic (no-number) graphs from a few settings ----------
  function clipLine(intercept, slope, lo, hi) { // p = intercept + slope*q, return pts with p in [lo,hi] and q in [4,104]
    var pts = [];
    [4, 104].forEach(function (q) { var p = intercept + slope * q; if (p < lo) { p = lo; } if (p > hi) { p = hi; } pts.push([(p - intercept) / slope, p]); });
    return pts;
  }
  // A preset's own default height for a shift arrow (v2.56). Every line a
  // preset draws is straight, so a clear price is arithmetic: both ends on the
  // plot (a leftward demand shift at 88 put the new curve past the P axis and
  // the arrow across it), no other line or marked point inside the arrow's
  // span, and away from the curve labels at the lines' ends. The nearest such
  // price to the old default wins, so a panel that was clear is unchanged.
  // A price that also keeps clear of the marks' dashed guides is preferred;
  // one that crosses a guide is taken only where nothing else is clear, which
  // is the house rule for arrows and guides.
  // lines: [{q: fn(p)}]; pair: [srcIndex, dstIndex]; marks: [[q, p]].
  function presetArrowP(lines, pair, pref, marks) {
    function offGuides(p, lo, hi) {
      return marks.every(function (m) {
        var crossesV = p < m[1] + 4 && m[0] > lo - 4 && m[0] < hi + 4,   // the leg down to Q
            crossesH = Math.abs(p - m[1]) < 4 && lo < m[0] + 4;           // the leg across to P
        return !crossesV && !crossesH;
      });
    }
    function clear(p, strict) {
      var q0 = lines[pair[0]].q(p), q1 = lines[pair[1]].q(p), lo = Math.min(q0, q1), hi = Math.max(q0, q1);
      if (lo < 12 || hi > 100 || hi - lo < 8) return false;
      for (var i = 0; i < lines.length; i++) {
        if (i === pair[0] || i === pair[1]) continue;
        var q = lines[i].q(p); if (q > lo - 6 && q < hi + 6) return false;
      }
      if (!marks.every(function (m) { return Math.abs(m[1] - p) >= 8 || m[0] < lo - 6 || m[0] > hi + 6; })) return false;
      return !strict || offGuides(p, lo, hi);
    }
    for (var pass = 0; pass < 2; pass++) {
      for (var k = 0; k <= 76; k++) {
        var up = pref + k, dn = pref - k;
        if (dn >= 16 && dn <= 92 && clear(dn, !pass)) return dn;
        if (up >= 16 && up <= 92 && clear(up, !pass)) return up;
      }
    }
    return pref;
  }
  function shiftPanel(o) { // o: {shift:'D'|'S', dir:'left'|'right', size, static, heading, labels}
    var d = (o.size || 20) * (o.dir === 'left' ? -1 : 1), D = o.shift === 'D', at1 = o.static ? 0 : 1, at3 = o.static ? 0 : 3;
    var S = clipLine(0, 1, 8, 100), Dl = clipLine(100, -1, 8, 100);
    var S2 = clipLine(-d, 1, 8, 100), D2 = clipLine(100 + d, -1, 8, 100);
    var e2 = D ? [50 + d / 2, 50 + d / 2] : [50 + d / 2, 50 - d / 2];
    var gap = D ? [50, 50 + d] : [50, 50 + d]; // quantity at P1 on the shifted curve
    var lineS = {q: function (p) { return p; }}, lineD = {q: function (p) { return 100 - p; }},
        lineS2 = {q: function (p) { return p + d; }}, lineD2 = {q: function (p) { return 100 + d - p; }};
    var ap = D ? presetArrowP([lineD, lineD2, lineS], [0, 1], 88, [[50, 50]])
               : presetArrowP([lineS, lineS2, lineD], [0, 1], 88, [[50, 50]]);
    var curves = D ? [{id: 'S', label: 'S', pts: S}, {id: 'D1', label: 'D₁', pts: Dl, thin: true}, {id: 'D2', label: 'D₂', pts: D2, color: 'red', from: 'D1', at: at1, arrowP: ap}]
                   : [{id: 'D', label: 'D', pts: Dl}, {id: 'S1', label: 'S₁', pts: S, thin: true}, {id: 'S2', label: 'S₂', pts: S2, color: 'red', from: 'S1', at: at1, arrowP: ap}];
    var isShort = (D && d > 0) || (!D && d < 0);
    var pn = {heading: o.heading, axes: {xmax: 110, ymax: 110}, curves: curves,
      points: [{q: 50, p: 50, pl: 'P₁', ql: 'Q₁'}, {q: e2[0], p: e2[1], pl: 'P₂', ql: 'Q₂', color: 'red', at: at3}]};
    if (!o.static) { pn.points.push({q: 50 + d, p: 50, color: 'red', at: 2, until: 3, showP: false, showQ: false});
      // below:true, as the hand-written symbolic template always has it: above
      // the axis the label lands on whichever curve crosses that price.
      pn.braces = [{p: 50, q1: 50, q2: 50 + d, label: isShort ? 'Shortage' : 'Surplus', below: true, at: 2, until: 3}]; }
    return pn;
  }
  function shiftSteps(o) {
    var D = o.shift === 'D', right = o.dir !== 'left', good = o.good ? ' for ' + o.good : '';
    var isShort = (D && right) || (!D && !right), pUp = isShort, qUp = right;
    var why = o.why || (D ? (right ? 'Buyers want more at every price' : 'Buyers want less at every price') : (right ? 'Selling is more profitable at every price' : 'Selling is less profitable at every price'));
    var ev = o.event ? o.event + ' ' : '';
    return [
      'The market' + good + ' is in equilibrium at P₁ and Q₁.',
      ev + why + ', so ' + (D ? 'demand' : 'supply') + ' shifts ' + (right ? 'right' : 'left') + ', from ' + (D ? 'D₁ to D₂' : 'S₁ to S₂') + '.',
      'At the old price P₁ there is now a ' + (isShort ? 'shortage: buyers want more than sellers offer, so the price rises.' : 'surplus: sellers offer more than buyers want, so the price falls.'),
      'The market settles at P₂ and Q₂. Price ' + (pUp ? 'up' : 'down') + ', quantity ' + (qUp ? 'up' : 'down') + '.'];
  }
  function doublePanel(o) { // o: {demand:'left'|'right', supply:'left'|'right', dD, dS, heading, static}
    var dD = (o.dD || 20) * (o.demand === 'left' ? -1 : 1), dS = (o.dS || 20) * (o.supply === 'left' ? -1 : 1);
    var q2 = (100 + dD + dS) / 2, p2 = q2 - dS, a1 = o.static ? 0 : 1, a2 = o.static ? 0 : 2, a3 = o.static ? 0 : 3;
    var L = [{q: function (p) { return 100 - p; }}, {q: function (p) { return 100 + dD - p; }},
             {q: function (p) { return p; }}, {q: function (p) { return p + dS; }}],
        marks = [[50, 50], [q2, p2]];
    return {heading: o.heading, axes: {xmax: 110, ymax: 110},
      curves: [{id: 'D1', label: 'D₁', pts: clipLine(100, -1, 8, 100), thin: true}, {id: 'S1', label: 'S₁', pts: clipLine(0, 1, 8, 100), thin: true},
               // A shift arrow only clears the pair it belongs to; the other
               // pair can lie across it. presetArrowP finds a height where it
               // does not (v2.56). arrowD/arrowS still override it.
               {id: 'D2', label: 'D₂', pts: clipLine(100 + dD, -1, 8, 100), color: 'red', from: 'D1', at: a1, arrowP: o.arrowD != null ? o.arrowD : presetArrowP(L, [0, 1], 32, marks)},
               {id: 'S2', label: 'S₂', pts: clipLine(-dS, 1, 8, 100), color: 'red', from: 'S1', at: a2, arrowP: o.arrowS != null ? o.arrowS : presetArrowP(L, [2, 3], 88, marks)}],
      points: [{q: 50, p: 50, pl: 'P₁', ql: 'Q₁', marker: '1'}, {q: q2, p: p2, pl: 'P₂', ql: 'Q₂', color: 'red', marker: '2', at: a3}]};
  }
  function doubleSteps(o, q2, p2) {
    var dr = o.demand !== 'left', sr = o.supply !== 'left';
    return ['Equilibrium at P₁ and Q₁ (Point 1).',
      'Demand shifts ' + (dr ? 'right' : 'left') + ', from D₁ to D₂.',
      'Supply shifts ' + (sr ? 'right' : 'left') + ', from S₁ to S₂.',
      'The new equilibrium is Point 2: price ' + (p2 > 50 ? 'up' : p2 < 50 ? 'down' : 'unchanged') + ', quantity ' + (q2 > 50 ? 'up' : q2 < 50 ? 'down' : 'unchanged') + '. ' + (o.note || '')];
  }
  function expand(cfg) {
    if (!cfg.preset) return cfg;
    var out = merge(cfg, {}); delete out.preset;
    if (cfg.preset === 'shift') {
      var pn = shiftPanel(cfg); for (var k in pn) out[k] = pn[k];
      if (!cfg.static && !cfg.steps) out.steps = shiftSteps(cfg);
    } else if (cfg.preset === 'double') {
      if (cfg.compare) { // two panels: bigger supply shift vs bigger demand shift
        var big = cfg.big || 40, small = cfg.small || 15;
        out.link = false; out.panels = [doublePanel(merge(cfg, {dD: small, dS: big, heading: cfg.headings ? cfg.headings[0] : 'Larger shift of supply'})),
                      doublePanel(merge(cfg, {dD: big, dS: small, heading: cfg.headings ? cfg.headings[1] : 'Larger shift of demand'}))];
        if (!cfg.static && !cfg.steps) { var s = doubleSteps(cfg, 50, 50); s[3] = 'Each panel ends at a new Point 2. ' + (cfg.note || 'Compare them: one of price or quantity moves the same way in both; the other depends on which shift is larger.'); out.steps = s; }
      } else {
        var one = doublePanel(cfg); for (var k2 in one) out[k2] = one[k2];
        var e = one.points[1]; if (!cfg.static && !cfg.steps) out.steps = doubleSteps(cfg, e.q, e.p);
      }
    }
    return out;
  }

  function mount(root) {
    var script = root.querySelector('script[type="application/json"]'); if (!script) return;
    var base; try { base = JSON.parse(script.textContent); } catch (e) { root.textContent = 'Widget config error: ' + e.message; return; }
    function draw(key) {
      var cfg = base;
      if (base.scenarios) { key = key || base.activeScenario || Object.keys(base.scenarios)[0]; cfg = merge(base, base.scenarios[key]); cfg.activeScenario = key; }
      new Widget(root, expand(cfg));
    }
    root.addEventListener('sdg-scenario', function (e) { draw(e.detail); });
    draw();
  }
  function init() { document.querySelectorAll('.sdg').forEach(mount); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
