"""The Wealth Blueprint – Ep. 002 "Why Rich People Don't Work for Money" (mesma identidade do Ep. 001).
Uso: WORK=/root/work/ep2 python3 ep002_build.py frames 10 60 | shots | render
"""
import sys, os, math, random, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wb_engine as WB
from wb_engine import *  # noqa  (helpers, palette, shot, CX, CY, W, H)

T, Ee, WT = WB.T, WB.E, WB.WT
WB.CH.update({1: 'The time trap', 2: 'What the wealthy actually work for', 3: 'Your money can clock in',
             4: 'Leverage: do the work once', 5: 'How to start without quitting your job', 6: 'The real question'})
L, R = 170, W - 170          # margens pra layouts fora do centro


def half_panel(c, side, a=1.0):
    x = 0 if side == 'l' else W / 2
    gr = cairo.LinearGradient(x, 0, x + W / 2, 0)
    if side == 'l':
        gr.add_color_stop_rgba(0, 1, 1, 1, 0.035 * a); gr.add_color_stop_rgba(1, 1, 1, 1, 0.0)
    else:
        gr.add_color_stop_rgba(0, 1, 1, 1, 0.0); gr.add_color_stop_rgba(1, 1, 1, 1, 0.035 * a)
    c.set_source(gr); c.rectangle(x, 0, W / 2, H); c.fill()


def clock(c, x, y, r, hours, a=1.0, col=GOLD2):
    c.new_path(); c.set_source_rgba(*col, a); c.set_line_width(3); c.arc(x, y, r, 0, 2 * math.pi); c.stroke()
    for k in range(12):
        ang = k / 12 * 2 * math.pi
        line(c, x + math.cos(ang) * r * .82, y + math.sin(ang) * r * .82, x + math.cos(ang) * r * .92, y + math.sin(ang) * r * .92, col, a * .7, 2)
    ah = (hours % 12) / 12 * 2 * math.pi - math.pi / 2
    am = (hours % 1) * 2 * math.pi - math.pi / 2
    line(c, x, y, x + math.cos(ah) * r * .5, y + math.sin(ah) * r * .5, IVORY, a, 5)
    line(c, x, y, x + math.cos(am) * r * .75, y + math.sin(am) * r * .75, IVORY, a, 3)
    c.set_source_rgba(*col, a); c.arc(x, y, 6, 0, 6.3); c.fill()


# ======================================================== SCENE 1 — HOOK
@WB.shot(0.0, cam='still')
def s_alarm(c, g):
    a = ap(g, 0.3, 0.8)
    glow(c, CX, CY - 40, 420, GOLD, 0.10 * a)
    blink = 1 if int(g * 2) % 2 == 0 or g > 3.6 else 0.35
    text(c, '6:00', CX, CY + 60, 230, 'light', IVORY, a * blink)
    text(c, 'AM', CX + 330, CY + 60, 54, 'semi', GOLD2, a * blink, 'l')
    rtext(c, 'TWO PEOPLE. SAME ALARM.', CX, CY + 170, 22, 'semi', GOLD, g, 0.8, None, track=8)


def split_people(c, g, t0, labels, sub, dim_left=0.0, dim_right=0.0):
    a = ap(g, t0, 0.6)
    half_panel(c, 'l', a); half_panel(c, 'r', a)
    line(c, CX, 120, CX, H - 120, GOLD, 0.35 * a, 1.2)
    for k, side in enumerate(('l', 'r')):
        x = W * (0.25 if side == 'l' else 0.75)
        d = dim_left if side == 'l' else dim_right
        col = IVORY if side == 'l' else GOLD2
        glow(c, x, CY - 20, 260, GOLD, (0.05 if side == 'l' else 0.12) * a * (1 - d))
        person(c, x, CY + 140, 330, a * (1 - 0.6 * d), col, 0.08)
        text(c, labels[k], x, CY + 230, 34, 'serifm', col, a * (1 - 0.6 * d))
        if sub[k]:
            text(c, sub[k], x, CY + 280, 24, 'light', MUTED, a * (1 - 0.6 * d))


@WB.shot(T(1) - 0.4, trans='cut', cam='pull')
def s_both(c, g):
    split_people(c, g, T(1) - 0.4, ('Person A', 'Person B'), ('works hard', 'works hard'))
    # ten years later
    p = ap(g, T(2) - 0.1, 0.5)
    if p > 0:
        rrect(c, CX - 170, 150, 340, 70, 35); c.set_source_rgba(*GOLD, 0.95 * p); c.fill()
        text(c, '10 YEARS LATER', CX, 196, 24, 'bold', BG0, p, 'c', 4)
    sa = ap(g, T(2) + 0.6, 0.6)
    text(c, 'Same place.', W * 0.25, CY - 290, 42, 'serifi', MUTED, sa)
    sb = ap(g, WT(3, 'built') - 0.2, 0.6)
    text(c, 'Built something', W * 0.75, CY - 320, 42, 'serifi', GOLD2, sb)
    text(c, 'that pays them.', W * 0.75, CY - 268, 42, 'serifi', GOLD2, sb)
    if sb > 0:
        for k in range(6):   # coins flowing to B
            q = ((g * 0.6 + k / 6) % 1)
            c.set_source_rgba(*GOLD2, sb * math.sin(q * math.pi) * 0.9)
            c.arc(W * 0.75 + math.sin(k * 2.1) * 120, CY - 220 + q * 260, 9, 0, 6.3); c.fill()


@WB.shot(T(4) - 0.4, trans='cut', cam='push')
def s_notluck(c, g):
    for k, (wd, t) in enumerate((('Talent', WT(4, 'talent')), ('Luck', WT(4, 'luck')))):
        x = CX + (k - 0.5) * 520
        a = ap(g, t - 0.2, 0.5)
        text(c, wd, x, CY - 60, 92, 'serif', MUTED, a)
        strike(c, x, CY - 90, tw(c, wd, 'serif', 92) + 30, eio((g - t - 0.3) / 0.5), RED, a, 5)
    rtext(c, "It's what they were working for.", CX, CY + 130, 56, 'serifi', GOLD2, g, T(5) - 0.1, None)


