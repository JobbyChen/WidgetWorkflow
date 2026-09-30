/* ===== sd-graph.js v2.40 — data-driven supply & demand widgets =====
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
     areas[]:  {pts:[[q,p],...], label, color, edge, lp, ldx, ldy, at, until}   a shaded polygon under the curves (CS, PS, deadweight loss)
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
     hlines[]: {p, label, tag, tagdy, tagq, control, color, at, until}              horizontal price line across the plot
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

  function h(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  // pct is money's opposite number (v2.35): the income-distribution chapter
  // plots a cumulative percent against a cumulative percent, and every value
  // on both axes carries a % in the source.
  function fmtP(v, ax) { if (ax.pct) return v + '%'; if (!ax.money) return String(v); if (ax.cents) return '$' + Number(v).toFixed(2); return '$' + (Number.isInteger(v) ? v : v.toFixed(2)); }
  function fmtQ(v, ax) { if (ax.pct) return v + '%'; if (ax.k && v >= 1000) return (v / 1000) + 'k'; return v.toLocaleString('en-US'); }
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
      var plain = t.replace(/_\{([^}]*)\}/g, function (m, inner) { subs += inner.length; return ''; });
      return 6.1 * (plain.length + 0.72 * subs);
    }
    var widest = 0;
    (ax.yticks || []).forEach(function (v) { widest = Math.max(widest, axw(fmtP(v, ax))); });
    (cfg.points || []).forEach(function (pt) {
      if (pt.showP === false) return;
      widest = Math.max(widest, axw(pt.pl != null ? pt.pl : fmtP(pt.p, ax)));
    });
    // A one-line price-axis title is a letter or two and sits just inside the
    // axis, where it has always sat. A wrapped one is a name -- "Wage /
    // Rate (W)" -- and the labor chapter puts that name clear to the left of
    // the axis, not pressed against it (v2.34). So it is anchored the other
    // way, and the margin carries it the same as a price label.
    var ytitle = String(ax.y || 'P').split('\n');
    var ytw = 0;
    if (ytitle.length > 1) {
      ytitle.forEach(function (rw) { ytw = Math.max(ytw, 9.8 * rw.length); });
    }
    var left = Math.max(ax.cents ? 62 : (ax.yticks && ax.yticks.length ? 54 : 40),
                        Math.ceil(widest) + 12,
                        Math.ceil(ytw) + 22) + (vleft ? 44 : 0);
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
        var plain = rw.replace(/_\{([^}]*)\}/g, function (m, inner) { subs += inner.length; return ''; });
        n = Math.max(n, plain.length + 0.72 * subs);
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
        var endsAt = left + (lp[0] / ax.xmax) * pw + (c.ldx == null ? 6 : c.ldx);
        var overflow = endsAt + 9.1 * labelChars(c) + 4 - W;
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
    // Drawn here, after the axes and before the curves, so a fill never hides a
    // line, a point or a label.
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
        // The centroid keeps a label inside its own shape, which is right for
        // the triangles this draws. A thin wedge has no room for one, so `lp`
        // places it by hand instead -- outside the shape if that is what fits.
        var n = a.pts.length,
            lp = a.lp || [a.pts.reduce(function (t, p) { return t + p[0]; }, 0) / n,
                          a.pts.reduce(function (t, p) { return t + p[1]; }, 0) / n];
        grp.appendChild(el('text', {class: 'arlbl', x: X(lp[0]) + (a.ldx || 0),
          y: Y(lp[1]) + (a.ldy || 0), 'text-anchor': 'middle', fill: cc}, a.label));
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
        // The 11px inset is measured off the drawn curves, so the arrow clears
        // both of them however far the spline bows.
        if (c.shiftArrow !== false) g.appendChild(reg(arrow(x0 + s * 11, yA, x1 - s * 11, yA, cc, 'shift'), {at: c.at || 0, until: c.until}));
      }
      g.appendChild(grp); reg(grp, c);
    });

    (cfg.hlines || []).forEach(function (l) {
      var cc = col(l.color || 'red'), grp = el('g', {});
      grp.appendChild(el('line', {class: 'hline', stroke: cc, x1: O.x, y1: Y(l.p), x2: O.x + PW + 8, y2: Y(l.p)}));
      if ((ax.yticks || []).indexOf(l.p) < 0) grp.appendChild(el('text', {class: 'tk strong', x: O.x - 6, y: Y(l.p) + 4, 'text-anchor': 'end', fill: cc}, l.label || fmtP(l.p, ax)));
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
      // Outside the widest price-axis label, not a fixed 32px in from the
      // axis (v2.33): the labor chapter's CWD brace spans two wages named
      // W_{Alaska} and W_{Hawaii}, and the brace was drawn straight through
      // both. The 44px this brace already adds to the left margin is what
      // there is room in.
      var x = b.left ? Math.min(O.x - 32, O.x - 24 - widest) : X(b.q);
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
      main.appendChild(cbox);
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
  function shiftPanel(o) { // o: {shift:'D'|'S', dir:'left'|'right', size, static, heading, labels}
    var d = (o.size || 20) * (o.dir === 'left' ? -1 : 1), D = o.shift === 'D', at1 = o.static ? 0 : 1, at3 = o.static ? 0 : 3;
    var S = clipLine(0, 1, 8, 100), Dl = clipLine(100, -1, 8, 100);
    var S2 = clipLine(-d, 1, 8, 100), D2 = clipLine(100 + d, -1, 8, 100);
    var e2 = D ? [50 + d / 2, 50 + d / 2] : [50 + d / 2, 50 - d / 2];
    var gap = D ? [50, 50 + d] : [50, 50 + d]; // quantity at P1 on the shifted curve
    var curves = D ? [{id: 'S', label: 'S', pts: S}, {id: 'D1', label: 'D₁', pts: Dl, thin: true}, {id: 'D2', label: 'D₂', pts: D2, color: 'red', from: 'D1', at: at1, arrowP: 88}]
                   : [{id: 'D', label: 'D', pts: Dl}, {id: 'S1', label: 'S₁', pts: S, thin: true}, {id: 'S2', label: 'S₂', pts: S2, color: 'red', from: 'S1', at: at1, arrowP: 88}];
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
    return {heading: o.heading, axes: {xmax: 110, ymax: 110},
      curves: [{id: 'D1', label: 'D₁', pts: clipLine(100, -1, 8, 100), thin: true}, {id: 'S1', label: 'S₁', pts: clipLine(0, 1, 8, 100), thin: true},
               // A shift arrow only clears the pair it belongs to. The other
               // pair can still lie across it, so arrowD/arrowS let a config
               // move it: at price p the demand arrow spans q = 100+dD-p to
               // 100-p, and S1 sits at q = p, which is inside that span
               // whenever (100+dD)/2 < p < 100 - dD/2 for a leftward shift.
               {id: 'D2', label: 'D₂', pts: clipLine(100 + dD, -1, 8, 100), color: 'red', from: 'D1', at: a1, arrowP: o.arrowD != null ? o.arrowD : 32},
               {id: 'S2', label: 'S₂', pts: clipLine(-dS, 1, 8, 100), color: 'red', from: 'S1', at: a2, arrowP: o.arrowS != null ? o.arrowS : 88}],
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
