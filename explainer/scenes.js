/* One voice note, one turn of the wheel: live scenes (agent_team E78-S2 round 3, Jordi's E78-A2 notes).
 *
 * Eight scenes, one per storyboard frame, drawn as SVG in the paper-deck style. Every frame is a pure function of
 * time: scene.draw(t) with t in seconds from the scene's start, nothing kept from the previous frame, no timers. So
 * the same code plays on a page (live.js drives t from the clock, loops, rests on the final frame) and renders frame
 * by frame in HyperFrames (the video seeks t). No dependencies.
 *
 *   LiveScenes.list               [{ id, headline, line, narration, settle, len }]  (words for the page and the voice)
 *   LiveScenes.mount(el, id)      draws the scene's SVG into el, returns { draw(t), settle, len, final() }
 *   settle  seconds until every step has landed (the final frame; continuous motion keeps going after it)
 *   len     seconds of one loop on a page, the final frame held about 3 s
 *
 * Plain JavaScript (ES5), no build: works as a <script> on any page, after paper.js. Colours and fonts are the paper
 * tokens: paper.js (window.PaperTokens) is written from video/library/brands/paper.json (deck.tokens plus explainer)
 * by skills/explainer-video/scripts/paper.mjs, so this file copies none of them (E53-S9).
 */