@WB.shot(T(6) - 0.4, trans='cut', cam='still')
def s_poster(c, g):
    a = ap(g, T(6) - 0.2, 0.6)
    tilt = -0.035
    c.save(); c.translate(CX, CY - 20); c.rotate(tilt)
    pw, ph = 760, 520
    rrect(c, -pw / 2, -ph / 2, pw, ph, 6); c.set_source_rgba(0.09, 0.1, 0.13, a); c.fill()
    c.set_source_rgba(*GOLD, a * 0.6); c.set_line_width(2); rrect(c, -pw / 2 + 22, -ph / 2 + 22, pw - 44, ph - 44, 4); c.stroke()
    text(c, 'RICH PEOPLE', 0, -60, 66, 'serif', IVORY, a, 'c', 4)
    text(c, "DON'T WORK", 0, 30, 66, 'serif', IVORY, a, 'c', 4)
    text(c, 'FOR MONEY', 0, 120, 66, 'serif', GOLD2, a, 'c', 4)
    for px, py in ((-pw / 2 + 30, -ph / 2 + 30), (pw / 2 - 30, -ph / 2 + 30)):
        c.set_source_rgba(*GOLD, a); c.arc(px, py, 7, 0, 6.3); c.fill()
    c.restore()
    rtext(c, 'A motivational poster…', CX, H - 120, 34, 'serifi', MUTED, g, T(7), T(8) - 0.2)
    rtext(c, '…or a real financial principle?', CX, H - 120, 34, 'serifi', GOLD2, g, T(8), None)


@WB.shot(T(9) - 0.4, trans='cut', cam='push')
def s_three(c, g):
    items = [('paycheck', 'Your paycheck', 'briefcase'), ('time', 'Your time', 'clock'), ('future', 'Your future', 'compass')]
    for k, (wd, lab, ic) in enumerate(items):
        t = WT(9, wd) - 0.25
        x = CX + (k - 1) * 520
        a = ap(g, t, 0.5)
        if a <= 0:
            continue
        glass(c, x - 210, CY - 210, 420, 400, 26, a)
        if ic == 'clock':
            clock(c, x, CY - 50, 70, 6 + g * 0.2, a)
        else:
            icon(c, ic, x, CY - 50, 130, a, GOLD2, 2.4)
        text(c, lab, x, CY + 120, 38, 'serifm', IVORY, a)
    rtext(c, '…in a completely different way.', CX, H - 130, 34, 'serifi', MUTED, g, WT(9, 'completely') - 0.3, None)


TITLE_T = Ee(9) + 0.5


@WB.shot(TITLE_T)
def s_title(c, g):
    t0 = TITLE_T
    glow(c, CX, CY, 800, GOLD, 0.10 * ap(g, t0, 1.5))
    rtext(c, 'THE WEALTH BLUEPRINT', CX, CY - 200, 22, 'semi', GOLD, g, t0 + 0.2, None, track=10)
    rtext(c, 'EPISODE 002', CX, CY - 158, 18, 'med', MUTED, g, t0 + 0.4, None, track=8)
    rtext(c, 'Why Rich People', CX, CY - 30, 96, 'serif', IVORY, g, t0 + 0.6, None, rise=30)
    rtext(c, "Don't Work", CX, CY + 80, 96, 'serif', IVORY, g, t0 + 0.8, None, rise=30)
    rtext(c, 'FOR MONEY', CX, CY + 175, 54, 'semi', GOLD2, g, t0 + 1.1, None, track=18)
    gline(c, CX, CY + 220, 420, g, t0 + 1.4)


# ======================================================== SCENE 2 — TIME TRAP
@WB.shot(T(10) - 0.5, 1, cam='right')
def s_trade(c, g):
    # left: text, right: punch clock / time-for-money scale
    rtext(c, 'How most people earn', L, 300, 22, 'semi', GOLD, g, T(10), None, align='l', track=6)
    rtext(c, 'Time', L, 420, 110, 'serif', IVORY, g, T(11) - 0.1, None, align='l')
    rtext(c, 'for a paycheck', L, 520, 64, 'serifi', GOLD2, g, WT(11, 'paycheck') - 0.3, None, align='l')
    rtext(c, 'One hour of work. One hour of pay.', L, 640, 34, 'light', IVORY, g, T(12), None, align='l', amax=0.85)
    # scale
    a = ap(g, T(11) - 0.2, 0.6)
    bx, by = W * 0.72, CY + 40
    tilt = 0.0
    line(c, bx, by - 220, bx, by + 200, GOLD, a, 4)
    line(c, bx - 160, by + 200, bx + 160, by + 200, GOLD, a, 4)
    c.save(); c.translate(bx, by - 220); c.rotate(tilt)
    line(c, -260, 0, 260, 0, GOLD, a, 4)
    for sx, lab in ((-260, '1 hour'), (260, '$30')):
        line(c, sx, 0, sx - 60, 120, GOLD, a * .6, 2); line(c, sx, 0, sx + 60, 120, GOLD, a * .6, 2)
        c.set_source_rgba(*GOLD, a * 0.15); c.move_to(sx - 90, 120); c.line_to(sx + 90, 120); c.line_to(sx + 60, 150); c.line_to(sx - 60, 150); c.close_path(); c.fill()
        b = ap(g, WT(12, 'hour') - 0.2 if sx < 0 else WT(12, 'pay') - 0.2, 0.5)
        if sx < 0:
            clock(c, sx, 60, 40, 9 + g * 0.5, a * b)
        text(c, lab, sx, 105 if sx > 0 else 200, 40 if sx > 0 else 28, 'semi', GOLD2 if sx > 0 else IVORY, a * b)
    c.restore()


@WB.shot(T(13) - 0.4, 1, trans='cut', cam='push')
def s_salary(c, g):
    x0, y0 = CX - 600, 250
    rows = [(T(13) + 0.3, '$30', 'per hour'), (WT(14, '2') - 0.3, '× 2,080', 'hours a year'),
            (WT(14, 'roughly') - 0.1, '≈ $62,400', 'a year, before taxes')]
    for k, (t, big, sub) in enumerate(rows):
        a = ap(g, t, 0.5)
        y = y0 + k * 190
        if k == 2:
            glow(c, CX, y + 60, 380, GOLD, 0.16 * a)
            line(c, x0, y - 40, x0 + 1200, y - 40, IVORY, 0.3 * a, 1.5)
        text(c, big, x0 + 560, y + 70, 110 if k == 2 else 96, 'semi', GOLD2 if k == 2 else IVORY, a, 'r')
        text(c, sub, x0 + 620, y + 60, 38, 'light', MUTED if k < 2 else IVORY, a, 'l')
    rtext(c, "Honest work. Nothing wrong with it.", CX, H - 110, 34, 'serifi', MUTED, g, T(15), None)


