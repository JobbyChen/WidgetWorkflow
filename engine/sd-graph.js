/* sd-graph.js — Smokin' Notes supply-and-demand widget engine, v2 (2026-09-16)
   Renders every <div class="sdg"> on the page from a JSON config.
   Schema, presets and geometry: docs/engine-reference.md
   One copy only. Published notes files embed this file verbatim (minus this
   header comment); scripts/check_file.py verifies byte identity. */

(function (global) {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";
  var VERSION = "v2";

  /* ---------- small helpers ------------------------------------------- */

  function isObj(v) {
    return v !== null && typeof v === "object" && !Array.isArray(v);
  }

  function merge(base, over) {
    if (!isObj(base) || !isObj(over)) return clone(over === undefined ? base : over);
    var out = clone(base);
    Object.keys(over).forEach(function (k) {
      out[k] = isObj(base[k]) && isObj(over[k]) ? merge(base[k], over[k]) : clone(over[k]);
    });
    return out;
  }

  function clone(v) {
    if (Array.isArray(v)) return v.map(clone);
    if (isObj(v)) {
      var o = {};
      Object.keys(v).forEach(function (k) { o[k] = clone(v[k]); });
      return o;
    }
    return v;
  }

  function el(tag, attrs, parent) {
    var node = document.createElementNS(NS, tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (attrs[k] !== null && attrs[k] !== undefined) node.setAttribute(k, attrs[k]);
    });
    if (parent) parent.appendChild(node);
    return node;
  }

  function html(tag, cls, parent) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (parent) parent.appendChild(node);
    return node;
  }

  function num(v, fallback) {
    return typeof v === "number" && isFinite(v) ? v : fallback;
  }

  function arr(v) {
    return Array.isArray(v) ? v : [];
  }

  /* Visibility: an item is drawn on step `s` when s >= at and (until is unset
     or s <= until). Both are 0-based step indexes. */
  function visible(item, step) {
    var at = num(item && item.at, 0);
    var until = item && item.until;
    if (step < at) return false;
    if (typeof until === "number" && step > until) return false;
    return true;
  }

  function isShift(color) {
    return color === "red" || color === "shift";
  }

  /* ---------- presets --------------------------------------------------- */
  /* A preset expands into a full config before rendering. Presets exist so a
     routine one-curve shift is a three-line config. Anything a preset cannot
     express is written out longhand instead. */

  var PRESETS = {};

  /* At a crossing the curves occupy the diagonals -- supply runs north-east to
     south-west, demand north-west to south-east -- so the free wedges are due
     north, south, east and west. Equilibrium labels use north and south, nudged
     sideways to clear the dashed guide that drops from the point. */
  var NORTH = { dx: 7, dy: -13, anchor: "start" };
  var SOUTH = { dx: -7, dy: 21, anchor: "end" };


  PRESETS.shift = function (cfg) {
    var curve = cfg.curve === "supply" ? "supply" : "demand";
    var dir = cfg.direction === "left" ? "left" : "right";
    var d = dir === "right" ? 1 : -1;
    var mag = num(cfg.magnitude, 18);
    var isD = curve === "demand";
    var tag = isD ? "D" : "S";
    var other = isD ? "S" : "D";
    var base = isD ? { from: [8, 96], to: [96, 8] } : { from: [8, 12], to: [96, 96] };
    var otherLine = isD ? { from: [8, 12], to: [96, 96] } : { from: [8, 96], to: [96, 8] };

    /* Equilibria are not written down here: "on" resolves each one to the real
       crossing of the two curves at render time. */
    var e1 = [tag + "\u2081", other];
    var e2 = [tag + "\u2082", other];

    /* Due north and due south-west of an equilibrium are the two wedges that no
       curve passes through, so that is where the E labels go. Which of the two
       equilibria is the higher one depends on the curve and the direction. */
    var e2North = isD === (dir === "right");

    return {
      title: cfg.title,
      mode: "symbolic",
      axes: {
        x: {
          label: "Q", min: 0, max: 110,
          ticks: [
            { on: e1, text: "Q\u2081" },
            { on: e2, text: "Q\u2082", color: "red", at: 2 }
          ]
        },
        y: {
          label: "P", min: 0, max: 110,
          ticks: [
            { on: e1, text: "P\u2081" },
            { on: e2, text: "P\u2082", color: "red", at: 2 }
          ]
        }
      },
      curves: [
        { id: other, kind: isD ? "supply" : "demand", from: otherLine.from, to: otherLine.to,
          label: { text: other, pos: "end", dx: 8, dy: isD ? -2 : 6 } },
        { id: tag + "\u2081", kind: curve, from: base.from, to: base.to,
          label: { text: tag + "\u2081", pos: "end", dx: 8, dy: isD ? 6 : -2 } },
        { id: tag + "\u2082", kind: curve, color: "red", at: 1,
          from: [base.from[0] + d * mag, base.from[1]],
          to: [base.to[0] + d * mag, base.to[1]],
          label: { text: tag + "\u2082", pos: "end", dx: 8, dy: isD ? 6 : -2 } }
      ],
      points: [
        { on: e1, label: merge({ text: "E\u2081" }, e2North ? SOUTH : NORTH) },
        { on: e2, color: "red", at: 2,
          label: merge({ text: "E\u2082" }, e2North ? NORTH : SOUTH) }
      ],
      guides: [
        { on: e1, axis: "h" }, { on: e1, axis: "v" },
        { on: e2, axis: "h", color: "red", at: 2 },
        { on: e2, axis: "v", color: "red", at: 2 }
      ],
      arrows: [
        { from: [base.from[0] + d * 8, 78], to: [base.from[0] + d * (8 + mag), 78], at: 1 }
      ],
      /* No brace: the one this preset used to emit lacked below:true and
         collided with the other curve. See docs/open-issues.md. */
      steps: cfg.steps || [
        { caption: "The market starts in equilibrium." },
        { caption: "The curve shifts." },
        { caption: "A new equilibrium is reached." }
      ]
    };
  };

  PRESETS.double = function (cfg) {
    /* Two panels side by side: the same shock drawn for two magnitudes, or two
       related markets. Panels are supplied by the author; the preset only sets
       symbolic axes and the shared step list. */
    var panels = arr(cfg.panels).map(function (p) {
      return merge({ mode: "symbolic", axes: symbolicAxes() }, p);
    });
    return { title: cfg.title, panels: panels, steps: cfg.steps || [] };
  };

  function symbolicAxes() {
    return {
      x: { label: "Q", min: 0, max: 110, ticks: [] },
      y: { label: "P", min: 0, max: 110, ticks: [] }
    };
  }

  /* ---------- geometry -------------------------------------------------- */

  var PLOT = { w: 460, h: 340, left: 52, right: 34, top: 22, bottom: 44 };

  function scaler(axes) {
    var xa = (axes && axes.x) || {}, ya = (axes && axes.y) || {};
    var x0 = num(xa.min, 0), x1 = num(xa.max, 110);
    var y0 = num(ya.min, 0), y1 = num(ya.max, 110);
    var px0 = PLOT.left, px1 = PLOT.w - PLOT.right;
    var py0 = PLOT.h - PLOT.bottom, py1 = PLOT.top;
    return {
      x: function (v) { return px0 + (v - x0) / (x1 - x0) * (px1 - px0); },
      y: function (v) { return py0 + (v - y0) / (y1 - y0) * (py1 - py0); },
      ix: function (p) { return x0 + (p - px0) / (px1 - px0) * (x1 - x0); },
      iy: function (p) { return y0 + (p - py0) / (py1 - py0) * (y1 - y0); },
      xMin: x0, xMax: x1, yMin: y0, yMax: y1,
      ox: px0, oy: py0, rx: px1, ty: py1
    };
  }

  /* A curve is a quadratic through from→to, bowed perpendicular to the chord
     by `bow` (a fraction of the chord length). bow 0 gives the straight line
     used on numeric graphs.

     The bow always displaces the middle of the curve DOWNWARD in price. On a
     demand curve that is the convex-to-the-origin shape of the printed artwork;
     on a supply curve it is the usual rises-ever-faster shape. Picking the side
     geometrically (nearest the origin, say) is not stable -- two supply curves a
     few units apart can land on opposite sides of the test and bow opposite
     ways -- so the side is fixed, and a negative `bow` flips it. */
  function controlPoint(s, c) {
    var a = { x: s.x(c.from[0]), y: s.y(c.from[1]) };
    var b = { x: s.x(c.to[0]), y: s.y(c.to[1]) };
    var bow = num(c.bow, c.shape === "line" ? 0 : 0.12);
    var mid = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 };
    if (!bow) return { a: a, b: b, c: mid, straight: true };

    var dx = b.x - a.x, dy = b.y - a.y;
    var len = Math.sqrt(dx * dx + dy * dy) || 1;
    var nx = -dy / len, ny = dx / len;
    /* +y is down the screen, which is down in price. */
    if (ny < 0 || (ny === 0 && nx < 0)) { nx = -nx; ny = -ny; }
    return {
      a: a, b: b, straight: false,
      c: { x: mid.x + nx * bow * len, y: mid.y + ny * bow * len }
    };
  }

  function curvePath(s, c) {
    var q = controlPoint(s, c);
    if (q.straight) return "M" + q.a.x + " " + q.a.y + " L" + q.b.x + " " + q.b.y;
    return "M" + q.a.x + " " + q.a.y + " Q" + q.c.x + " " + q.c.y + " " + q.b.x + " " + q.b.y;
  }

  function pointOnCurve(s, c, t) {
    var q = controlPoint(s, c);
    var u = 1 - t;
    return {
      x: u * u * q.a.x + 2 * u * t * q.c.x + t * t * q.b.x,
      y: u * u * q.a.y + 2 * u * t * q.c.y + t * t * q.b.y
    };
  }

  /* Where two curves cross, in data coordinates. Both are sampled as polylines
     in pixel space -- the space they are drawn in, so a bowed curve's crossing
     is the crossing you see -- and the first segment pair that meets is solved
     exactly. Returns null if they never cross.

     This exists so no author has to eyeball an equilibrium: write
     "on": ["D1", "S"] on a point, a guide or an axis tick and the engine puts it
     on the crossing. Hand-guessed equilibria were the main source of dots that
     sit beside the intersection instead of on it. */
  function intersect(s, c1, c2) {
    var N = 240, i, j, a = [], b = [];
    for (i = 0; i <= N; i++) {
      a.push(pointOnCurve(s, c1, i / N));
      b.push(pointOnCurve(s, c2, i / N));
    }
    for (i = 0; i < N; i++) {
      for (j = 0; j < N; j++) {
        var hit = segHit(a[i], a[i + 1], b[j], b[j + 1]);
        if (hit) return { x: s.ix(hit.x), y: s.iy(hit.y) };
      }
    }
    return null;
  }

  function segHit(p1, p2, p3, p4) {
    var d = (p2.x - p1.x) * (p4.y - p3.y) - (p2.y - p1.y) * (p4.x - p3.x);
    if (!d) return null;
    var t = ((p3.x - p1.x) * (p4.y - p3.y) - (p3.y - p1.y) * (p4.x - p3.x)) / d;
    var u = ((p3.x - p1.x) * (p2.y - p1.y) - (p3.y - p1.y) * (p2.x - p1.x)) / d;
    if (t < 0 || t > 1 || u < 0 || u > 1) return null;
    return { x: p1.x + t * (p2.x - p1.x), y: p1.y + t * (p2.y - p1.y) };
  }

  /* The point on one curve at a given price or quantity, in data coordinates.
     Samples the curve and interpolates across the step that straddles the
     target, so it lands on the drawn curve rather than on its chord. */
  function along(s, c, axis, value) {
    var N = 240, i, prev = null;
    for (i = 0; i <= N; i++) {
      var px = pointOnCurve(s, c, i / N);
      var cur = { x: s.ix(px.x), y: s.iy(px.y) };
      if (prev) {
        var a = prev[axis], b = cur[axis];
        if ((a - value) * (b - value) <= 0 && a !== b) {
          var t = (value - a) / (b - a);
          return { x: prev.x + t * (cur.x - prev.x), y: prev.y + t * (cur.y - prev.y) };
        }
      }
      prev = cur;
    }
    return null;
  }

  /* Resolves every "on" and "onCurve" reference in a panel into real
     coordinates, once, before anything is drawn.

       "on":      ["D1", "S"]        the crossing of two curves
       "onCurve": {"curve": "D", "y": 70}   the point on one curve at that price
       "onCurve": {"curve": "D", "x": 36}   ... or at that quantity  */
  function resolveOn(panel, s) {
    var byId = {};
    arr(panel.curves).forEach(function (c) { if (c.id) byId[c.id] = c; });

    function resolve(spec) {
      if (!spec) return null;
      if (Array.isArray(spec.on) && spec.on.length === 2) {
        var c1 = byId[spec.on[0]], c2 = byId[spec.on[1]];
        return c1 && c2 ? intersect(s, c1, c2) : null;
      }
      var oc = spec.onCurve;
      if (isObj(oc) && byId[oc.curve]) {
        if (typeof oc.y === "number") return along(s, byId[oc.curve], "y", oc.y);
        if (typeof oc.x === "number") return along(s, byId[oc.curve], "x", oc.x);
      }
      return null;
    }

    arr(panel.points).forEach(function (p) {
      var pt = resolve(p);
      if (pt) { p.x = pt.x; p.y = pt.y; }
    });

    arr(panel.guides).forEach(function (g) {
      var pt = resolve(g);
      if (!pt) return;
      if (g.axis === "v") {
        g.x = pt.x;
        if (g.to === undefined) g.to = pt.y;
      } else {
        g.y = pt.y;
        if (g.to === undefined) g.to = pt.x;
      }
    });

    arr(panel.arrows).concat(arr(panel.moves)).forEach(function (a) {
      ["from", "to"].forEach(function (endKey) {
        var pt = resolve(a[endKey]);
        if (pt) a[endKey] = [pt.x, pt.y];
      });
    });

    [["x", "x"], ["y", "y"]].forEach(function (pair) {
      var axis = panel.axes && panel.axes[pair[0]];
      arr(axis && axis.ticks).forEach(function (t) {
        var pt = resolve(t);
        if (pt) t.value = pt[pair[1]];
      });
    });
  }

  /* ---------- drawing --------------------------------------------------- */

  function defsFor(svg, uid) {
    var defs = el("defs", null, svg);
    ["arrow", "ink"].forEach(function (kind) {
      var m = el("marker", {
        id: uid + "-" + kind, viewBox: "0 0 10 10", refX: 9, refY: 5,
        markerWidth: 6, markerHeight: 6, orient: "auto-start-reverse"
      }, defs);
      el("path", {
        d: "M0 0 L10 5 L0 10 z",
        fill: kind === "arrow" ? "var(--sdg-arrow)" : "var(--sdg-ink)"
      }, m);
    });
  }

  function drawText(parent, x, y, spec, extraClass) {
    var cls = "sdg-text" + (extraClass ? " " + extraClass : "");
    if (spec.bold) cls += " is-bold";
    var t = el("text", {
      x: x + num(spec.dx, 0),
      y: y + num(spec.dy, 0),
      "text-anchor": spec.anchor || "start",
      "dominant-baseline": spec.baseline || "auto",
      class: cls
    }, parent);
    t.textContent = spec.text == null ? "" : String(spec.text);
    return t;
  }

  function drawAxes(g, s, axes, step, uid) {
    var xa = (axes && axes.x) || {}, ya = (axes && axes.y) || {};
    el("path", {
      d: "M" + s.ox + " " + s.ty + " L" + s.ox + " " + s.oy + " L" + s.rx + " " + s.oy,
      class: "sdg-axis"
    }, g);

    drawText(g, s.ox - 10, s.ty - 6, { text: ya.label || "P", anchor: "middle" }, "sdg-axislabel");
    drawText(g, s.rx + 6, s.oy + 4, { text: xa.label || "Q", anchor: "start" }, "sdg-axislabel");

    arr(xa.ticks).forEach(function (t) {
      if (!visible(t, step)) return;
      var px = s.x(t.value);
      el("line", { x1: px, y1: s.oy, x2: px, y2: s.oy + 4, class: "sdg-tick" }, g);
      drawText(g, px, s.oy + 17, { text: t.text, anchor: "middle" },
        "sdg-ticktext" + (isShift(t.color) ? " is-shift" : ""));
    });

    arr(ya.ticks).forEach(function (t) {
      if (!visible(t, step)) return;
      var py = s.y(t.value);
      el("line", { x1: s.ox - 4, y1: py, x2: s.ox, y2: py, class: "sdg-tick" }, g);
      drawText(g, s.ox - 8, py + 4, { text: t.text, anchor: "end" },
        "sdg-ticktext" + (isShift(t.color) ? " is-shift" : ""));
    });
  }

  function drawCurves(g, s, curves, step) {
    curves.forEach(function (c) {
      if (!visible(c, step)) return;
      var shift = isShift(c.color);
      var cls = "sdg-curve" + (shift ? " is-shift" : "") + (c.dash ? " is-dashed" : "");
      el("path", { d: curvePath(s, c), class: cls }, g);

      if (c.label && c.label.text) {
        var t = c.label.pos === "start" ? 0
          : (typeof c.label.pos === "number" ? c.label.pos : 1);
        var p = pointOnCurve(s, c, t);
        drawText(g, p.x, p.y + 4, c.label, shift ? "is-bold is-shift" : "is-bold");
      }
      if (c.marker) drawMarker(g, s, c, shift);
    });
  }

  /* Numbered marker discs sit on the curve on conceptual graphs, matching the
     printed artwork. marker: {n: 1, at: 0.35, dx: 0, dy: 0} */
  function drawMarker(g, s, c, shift) {
    var m = c.marker;
    var p = pointOnCurve(s, c, num(m.pos, 0.4));
    var cx = p.x + num(m.dx, 0), cy = p.y + num(m.dy, 0);
    el("circle", { cx: cx, cy: cy, r: 8, class: "sdg-marker-disc" + (shift ? " is-shift" : "") }, g);
    var t = el("text", {
      x: cx, y: cy + 3.5, "text-anchor": "middle",
      class: "sdg-marker-text" + (shift ? " is-shift" : "")
    }, g);
    t.textContent = String(m.n == null ? "" : m.n);
  }

  function drawGuides(g, s, guides, step) {
    guides.forEach(function (gu) {
      if (!visible(gu, step)) return;
      var cls = "sdg-guide" + (gu.dash === false ? " is-solid" : "");
      var d;
      if (typeof gu.y === "number") {
        d = "M" + s.x(num(gu.from, s.xMin)) + " " + s.y(gu.y) +
            " L" + s.x(num(gu.to, s.xMax)) + " " + s.y(gu.y);
      } else if (typeof gu.x === "number") {
        d = "M" + s.x(gu.x) + " " + s.y(num(gu.from, s.yMin)) +
            " L" + s.x(gu.x) + " " + s.y(num(gu.to, s.yMax));
      } else { return; }
      var path = el("path", { d: d, class: cls }, g);
      if (isShift(gu.color)) path.style.stroke = "var(--sdg-shift)";
      if (gu.label && gu.label.text) {
        var lx = typeof gu.y === "number" ? s.x(num(gu.to, s.xMax)) : s.x(gu.x);
        var ly = typeof gu.y === "number" ? s.y(gu.y) : s.y(num(gu.to, s.yMax));
        drawText(g, lx, ly, gu.label, isShift(gu.color) ? "is-shift" : "");
      }
    });
  }

  function drawPoints(g, s, points, step) {
    points.forEach(function (p) {
      if (!visible(p, step)) return;
      var shift = isShift(p.color);
      var cls = "sdg-dot" + (p.style === "solid" ? " is-solid" : "") + (shift ? " is-shift" : "");
      el("circle", { cx: s.x(p.x), cy: s.y(p.y), r: num(p.r, 4), class: cls }, g);
      if (p.label && p.label.text) {
        drawText(g, s.x(p.x), s.y(p.y) + 4, p.label, shift ? "is-bold is-shift" : "is-bold");
      }
    });
  }

  /* Every arrow is red — shift arrows, movement-along arrows and schedule
     arrows alike. There is deliberately no colour option. */
  function drawArrows(g, s, arrows, step, uid) {
    arrows.forEach(function (a) {
      if (!visible(a, step)) return;
      var x1 = s.x(a.from[0]), y1 = s.y(a.from[1]);
      var x2 = s.x(a.to[0]), y2 = s.y(a.to[1]);
      var d;
      if (a.curved) {
        var mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
        var dx = x2 - x1, dy = y2 - y1;
        var len = Math.sqrt(dx * dx + dy * dy) || 1;
        var k = num(a.curved === true ? 0.18 : a.curved, 0.18) * len;
        d = "M" + x1 + " " + y1 + " Q" + (mx - dy / len * k) + " " + (my + dx / len * k) +
            " " + x2 + " " + y2;
      } else {
        d = "M" + x1 + " " + y1 + " L" + x2 + " " + y2;
      }
      el("path", { d: d, class: "sdg-arrow", "marker-end": "url(#" + uid + "-arrow)" }, g);
      if (a.label && a.label.text) {
        drawText(g, (x1 + x2) / 2, (y1 + y2) / 2, a.label, "is-arrow is-bold");
      }
    });
  }

  /* Braces span a gap (a surplus, a shortage, the size of a shift). `below`
     puts the label on the far side of the brace — set it whenever the near
     side already holds a curve or another label. */
  function drawBraces(g, s, braces, step) {
    braces.forEach(function (b) {
      if (!visible(b, step)) return;
      var horiz = typeof b.y === "number";
      var depth = num(b.depth, 7) * (b.below ? 1 : -1);
      var a1, a2, mid, d;
      if (horiz) {
        var yb = s.y(b.y);
        a1 = s.x(num(b.from, s.xMin)); a2 = s.x(num(b.to, s.xMax));
        mid = (a1 + a2) / 2;
        d = "M" + a1 + " " + yb + " q0 " + depth + " " + ((mid - a1) / 2) + " " + depth +
            " L" + (mid - (mid - a1) / 4) + " " + (yb + depth) +
            " Q" + mid + " " + (yb + depth) + " " + mid + " " + (yb + depth * 1.8) +
            " Q" + mid + " " + (yb + depth) + " " + (mid + (a2 - mid) / 4) + " " + (yb + depth) +
            " L" + (mid + (a2 - mid) / 2) + " " + (yb + depth) +
            " q" + ((a2 - mid) / 2) + " 0 " + ((a2 - mid) / 2) + " " + (-depth);
        el("path", { d: d, class: "sdg-brace" }, g);
        if (b.label && b.label.text) {
          drawText(g, mid, yb + depth * 2.6 + (b.below ? 6 : -2),
            merge({ anchor: "middle" }, b.label), "is-bold");
        }
      } else {
        var xb = s.x(b.x);
        a1 = s.y(num(b.from, s.yMin)); a2 = s.y(num(b.to, s.yMax));
        mid = (a1 + a2) / 2;
        d = "M" + xb + " " + a1 + " q" + depth + " 0 " + depth + " " + ((mid - a1) / 2) +
            " L" + (xb + depth) + " " + (mid - (mid - a1) / 4) +
            " Q" + (xb + depth) + " " + mid + " " + (xb + depth * 1.8) + " " + mid +
            " Q" + (xb + depth) + " " + mid + " " + (xb + depth) + " " + (mid + (a2 - mid) / 4) +
            " L" + (xb + depth) + " " + (mid + (a2 - mid) / 2) +
            " q0 " + ((a2 - mid) / 2) + " " + (-depth) + " " + ((a2 - mid) / 2);
        el("path", { d: d, class: "sdg-brace" }, g);
        if (b.label && b.label.text) {
          drawText(g, xb + depth * 2.6 + (b.below ? 6 : -6), mid + 4,
            merge({ anchor: b.below ? "start" : "end" }, b.label), "is-bold");
        }
      }
    });
  }

  function drawLabels(g, s, labels, step) {
    labels.forEach(function (l) {
      if (!visible(l, step)) return;
      drawText(g, s.x(num(l.x, s.xMin)), s.y(num(l.y, s.yMin)) + 4, l,
        isShift(l.color) ? "is-shift" : "");
    });
  }

  function renderPanel(panel, step, uid) {
    var wrap = html("div", "sdg-panel");
    if (panel.label) {
      var h = html("p", "sdg-panel-label", wrap);
      h.textContent = panel.label;
    }
    var svg = el("svg", {
      viewBox: "0 0 " + PLOT.w + " " + PLOT.h,
      role: "img",
      "aria-label": panel.alt || panel.label || "Supply and demand graph"
    });
    wrap.appendChild(svg);
    defsFor(svg, uid);
    var g = el("g", null, svg);
    var s = scaler(panel.axes);
    resolveOn(panel, s);

    drawAxes(g, s, panel.axes, step, uid);
    drawGuides(g, s, arr(panel.guides), step);
    drawCurves(g, s, arr(panel.curves), step);
    drawBraces(g, s, arr(panel.braces), step);
    drawArrows(g, s, arr(panel.arrows).concat(arr(panel.moves)), step, uid);
    drawPoints(g, s, arr(panel.points), step);
    drawLabels(g, s, arr(panel.labels), step);
    return wrap;
  }

  /* ---------- schedules ------------------------------------------------- */

  function renderSchedule(sch, step) {
    var wrap = html("div", "sdg-schedule");
    if (sch.heading) {
      var cap = html("p", "sdg-schedule-caption", wrap);
      cap.textContent = sch.heading;
    }
    var table = html("table", null, wrap);
    var thead = html("thead", null, table);
    var hrow = html("tr", null, thead);
    var heads = arr(sch.head);
    /* An arrows array of nothing but nulls must not add an empty column. */
    var hasArrows = arr(sch.arrows).some(function (a) { return !!a; });

    heads.forEach(function (h, i) {
      var th = html("th", null, hrow);
      th.textContent = h;
      if (sch.shiftColumn != null && i === sch.shiftColumn) th.className = "is-shift";
    });
    if (hasArrows) html("th", "sdg-rowarrow", hrow);

    var tbody = html("tbody", null, table);
    arr(sch.rows).forEach(function (row, ri) {
      var tr = html("tr", null, tbody);
      var hi = arr(sch.highlight).some(function (h) {
        return h.row === ri && visible(h, step);
      });
      if (hi) tr.className = "is-highlight";
      arr(row).forEach(function (cell, ci) {
        var td = html("td", null, tr);
        td.textContent = cell == null ? "" : String(cell);
        if (sch.shiftColumn != null && ci === sch.shiftColumn) td.className = "is-shift";
      });
      if (hasArrows) {
        var td2 = html("td", "sdg-rowarrow", tr);
        var a = sch.arrows[ri];
        td2.textContent = a === "up" ? "↑" : a === "down" ? "↓" : a || "";
      }
    });
    return wrap;
  }

  /* ---------- widget ---------------------------------------------------- */

  var uidCounter = 0;

  function Widget(node, config) {
    this.node = node;
    this.base = config;
    this.uid = "sdg" + (++uidCounter);
    this.scenario = 0;
    this.step = 0;
    this.build();
  }

  Widget.prototype.active = function () {
    var scenarios = arr(this.base.scenarios);
    if (!scenarios.length) return this.base;
    var overlay = scenarios[this.scenario] || {};
    return merge(this.base, overlay.overlay || {});
  };

  Widget.prototype.panels = function (cfg) {
    if (Array.isArray(cfg.panels) && cfg.panels.length) return cfg.panels;
    return [cfg];
  };

  Widget.prototype.build = function () {
    var self = this;
    var cfg = this.active();
    this.node.textContent = "";

    if (cfg.title) {
      var t = html("p", "sdg-title", this.node);
      t.textContent = cfg.title;
    }

    var scenarios = arr(this.base.scenarios);
    if (scenarios.length) {
      var bar = html("div", "sdg-scenarios", this.node);
      scenarios.forEach(function (sc, i) {
        var b = html("button", "sdg-scenario", bar);
        b.type = "button";
        b.textContent = sc.label || "Case " + (i + 1);
        b.setAttribute("aria-pressed", String(i === self.scenario));
        b.addEventListener("click", function () {
          if (self.scenario === i) return;
          self.scenario = i;
          self.step = 0;
          self.build();
        });
      });
    }

    this.stage = html("div", "sdg-stage", this.node);
    this.caption = html("p", "sdg-caption", this.node);

    var steps = arr(cfg.steps);
    if (steps.length > 1) {
      var ctl = html("div", "sdg-controls", this.node);
      this.prev = html("button", null, ctl);
      this.prev.type = "button";
      this.prev.textContent = "← Back";
      this.next = html("button", null, ctl);
      this.next.type = "button";
      this.next.textContent = "Next →";
      this.count = html("span", "sdg-stepcount", ctl);
      this.prev.addEventListener("click", function () { self.go(self.step - 1); });
      this.next.addEventListener("click", function () { self.go(self.step + 1); });
    }
    this.draw();
  };

  Widget.prototype.go = function (i) {
    var steps = arr(this.active().steps);
    var max = Math.max(0, steps.length - 1);
    this.step = Math.min(max, Math.max(0, i));
    this.draw();
  };

  Widget.prototype.draw = function () {
    var cfg = this.active();
    var step = this.step;
    this.stage.textContent = "";

    var self = this;
    this.panels(cfg).forEach(function (p, i) {
      self.stage.appendChild(renderPanel(p, step, self.uid + "-p" + i));
    });

    var schedules = cfg.schedules ? arr(cfg.schedules) : (cfg.schedule ? [cfg.schedule] : []);
    schedules.forEach(function (sch) {
      if (!visible(sch, step)) return;
      self.stage.appendChild(renderSchedule(sch, step));
    });

    var steps = arr(cfg.steps);
    this.caption.textContent = steps.length ? (steps[step] && steps[step].caption) || "" : (cfg.caption || "");

    if (this.count) {
      this.prev.disabled = step === 0;
      this.next.disabled = step === steps.length - 1;
      this.count.textContent = "Step " + (step + 1) + " of " + steps.length;
    }
  };

  /* ---------- bootstrap ------------------------------------------------- */

  function readConfig(node) {
    var script = node.querySelector('script[type="application/json"]');
    var raw = script ? script.textContent : node.textContent;
    var cfg = JSON.parse(raw);
    if (cfg.preset) {
      var expand = PRESETS[cfg.preset];
      if (!expand) throw new Error('unknown preset "' + cfg.preset + '"');
      cfg = merge(expand(cfg), stripPreset(cfg));
    }
    if (!cfg.panels && !cfg.axes) {
      throw new Error("config needs axes (or panels); figure mode is not implemented");
    }
    return cfg;
  }

  function stripPreset(cfg) {
    var out = clone(cfg);
    ["preset", "curve", "direction", "magnitude", "panels"].forEach(function (k) {
      if (k !== "panels" || cfg.preset !== "double") delete out[k];
    });
    return out;
  }

  function render(node) {
    try {
      var cfg = readConfig(node);
      var w = new Widget(node, cfg);
      node.sdGraph = w;
      return w;
    } catch (e) {
      node.textContent = "";
      var p = html("p", "sdg-error", node);
      p.textContent = "sd-graph " + VERSION + ": " + e.message;
      if (global.console) global.console.error("sd-graph:", e);
      return null;
    }
  }

  function renderAll(root) {
    var nodes = (root || document).querySelectorAll("div.sdg");
    var out = [];
    Array.prototype.forEach.call(nodes, function (n) {
      if (!n.sdGraph) out.push(render(n));
    });
    return out;
  }

  global.SDGraph = { version: VERSION, render: render, renderAll: renderAll, presets: PRESETS };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { renderAll(); });
  } else {
    renderAll();
  }
}(this));
