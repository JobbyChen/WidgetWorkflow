/* ===== sd-graph.js v2.5 — data-driven supply & demand widgets =====
   Markup:  <div class="sdg"><script type="application/json">{ ...config... }<\/script></div>
   Top-level config:
     title, lede, caption         heading / intro / static caption (caption used only when there are no steps)
     steps: [caption, ...]        index 0 = start state; elements use `at`/`until` (step indices) to appear/vanish
     scenarios: {key:{label, ...overrides}}   one button per scenario; overrides merge over the base config
     panels: [panelCfg, panelCfg]  two side-by-side graphs (two-market). Otherwise the panel keys live at top level.
   Panel config:
     heading                      title above the panel (two-market only)
     axes: {x, y, xmax, ymax, xticks[], yticks[], money, cents, k, grid, bg:false}
        x, y = axis titles, default 'Q' and 'P'. A word or two fits; they are never wrapped.
     curves[]: {id, label, pts:[[q,p],...], color, at, until, from, arrowP, shiftArrow, curved, thin, dashed, lstart, ldx, ldy}
        lstart = put the curve label at the first point instead of the last; ldx/ldy nudge it
        label:"" draws no label at all (a lone PPF needs none); omitting label falls back to the id
        from   = id of the curve this one shifts away from (animated shift + arrow); arrowP = price height of arrow
        shiftArrow:false = animate and dim as usual but draw no shift arrow. Use it whenever the
                 widget already shows per-row arrows (table.arrows), which say the same thing once per row.
        curved = smooth through 3+ points (conceptual, non-linear look)
     points[]: {id, q, p, label, marker, pl, ql, color, at, until, dx, dy, guides:false, showP:false, showQ:false}
        marker = "1"/"2" numbered circle;  pl/ql = symbolic axis labels ("P₁","Q₁") instead of numbers
     moves[]:  {from:[q,p], to:[q,p], at, until, color, offset}  arrow between two points, drawn `offset` px beside the curve (default 14; negative = other side)
     hlines[]: {p, label, color, at, until}                       horizontal price line across the plot
     braces[]: {p, q1, q2, label, at, until, below, color}        curly brace spanning a gap at price p
     vbraces[]:{p1, p2, q, label, at, until, left, side, color}   the same brace turned upright, spanning a
        price gap. left:true is the mirror of a brace's below:true: it sits outside the P axis, clear of the
        plot and the tick numbers, with its label running up the axis, and widens the left margin to fit.
        Without left it sits inside the plot at quantity q, opening right unless side:'left'.
     table:    {cols[], series[], rows[[price,q,...]], arrows}    schedule beside the graph; arrows draws row shift arrows
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
  function h(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function fmtP(v, ax) { if (!ax.money) return String(v); if (ax.cents) return '$' + Number(v).toFixed(2); return '$' + (Number.isInteger(v) ? v : v.toFixed(2)); }
  function fmtQ(v, ax) { if (ax.k && v >= 1000) return (v / 1000) + 'k'; return v.toLocaleString('en-US'); }
  function merge(a, b) { var o = {}; for (var k in a) o[k] = a[k]; for (var k2 in b) o[k2] = b[k2]; return o; }

  // ---------- one SVG panel ----------
  function buildPanel(cfg) {
    var ax = cfg.axes, W = 372, below = (cfg.braces || []).some(function (b) { return b.below; }), H = below ? 268 : 250;
    // A brace outside the P axis needs margin to sit in, the way a brace below
    // the Q axis needs the extra panel height above.
    var vleft = (cfg.vbraces || []).some(function (b) { return b.left; });
    var left = (ax.cents ? 62 : (ax.yticks && ax.yticks.length ? 54 : 40)) + (vleft ? 44 : 0);
    var O = {x: left, y: 205}, PW = W - left - 36, PH = 178;
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
    g.appendChild(el('text', {class: 'axlbl', x: W - 2, y: O.y + 16, 'text-anchor': 'end'}, ax.x || 'Q'));
    g.appendChild(el('text', {class: 'axlbl', x: O.x - 2, y: 11}, ax.y || 'P'));

    function arrow(x1, y1, x2, y2, c, cls) {
      var dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy), ux = dx / len, uy = dy / len, hh = 7, ww = 3.6, bx = x2 - ux * hh, by = y2 - uy * hh;
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
    function qAt(pts, p) {
      for (var i = 0; i < pts.length - 1; i++) { var a = pts[i], b = pts[i + 1]; if ((p - a[1]) * (p - b[1]) <= 0 && a[1] !== b[1]) return a[0] + (p - a[1]) * (b[0] - a[0]) / (b[1] - a[1]); }
      var a2 = pts[0], b2 = pts[pts.length - 1]; return a2[0] + (p - a2[1]) * (b2[0] - a2[0]) / (b2[1] - a2[1]);
    }

    (cfg.curves || []).forEach(function (c) {
      var cc = col(c.color), grp = el('g', {class: 'curve-g'});
      var path = el('path', {class: 'curve' + (c.thin ? ' thin' : ''), d: pathD(c.pts, c.curved), stroke: cc});
      if (c.dashed) path.setAttribute('stroke-dasharray', '6 4');
      grp.appendChild(path);
      var last = c.pts[c.pts.length - 1], up = last[1] > c.pts[0][1], lp = c.lstart ? c.pts[0] : last;
      // label:"" draws nothing. A lone frontier needs no name -- the axis titles
      // already say what it is -- but the id is still needed by table.series, and
      // falling back to it parked "PPF" on the curve. Omitting label still uses the id.
      grp.appendChild(el('text', {class: 'clbl', x: X(lp[0]) + (c.ldx || 6), y: Y(lp[1]) + (c.ldy || (up ? 2 : 6)), fill: cc}, c.label != null ? c.label : (c.id || '')));
      if (c.from && byId[c.from]) {
        var src = byId[c.from].spec, ap = c.arrowP != null ? c.arrowP : (c.pts[0][1] + last[1]) / 2;
        var q0 = qAt(src.pts, ap), q1 = qAt(c.pts, ap), s = Math.sign(q1 - q0);
        grp.dataset.dx = X(q1) - X(q0); grp.dataset.dy = 0; grp.classList.add('move');
        // shiftArrow:false keeps the slide and the dimming but drops the arrow, for
        // widgets whose per-row arrows already show the shift once per schedule row.
        if (c.shiftArrow !== false) g.appendChild(reg(arrow(X(q0) + s * 8, Y(ap), X(q1) - s * 8, Y(ap), cc, 'shift'), {at: c.at || 0, until: c.until}));
      }
      g.appendChild(grp); reg(grp, c);
    });

    (cfg.hlines || []).forEach(function (l) {
      var cc = col(l.color || 'red'), grp = el('g', {});
      grp.appendChild(el('line', {class: 'hline', stroke: cc, x1: O.x, y1: Y(l.p), x2: O.x + PW + 8, y2: Y(l.p)}));
      if ((ax.yticks || []).indexOf(l.p) < 0) grp.appendChild(el('text', {class: 'tk strong', x: O.x - 6, y: Y(l.p) + 4, 'text-anchor': 'end', fill: cc}, l.label || fmtP(l.p, ax)));
      g.appendChild(grp); reg(grp, l);
    });

    (cfg.braces || []).forEach(function (b) {
      var cc = col(b.color || 'red'), grp = el('g', {});
      var x1 = X(Math.min(b.q1, b.q2)), x2 = X(Math.max(b.q1, b.q2)), y = b.below ? O.y + 22 : Y(b.p) - 8, dir = b.below ? 1 : -1, hh = 7, m = (x1 + x2) / 2;
      var d = 'M' + x1 + ' ' + y + ' Q' + x1 + ' ' + (y + dir * hh) + ' ' + (x1 + hh) + ' ' + (y + dir * hh) + ' L' + (m - hh) + ' ' + (y + dir * hh) + ' Q' + m + ' ' + (y + dir * hh) + ' ' + m + ' ' + (y + dir * 2 * hh) +
              ' Q' + m + ' ' + (y + dir * hh) + ' ' + (m + hh) + ' ' + (y + dir * hh) + ' L' + (x2 - hh) + ' ' + (y + dir * hh) + ' Q' + x2 + ' ' + (y + dir * hh) + ' ' + x2 + ' ' + y;
      grp.appendChild(el('path', {class: 'brace', stroke: cc, d: d}));
      grp.appendChild(el('text', {class: 'tag', x: m, y: y + dir * 2 * hh + (b.below ? 12 : -4), 'text-anchor': 'middle', fill: cc}, b.label));
      if (!b.below) { [b.q1, b.q2].forEach(function (q) { grp.appendChild(el('line', {class: 'guide', stroke: cc, x1: X(q), y1: Y(b.p), x2: X(q), y2: O.y})); }); }
      g.appendChild(grp); reg(grp, b);
    });

    // The brace turned upright, spanning a price gap. left:true mirrors the
    // horizontal brace's below:true -- outside the P axis, clear of the plot and
    // the tick numbers, label running up the axis because horizontal text does
    // not fit in the margin.
    (cfg.vbraces || []).forEach(function (b) {
      var cc = col(b.color || 'red'), grp = el('g', {});
      var y1 = Y(Math.max(b.p1, b.p2)), y2 = Y(Math.min(b.p1, b.p2));
      var x = b.left ? O.x - 32 : X(b.q);
      var dir = (b.left || b.side === 'left') ? -1 : 1, hh = 7, m = (y1 + y2) / 2;
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
        grp.appendChild(el('text', {class: 'tag', x: x + dir * (2 * hh + 6), y: m + 4,
          'text-anchor': dir > 0 ? 'start' : 'end', fill: cc}, b.label));
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
      if (p.guides !== false) grp.appendChild(el('path', {class: 'guide', stroke: cc, d: 'M' + O.x + ' ' + Y(p.p) + ' L' + X(p.q) + ' ' + Y(p.p) + ' L' + X(p.q) + ' ' + O.y}));
      grp.appendChild(el('circle', {class: 'pt' + (p.marker ? ' mk' : ''), cx: X(p.q), cy: Y(p.p), r: p.marker ? 6 : 4.2, stroke: cc}));
      if (p.marker) grp.appendChild(el('text', {class: 'mktxt', x: X(p.q), y: Y(p.p) + 2.6, 'text-anchor': 'middle'}, p.marker));
      if (p.label) grp.appendChild(el('text', {class: 'tag', x: X(p.q) + (p.dx != null ? p.dx : 9), y: Y(p.p) + (p.dy != null ? p.dy : -9), fill: cc}, p.label));
      var pl = p.pl || ((p.showP !== false && (ax.yticks || []).indexOf(p.p) < 0 && !(cfg.hlines || []).some(function (l) { return l.p === p.p; })) ? fmtP(p.p, ax) : null);
      var ql = p.ql || ((p.showQ !== false && (ax.xticks || []).indexOf(p.q) < 0) ? fmtQ(p.q, ax) : null);
      if (pl) grp.appendChild(el('text', {class: 'tk strong', x: O.x - 6, y: Y(p.p) + 4, 'text-anchor': 'end', fill: cc}, pl));
      if (ql) grp.appendChild(el('text', {class: 'tk strong', x: X(p.q), y: O.y + 15, 'text-anchor': 'middle', fill: cc}, ql));
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
    host.appendChild(body);
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
    this.panels.forEach(function (pn) {
      pn.parts.forEach(function (pt) {
        var at = pt.spec.at || 0, until = pt.spec.until, on = s >= at && (until == null || s < until);
        pt.node.classList.toggle('off', !on);
        if (pt.node.dataset.dx != null) pt.node.style.transform = on ? 'translate(0,0)' : 'translate(' + (-pt.node.dataset.dx) + 'px,0)';
      });
      (pn.cfg.curves || []).forEach(function (c) { if (c.from && pn.byId[c.from]) pn.byId[c.from].node.classList.toggle('dim', s >= (c.at || 0)); });
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
      pn.braces = [{p: 50, q1: 50, q2: 50 + d, label: isShort ? 'Shortage' : 'Surplus', at: 2, until: 3}]; }
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
               {id: 'D2', label: 'D₂', pts: clipLine(100 + dD, -1, 8, 100), color: 'red', from: 'D1', at: a1, arrowP: 32},
               {id: 'S2', label: 'S₂', pts: clipLine(-dS, 1, 8, 100), color: 'red', from: 'S1', at: a2, arrowP: 88}],
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