@WB.shot(T(16) - 0.4, 1, trans='cut', cam='still')
def s_ring(c, g):
    # 24-hour ring filling; ceiling
    rx, ry, r = W * 0.34, CY + 10, 300
    a = ap(g, T(16) - 0.3, 0.6)
    c.new_path(); c.set_source_rgba(1, 1, 1, 0.06 * a); c.set_line_width(46); c.arc(rx, ry, r, 0, 2 * math.pi); c.stroke()
    p = eio((g - T(17) + 0.2) / 2.2)
    segs = [(8, (0.30, 0.34, 0.44), 'Sleep'), (9, GOLD, 'Work + commute'), (7, (0.45, 0.50, 0.60), 'Everything else')]
    st = -math.pi / 2; acc = 0
    for hrs, col, lab in segs:
        frac = hrs / 24
        e = st + frac * 2 * math.pi * clamp((p * 24 - acc) / hrs)
        if p * 24 > acc:
            c.new_path(); c.set_source_rgba(*col, a); c.arc(rx, ry, r, st, e); c.stroke()
            mid = st + frac * math.pi
            la = ap(g, T(17) + 0.4 + acc / 12, 0.4)
            text(c, f'{lab}', rx + math.cos(mid) * (r + 90), ry + math.sin(mid) * (r + 90), 24, 'med', IVORY, a * la)
        st += frac * 2 * math.pi; acc += hrs
    c.set_line_width(2)
    text(c, '24', rx, ry + 30, 120, 'light', IVORY, a)
    text(c, 'HOURS', rx, ry + 80, 22, 'semi', GOLD, a, 'c', 6)
    rtext(c, "There's a ceiling.", W * 0.72, CY - 160, 66, 'serif', IVORY, g, T(16) - 0.1, None)
    opts = [('Work more hours', WT(18, 'work') - 0.2), ('Ask for a raise', WT(18, 'raise') - 0.4), ('Get a better job', WT(18, 'better') - 0.3)]
    for k, (s, t) in enumerate(opts):
        b = ap(g, t, 0.4)
        y = CY - 40 + k * 80
        check(c, W * 0.60, y - 10, 20, b, clamp((g - t) / 0.5))
        text(c, s, W * 0.60 + 44, y, 34, 'light', IVORY, b, 'l')
    rtext(c, 'And you should.', W * 0.60, CY + 240, 34, 'serifi', GOLD2, g, T(19) - 0.1, None, align='l')


@WB.shot(T(20) - 0.4, 1, trans='cut', cam='left')
def s_presence(c, g):
    # income line that drops to zero when you stop
    x0, x1, base, top = 220, W - 220, CY + 260, CY - 160
    a = ap(g, T(20) - 0.3, 0.6)
    line(c, x0, base, x1, base, MUTED, 0.5 * a, 1.5)
    text(c, 'INCOME', x0, top - 40, 20, 'semi', MUTED, a, 'l', 4)
    stops = [(WT(21, 'sick'), 'sick'), (WT(21, 'stop'), 'stop'), (WT(21, 'break'), 'break')]
    p = clamp((g - T(20)) / (Ee(21) - T(20) + 0.5))
    c.set_source_rgba(*GOLD2, a); c.set_line_width(5)
    xs = lerp(x0, x1, p)
    n = 120
    gaps = [(0.34, 0.42), (0.58, 0.66), (0.80, 0.88)]
    c.move_to(x0, top)
    for k in range(1, n + 1):
        q = k / n
        xx = lerp(x0, x1, q)
        if xx > xs:
            break
        down = any(a_ <= q <= b_ for a_, b_ in gaps)
        c.line_to(xx, base if down else top)
    c.stroke()
    for k, (t, lab) in enumerate(stops):
        gx = lerp(x0, x1, (gaps[k][0] + gaps[k][1]) / 2)
        b = ap(g, t - 0.1, 0.4)
        text(c, lab.upper(), gx, base + 50, 24, 'bold', RED, b, 'c', 4)
    rtext(c, 'Your income is tied to your presence.', CX, 200, 46, 'serif', IVORY, g, T(20), None)
    rtext(c, 'When you stop, the money stops too.', CX, H - 90, 34, 'serifi', RED, g, WT(21, 'money') - 0.3, None)