(function (root) {
  var T = root.PaperTokens || {};
  var C = { bg: T['--bg'], stage: T['--stage'], stage2: T['--stage-2'], ink: T['--ink'], muted: T['--muted'], faint: T['--faint'],
    line: T['--line'], accent: T['--accent'], soft: T['--accent-soft'], warm: T.warm };
  var SERIF = T['--serif'], SANS = T['--sans'];
  var NS = 'http://www.w3.org/2000/svg';

  /* ---------- small helpers ---------- */
  function clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function p(t, a, d) { return clamp((t - a) / d); }               // progress of a step starting at a, lasting d
  function out(x) { return 1 - Math.pow(1 - x, 3); }                // ease-out cubic
  function io(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  function lerp(a, b, k) { return a + (b - a) * k; }
  function hex(c) {                                                  // '#rrggbb' or 'rgb(r,g,b)' → [r, g, b]
    if (c.charAt(0) !== '#') return c.slice(4, -1).split(',').map(Number);
    return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
  }
  function mix(a, b, k) {
    var x = hex(a), y = hex(b);
    return 'rgb(' + Math.round(lerp(x[0], y[0], k)) + ',' + Math.round(lerp(x[1], y[1], k)) + ',' + Math.round(lerp(x[2], y[2], k)) + ')';
  }
  function bump(x, a, b) { return x <= a || x >= b ? 0 : Math.sin(Math.PI * (x - a) / (b - a)); } // 0 → 1 → 0
  function el(parent, tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function set(e, attrs) { for (var k in attrs) e.setAttribute(k, attrs[k]); }
  function txt(parent, x, y, s, size, o) {
    o = o || {};
    return el(parent, 'text', { x: x, y: y, 'font-family': o.serif ? SERIF : SANS, 'font-size': size,
      'font-weight': o.weight || 400, fill: o.fill || C.ink, 'text-anchor': o.anchor || 'middle',
      'dominant-baseline': 'central' }, s);
  }
  function show(e, k, dy) {                                          // fade in and rise dy px
    set(e, { opacity: k, transform: 'translate(0 ' + ((1 - k) * (dy == null ? 12 : dy)) + ')' });
  }
  function svgIn(host) {
    host.innerHTML = '';
    return el(host, 'svg', { viewBox: '0 0 1000 1000', width: '100%', role: 'img', style: 'display:block' });
  }
  function boxEdge(cx, cy, hw, hh, dx, dy) {                        // where a ray from a box centre leaves the box
    var k = Math.min(dx ? hw / Math.abs(dx) : 1e9, dy ? hh / Math.abs(dy) : 1e9);
    return [cx + dx * k, cy + dy * k];
  }
  function quad(a, c, b, k) {                                        // point on a quadratic curve
    return [lerp(lerp(a[0], c[0], k), lerp(c[0], b[0], k), k), lerp(lerp(a[1], c[1], k), lerp(c[1], b[1], k), k)];
  }
  function drawLine(e, len, k) { set(e, { 'stroke-dasharray': len, 'stroke-dashoffset': len * (1 - k) }); }
  function arrowHead(parent, color) {
    return el(parent, 'path', { d: 'M -14 -9 L 0 0 L -14 9', fill: 'none', stroke: color, 'stroke-width': 4,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  }
  function place(e, x, y, angleDeg, k) {
    set(e, { transform: 'translate(' + x + ' ' + y + ') rotate(' + angleDeg + ')', opacity: k == null ? 1 : k });
  }

  /* ---------- the wheel: the repo in the middle, six personas around it ---------- */
  var PERSONAS = ['Delivery manager', 'Writer', 'Scout', 'Unblocker', 'Reporter', 'Responder'];
  var CX = 500, CY = 520, R = 320, REPO = { hw: 150, hh: 80 };

  function wheel(svg, o) {
    o = o || {};
    var w = { g: el(svg, 'g', {}) };
    w.rimG = el(w.g, 'g', {});
    el(w.rimG, 'circle', { cx: CX, cy: CY, r: R, fill: 'none', stroke: C.line, 'stroke-width': 3, 'stroke-dasharray': '2 14', 'stroke-linecap': 'round' });
    w.rim = el(w.rimG, 'g', {});                                      // turning chevrons between personas
    for (var i = 0; i < 6; i++) {
      var a = (-60 + i * 60) * Math.PI / 180;
      var c = el(w.rim, 'path', { d: 'M -10 -12 L 4 0 L -10 12', fill: 'none', stroke: C.faint, 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
      set(c, { transform: 'translate(' + (CX + R * Math.cos(a)) + ' ' + (CY + R * Math.sin(a)) + ') rotate(' + (-60 + i * 60 + 90) + ')' });
    }
    w.under = el(w.g, 'g', {});                                       // spokes and packets go under the boxes
    w.repoG = el(w.g, 'g', {});
    w.repo = el(w.repoG, 'rect', { x: CX - REPO.hw, y: CY - REPO.hh, width: REPO.hw * 2, height: REPO.hh * 2, rx: 14, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
    w.repoText = txt(w.repoG, CX, CY + (o.repoLow ? -26 : 0), 'The repo', 62, { serif: true });
    w.p = PERSONAS.map(function (name, i) {
      var ang = (-90 + i * 60) * Math.PI / 180, x = CX + R * Math.cos(ang), y = CY + R * Math.sin(ang);
      var wd = i === 0 ? 384 : 232, g = el(w.g, 'g', {});
      var halo = el(g, 'circle', { cx: x, cy: y, r: 60, fill: 'none', stroke: C.accent, 'stroke-width': 3, opacity: 0 });
      var rect = el(g, 'rect', { x: x - wd / 2, y: y - 42, width: wd, height: 84, rx: 42, 'stroke-width': 3 });
      var t = txt(g, x, y + 1, name, 42, { weight: 500 });
      return { g: g, rect: rect, text: t, halo: halo, x: x, y: y, hw: wd / 2, hh: 42, ang: -90 + i * 60 };
    });
    w.setP = function (i, awake, lit) {                               // idle → awake (ink) → lit (accent)
      var q = w.p[i];
      set(q.rect, { fill: mix(C.bg, C.accent, lit), stroke: mix(mix(C.line, C.ink, awake), C.accent, lit) });
      set(q.text, { fill: mix(mix(mix(C.faint, C.muted, 0.38), C.ink, awake), C.bg, clamp((lit - 0.25) * 4)) }); // flips to paper once the fill is dark
    };
    w.ring = function (i, k) {                                        // a ring that pulses out once, k 0..1
      var q = w.p[i];
      set(q.halo, { r: lerp(40, q.hw + 40, k), opacity: k > 0 && k < 1 ? (1 - k) * 0.9 : 0 });
    };
    w.turn = function (deg) { set(w.rim, { transform: 'rotate(' + deg + ' ' + CX + ' ' + CY + ')' }); };
    w.spoke = function (i) {                                          // repo edge → persona edge
      var q = w.p[i], dx = q.x - CX, dy = q.y - CY;
      return { a: boxEdge(CX, CY, REPO.hw + 8, REPO.hh + 8, dx, dy), b: boxEdge(q.x, q.y, q.hw + 8, q.hh + 8, -dx, -dy) };
    };
    for (var j = 0; j < 6; j++) w.setP(j, o.awake ? 1 : 0, 0);
    return w;
  }

  function satellite(svg, x, y, r) {
    var g = el(svg, 'g', {});
    var c = el(g, 'circle', { cx: x, cy: y, r: r, 'stroke-width': 3 });
    var t1 = txt(g, x, y, 'Zenod', r > 100 ? 64 : 36, { serif: true });
    return { g: g, c: c, t: t1, x: x, y: y, r: r, lit: function (k) {
      set(c, { fill: mix(C.bg, C.accent, k), stroke: C.accent });
      set(t1, { fill: mix(C.accent, C.bg, k) });
    } };
  }

  /* ---------- the eight scenes ---------- */
  var SCENES = [
    { id: 'say', headline: 'I say it once.', line: 'A voice note while I walk.',
      narration: 'I say what I want once, in a voice note.', settle: 3.4, len: 7,
      label: 'Me, holding a voice note with moving sound bars; the note flies into Zenod, which lights up and keeps every word.',
      build: function (svg) {
        var s = {};
        s.me = el(svg, 'g', {});
        el(s.me, 'rect', { x: 50, y: 330, width: 360, height: 300, rx: 22, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
        txt(s.me, 230, 400, 'Me', 56, { serif: true });
        s.bars = [];
        for (var i = 0; i < 9; i++) s.bars.push(el(s.me, 'rect', { x: 132 + i * 22, width: 12, rx: 6, fill: C.ink }));
        s.z = satellite(svg, 760, 480, 150);
        s.sub = txt(svg, 760, 690, 'keeps every word', 44, { fill: C.accent, weight: 500 });
        s.path = el(svg, 'path', { d: 'M 420 470 Q 520 300 600 430', fill: 'none', stroke: C.accent, 'stroke-width': 4, 'stroke-dasharray': '1 12', 'stroke-linecap': 'round' });
        s.note = el(svg, 'g', {});
        el(s.note, 'rect', { x: -34, y: -22, width: 68, height: 44, rx: 22, fill: C.accent });
        for (var b = 0; b < 4; b++) el(s.note, 'rect', { x: -19 + b * 11, y: -9 + (b % 2 ? -4 : 0), width: 6, height: b % 2 ? 26 : 18, rx: 3, fill: C.bg });
        s.q = txt(svg, 500, 860, 'How does that become work done?', 54, { serif: true });
        return s;
      },
      draw: function (s, t) {
        var amp = lerp(1, 0.18, p(t, 1.4, 0.8));
        s.bars.forEach(function (b, i) {
          var h = 18 + 92 * amp * Math.abs(Math.sin(t * 5.2 + i * 0.85)) * (0.55 + 0.45 * Math.sin(i * 1.7 + 1));
          set(b, { y: 530 - h / 2, height: h });
        });
        var f = io(p(t, 1.3, 0.9));
        var pt = quad([420, 470], [520, 300], [600, 430], f);
        place(s.note, pt[0], pt[1], 0, f > 0 && f < 1 ? 1 : 0);
        drawLine(s.path, 300, f);
        s.z.lit(out(p(t, 2.1, 0.45)));
        set(s.z.c, { r: 150 + 14 * bump(t, 2.1, 2.7) });
        show(s.sub, out(p(t, 2.3, 0.45)));
        show(s.q, out(p(t, 2.5, 0.5)), 16);
      } },

    { id: 'push', headline: 'Zenod pushes the Delivery manager', line: 'My memory sits outside the wheel. It sets one turn going.',
      narration: 'Zenod keeps every word, and wakes the Delivery manager.', settle: 3.2, len: 7,
      label: 'The wheel of six personas around the repo; Zenod, outside the wheel, sends one push into the Delivery manager, who lights up, and the wheel turns one notch.',
      build: function (svg) {
        var s = { w: wheel(svg) };
        s.z = satellite(svg, 868, 92, 70);
        s.z.lit(1);
        s.mem = txt(svg, 868, 190, 'my memory', 36, { fill: C.muted });
        s.path = el(svg, 'path', { d: 'M 806 124 Q 740 170 664 186', fill: 'none', stroke: C.accent, 'stroke-width': 5, 'stroke-linecap': 'round' });
        s.head = arrowHead(svg, C.accent);
        s.word = txt(svg, 700, 112, 'one push', 38, { fill: C.accent, weight: 600 });
        return s;
      },
      draw: function (s, t) {
        var f = io(p(t, 0.5, 0.7));
        drawLine(s.path, 160, f);
        var pt = quad([806, 124], [740, 170], [664, 186], f), pv = quad([806, 124], [740, 170], [664, 186], Math.max(0, f - 0.05));
        place(s.head, pt[0], pt[1], Math.atan2(pt[1] - pv[1], pt[0] - pv[0]) * 180 / Math.PI, f > 0.05 ? 1 : 0);
        show(s.word, out(p(t, 0.7, 0.45)), 8);
        var lit = out(p(t, 1.15, 0.4));
        s.w.setP(0, 1, lit);
        s.w.ring(0, p(t, 1.15, 0.9));
        s.w.turn(60 * io(p(t, 1.5, 1.4)));
      } },

    { id: 'tickets', headline: 'It writes the tickets, then wakes the team', line: 'Tickets go into the repo. Each persona wakes for its part.',
      narration: 'It writes the tickets into the repo, then wakes the team.', settle: 3.6, len: 7.5,
      label: 'The Delivery manager drops three tickets into the repo, then a wave runs round the wheel and wakes each persona.',
      build: function (svg) {
        var s = { w: wheel(svg, { repoLow: true }) };
        s.tag = txt(svg, 500, 116, 'writes 3 tickets', 40, { fill: C.accent, weight: 600 });
        s.tk = [0, 1, 2].map(function () {
          var g = el(svg, 'g', {});
          var r = el(g, 'rect', { x: -32, y: -24, width: 64, height: 48, rx: 6, 'stroke-width': 3 });
          el(g, 'rect', { x: -20, y: -11, width: 40, height: 5, rx: 2, fill: C.ink });
          el(g, 'rect', { x: -20, y: 3, width: 26, height: 5, rx: 2, fill: C.muted });
          return { g: g, r: r };
        });
        s.dots = [1, 2, 3, 4, 5].map(function () { return el(svg, 'circle', { r: 11, fill: C.accent }); });
        s.wake = txt(svg, 500, 960, 'wakes each persona', 40, { fill: C.accent, weight: 600 });
        return s;
      },
      draw: function (s, t) {
        s.w.setP(0, 1, 1);
        show(s.tag, out(p(t, 0.2, 0.4)), 8);
        s.tk.forEach(function (k, i) {
          var f = io(p(t, 0.35 + i * 0.4, 0.7)), tx = 420 + i * 80;
          place(k.g, lerp(500, tx, f), lerp(200, CY + 34, f), lerp(-8, 0, f), p(t, 0.35 + i * 0.4, 0.1));
          var landed = p(t, 1.0 + i * 0.4, 0.3);
          set(k.r, { fill: mix(C.bg, C.soft, landed), stroke: mix(C.ink, C.accent, landed) });
        });
        for (var i = 1; i < 6; i++) {
          var st = 2.0, dur = 0.26 * i, f = out(p(t, st, dur)), a = (-90 + 60 * i * f) * Math.PI / 180;
          set(s.dots[i - 1], { cx: CX + R * Math.cos(a), cy: CY + R * Math.sin(a), opacity: f > 0 && f < 1 ? 1 : 0 });
          var arrive = st + dur;
          s.w.setP(i, out(p(t, arrive, 0.3)), 0.35 * bump(t, arrive - 0.05, arrive + 0.6));
          s.w.ring(i, p(t, arrive, 0.8));
        }
        show(s.wake, out(p(t, 2.1, 0.45)), 8);
      } },

    { id: 'readwrite', headline: 'Everyone reads and writes the repo', line: 'Read the tickets in. Write the work back.',
      narration: 'Everyone reads the repo, does their part, and writes the work back.', settle: 1.2, len: 9,
      label: 'All six personas are awake; along each spoke a hollow dot runs out of the repo (a read) and a green dot runs back in (a write), round and round.',
      build: function (svg) {
        var s = { w: wheel(svg, { awake: true }), sp: [] };
        for (var i = 0; i < 6; i++) {
          var e = s.w.spoke(i), len = Math.hypot(e.b[0] - e.a[0], e.b[1] - e.a[1]);
          var line = el(s.w.under, 'line', { x1: e.a[0], y1: e.a[1], x2: e.b[0], y2: e.b[1], stroke: C.line, 'stroke-width': 3 });
          var rd = el(s.w.under, 'circle', { r: 13, fill: C.bg, stroke: C.ink, 'stroke-width': 4 });
          var wr = el(s.w.under, 'circle', { r: 14, fill: C.accent });
          s.sp.push({ a: e.a, b: e.b, len: len, line: line, rd: rd, wr: wr });
        }
        var lg = el(svg, 'g', {});
        el(lg, 'circle', { cx: 250, cy: 962, r: 13, fill: C.bg, stroke: C.ink, 'stroke-width': 4 });
        txt(lg, 274, 962, 'reads', 42, { anchor: 'start', fill: C.muted });
        el(lg, 'circle', { cx: 600, cy: 962, r: 14, fill: C.accent });
        txt(lg, 624, 962, 'writes', 42, { anchor: 'start', fill: C.muted });
        s.lg = lg;
        return s;
      },
      draw: function (s, t) {
        var P = 2.4, hit = 0;
        s.sp.forEach(function (q, i) {
          drawLine(q.line, q.len, out(p(t, i * 0.08, 0.6)));
          var u = t - 0.6 - i * 0.37, on = u >= 0;
          u = ((u % P) + P) % P / P;
          var r = p(u, 0, 0.42), w = p(u, 0.52, 0.42);
          var rp = [lerp(q.a[0], q.b[0], io(r)), lerp(q.a[1], q.b[1], io(r))];
          var wp = [lerp(q.b[0], q.a[0], io(w)), lerp(q.b[1], q.a[1], io(w))];
          set(q.rd, { cx: rp[0], cy: rp[1], opacity: on && r > 0 && r < 1 ? 1 : 0 });
          set(q.wr, { cx: wp[0], cy: wp[1], opacity: on && w > 0 && w < 1 ? 1 : 0 });
          s.w.setP(i, 1, on ? 0.8 * bump(u, 0.4, 0.56) : 0);           // the persona works between read and write
          if (on) hit = Math.max(hit, bump(u, 0.9, 1));
        });
        set(s.w.repo, { stroke: mix(C.ink, C.accent, hit), 'stroke-width': 3 + 3 * hit });
        show(s.lg, out(p(t, 0.6, 0.45)), 8);
      } },

    { id: 'inside', headline: 'In the middle: one repo', line: 'Everything they read and write lives here.',
      narration: 'Inside: the chat, the goals, the deck, the personas, the screens.', settle: 2.6, len: 8,
      label: 'Inside the repo five parts appear: chat lane, goal tree, spine deck, personas and canvases; next to each, who writes into it or reads from it, with dots moving that way.',
      build: function (svg) {
        var s = { rows: [] };
        el(svg, 'rect', { x: 30, y: 40, width: 940, height: 920, rx: 22, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
        txt(svg, 74, 104, 'The repo', 54, { serif: true, anchor: 'start' });
        var rows = [
          ['Chat lane', 'what I say, their asks', 'Me', 'says', 1],
          ['Goal tree', 'goals and status', 'Delivery manager', 'writes', 1],
          ['Spine deck', 'a page per goal', 'Me', 'reads', 0],
          ['Personas', 'who each one is', 'Every persona', 'reads', 0],
          ['Canvases', 'Pipeline, Kanban', 'Writer', 'writes', 1]];
        rows.forEach(function (r, i) {
          var y = 160 + i * 158, g = el(svg, 'g', {});
          el(g, 'rect', { x: 60, y: y, width: 470, height: 132, rx: 12, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
          txt(g, 92, y + 48, r[0], 46, { anchor: 'start', weight: 500 });
          txt(g, 92, y + 96, r[1], 34, { anchor: 'start', fill: C.muted });
          var who = el(g, 'g', {}), cy = y + 66;
          el(who, 'rect', { x: 688, y: cy - 40, width: 272, height: 80, rx: 40, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
          txt(who, 824, cy + 1, r[2], r[2].length > 13 ? 30 : r[2].length > 3 ? 34 : 38, { weight: 500 });
          var ln = el(g, 'line', { x1: 540, y1: cy, x2: 676, y2: cy, stroke: C.line, 'stroke-width': 4 });
          var hd = arrowHead(g, C.ink);
          var vb = txt(g, 608, cy - 32, r[3], 34, { fill: r[4] ? C.accent : C.muted, weight: 600 });
          var dot = r[4] ? el(g, 'circle', { r: 13, fill: C.accent }) : el(g, 'circle', { r: 12, fill: C.bg, stroke: C.ink, 'stroke-width': 4 });
          s.rows.push({ g: g, who: who, ln: ln, hd: hd, vb: vb, dot: dot, cy: cy, write: r[4] });
        });
        return s;
      },
      draw: function (s, t) {
        s.rows.forEach(function (r, i) {
          show(r.g, out(p(t, 0.15 + i * 0.3, 0.45)), 14);
          var a = out(p(t, 1.7 + i * 0.12, 0.5));
          show(r.who, a, 0);
          drawLine(r.ln, 136, a);
          set(r.vb, { opacity: a });
          // a write points into the row (right to left), a read out of it
          if (r.write) place(r.hd, 544, r.cy, 180, a); else place(r.hd, 676, r.cy, 0, a);
          var u = t - 2.2 - i * 0.25, on = u >= 0, f = io(((u % 1.6) + 1.6) % 1.6 / 1.6);
          var x = r.write ? lerp(672, 550, f) : lerp(550, 672, f);
          set(r.dot, { cx: x, cy: r.cy, opacity: on && f > 0.02 && f < 0.98 ? 1 : 0 });
        });
      } },

    { id: 'writes', headline: 'Each persona writes one thing', line: 'Its own lane, nothing else.',
      narration: 'Each persona writes one thing: goals, posts, topics, replies.', settle: 3.4, len: 7.5,
      label: 'Row by row, each persona sends a green dot into the one thing it writes, which fills green: goals and tasks, posts, topics, replies, answers.',
      build: function (svg) {
        var rows = [['Delivery manager', 'Goals and tasks'], ['Writer', 'Posts in the Pipeline'], ['Scout', 'Topics worth a post'],
          ['Responder', 'Replies to check'], ['Unblocker', 'Answers to questions']];
        return { rows: rows.map(function (r, i) {
          var y = 120 + i * 172, g = el(svg, 'g', {});
          el(g, 'rect', { x: 16, y: y - 52, width: 350, height: 104, rx: 52, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
          txt(g, 191, y + 1, r[0], r[0].length > 12 ? 38 : 44, { weight: 500 });
          var ln = el(svg, 'line', { x1: 378, y1: y, x2: 548, y2: y, stroke: C.line, 'stroke-width': 4 });
          var hd = arrowHead(svg, C.accent);
          var box = el(svg, 'rect', { x: 566, y: y - 58, width: 420, height: 116, rx: 12, 'stroke-width': 3 });
          var lb = txt(svg, 776, y + 1, r[1], r[1].length > 18 ? 37 : 42, { serif: true });
          var dot = el(svg, 'circle', { r: 13, fill: C.accent });
          return { g: g, ln: ln, hd: hd, box: box, lb: lb, dot: dot, y: y };
        }) };
      },
      draw: function (s, t) {
        s.rows.forEach(function (r, i) {
          var st = 0.2 + i * 0.5;
          show(r.g, out(p(t, st, 0.35)), 10);
          var a = out(p(t, st + 0.2, 0.45));
          drawLine(r.ln, 170, a);
          place(r.hd, 552, r.y, 0, a);
          var f = io(p(t, st + 0.45, 0.45));
          set(r.dot, { cx: lerp(378, 560, f), cy: r.y, opacity: f > 0 && f < 1 ? 1 : 0 });
          var fill = out(p(t, st + 0.85, 0.35));
          set(r.box, { fill: mix(C.bg, C.soft, fill), stroke: mix(C.line, C.accent, fill), opacity: 0.4 + 0.6 * a });
          set(r.lb, { fill: mix(C.faint, C.ink, Math.max(a * 0.6, fill)), opacity: 0.4 + 0.6 * a });
        });
      } },

    { id: 'card', headline: 'Done work lands on my phone', line: 'A card to check, or a question.',
      narration: 'Finished work lands on my phone as a card.', settle: 3.0, len: 7.5,
      label: 'A phone shows Team home; a done card slides up with Yes and Notes, then a question card; a tap on Yes ripples and the card says sent.',
      build: function (svg) {
        var s = {};
        var clip = el(el(svg, 'defs', {}), 'clipPath', { id: 'e78-phone' });
        el(clip, 'rect', { x: 268, y: 160, width: 464, height: 790 });
        el(svg, 'rect', { x: 250, y: 30, width: 500, height: 950, rx: 64, fill: C.bg, stroke: C.ink, 'stroke-width': 14 });
        txt(svg, 300, 112, 'Team home', 42, { serif: true, anchor: 'start' });
        var inner = el(svg, 'g', { 'clip-path': 'url(#e78-phone)' });
        s.c1 = el(inner, 'g', {});
        el(s.c1, 'rect', { x: 290, y: 180, width: 420, height: 380, rx: 16, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
        txt(s.c1, 322, 232, 'Done, check it', 38, { anchor: 'start', weight: 500 });
        el(s.c1, 'rect', { x: 322, y: 280, width: 356, height: 130, rx: 8, fill: C.stage });
        s.yes = el(s.c1, 'rect', { x: 322, y: 450, width: 170, height: 76, rx: 10, fill: C.accent });
        s.yesT = txt(s.c1, 407, 488, 'Yes', 36, { fill: C.bg, weight: 600 });
        el(s.c1, 'rect', { x: 508, y: 450, width: 170, height: 76, rx: 10, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
        txt(s.c1, 593, 488, 'Notes', 34, { weight: 500 });
        s.rip = el(s.c1, 'circle', { cx: 407, cy: 488, fill: 'none', stroke: C.accent, 'stroke-width': 5 });
        s.c2 = el(inner, 'g', {});
        el(s.c2, 'rect', { x: 290, y: 590, width: 420, height: 190, rx: 16, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
        txt(s.c2, 322, 650, 'A question', 40, { serif: true, anchor: 'start' });
        txt(s.c2, 322, 714, 'one tap to answer', 36, { anchor: 'start', fill: C.muted });
        return s;
      },
      draw: function (s, t) {
        var a = io(p(t, 0.25, 0.8)), b = io(p(t, 1.2, 0.7));
        set(s.c1, { transform: 'translate(0 ' + (1 - a) * 820 + ')' });
        set(s.c2, { transform: 'translate(0 ' + (1 - b) * 420 + ')' });
        var tap = p(t, 2.2, 0.8);
        set(s.rip, { r: lerp(20, 130, out(tap)), opacity: tap > 0 && tap < 1 ? 1 - tap : 0 });
        s.yesT.textContent = t >= 2.6 ? 'Sent' : 'Yes';
        set(s.yes, { fill: mix(C.accent, C.ink, bump(t, 2.2, 2.6)) });
      } },

    { id: 'rule', headline: 'My answer becomes a rule', line: 'The next turn starts smarter.',
      narration: 'My answer becomes a rule, and the next turn starts smarter.', settle: 3.4, len: 8,
      label: 'My answer, not like that, drops into the repo, where a new rule types itself: ask before posting; then the next turn of the wheel spins faster.',
      build: function (svg) {
        var s = {};
        s.bub = el(svg, 'g', {});
        el(s.bub, 'rect', { x: 290, y: 30, width: 420, height: 104, rx: 52, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
        txt(s.bub, 500, 83, 'Not like that', 42, { serif: true });
        s.ans = txt(svg, 530, 200, 'my answer', 36, { anchor: 'start', fill: C.accent, weight: 600 });
        s.drop = el(svg, 'circle', { cx: 500, r: 15, fill: C.accent });
        s.repo = el(svg, 'g', {});
        el(s.repo, 'rect', { x: 110, y: 270, width: 780, height: 290, rx: 18, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
        txt(s.repo, 150, 330, 'The repo', 50, { serif: true, anchor: 'start' });
        s.rule = el(s.repo, 'rect', { x: 150, y: 384, width: 700, height: 128, rx: 12, fill: C.soft, stroke: C.accent, 'stroke-width': 3 });
        s.ruleT = txt(s.repo, 500, 448, '', 40, { fill: C.accent, weight: 600 });
        s.down = el(svg, 'line', { x1: 500, y1: 576, x2: 500, y2: 668, stroke: C.accent, 'stroke-width': 4 });
        s.downH = arrowHead(svg, C.accent);
        s.every = txt(svg, 524, 622, 'every wake reads it', 36, { anchor: 'start', fill: C.muted });
        s.loop = el(svg, 'g', {});
        el(s.loop, 'circle', { cx: 500, cy: 820, r: 128, fill: 'none', stroke: C.accent, 'stroke-width': 6, 'stroke-dasharray': '120 40' });
        s.spin = el(s.loop, 'g', {});
        for (var i = 0; i < 3; i++) {
          var a = i * 120 * Math.PI / 180, c = el(s.spin, 'path', { d: 'M -12 -14 L 4 0 L -12 14', fill: 'none', stroke: C.accent, 'stroke-width': 6, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
          set(c, { transform: 'translate(' + (500 + 128 * Math.cos(a)) + ' ' + (820 + 128 * Math.sin(a)) + ') rotate(' + (i * 120 + 90) + ')' });
        }
        txt(s.loop, 500, 820, 'next turn', 40, { serif: true });
        return s;
      },
      draw: function (s, t) {
        show(s.bub, out(p(t, 0.1, 0.4)), 10);
        var f = io(p(t, 0.6, 0.6));
        set(s.drop, { cy: lerp(140, 400, f), opacity: f > 0 && f < 1 ? 1 : 0 });
        show(s.ans, out(p(t, 0.6, 0.4)), 0);
        var rule = 'New rule: ask before posting', n = Math.round(rule.length * p(t, 1.25, 1.0));
        s.ruleT.textContent = rule.slice(0, n);
        set(s.rule, { opacity: out(p(t, 1.15, 0.3)) });
        var d = out(p(t, 2.3, 0.4));
        drawLine(s.down, 92, d);
        place(s.downH, 500, 670, 90, d);
        set(s.every, { opacity: d });
        show(s.loop, out(p(t, 2.5, 0.45)), 10);
        var u = Math.max(0, t - 2.6);
        set(s.spin, { transform: 'rotate(' + (50 * u + 34 * u * u) + ' 500 820)' });
      } }
  ];

  function mount(host, id) {
    var sc = null;
    for (var i = 0; i < SCENES.length; i++) if (SCENES[i].id === id) sc = SCENES[i];
    if (!sc) throw new Error('no scene ' + id);
    var svg = svgIn(host);
    svg.setAttribute('aria-label', sc.label);
    var st = sc.build(svg);
    var h = { svg: svg, settle: sc.settle, len: sc.len,
      draw: function (t) { sc.draw(st, t); },
      final: function () { sc.draw(st, sc.settle + 0.9); } };
    h.final();
    return h;
  }

  root.LiveScenes = {
    list: SCENES.map(function (s) { return { id: s.id, headline: s.headline, line: s.line, narration: s.narration, settle: s.settle, len: s.len, label: s.label }; }),
    intro: { question: 'How does one thing I say turn into work done?',
      answer: 'Zenod keeps what I say and pushes the Delivery manager. It writes tickets and wakes the personas. Each reads the repo and writes its work back, and my answer comes back as a rule.',
      narration: 'How does one thing I say turn into work done?' },
    // url: the public address on the end card (E78-S4 round 2: final, public; was the brand's tailnet domain).
    outro: { claim: 'One voice note, one turn of the wheel.', narration: '', url: 'epicspine.dev/explainer' },
    mount: mount, colors: C
  };
})(typeof window !== 'undefined' ? window : this);
