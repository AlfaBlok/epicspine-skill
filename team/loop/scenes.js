/* The whole loop, animated: live scenes (agent_team E84-S12, after Jordi agreed the E84-S10 frames on E84-A2).
 *
 * Nine scenes: the zoom-out landing view Jordi asked for on E84-A2 ("once you zoom out from the circle ... unstructured
 * feedback to structured plan with tickets, and then a delivery engine ... an iterative delivery engine ... an
 * aggregated feedback channel"), the seven agreed frames of docs/proposals/e84-s10-whole-loop (one voice note going
 * round the loop), and the landing view again at the end. Same contract as e78-explainer-r3/scenes.js: every frame is a
 * pure function of time, scene.draw(t), so the page (live.js) and the video (stitch_scenes.mjs) share this file.
 *
 *   LiveScenes.list   [{ id, headline, line, narration, settle, len, label }]
 *   LiveScenes.mount(el, id)  → { draw(t), settle, len, final() }
 *   LiveScenes.viewH  the scenes are 1000 x 1100 (taller than e78's square, so the video fills the frame down to the
 *                     captions, branded-video Rules, Jordi 2026-11-09)
 *   LiveScenes.intro  null: the landing view opens the video itself, no title card
 *
 * The two phone scenes show real screens captured read-only from the live console (shots/desk.jpg, shots/inbox.jpg,
 * every write refused in the browser; see README.md). Colours and fonts are paper tokens (paper.js), none copied here.
 */