@WB.shot(T(22) - 0.4, 1, trans='cut', cam='push')
def s_raise(c, g):
    rtext(c, 'Even a raise follows the same rule.', CX, 230, 46, 'serif', IVORY, g, T(22) - 0.1, None)
    a = ap(g, T(23) - 0.1, 0.6)
    runs(c, [('3% raise on $62,400', 'semi', 64, IVORY)], CX, CY - 40, a)
    b = ap(g, WT(23, 'less') - 0.2, 0.6)
    runs(c, [('= ', 'light', 64, IVORY), ('+$1,872', 'semi', 100, GOLD2), (' / year', 'light', 48, IVORY)], CX, CY + 100, b)
    cc = ap(g, T(24) + 0.6, 0.6)
    for k in range(40):
        x = CX - 590 + (k % 20) * 62
        y = CY + 210 + (k // 20) * 62
        clock(c, x, y, 22, 8 + k * 0.37, cc * 0.6, GOLD)
    rtext(c, '…and you still show up for every hour.', CX, H - 80, 30, 'serifi', MUTED, g, WT(24, 'every') - 0.5, None)


@WB.shot(T(25) - 0.4, 1, trans='cut', cam='still')
def s_trap(c, g):
    a = ap(g, T(25) - 0.2, 0.6)
    glow(c, CX, CY - 40, 520, RED, 0.08 * a)
    text(c, 'THE TIME TRAP', CX, CY + 10, 120, 'serif', IVORY, a, 'c', 10)
    gline(c, CX, CY + 60, 700, g, T(25) + 0.3, a, RED)
    para(c, "Time is the one resource you can't produce more of.", CX, CY + 170, 40, 'serifi', GOLD2, g, WT(26, 'time') - 0.3, None, 1400)


WB.chapter_card(2, Ee(26) + 0.5)


# ======================================================== SCENE 3 — OWNERSHIP
@WB.shot(T(27) - 0.5, 2, cam='push')
def s_shift(c, g):
    rtext(c, "Here's the shift.", CX, H - 90, 40, 'serifi', MUTED, g, T(27), T(28))
    split_people(c, g, T(28) - 0.2, ('Paycheck', 'Ownership'), ('works for income', 'works for assets'),
                 dim_left=ap(g, T(31) - 0.1, 0.8), dim_right=0)
    rtext(c, "They don't stop working.", W * 0.25, 230, 34, 'serifi', IVORY, g, T(28), None)
    rtext(c, 'The difference is what for.', W * 0.75, 230, 34, 'serifi', GOLD2, g, T(29), None)


@WB.shot(T(32) - 0.4, 2, trans='cut', cam='right')
def s_assets(c, g):
    rtext(c, 'OWNERSHIP OF ASSETS', L, 220, 24, 'semi', GOLD, g, T(32), None, align='l', track=8)
    para(c, 'Things that produce value without requiring your time every hour.', L, 300, 40, 'serifm', IVORY, g, WT(32, 'Things') - 0.2, None, 760, align='l')
    cards = [('Shares of companies', 'bolt', T(33)), ('A business with a team', 'briefcase', T(34)),
             ('Property that earns rent', 'house', T(35)), ('Products & ideas', 'compass', T(36))]
    for k, (lab, ic, t) in enumerate(cards):
        x = W * 0.58 + (k % 2) * 380
        y = 260 + (k // 2) * 360
        a = ap(g, t - 0.15, 0.5)
        if a <= 0:
            continue
        dy = (1 - eo((g - t) / 0.6)) * 30
        glass(c, x, y + dy, 340, 310, 24, a)
        if k == 0:   # mini chart icon
            c.set_source_rgba(*GOLD2, a); c.set_line_width(4)
            pts = [(x + 90, y + dy + 170), (x + 140, y + dy + 130), (x + 180, y + dy + 150), (x + 250, y + dy + 80)]
            c.move_to(*pts[0]); [c.line_to(*p) for p in pts[1:]]; c.stroke()
        else:
            icon(c, ic, x + 170, y + dy + 130, 120, a, GOLD2, 2.4)
        text(c, lab, x + 170, y + dy + 255, 28, 'med', IVORY, a)


@WB.shot(T(37) - 0.4, 2, trans='cut', cam='push')
def s_fed(c, g):
    rtext(c, 'FEDERAL RESERVE · SURVEY OF CONSUMER FINANCES', CX, 180, 20, 'semi', GOLD, g, T(37), None, track=5)
    rtext(c, 'Where the wealth sits', CX, 250, 52, 'serif', IVORY, g, T(38) - 0.3, None)
    x0, bw = 400, 1300
    rows = [('Wealthiest households', T(38) + 1.0, [(0.62, GOLD, 'Stocks & private businesses'), (0.38, (0.35, 0.40, 0.50), 'Homes, cars, savings')]),
            ('Most families', T(39), [(0.22, GOLD, ''), (0.78, (0.35, 0.40, 0.50), 'Home, car, savings account')])]
    for k, (lab, t, segs) in enumerate(rows):
        y = 420 + k * 230
        a = ap(g, t, 0.5)
        text(c, lab, x0, y - 20, 34, 'semi', IVORY, a, 'l')
        xx = x0
        for fr, col, sl in segs:
            p = eio((g - t - 0.2) / 1.0)
            w = bw * fr * p
            c.set_source_rgba(*col, 0.95 * a); c.rectangle(xx, y, w, 80); c.fill()
            if sl and p > 0.9:
                text(c, sl, xx + 24, y + 52, 24, 'semi', BG0 if col == GOLD else IVORY, a, 'l')
            xx += bw * fr * p
    text(c, 'Illustrative proportions showing the general pattern in the Federal Reserve data.', CX, H - 70, 20, 'light', MUTED, 0.75 * ap(g, T(38), 1))


@WB.shot(T(40) - 0.4, 2, trans='cut', cam='left')
def s_balance(c, g):
    rtext(c, 'Two balance sheets', CX, 170, 50, 'serif', IVORY, g, T(40) - 0.1, None)
    sheets = [(W * 0.27, 'LOOKS RICHER', [('Nice car', 'car', WT(41, 'car')), ('Nice phone', 'bolt', WT(41, 'phone')),
                                          ('House + big mortgage', 'house', WT(41, 'mortgage'))], IVORY),
              (W * 0.73, 'BUILDING MORE', [('Modest car', 'car', WT(42, 'modest')), ('Investments', 'compass', WT(42, 'investments')),
                                           ('…and growing', 'bolt', WT(42, 'growing'))], GOLD2)]
    for x, head, items, col in sheets:
        a = ap(g, items[0][2] - 0.6, 0.5)
        glass(c, x - 330, 250, 660, 640, 24, a)
        text(c, head, x, 320, 24, 'bold', col, a, 'c', 6)
        line(c, x - 270, 350, x + 270, 350, col, 0.3 * a, 1.5)
        for k, (lab, ic, t) in enumerate(items):
            b = ap(g, t - 0.2, 0.4)
            y = 450 + k * 140
            icon(c, ic, x - 200, y - 10, 70, b, col, 2.2)
            text(c, lab, x - 130, y, 34, 'light', IVORY, b, 'l')
        if col == GOLD2:
            p = eio((g - WT(42, 'growing')) / 2.0)
            c.set_source_rgba(*GOLD2, a); c.set_line_width(4)
            c.move_to(x - 260, 850)
            for k in range(41):
                q = k / 40 * p
                c.line_to(x - 260 + q * 520, 850 - (q ** 2) * 90)
            c.stroke()
    rtext(c, 'From the outside, the first looks richer.', W * 0.27, H - 70, 28, 'serifi', MUTED, g, T(43), None)
    rtext(c, 'On paper, the second is building more.', W * 0.73, H - 70, 28, 'serifi', GOLD2, g, T(44), None)


@WB.shot(T(45) - 0.4, 2, trans='cut', cam='still')
def s_use_grow(c, g):
    a = ap(g, T(45) - 0.2, 0.6)
    text(c, 'Things they', W * 0.3, CY - 40, 50, 'serif', MUTED, a)
    text(c, 'USE', W * 0.3, CY + 80, 130, 'serif', MUTED, a, 'c', 12)
    b = ap(g, T(46) - 0.2, 0.6)
    glow(c, W * 0.7, CY + 20, 380, GOLD, 0.15 * b)
    text(c, 'Things that can', W * 0.7, CY - 40, 50, 'serif', IVORY, b)
    text(c, 'GROW', W * 0.7, CY + 80, 130, 'serif', GOLD2, b, 'c', 12)
    line(c, CX, CY - 150, CX, CY + 150, GOLD, 0.35 * b, 1.2)


WB.chapter_card(3, Ee(46) + 0.5)


# ======================================================== SCENE 4 — MONEY CLOCKS IN
@WB.shot(T(47) - 0.5, 3, cam='pull')
def s_ep1(c, g):
    a = ap(g, T(47) - 0.3, 0.6)
    # thumbnail-like card of ep 001
    x, y, w, h = 200, 230, 820, 470
    glass(c, x, y, w, h, 20, a)
    text(c, 'EPISODE 001', x + 50, y + 70, 20, 'semi', GOLD, a, 'l', 6)
    text(c, 'The First', x + 50, y + 170, 64, 'serif', IVORY, a, 'l')
    text(c, '$100,000', x + 50, y + 290, 110, 'semi', GOLD2, a, 'l')
    text(c, 'Is the Hardest', x + 50, y + 370, 50, 'serif', IVORY, a, 'l')
    rtext(c, 'This is why', W * 0.73, CY - 60, 56, 'serif', IVORY, g, T(48), None)
    rtext(c, 'it matters.', W * 0.73, CY + 20, 56, 'serifi', GOLD2, g, T(48) + 0.4, None)
    rtext(c, 'Your money can start doing some of the work.', CX, H - 120, 36, 'serifi', IVORY, g, T(49), None, amax=0.9)


@WB.shot(T(50) - 0.4, 3, trans='cut', cam='push')
def s_timecard(c, g):
    rtext(c, 'Every dollar = a tiny employee', CX, 190, 52, 'serif', IVORY, g, T(50) - 0.1, None)
    # timecard
    a = ap(g, T(50) + 0.4, 0.6)
    x, y, w, h = CX - 560, 280, 1120, 560
    rrect(c, x, y, w, h, 18); c.set_source_rgba(0.93, 0.90, 0.82, 0.07 * a); c.fill()
    c.set_source_rgba(*GOLD, 0.6 * a); c.set_line_width(2); rrect(c, x, y, w, h, 18); c.stroke()
    text(c, 'TIME CARD · YOUR MONEY', x + 40, y + 60, 22, 'semi', GOLD, a, 'l', 5)
    rows = [('Needs a desk?', 'NO', WT(51, 'desk')), ('Takes vacations?', 'NO', WT(51, 'vacations')),
            ('Works while you sleep?', 'YES', WT(51, 'sleep'))]
    for k, (q, ans, t) in enumerate(rows):
        yy = y + 170 + k * 120
        b = ap(g, t - 0.4, 0.4)
        line(c, x + 40, yy + 40, x + w - 40, yy + 40, IVORY, 0.12 * a, 1)
        text(c, q, x + 60, yy, 40, 'light', IVORY, b, 'l')
        st = ap(g, t, 0.15)
        if st > 0:
            col = GOLD2 if ans == 'YES' else MUTED
            c.save(); c.translate(x + w - 200, yy - 14); c.rotate(-0.08); c.scale(1 + 0.4 * (1 - st), 1 + 0.4 * (1 - st))
            c.set_source_rgba(*col, st); c.set_line_width(4); rrect(c, -90, -40, 180, 64, 8); c.stroke()
            text(c, ans, 0, 10, 38, 'xb', col, st, 'c', 4)
            c.restore()
    # coins clocking in
    for k in range(5):
        q = ((g * 0.5 + k / 5) % 1)
        c.set_source_rgba(*GOLD2, a * 0.8 * math.sin(q * math.pi)); c.arc(x + w + 80, y + 40 + q * (h - 80), 12, 0, 6.3); c.fill()


@WB.shot(T(52) - 0.4, 3, trans='cut', cam='right')
def s_portfolio(c, g):
    a = ap(g, T(52) - 0.2, 0.6)
    # portfolio block (left) -> flow -> yearly income (right)
    lx = W * 0.27
    glow(c, lx, CY, 360, GOLD, 0.12 * a)
    text(c, 'PORTFOLIO', lx, CY - 140, 22, 'semi', GOLD, a, 'c', 6)
    v = 500000 * eio((g - T(52)) / 1.2)
    text(c, money(v), lx, CY - 30, 96, 'semi', IVORY, a)
    text(c, '4% hypothetical yield', lx, CY + 40, 30, 'light', MUTED, a)
    b = ap(g, WT(52, 'dividends') - 0.3, 0.6)
    for k in range(7):
        q = ((g * 0.45 + k / 7) % 1)
        c.set_source_rgba(*GOLD2, b * math.sin(q * math.pi)); c.arc(lerp(W * 0.43, W * 0.57, q), CY - 30 + math.sin(q * 6) * 8, 9, 0, 6.3); c.fill()
    rx = W * 0.73
    cc = ap(g, T(53) - 0.2, 0.6)
    glow(c, rx, CY, 360, GOLD, 0.18 * cc)
    text(c, 'PER YEAR', rx, CY - 140, 22, 'semi', GOLD, cc, 'c', 6)
    text(c, money(20000 * eio((g - T(53)) / 1.0)), rx, CY - 30, 110, 'semi', GOLD2, cc)
    text(c, '+0 hours of work', rx, CY + 40, 30, 'med', IVORY, ap(g, T(54) - 0.1, 0.5))
    rtext(c, 'Returns are never guaranteed. Dividends can be cut. Markets can fall. Taxes apply.', CX, H - 90, 26, 'light', MUTED, g, T(55), None)


@WB.shot(T(56) - 0.4, 3, trans='cut', cam='push')
def s_flip(c, g):
    rtext(c, 'Now flip the math.', CX, 190, 46, 'serifi', MUTED, g, T(56), None)
    a = ap(g, T(57) - 0.1, 0.5)
    runs(c, [('$62,400', 'semi', 84, IVORY), (' ÷ ', 'light', 84, MUTED), ('4%', 'semi', 84, IVORY)], CX, CY - 90, a)
    b = ap(g, WT(57, 'million') - 0.8, 0.7)
    glow(c, CX, CY + 60, 520, GOLD, 0.18 * b)
    runs(c, [('≈ ', 'light', 110, IVORY), ('$1,560,000', 'semi', 140, GOLD2)], CX, CY + 110, b)
    rtext(c, 'in assets to replace the salary (hypothetical)', CX, CY + 190, 30, 'light', MUTED, g, WT(57, 'assets') - 0.2, None)
    rtext(c, 'Enormous? Yes.', CX, H - 110, 40, 'serifi', IVORY, g, T(58), None)


@WB.shot(T(60) - 0.4, 3, trans='cut', cam='left')
def s_hours(c, g):
    # 40-hour week grid; asset income lights blocks
    rtext(c, 'Every asset replaces a piece of your work week.', CX, 180, 44, 'serif', IVORY, g, T(60) - 0.1, None)
    a = ap(g, T(60) + 0.4, 0.6)
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
    lit = int(40 * clamp((g - T(61)) / 9.0) * 0.25)
    for d in range(5):
        text(c, days[d], 360, 330 + d * 110, 22, 'semi', MUTED, a, 'r', 3)
        for hh in range(8):
            k = d * 8 + hh
            x = 400 + hh * 150
            y = 280 + d * 110
            on = k < lit
            rrect(c, x, y, 130, 80, 10)
            c.set_source_rgba(*(GOLD if on else (1, 1, 1)), (0.85 if on else 0.06) * a); c.fill()
    text(c, f'{lit} of 40 hours covered by assets', CX, H - 150, 32, 'semi', GOLD2, ap(g, T(61), 0.5))
    rtext(c, 'You don’t need all 40 to feel the difference.', CX, H - 90, 30, 'serifi', IVORY, g, T(62), None, amax=0.85)


@WB.shot(T(63) - 0.4, 3, trans='cut', cam='still')
def s_paysyou(c, g):
    rtext(c, 'But the principle is powerful.', CX, 260, 40, 'serifi', MUTED, g, T(63), None)
    a = ap(g, T(64) - 0.1, 0.6)
    glass(c, 200, 380, 700, 360, 26, a)
    clock(c, 550, 500, 70, 9 + g * 0.3, a, IVORY)
    text(c, 'Your job pays you for', 550, 640, 34, 'light', IVORY, a)
    text(c, 'your TIME', 550, 700, 50, 'serif', IVORY, a)
    b = ap(g, T(65) - 0.1, 0.6)
    glass(c, W - 900, 380, 700, 360, 26, b)
    glow(c, W - 550, 520, 220, GOLD, 0.2 * b)
    icon(c, 'shield', W - 550, 500, 120, b, GOLD2, 2.6)
    text(c, 'Your assets can pay you for', W - 550, 640, 34, 'light', IVORY, b)
    text(c, 'your OWNERSHIP', W - 550, 700, 50, 'serif', GOLD2, b)


WB.chapter_card(4, Ee(65) + 0.5)


# ======================================================== SCENE 5 — LEVERAGE
@WB.shot(T(66) - 0.5, 4, cam='push')
def s_leverage(c, g):
    a = ap(g, T(67) - 0.2, 0.7)
    # lever + fulcrum
    fx, fy = CX, CY + 220
    c.set_source_rgba(*GOLD, a); c.move_to(fx - 70, fy + 80); c.line_to(fx + 70, fy + 80); c.line_to(fx, fy); c.close_path(); c.fill()
    tilt = -0.18 * eio((g - T(67)) / 1.2)
    c.save(); c.translate(fx, fy); c.rotate(tilt)
    line(c, -620, 0, 620, 0, IVORY, a, 8)
    rrect(c, 520, -150, 200, 150, 10); c.set_source_rgba(*GOLD2, a * 0.9); c.fill()
    text(c, 'RESULTS', 620, -62, 26, 'bold', BG0, a, 'c', 3)
    person(c, -560, 0, 140, a, IVORY, 0.1)
    c.restore()
    rtext(c, 'Another reason the wealthy think differently…', CX, 170, 34, 'serifi', MUTED, g, T(66), None)
    rtext(c, 'LEVERAGE', CX, 330, 110, 'serif', GOLD2, g, T(67) - 0.1, None, track=20)


@WB.shot(T(68) - 0.4, 4, trans='cut', cam='right')
def s_once_many(c, g):
    # left: hour sold once; right: one -> many
    a = ap(g, T(68) - 0.2, 0.5)
    lx = W * 0.25
    text(c, 'HOURLY JOB', lx, 230, 22, 'semi', MUTED, a, 'c', 6)
    clock(c, lx, CY - 40, 80, 3 + g * 0.2, a, IVORY)
    line(c, lx, CY + 60, lx, CY + 200, IVORY, a * 0.7, 3)
    person(c, lx, CY + 360, 140, a, IVORY, 0.1)
    text(c, '1 hour → sold once', lx, H - 110, 34, 'med', IVORY, a)
    b = ap(g, T(69) - 0.1, 0.5)
    rx = W * 0.68
    text(c, 'BUILT ONCE', rx, 230, 22, 'semi', GOLD, b, 'c', 6)
    c.set_source_rgba(*GOLD2, b); rrect(c, rx - 70, CY - 110, 140, 140, 18); c.fill()
    text(c, '1×', rx, CY - 18, 54, 'xb', BG0, b)
    n = int(140 * clamp((g - T(71)) / 3.0)) + (8 if b > 0 else 0)
    rr = random.Random(3)
    for k in range(min(n, 148)):
        ang = rr.uniform(-math.pi * 0.95, math.pi * 0.95) + math.pi / 2
        dist = rr.uniform(170, 430)
        px, py = rx + math.cos(ang) * dist * 1.25, CY - 40 + math.sin(ang) * dist * 0.85
        if py > H - 140:
            continue
        line(c, rx, CY - 40, px, py, GOLD, 0.08 * b, 1)
        c.set_source_rgba(*IVORY, 0.85 * b); c.arc(px, py, 5, 0, 6.3); c.fill()
    labs = [('Software', WT(70, 'software')), ('A book', WT(70, 'book')), ('A course', WT(70, 'course')), ('A video', WT(70, 'video'))]
    for k, (s, t) in enumerate(labs):
        cc = ap(g, t - 0.15, 0.4)
        x = rx - 420 + k * 280
        rrect(c, x - 110, 130 - 40, 220, 60, 30); c.set_source_rgba(*GOLD, 0.15 * cc); c.fill()
        text(c, s, x, 130, 26, 'semi', GOLD2, cc)
    text(c, '1 person… or 100,000', rx, H - 110, 34, 'med', GOLD2, ap(g, WT(71, 'serve') - 0.2, 0.5))


@WB.shot(T(72) - 0.4, 4, trans='cut', cam='push')
def s_guide(c, g):
    a = ap(g, T(72) - 0.2, 0.6)
    # product card left
    x, y = 260, 260
    glass(c, x, y, 520, 600, 24, a)
    c.set_source_rgba(*GOLD, 0.9 * a); rrect(c, x + 150, y + 70, 220, 290, 10); c.fill()
    text(c, 'GUIDE', x + 260, y + 200, 40, 'serif', BG0, a)
    line(c, x + 190, y + 240, x + 330, y + 240, BG0, a * .6, 2)
    text(c, 'Digital guide', x + 260, y + 450, 38, 'serifm', IVORY, a)
    text(c, '$50', x + 260, y + 530, 64, 'semi', GOLD2, a)
    b = ap(g, T(73) - 0.1, 0.5)
    runs(c, [('$50', 'semi', 72, IVORY), (' × ', 'light', 72, MUTED), ('1,000', 'semi', 72, IVORY)], W * 0.66, CY - 80, b)
    sales = 50000 * eio((g - WT(73, '$50') - 0.2) / 1.6)
    glow(c, W * 0.66, CY + 60, 380, GOLD, 0.16 * b)
    text(c, money(sales), W * 0.66, CY + 90, 120, 'semi', GOLD2, b)
    text(c, 'in sales · hypothetical', W * 0.66, CY + 150, 28, 'light', MUTED, b)
    rtext(c, 'Most products need marketing, updates and support.', W * 0.66, H - 160, 28, 'light', IVORY, g, T(74), None, amax=0.85)
    rtext(c, 'But the structure is different from an hourly job.', W * 0.66, H - 110, 30, 'serifi', GOLD2, g, T(75), None)


@WB.shot(T(76) - 0.4, 4, trans='cut', cam='left')
def s_team(c, g):
    rtext(c, 'Leverage from people and capital', CX, 180, 48, 'serif', IVORY, g, T(76) - 0.1, None)
    a = ap(g, T(77) - 0.2, 0.5)
    person(c, CX, CY + 40, 190, a, GOLD2, 0.12)
    text(c, 'OWNER', CX, CY + 90, 22, 'bold', GOLD2, a, 'c', 5)
    for k in range(10):
        t = T(77) + 0.3 + k * 0.15
        b = ap(g, t, 0.3)
        ang = math.pi + k / 9 * math.pi
        px, py = CX + math.cos(ang) * 600, CY + 60 + math.sin(ang) * -300 * 0.0 + (0 if k in (0, 9) else 0)
        px = CX - 760 + k * 168
        py = CY + 330
        line(c, CX, CY + 100, px, py - 130, GOLD, 0.25 * b, 1.4)
        person(c, px, py, 110, b, IVORY, 0.06)
    text(c, '10 people × 8 hours = 80 hours a day', CX, H - 60, 30, 'semi', GOLD2, ap(g, WT(77, '8') - 0.2, 0.5))
    rtext(c, 'An investor isn’t limited to their own salary.', CX, 250, 30, 'serifi', MUTED, g, T(78), None)


@WB.shot(T(79) - 0.4, 4, trans='cut', cam='push')
def s_sell_build(c, g):
    rtext(c, 'Same hours. Different places.', CX, 220, 50, 'serif', IVORY, g, T(79), None)
    a = ap(g, T(80) - 0.1, 0.5)
    text(c, 'One sells', W * 0.3, CY + 40, 70, 'serif', MUTED, a)
    text(c, 'their time.', W * 0.3, CY + 130, 70, 'serif', MUTED, a)
    b = ap(g, T(81) - 0.1, 0.5)
    glow(c, W * 0.7, CY + 80, 360, GOLD, 0.16 * b)
    text(c, 'The other', W * 0.7, CY + 40, 70, 'serif', IVORY, b)
    text(c, 'multiplies it.', W * 0.7, CY + 130, 70, 'serifi', GOLD2, b)


WB.chapter_card(5, Ee(81) + 0.5)


# ======================================================== SCENE 6 — HOW TO START
@WB.shot(T(82) - 0.5, 5, cam='push')
def s_quit(c, g):
    a = ap(g, T(82) - 0.2, 0.6)
    text(c, 'Quit your job tomorrow?', CX, CY - 60, 76, 'serif', IVORY, a)
    b = ap(g, T(83) - 0.1, 0.25)
    if b > 0:
        s = 1 + 0.5 * (1 - eo((g - T(83)) / 0.25))
        c.save(); c.translate(CX, CY + 110); c.rotate(-0.08); c.scale(s, s)
        c.set_source_rgba(*RED, b); c.set_line_width(7); rrect(c, -140, -80, 280, 120, 12); c.stroke()
        text(c, 'NO', 0, 14, 96, 'xb', RED, b, 'c', 6)
        c.restore()
    rtext(c, 'For most people, the paycheck is the engine that makes ownership possible.', CX, H - 110, 32, 'serifi', GOLD2, g, T(84), None)


def step_tag(c, g, n, title, t0):
    a = ap(g, t0, 0.5)
    c.set_source_rgba(*GOLD, a); c.set_line_width(2); c.new_path(); c.arc(L + 34, 170, 34, 0, 6.3); c.stroke()
    text(c, f'{n:02d}', L + 34, 181, 28, 'semi', GOLD2, a)
    text(c, title, L + 94, 184, 44, 'serif', IVORY, a, 'l')


@WB.shot(T(86) - 0.4, 5, trans='cut', cam='right')
def s_step1(c, g):
    step_tag(c, g, 1, 'Buy ownership every month', T(86) - 0.3)
    # stacked area: contributions vs growth (300/mo, 20y, 7%)
    x0, x1, y0, y1 = 260, W - 260, H - 170, 300
    a = ap(g, T(88) - 0.3, 0.6)
    r = 0.07 / 12
    def bal(m): return 300 * ((1 + r) ** m - 1) / r
    vmax = bal(240)
    def X(m): return lerp(x0, x1, m / 240)
    def Y(v): return lerp(y0, y1, v / vmax)
    for v in (50000, 100000, 150000):
        line(c, x0, Y(v), x1, Y(v), MUTED, 0.12 * a, 1)
        text(c, f'${v // 1000}K', x0 - 16, Y(v) + 7, 20, 'reg', MUTED, a * .8, 'r')
    for yr in (0, 5, 10, 15, 20):
        text(c, f'Year {yr}', X(yr * 12), y0 + 40, 20, 'reg', MUTED, a * .8)
    p = eio((g - T(88)) / 6.0)
    head = 240 * p
    if head > 1:
        c.move_to(X(0), Y(0))
        for k in range(101):
            m = head * k / 100; c.line_to(X(m), Y(bal(m)))
        c.line_to(X(head), Y(0)); c.close_path()
        c.set_source_rgba(*GOLD, 0.40 * a); c.fill()
        c.move_to(X(0), Y(0))
        for k in range(101):
            m = head * k / 100; c.line_to(X(m), Y(300 * m))
        c.line_to(X(head), Y(0)); c.close_path()
        c.set_source_rgba(0.40, 0.45, 0.56, 0.9 * a); c.fill()
        c.move_to(X(0), Y(0))
        for k in range(101):
            m = head * k / 100; c.line_to(X(m), Y(bal(m)))
        c.set_source_rgba(*GOLD2, a); c.set_line_width(4); c.stroke()
        glow(c, X(head), Y(bal(head)), 50, GOLD2, 0.6 * a)
    b = ap(g, WT(88, 'roughly') - 0.2, 0.5)
    text(c, '≈ $156,278', X(240) - 10, Y(vmax) - 30, 44, 'semi', GOLD2, b, 'r')
    cc = ap(g, T(89) - 0.1, 0.5)
    text(c, 'You put in $72,000', X(150), Y(300 * 200) + 70, 28, 'semi', IVORY, cc)
    text(c, 'GROWTH', X(215), Y((bal(215) + 300 * 215) / 2) + 10, 26, 'bold', BG0, cc, 'c', 5)
    text(c, '$300/month · 20 years · 7% hypothetical average return · not guaranteed', CX, 260, 24, 'light', MUTED, a * 0.9)


@WB.shot(T(91) - 0.4, 5, trans='cut', cam='left')
def s_step2(c, g):
    step_tag(c, g, 2, 'Build one asset with your skills', T(91) - 0.3)
    opts = [('A small business', 'briefcase', WT(92, 'business')), ('A digital product', 'bolt', WT(92, 'digital')),
            ('A service that scales', 'compass', WT(92, 'service'))]
    for k, (lab, ic, t) in enumerate(opts):
        x = CX + (k - 1) * 520
        a = ap(g, t - 0.2, 0.5)
        glass(c, x - 220, 330, 440, 380, 24, a)
        icon(c, ic, x, 470, 130, a, GOLD2, 2.4)
        text(c, lab, x, 640, 34, 'serifm', IVORY, a)
    words = [('Start small.', T(93)), ('Learn how it works.', WT(93, 'Learn') - 0.1), ('Make it sustainable.', WT(93, 'sustainable') - 0.5)]
    for k, (s, t) in enumerate(words):
        text(c, s, CX + (k - 1) * 520, H - 140, 34, 'serifi', GOLD2, ap(g, t, 0.4))


@WB.shot(T(94) - 0.4, 5, trans='cut', cam='push')
def s_step3(c, g):
    step_tag(c, g, 3, 'Increase the value of your time', T(94) - 0.3)
    chain = [('Better skills', T(95)), ('Higher income', WT(95, 'higher') - 0.2), ('More assets', WT(95, 'assets', 0) - 0.4)]
    for k, (lab, t) in enumerate(chain):
        x = CX + (k - 1) * 560
        a = ap(g, t, 0.5)
        glow(c, x, CY, 200, GOLD, 0.12 * a)
        c.set_source_rgba(*GOLD, a); c.set_line_width(3); c.new_path(); c.arc(x, CY, 150, 0, 6.3); c.stroke()
        text(c, lab, x, CY + 12, 32, 'serifm', GOLD2 if k == 2 else IVORY, a)
        if k < 2:
            b = ap(g, chain[k + 1][1] - 0.3, 0.4)
            line(c, x + 170, CY, x + 380, CY, GOLD, b, 3)
            c.set_source_rgba(*GOLD, b); c.move_to(x + 380, CY - 12); c.line_to(x + 400, CY); c.line_to(x + 380, CY + 12); c.fill()


@WB.shot(T(96) - 0.4, 5, trans='cut', cam='still')
def s_warning(c, g):
    a = ap(g, T(96) - 0.1, 0.4)
    dy = (1 - eo((g - T(96)) / 0.5)) * -70
    x, y, w, h = CX - 520, CY - 220 + dy, 1040, 220
    rrect(c, x, y, w, h, 30); c.set_source_rgba(0.13, 0.14, 0.18, 0.96 * a); c.fill()
    text(c, 'GURU · SPONSORED', x + 44, y + 58, 20, 'semi', MUTED, a, 'l', 4)
    text(c, '“$10K/month passive income in 30 days.', x + 44, y + 120, 38, 'semi', IVORY, a, 'l')
    text(c, 'Guaranteed!”', x + 44, y + 172, 38, 'semi', IVORY, a, 'l')
    s = eio((g - WT(96, 'guaranteed') - 0.2) / 0.5)
    if s > 0:
        c.set_source_rgba(*RED, s); c.set_line_width(4); rrect(c, x, y, w, h, 30); c.stroke()
        cross(c, x + w - 70, y + 60, 20 * s, RED, a)
    rtext(c, 'Real ownership takes time to build.', CX, CY + 220, 56, 'serif', GOLD2, g, T(97) - 0.1, None)


WB.chapter_card(6, Ee(97) + 0.5)


# ======================================================== SCENE 7 — THE REAL QUESTION
@WB.shot(T(98) - 0.5, 6, cam='pull')
def s_question(c, g):
    WB.draw_sky(c, 'dawn', g, T(98) - 0.5, Ee(101) + 2, 1.12, 1.02, -0.4, 0.2)
    c.set_source_rgba(0, 0, 0, 0.42); c.paint()
    a = vis(g, T(98) - 0.1, T(100) - 0.3)
    text(c, 'Most people ask:', CX, CY - 120, 40, 'serifi', MUTED, a)
    text(c, '“How much do I make per hour?”', CX, CY - 20, 66, 'serif', IVORY, a * ap(g, T(99) - 0.1, 0.5))
    b = ap(g, T(100) - 0.1, 0.6)
    text(c, 'Wealthy people learn to ask:', CX, CY - 120, 40, 'serifi', GOLD, b)
    cc = ap(g, T(101) - 0.1, 0.7)
    glow(c, CX, CY, 600, GOLD, 0.14 * cc)
    text(c, '“What do I own that works,', CX, CY - 10, 70, 'serif', GOLD2, cc)
    text(c, 'even when I don’t?”', CX, CY + 80, 70, 'serif', GOLD2, cc)


@WB.shot(T(102) - 0.4, 6, trans='cut', cam='push')
def s_start_small(c, g):
    rtext(c, 'No mansion required.', CX, 220, 50, 'serif', IVORY, g, T(102), None)
    items = [('Your first share', WT(103, 'share') - 0.3, 'bolt'), ('Your first product', WT(103, 'product') - 0.3, 'briefcase'),
             ('Your first $100 invested', WT(103, '$100') - 0.4, 'compass')]
    for k, (lab, t, ic) in enumerate(items):
        x = CX + (k - 1) * 520
        a = ap(g, t, 0.5)
        glass(c, x - 220, 330, 440, 380, 24, a)
        icon(c, ic, x, 470, 120, a, GOLD2, 2.4)
        text(c, lab, x, 640, 32, 'serifm', IVORY, a)
    rtext(c, "The goal isn't to stop working.", CX, H - 170, 36, 'serifi', MUTED, g, T(104), None)
    rtext(c, 'It’s to stop depending only on your time.', CX, H - 110, 40, 'serif', GOLD2, g, T(105), None)


@WB.shot(T(106) - 0.4, 6, trans='cut', cam='still')
def s_ask(c, g):
    rtext(c, 'So let me ask you', CX, 260, 34, 'serifi', GOLD2, g, T(106), None)
    a = ap(g, T(107) - 0.1, 0.6)
    glow(c, CX, CY, 600, GOLD, 0.12 * a)
    text(c, 'What’s the first asset', CX, CY - 20, 90, 'serif', IVORY, a)
    text(c, 'you want to own?', CX, CY + 90, 90, 'serif', GOLD2, a)
    b = ap(g, T(108) - 0.2, 0.5)
    icon(c, 'chat', CX - 250, CY + 270, 70, b, GOLD2, 2.6)
    text(c, 'Tell me in the comments', CX + 50, CY + 282, 40, 'med', IVORY, b)


@WB.shot(T(109) - 0.4, 6)
def s_end(c, g):
    t0 = T(109) - 0.4
    a = ap(g, t0, 0.8)
    my = 220
    c.set_source_rgba(*GOLD, a); c.set_line_width(2)
    c.rectangle(CX - 46, my - 46, 92, 92); c.stroke(); c.rectangle(CX - 38, my - 38, 76, 76); c.stroke()
    text(c, 'WB', CX, my + 16, 40, 'serif', GOLD2, a)
    text(c, 'THE WEALTH BLUEPRINT', CX, my + 130, 44, 'serif', IVORY, a, 'c', 10)
    gline(c, CX, my + 170, 360, g, t0 + 0.4, a)
    b = ap(g, WT(109, 'subscribe') - 0.1, 0.6)
    pulse = 1 + 0.03 * math.sin(g * 5) * ap(g, WT(109, 'subscribe') + 0.5, 0.5)
    c.save(); c.translate(CX, my + 290); c.scale(pulse, pulse)
    rrect(c, -170, -42, 340, 84, 42); c.set_source_rgba(*GOLD, b); c.fill()
    text(c, 'SUBSCRIBE', 18, 11, 28, 'bold', BG0, b, 'c', 4)
    icon(c, 'bell', -110, 0, 36, b, BG0, 3)
    c.restore()
    rtext(c, 'Stories, strategies and lessons about building wealth.', CX, my + 410, 30, 'light', MUTED, g, WT(109, 'stories') - 0.2, None)
    rtext(c, 'Understand money. Build wealth.', CX, H - 150, 46, 'serifi', GOLD2, g, T(110) - 0.1, None)


if __name__ == '__main__':
    WB.main(sys.argv)