(function (root) {
  var T = root.PaperTokens || {};
  var C = { bg: T['--bg'], stage: T['--stage'], stage2: T['--stage-2'], ink: T['--ink'], muted: T['--muted'], faint: T['--faint'],
    line: T['--line'], accent: T['--accent'], soft: T['--accent-soft'], onAccent: T['--accent-ink'], warn: T['--warn'], warm: T.warm };
  var SERIF = T['--serif'], SANS = T['--sans'];
  var NS = 'http://www.w3.org/2000/svg', XL = 'http://www.w3.org/1999/xlink';
  var WHITE = 'rgb(255,255,255)';                                    // the phone screen and the half-white boxes
  var VW = 1000, VH = 1100;
  var uid = 0;

  /* ---------- small helpers (as in e78-explainer-r3) ---------- */
  function clamp(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }
  function p(t, a, d) { return clamp((t - a) / d); }
  function out(x) { return 1 - Math.pow(1 - x, 3); }
  function io(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
  function lerp(a, b, k) { return a + (b - a) * k; }
  function hex(c) {
    if (c.charAt(0) !== '#') return c.slice(4, -1).split(',').map(Number);
    return [parseInt(c.slice(1, 3), 16), parseInt(c.slice(3, 5), 16), parseInt(c.slice(5, 7), 16)];
  }
  function mix(a, b, k) {
    var x = hex(a), y = hex(b);
    return 'rgb(' + Math.round(lerp(x[0], y[0], k)) + ',' + Math.round(lerp(x[1], y[1], k)) + ',' + Math.round(lerp(x[2], y[2], k)) + ')';
  }
  function bump(x, a, b) { return x <= a || x >= b ? 0 : Math.sin(Math.PI * (x - a) / (b - a)); }
  function el(parent, tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }
  function set(e, attrs) { for (var k in attrs) e.setAttribute(k, attrs[k]); }
  function txt(parent, x, y, s, size, o) {                          // s may hold \n: one tspan per line, centred on y
    o = o || {};
    var lines = String(s).split('\n'), lh = size * (o.lh || 1.15);
    var e = el(parent, 'text', { x: x, y: y, 'font-family': o.serif ? SERIF : SANS, 'font-size': size,
      'font-weight': o.weight || 400, fill: o.fill || C.ink, 'text-anchor': o.anchor || 'middle',
      'dominant-baseline': 'central', 'font-style': o.italic ? 'italic' : 'normal' });
    if (lines.length === 1) { e.textContent = s; return e; }
    lines.forEach(function (l, i) { el(e, 'tspan', { x: x, y: y + (i - (lines.length - 1) / 2) * lh }, l); });
    return e;
  }
  function show(e, k, dy) { set(e, { opacity: k, transform: 'translate(0 ' + ((1 - k) * (dy == null ? 12 : dy)) + ')' }); }
  function svgIn(host) {
    host.innerHTML = '';
    return el(host, 'svg', { viewBox: '0 0 ' + VW + ' ' + VH, width: '100%', role: 'img', style: 'display:block' });
  }
  function drawLine(e, len, k) { set(e, { 'stroke-dasharray': len, 'stroke-dashoffset': len * (1 - k) }); }
  function arrowHead(parent, color, w) {
    return el(parent, 'path', { d: 'M -14 -9 L 0 0 L -14 9', fill: 'none', stroke: color, 'stroke-width': w || 4,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
  }
  function place(e, x, y, deg, k) { set(e, { transform: 'translate(' + x + ' ' + y + ') rotate(' + deg + ')', opacity: k == null ? 1 : k }); }
  function bars(parent, x, y, n, gap, w, fill) {                     // sound bars of a voice note
    var a = [];
    for (var i = 0; i < n; i++) a.push(el(parent, 'rect', { x: x + i * gap, y: y, width: w, height: 10, rx: w / 2, fill: fill }));
    return function (t, amp) {
      a.forEach(function (b, i) {
        var h = 10 + 46 * amp * Math.abs(Math.sin(t * 5.4 + i * 0.9)) * (0.5 + 0.5 * Math.sin(i * 1.9 + 1));
        set(b, { y: y - h / 2, height: h });
      });
    };
  }

  /* ---------- the loop of the agreed frames: seven stops on an oval, Jordi's day ---------- */
  var STOPS = [
    { id: 'say', label: 'I say it', me: 1 },
    { id: 'keep', label: 'Zenod\nkeeps it' },
    { id: 'hear', label: 'My team\nhears it' },
    { id: 'tickets', label: 'Desk writes\ntickets' },
    { id: 'work', label: 'Agents\nwork' },
    { id: 'ready', label: 'WhatsApp:\nready', me: 1 },
    { id: 'unblock', label: 'One tap\nto unblock', me: 1 }];
  var LX = 500, LY = 310, RX = 330, RY = 250, BW = 236, BH = 96;
  function ang(i) { return (-90 + i * 360 / 7) * Math.PI / 180; }
  function onOval(a) { return [LX + RX * Math.cos(a), LY + RY * Math.sin(a)]; }

  function loop(svg) {
    var L = { g: el(svg, 'g', {}) };
    el(L.g, 'ellipse', { cx: LX, cy: LY, rx: RX, ry: RY, fill: 'none', stroke: C.line, 'stroke-width': 3, 'stroke-dasharray': '2 14', 'stroke-linecap': 'round' });
    L.chev = el(L.g, 'g', {});
    for (var i = 0; i < 7; i++) {                                      // a chevron half-way between stops, pointing on
      var a = (ang(i) + ang(i + 1)) / 2, q = onOval(a), d = Math.atan2(RY * Math.cos(a), -RX * Math.sin(a)) * 180 / Math.PI;
      place(arrowHead(L.chev, C.faint, 4), q[0], q[1], d);
    }
    L.center = txt(L.g, LX, LY, 'Every day,\nthe wheel\nturns once.', 40, { serif: true, fill: C.muted });
    L.dot = el(L.g, 'circle', { r: 14, fill: C.accent, opacity: 0 });
    L.s = STOPS.map(function (s, i) {
      var q = onOval(ang(i)), g = el(L.g, 'g', {});
      var halo = el(g, 'rect', { x: q[0] - BW / 2 - 8, y: q[1] - BH / 2 - 8, width: BW + 16, height: BH + 16, rx: 20, fill: 'none', stroke: C.accent, 'stroke-width': 3, opacity: 0 });
      var r = el(g, 'rect', { x: q[0] - BW / 2, y: q[1] - BH / 2, width: BW, height: BH, rx: 14, 'stroke-width': 3 });
      var t = txt(g, q[0], q[1] + 1, s.label, 34, { weight: 500, lh: 1.08 });
      return { g: g, r: r, t: t, halo: halo, x: q[0], y: q[1], me: s.me };
    });
    // state of every stop: before the focus ink, the focus green as k goes 0 → 1, after it muted (as in the frames)
    L.state = function (focus, k) {
      L.s.forEach(function (q, i) {
        var base = q.me ? C.warm : mix(C.bg, WHITE, 0.5);
        var later = q.me ? mix(C.warm, C.stage, 0.55) : C.stage;
        var fill, stroke, ink;
        if (i < focus) { fill = base; stroke = C.ink; ink = C.ink; }
        else if (i === focus) { fill = mix(later, C.soft, k); stroke = mix(C.line, C.accent, k); ink = mix(C.muted, C.accent, k); }
        else { fill = later; stroke = C.line; ink = C.muted; }
        set(q.r, { fill: fill, stroke: stroke, 'stroke-width': i === focus ? 3 + 2 * k : 3 });
        set(q.t, { fill: ink });
      });
    };
    L.ring = function (i, k) {                                         // the focus pulses once
      set(L.s[i].halo, { opacity: k > 0 && k < 1 ? (1 - k) : 0, transform: 'translate(' + L.s[i].x + ' ' + L.s[i].y + ') scale(' + (1 + 0.25 * k) + ') translate(' + (-L.s[i].x) + ' ' + (-L.s[i].y) + ')' });
    };
    L.travel = function (from, to, k) {                                // the note travels along the oval
      var a0 = ang(from), a1 = ang(to); if (a1 < a0) a1 += 2 * Math.PI;
      var q = onOval(lerp(a0, a1, io(k)));
      set(L.dot, { cx: q[0], cy: q[1], opacity: k > 0 && k < 1 ? 1 : 0 });
    };
    return L;
  }

  // The usual frame: the loop on top (the note arrives at this stop, it lights up), the thing it made in a panel below.
  var PY = 640, PH = 440;
  function frameScene(o) {
    return { id: o.id, headline: o.headline, line: o.line, narration: o.narration, settle: o.settle, len: o.len || 7, label: o.label,
      build: function (svg) {
        var s = { L: loop(svg), i: STOPS.map(function (x) { return x.id; }).indexOf(o.id) };
        s.panel = el(svg, 'g', {});
        el(s.panel, 'rect', { x: 40, y: PY, width: 920, height: PH, rx: 18, fill: mix(C.bg, WHITE, 0.55), stroke: C.ink, 'stroke-width': 3 });
        if (o.meta) txt(s.panel, 84, PY + 52, o.meta, 34, { anchor: 'start', fill: C.muted });
        s.p = o.build ? o.build(s.panel, svg, s) : {};
        return s;
      },
      draw: function (s, t) {
        var prev = (s.i + 6) % 7;
        s.L.travel(prev, s.i, p(t, 0.05, 0.7));
        var lit = out(p(t, 0.6, 0.4));
        s.L.state(s.i, lit);
        s.L.ring(s.i, p(t, 0.6, 0.8));
        show(s.panel, out(p(t, 0.8, 0.45)), 24);
        if (o.draw) o.draw(s.p, t, s);
      } };
  }

  // A phone scene: the loop first (the note arrives), then we zoom into that stop and the real screen rises.
  var PHX = 150, PHW = 700, PHY = 70, SCR = 22;                      // phone frame; its bottom runs off the scene
  function phoneScene(o) {
    return { id: o.id, headline: o.headline, line: o.line, narration: o.narration, settle: o.settle, len: o.len || 8, label: o.label,
      build: function (svg) {
        var s = { L: loop(svg), i: STOPS.map(function (x) { return x.id; }).indexOf(o.id) };
        s.ph = el(svg, 'g', {});
        var cid = 'e84s12-scr-' + (++uid);
        var cp = el(el(s.ph, 'defs', {}), 'clipPath', { id: cid });
        var sw = PHW - 2 * SCR;
        el(cp, 'rect', { x: PHX + SCR, y: PHY + 70, width: sw, height: VH - PHY - 70 });
        el(s.ph, 'rect', { x: PHX, y: PHY, width: PHW, height: VH - PHY + 60, rx: 70, fill: C.ink });
        el(s.ph, 'rect', { x: PHX + PHW / 2 - 70, y: PHY + 26, width: 140, height: 26, rx: 13, fill: C.muted });
        s.scr = el(s.ph, 'g', { 'clip-path': 'url(#' + cid + ')' });
        el(s.scr, 'rect', { x: PHX + SCR, y: PHY + 70, width: sw, height: VH, fill: WHITE });
        s.k = sw / 780;                                                // screenshots are 780 px wide (390 CSS px at 2x)
        s.img = el(s.scr, 'image', { x: PHX + SCR, y: PHY + 70, width: sw, height: o.imgH * s.k, href: o.img, preserveAspectRatio: 'xMidYMin meet' });
        s.img.setAttributeNS(XL, 'xlink:href', o.img);
        s.tag = el(svg, 'g', {});
        var tw = o.tag.length * 19 + 60;
        el(s.tag, 'rect', { x: PHX + PHW - tw + 30, y: PHY - 34, width: tw, height: 64, rx: 32, fill: C.accent });
        txt(s.tag, PHX + PHW - tw / 2 + 30, PHY - 2, o.tag, 32, { fill: C.onAccent, weight: 600 });
        s.p = o.build ? o.build(svg, s) : {};
        return s;
      },
      draw: function (s, t) {
        var prev = (s.i + 6) % 7;
        s.L.travel(prev, s.i, p(t, 0.05, 0.6));
        s.L.state(s.i, out(p(t, 0.5, 0.35)));
        s.L.ring(s.i, p(t, 0.5, 0.7));
        var z = io(p(t, 0.95, 0.6)), q = s.L.s[s.i];                // zoom into the stop, the loop fades
        set(s.L.g, { opacity: 1 - z, transform: 'translate(' + q.x + ' ' + q.y + ') scale(' + (1 + 1.4 * z) + ') translate(' + (-q.x) + ' ' + (-q.y) + ')' });
        var r = out(p(t, 1.15, 0.7));
        set(s.ph, { opacity: clamp(r * 2), transform: 'translate(0 ' + (1 - r) * 700 + ')' });
        show(s.tag, out(p(t, 1.6, 0.4)), 10);
        if (o.draw) o.draw(s.p, t, s);
      } };
  }

  /* ---------- the landing view: zoomed out, one machine (Jordi's E84-A2 words) ---------- */
  var BX = 170, BWW = 790, ST = [{ y: 30, h: 210 }, { y: 300, h: 210 }, { y: 570, h: 210 }, { y: 840, h: 230 }];
  function machine(o) {
    // o.at: when each stage arrives (the voice line names them in order)
    return { id: o.id, headline: o.headline, line: o.line, narration: o.narration, settle: o.settle, len: o.len, label: o.label,
      build: function (svg) {
        var s = { st: [] };
        var words = [['My unstructured ideas', 'voice notes, whenever I think'], ['A plan with tickets', 'structured, ready to start'],
          ['A delivery engine', 'it works, again and again'], ['One channel back to me', '']];
        ST.forEach(function (b, i) {
          var g = el(svg, 'g', {});
          var r = el(g, 'rect', { x: BX, y: b.y, width: BWW, height: b.h, rx: 18, fill: i === 0 || i === 3 ? C.warm : mix(C.bg, WHITE, 0.5), stroke: C.ink, 'stroke-width': 3 });
          txt(g, BX + 36, b.y + 52, words[i][0], 48, { serif: true, anchor: 'start' });
          if (words[i][1]) txt(g, BX + 36, b.y + 104, words[i][1], 34, { anchor: 'start', fill: C.muted });
          s.st.push({ g: g, r: r });
        });
        // 1. ideas: loose voice notes drifting at odd angles
        s.ideas = [];
        var seeds = [[300, 204, -9], [430, 192, 7], [570, 210, -4], [710, 190, 11], [850, 206, -7]];
        seeds.forEach(function (q) {
          var g = el(s.st[0].g, 'g', {});
          el(g, 'rect', { x: -48, y: -20, width: 96, height: 40, rx: 20, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
          for (var b = 0; b < 4; b++) el(g, 'rect', { x: -22 + b * 13, y: b % 2 ? -11 : -6, width: 6, height: b % 2 ? 22 : 12, rx: 3, fill: C.ink });
          s.ideas.push({ g: g, x: q[0], y: q[1], a: q[2] });
        });
        // 2. tickets: snap into one neat row
        s.tk = [0, 1, 2, 3, 4].map(function (i) {
          var g = el(s.st[1].g, 'g', {});
          var r = el(g, 'rect', { x: -52, y: -30, width: 104, height: 60, rx: 8, 'stroke-width': 3 });
          el(g, 'rect', { x: -34, y: -12, width: 68, height: 7, rx: 3, fill: C.ink });
          el(g, 'rect', { x: -34, y: 6, width: 42, height: 7, rx: 3, fill: C.muted });
          return { g: g, r: r, x: 600 + i * 74 - 148 + (i - 2) * 50, y: 300 + 160 };
        });
        // 3. the engine: a small wheel that keeps turning
        s.wheel = el(s.st[2].g, 'g', {});
        el(s.wheel, 'circle', { cx: 0, cy: 0, r: 62, fill: 'none', stroke: C.accent, 'stroke-width': 6, 'stroke-dasharray': '70 27' });
        for (var k = 0; k < 4; k++) {
          var a = k * Math.PI / 2, c = arrowHead(s.wheel, C.accent, 6);
          place(c, 62 * Math.cos(a), 62 * Math.sin(a), k * 90 + 90);
        }
        s.wheelAt = [820, 570 + 105];
        // 4. what comes back: two chips
        s.chips = [['Delivered jobs', C.accent, C.onAccent], ['Open questions', C.bg, C.ink]].map(function (c, i) {
          var g = el(s.st[3].g, 'g', {});
          var w = 330, x = BX + 36 + i * (w + 30), y = 840 + 120;
          el(g, 'rect', { x: x, y: y, width: w, height: 80, rx: 40, fill: c[1], stroke: i ? C.ink : C.accent, 'stroke-width': 3 });
          txt(g, x + w / 2, y + 41, c[0], 36, { fill: c[2], weight: 600 });
          return g;
        });
        // arrows down between the stages, and the channel back up on the left
        s.down = [0, 1, 2].map(function (i) {
          var y0 = ST[i].y + ST[i].h + 6, y1 = ST[i + 1].y - 8, x = BX + BWW / 2;
          var ln = el(svg, 'line', { x1: x, y1: y0, x2: x, y2: y1, stroke: C.ink, 'stroke-width': 4 });
          return { ln: ln, hd: arrowHead(svg, C.ink), x: x, y0: y0, y1: y1 };
        });
        s.back = el(svg, 'path', { d: 'M ' + BX + ' ' + (ST[3].y + 115) + ' L 80 ' + (ST[3].y + 115) + ' L 80 ' + (ST[0].y + 105) + ' L ' + (BX - 8) + ' ' + (ST[0].y + 105),
          fill: 'none', stroke: C.accent, 'stroke-width': 6, 'stroke-linejoin': 'round' });
        s.backHd = arrowHead(svg, C.accent, 6);
        s.backT = txt(svg, 0, 0, 'back to me', 34, { fill: C.accent, weight: 600 });
        s.dot = el(svg, 'circle', { r: 14, fill: C.accent, opacity: 0 });
        return s;
      },
      draw: function (s, t) {
        var A = o.at;
        s.st.forEach(function (b, i) { show(b.g, out(p(t, A[i], 0.45)), 18); });
        var mess = 1 - io(p(t, A[1] + 0.1, 0.8));                       // the ideas drift until the plan takes them
        s.ideas.forEach(function (q, i) {
          var jx = 10 * Math.sin(t * 1.3 + i * 2.1), jy = 5 * Math.cos(t * 1.1 + i * 1.3);
          place(q.g, q.x + jx, q.y + jy, q.a + 4 * Math.sin(t * 0.9 + i), lerp(0.35, 1, mess));
        });
        s.tk.forEach(function (k, i) {
          var f = io(p(t, A[1] + 0.2 + i * 0.12, 0.5));
          place(k.g, lerp(BX + 300 + i * 60, 260 + i * 140, f), lerp(430 + (i % 2 ? -14 : 20), 458, f), lerp(i % 2 ? 12 : -10, 0, f), p(t, A[1] + 0.2 + i * 0.12, 0.15));
          var ok = p(t, A[1] + 0.8 + i * 0.1, 0.3);
          set(k.r, { fill: mix(C.bg, C.soft, ok), stroke: mix(C.ink, C.accent, ok) });
        });
        var spin = Math.max(0, t - A[2]);
        set(s.wheel, { transform: 'translate(' + s.wheelAt[0] + ' ' + s.wheelAt[1] + ') rotate(' + 80 * spin + ')' });
        s.chips.forEach(function (c, i) { show(c, out(p(t, A[3] + 0.3 + i * 0.35, 0.4)), 14); });
        s.down.forEach(function (d, i) {
          var k = out(p(t, A[i + 1] - 0.35, 0.35));
          drawLine(d.ln, d.y1 - d.y0, k);
          place(d.hd, d.x, d.y0 + (d.y1 - d.y0) * k, 90, k);
        });
        var b = io(p(t, A[4], 0.9)), len = 115 + (ST[3].y + 115 - ST[0].y - 105) + (BX - 88) + 90;
        drawLine(s.back, len, b);
        place(s.backHd, BX - 6, ST[0].y + 105, 0, p(t, A[4] + 0.8, 0.1));
        set(s.backT, { transform: 'translate(52 ' + ((ST[0].y + ST[3].y) / 2 + 110) + ') rotate(-90)', opacity: out(p(t, A[4] + 0.4, 0.4)) });
        // one dot walks the machine: down through the stages, then back up the channel
        var u = t - A[0] - 0.4, pos = null;
        if (u >= 0 && t < A[4] + 1.2) {
          var cy = [ST[0].y + 105, ST[1].y + 105, ST[2].y + 105, ST[3].y + 115];
          var seg = A[1] <= t ? (A[2] <= t ? (A[3] <= t ? 3 : 2) : 1) : 0;
          if (seg < 3) pos = [BX + BWW / 2, lerp(cy[seg], cy[seg + 1], io(p(t, A[seg + 1] - 0.5, 0.5)))];
          if (seg === 3) pos = t < A[4] ? [BX + BWW / 2, cy[3]] : (function () {
            var f = io(p(t, A[4], 0.9)), L1 = BX + BWW / 2 - 80, L2 = cy[3] - cy[0], L3 = BX - 80, d = f * (L1 + L2 + L3);
            if (d < L1) return [BX + BWW / 2 - d, cy[3]];
            if (d < L1 + L2) return [80, cy[3] - (d - L1)];
            return [80 + (d - L1 - L2), cy[0]];
          })();
        }
        set(s.dot, { cx: pos ? pos[0] : 0, cy: pos ? pos[1] : 0, opacity: pos ? 1 : 0 });
      } };
  }

  /* ---------- the scenes ---------- */
  var SCENES = [
    machine({ id: 'machine', headline: 'Unstructured ideas in. Delivered work out.',
      line: 'Zoom out from the wheel and it is one machine.',
      narration: 'Zoom out: one machine. Unstructured ideas go in, become a plan with tickets, get delivered again and again, and come back as jobs done and open questions.',
      at: [0.6, 2.7, 4.2, 5.8, 7.4], settle: 8.4, len: 11.5,
      label: 'Four stages stacked: my unstructured ideas, a plan with tickets, a delivery engine that keeps turning, and one channel back to me with delivered jobs and open questions; a dot walks down through them and back up to me.' }),

    frameScene({ id: 'say', headline: 'I say it once.', line: 'Pure voice. I just talk my mind.',
      narration: 'I just talk my mind, in one voice note.', settle: 2.4, meta: 'WhatsApp · today 20:15',
      label: 'The loop of seven stops, I say it lit; below, a voice note on WhatsApp at 20:15 with moving sound bars and my words.',
      build: function (g) {
        var s = {};
        el(g, 'rect', { x: 84, y: PY + 100, width: 832, height: 120, rx: 60, fill: C.warm, stroke: C.ink, 'stroke-width': 3 });
        el(g, 'path', { d: 'M 140 ' + (PY + 136) + ' L 140 ' + (PY + 184) + ' L 180 ' + (PY + 160) + ' Z', fill: C.ink });
        s.bars = bars(g, 214, PY + 160, 22, 26, 12, C.ink);
        txt(g, 870, PY + 160, '0:42', 32, { anchor: 'end', fill: C.muted });
        s.q = txt(g, 84, PY + 320, '“I dump ideas into my memory,\nwhich is Zenod.”', 44, { serif: true, anchor: 'start', italic: true, lh: 1.25 });
        return s;
      },
      draw: function (s, t) { s.bars(t, lerp(1, 0.25, p(t, 2.0, 0.6))); show(s.q, out(p(t, 1.3, 0.5)), 10); } }),

    frameScene({ id: 'keep', headline: 'My memory keeps every word.', line: 'Zenod writes it into my brain.',
      narration: 'Zenod keeps every word, in my memory.', settle: 2.4, meta: 'Zenod · my brain · 20:25',
      label: 'Zenod keeps it lit; below, a page in my brain filed under Zenod, the words typing themselves.',
      build: function (g) {
        var s = {};
        txt(g, 84, PY + 130, 'Filed under Zenod', 52, { serif: true, anchor: 'start' });
        s.l1 = txt(g, 84, PY + 220, '', 40, { anchor: 'start' });
        s.l2 = txt(g, 84, PY + 285, '', 40, { anchor: 'start' });
        s.chip = el(g, 'g', {});
        el(s.chip, 'rect', { x: 84, y: PY + 340, width: 300, height: 64, rx: 32, fill: C.soft, stroke: C.accent, 'stroke-width': 3 });
        txt(s.chip, 234, PY + 373, 'kept for good', 32, { fill: C.accent, weight: 600 });
        return s;
      },
      draw: function (s, t) {
        var a = 'Every word, as I said it.', b = 'The audio kept too.';
        s.l1.textContent = a.slice(0, Math.round(a.length * p(t, 1.0, 0.7)));
        s.l2.textContent = b.slice(0, Math.round(b.length * p(t, 1.6, 0.5)));
        show(s.chip, out(p(t, 2.0, 0.35)), 8);
      } }),

    phoneScene({ id: 'hear', headline: 'Then it tells whoever is listening.', line: 'My team is subscribed. Its desk reads the note.',
      narration: 'My team is listening, so its desk reads the note.', settle: 3.0, tag: 'Team desk', img: 'loop/shots/desk.jpg', imgH: 2339,
      label: 'My team hears it lit, then a phone rises with the real Team desk: my 20:15 voice note, word for word, scrolling to the desk’s answer.',
      draw: function (q, t, s) {                                     // hold on the voice note, then scroll to the desk's answer
        var maxY = 2339 * s.k - (VH - PHY - 70);
        set(s.img, { transform: 'translate(0 ' + (-maxY * io(p(t, 2.0, 0.9))) + ')' });
      } }),

    frameScene({ id: 'tickets', headline: 'The desk writes the tickets itself.', line: 'My talk turns into a ticketing system.',
      narration: 'The desk turns my talk into tickets, by itself.', settle: 2.5, meta: 'New ticket · from my voice note',
      label: 'Desk writes tickets lit; below, a new ticket drops in: explain the whole loop, very simply, and its status turns to ready.',
      build: function (g) {
        var s = {};
        s.card = el(g, 'g', {});
        el(s.card, 'rect', { x: 84, y: PY + 90, width: 832, height: 220, rx: 14, fill: C.bg, stroke: C.ink, 'stroke-width': 3 });
        txt(s.card, 124, PY + 160, 'Explain the whole loop,\nvery simply', 46, { serif: true, anchor: 'start', lh: 1.15 });
        txt(s.card, 124, PY + 272, 'Your words are in the ticket.', 34, { anchor: 'start', fill: C.muted });
        s.st = el(g, 'rect', { x: 84, y: PY + 340, width: 280, height: 66, rx: 33, 'stroke-width': 3 });
        s.stT = txt(g, 224, PY + 374, 'Draft', 34, { weight: 600 });
        return s;
      },
      draw: function (s, t) {
        var f = io(p(t, 0.95, 0.6));
        set(s.card, { transform: 'translate(0 ' + (1 - f) * -90 + ')', opacity: clamp(f * 2) });
        var r = out(p(t, 1.8, 0.4));
        set(s.st, { fill: mix(C.stage, C.accent, r), stroke: mix(C.line, C.accent, r) });
        s.stT.textContent = t >= 1.9 ? 'Ready to start' : 'New';
        set(s.stT, { fill: mix(C.muted, C.onAccent, r) });
      } }),

    frameScene({ id: 'work', headline: 'Everybody wakes and works, in order.', line: 'The wheel turns. Things get executed.',
      narration: 'Everybody wakes up and works, in order.', settle: 2.5, meta: 'Agent at work · 20:46',
      label: 'Agents work lit; below, one agent after another wakes, and a progress bar fills on this very video.',
      build: function (g) {
        var s = { who: [] };
        ['Manager', 'Agent', 'Agent', 'Tester'].forEach(function (n, i) {
          var x = 84 + i * 212, w = el(g, 'g', {});
          var r = el(w, 'rect', { x: x, y: PY + 100, width: 196, height: 84, rx: 42, 'stroke-width': 3 });
          var tt = txt(w, x + 98, PY + 143, n, 34, { weight: 500 });
          s.who.push({ r: r, t: tt });
        });
        txt(g, 84, PY + 250, 'This video is one of those tickets.', 40, { serif: true, anchor: 'start' });
        el(g, 'rect', { x: 84, y: PY + 320, width: 832, height: 30, rx: 15, fill: C.stage });
        s.bar = el(g, 'rect', { x: 84, y: PY + 320, width: 0, height: 30, rx: 15, fill: C.accent });
        return s;
      },
      draw: function (s, t) {
        s.who.forEach(function (w, i) {
          var a = out(p(t, 1.0 + i * 0.3, 0.3));
          set(w.r, { fill: mix(C.stage, C.soft, a), stroke: mix(C.line, C.accent, a) });
          set(w.t, { fill: mix(C.faint, C.accent, a) });
        });
        set(s.bar, { width: 832 * io(p(t, 1.2, 1.4)) });
      } }),

    frameScene({ id: 'ready', headline: 'WhatsApp tells me it is ready.', line: 'One message when there is something to check.',
      narration: 'Then WhatsApp tells me: it is ready to review.', settle: 2.3, meta: 'WhatsApp · from my team',
      label: 'WhatsApp ready lit; below, the phone buzzes and a green message slides in: this is there for you to review.',
      build: function (g) {
        var s = {};
        s.b = el(g, 'g', {});
        el(s.b, 'rect', { x: 84, y: PY + 110, width: 760, height: 200, rx: 26, fill: C.soft, stroke: C.accent, 'stroke-width': 3 });
        txt(s.b, 124, PY + 210, 'This is there for you to review:\nthe whole loop, explained simply.', 40, { anchor: 'start', fill: C.ink, lh: 1.3 });
        s.ts = txt(g, 840, PY + 350, '✓✓ 21:02', 32, { anchor: 'end', fill: C.muted });
        return s;
      },
      draw: function (s, t) {
        var f = out(p(t, 1.0, 0.5)), buzz = bump(t, 0.85, 1.25) * 8 * Math.sin(t * 90);
        set(s.b, { transform: 'translate(' + ((1 - f) * -160 + buzz) + ' 0)', opacity: f });
        set(s.ts, { opacity: out(p(t, 1.6, 0.3)) });
      } }),

    phoneScene({ id: 'unblock', headline: 'One inbox. One tap to unblock.', line: 'I leave a voice note. The wheel turns again.',
      narration: 'One inbox, one tap, one voice note. Unblocked.', settle: 3.0, tag: 'My inbox', img: 'loop/shots/inbox.jpg', imgH: 1130,
      label: 'One tap to unblock lit, then a phone rises with the real inbox, waiting on me; a finger taps Answer and a voice note goes in.',
      build: function (svg, s) {
        var q = {}, k = s.k, X = PHX + SCR, Y = PHY + 70;
        q.ax = X + 614 * k; q.ay = Y + 470 * k;                          // the Answer button on the real screen
        q.rip = el(svg, 'circle', { cx: q.ax, cy: q.ay, fill: 'none', stroke: C.accent, 'stroke-width': 6 });
        q.tip = el(svg, 'circle', { cx: q.ax, cy: q.ay, r: 26, fill: C.accent, opacity: 0 });
        q.note = el(svg, 'g', {});
        el(q.note, 'rect', { x: 230, y: 860, width: 540, height: 110, rx: 55, fill: C.accent });
        q.bars = bars(q.note, 300, 915, 12, 24, 10, C.onAccent);
        txt(q.note, 700, 915, 'sent', 34, { fill: C.onAccent, weight: 600 });
        return q;
      },
      draw: function (q, t) {
        var tap = p(t, 2.0, 0.7);
        set(q.rip, { r: lerp(20, 110, out(tap)), opacity: tap > 0 && tap < 1 ? 1 - tap : 0 });
        set(q.tip, { opacity: bump(t, 1.85, 2.3) });
        show(q.note, out(p(t, 2.5, 0.4)), 30);
        q.bars(t, lerp(1, 0.3, p(t, 2.9, 0.4)));
      } }),

    machine({ id: 'again', headline: 'Unstructured ideas in. Delivered work out.',
      line: 'Every day, the machine turns once more.',
      narration: 'Unstructured ideas in. Delivered work out.',
      at: [0, 0.35, 0.7, 1.05, 1.5], settle: 2.5, len: 7,
      label: 'The landing view again, quickly: ideas in, a plan with tickets, the delivery engine turning, and back to me.' })
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
    viewH: VH,
    intro: null,
    poster: 'machine',
    question: 'What happens after I send one voice note?',
    answer: 'Zoom out and it is one machine: my unstructured ideas go in, become a plan with tickets, a delivery engine works them again and again, and it all comes back to me as delivered jobs and open questions.',
    outro: { claim: 'Ideas in. Delivered jobs and open questions out.', narration: '', url: 'epicteam.app' },
    mount: mount, colors: C
  };
})(typeof window !== 'undefined' ? window : this);
