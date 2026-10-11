#!/usr/bin/env python3
"""
MathQuest — Comprehensive Math Learning App for K-12 and Undergraduate
Built with PySide6
"""

import sys, json, os, random, math, time
from pathlib import Path
from datetime import datetime
from fractions import Fraction

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QStackedWidget,
    QProgressBar, QComboBox, QSpinBox, QRadioButton, QButtonGroup,
    QFrame, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QTimer, Signal, QRectF, QSize
from PySide6.QtGui import (
    QColor, QFont, QPainter, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPainterPath
)

# ──────────────────────────── THEME ────────────────────────────

THEME = {
    "primary": "#6366F1", "primary_light": "#818CF8", "primary_dark": "#4F46E5",
    "secondary": "#EC4899", "success": "#10B981", "warning": "#F59E0B",
    "error": "#EF4444", "info": "#3B82F6",
    "bg_main": "#F1F5F9", "bg_card": "#FFFFFF", "bg_sidebar": "#1E1B4B",
    "text_primary": "#1E293B", "text_secondary": "#64748B", "text_light": "#F8FAFC",
    "border": "#E2E8F0", "hover": "#EEF2FF",
}

LEVELS = {
    "elementary":    {"name": "Elementary (K‑5)",        "icon": "🌟", "color": "#10B981"},
    "middle_school": {"name": "Middle School (6‑8)",     "icon": "📚", "color": "#3B82F6"},
    "high_school":   {"name": "High School (9‑12)",      "icon": "🔬", "color": "#8B5CF6"},
    "undergraduate": {"name": "Undergraduate",           "icon": "🎓", "color": "#EC4899"},
}

TOPICS = {
    "elementary": [
        ("add_sub",      "Addition & Subtraction",   "➕"),
        ("mul_div",      "Multiplication & Division", "✖️"),
        ("fractions",    "Basic Fractions",           "🥧"),
        ("place_value",  "Place Value & Rounding",    "🔢"),
    ],
    "middle_school": [
        ("frac_dec",     "Fractions & Decimals",      "⅓"),
        ("ratios",       "Ratios & Proportions",      "⚖️"),
        ("algebra",      "Basic Algebra",             "🔤"),
        ("geometry",     "Geometry Basics",           "📐"),
    ],
    "high_school": [
        ("algebra2",     "Algebra II",                "📈"),
        ("trig",         "Trigonometry",              "📊"),
        ("geometry2",    "Geometry",                  "📏"),
        ("precalc",      "Precalculus",               "🔄"),
    ],
    "undergraduate": [
        ("derivatives",  "Calculus: Derivatives",     "∂"),
        ("integrals",    "Calculus: Integrals",       "∫"),
        ("linalg",       "Linear Algebra",            "🔲"),
        ("statistics",   "Probability & Statistics",  "🎲"),
    ],
}

SAVE_PATH = Path.home() / ".mathlearningapp" / "progress.json"

# ──────────────────────── PROBLEM GENERATOR ────────────────────

class ProblemGenerator:
    """Generates math problems for each level/topic/difficulty combination."""

    @staticmethod
    def generate(level: str, topic: str, difficulty: str) -> dict:
        key = f"_gen_{level}_{topic}"
        method = getattr(ProblemGenerator, key, None)
        if method:
            return method(difficulty)
        return ProblemGenerator._default()

    # ── helpers ──

    @staticmethod
    def _int_choices(answer, lo=None, hi=None):
        s = {answer}
        if lo is None: lo = max(0, answer - 15)
        if hi is None: hi = answer + 15
        offsets = [-3,-2,-1,1,2,3,5,10,-5,-10]
        random.shuffle(offsets)
        for o in offsets:
            w = answer + o
            if w >= 0 and w not in s: s.add(w)
            if len(s) >= 4: break
        while len(s) < 4:
            w = random.randint(lo, hi)
            if w not in s: s.add(w)
        r = sorted(s); random.shuffle(r)
        return [str(x) for x in r]

    @staticmethod
    def _float_choices(answer, decimals=2):
        s = {round(answer, decimals)}
        for o in [-2,-1,-0.5,0.5,1,2,3,5]:
            w = round(answer + o, decimals)
            if w >= 0 and w not in s: s.add(w)
            if len(s) >= 4: break
        while len(s) < 4:
            w = round(answer + random.uniform(-10, 10), decimals)
            if w >= 0 and w not in s: s.add(w)
        r = list(s); random.shuffle(r)
        return [str(x) for x in r]

    @staticmethod
    def _frac_choices(frac: Fraction):
        s = {frac}
        for o in [Fraction(1,2), Fraction(1,3), Fraction(1,4),
                   Fraction(-1,2), Fraction(2,1), Fraction(1,1)]:
            w = frac + o
            if w > 0 and w not in s and w.denominator <= 20: s.add(w)
            if len(s) >= 4: break
        while len(s) < 4:
            n = random.randint(1, 12); d = random.randint(2, 12)
            w = Fraction(n, d)
            if w not in s: s.add(w)
        r = list(s); random.shuffle(r)
        return [str(f) for f in r]

    @staticmethod
    def _default():
        return {"question":"1 + 1 = ?","answer":"2",
                "choices":["1","2","3","4"],
                "hint":"Think about counting.","explanation":"1 + 1 = 2"}

    # ═══════════════ ELEMENTARY ═══════════════

    @staticmethod
    def _gen_elementary_add_sub(diff):
        if diff == "easy":
            a, b = random.randint(1,20), random.randint(1,20)
        elif diff == "medium":
            a, b = random.randint(10,99), random.randint(10,99)
        else:
            a, b = random.randint(100,999), random.randint(100,999)
        op = random.choice(["+","−"])
        if op == "−" and a < b: a, b = b, a
        ans = a + b if op == "+" else a - b
        q = f"What is {a} {op} {b}?"
        return {"question":q,"answer":str(ans),
                "choices":ProblemGenerator._int_choices(ans),
                "hint":"Line up the numbers and work right to left.",
                "explanation":f"{a} {op} {b} = {ans}"}

    @staticmethod
    def _gen_elementary_mul_div(diff):
        if diff == "easy":
            a, b = random.randint(1,10), random.randint(1,10)
        elif diff == "medium":
            a, b = random.randint(2,12), random.randint(2,12)
        else:
            a, b = random.randint(10,25), random.randint(2,12)
        if random.random() < 0.5:
            ans = a * b
            q = f"What is {a} × {b}?"
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, 0, ans+20),
                    "hint":"Think of it as repeated addition.",
                    "explanation":f"{a} × {b} = {ans}"}
        else:
            ans = a; b2 = b; product = a * b
            q = f"What is {product} ÷ {b2}?"
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, 0, product),
                    "hint":"How many times does {b2} fit into {product}?".format(b2=b2,product=product),
                    "explanation":f"{product} ÷ {b2} = {ans}"}

    @staticmethod
    def _gen_elementary_fractions(diff):
        if diff == "easy":
            d = random.choice([2,3,4,5,6])
            n = random.randint(1, d-1)
            q = f"What is {n}/{d} of {d}?"
            ans = n
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,1,d+3),
                    "hint":f"Multiply {n}/{d} × {d}",
                    "explanation":f"{n}/{d} × {d} = {ans}"}
        elif diff == "medium":
            d = random.choice([4,5,6,8,10,12])
            n1 = random.randint(1, d-1); n2 = random.randint(1, d-1)
            s = n1 + n2
            q = f"What is {n1}/{d} + {n2}/{d}?"
            g = math.gcd(s, d)
            ans_str = f"{s//g}/{d//g}" if s != d else "1"
            ans_disp = f"{s}/{d}" if s != d else "1"
            choices = [ans_disp]
            for off in [1,2,-1]:
                w = s + off
                if 0 < w <= d*2:
                    g2 = math.gcd(abs(w), d)
                    ws = f"{w//g2}/{d//g2}" if w != d else "1"
                    choices.append(ws)
            while len(choices) < 4:
                w = random.randint(1, d*2)
                g2 = math.gcd(w, d)
                ws = f"{w//g2}/{d//g2}" if w != d else "1"
                if ws not in choices: choices.append(ws)
            random.shuffle(choices)
            return {"question":q,"answer":ans_disp,"choices":choices,
                    "hint":"Add the numerators, keep the denominator.",
                    "explanation":f"{n1}/{d} + {n2}/{d} = {n1+n2}/{d} = {ans_disp}"}
        else:
            d = random.choice([6,8,10,12])
            n = random.randint(1, d-1)
            q = f"Which fraction is equivalent to {n}/{d}?"
            m = random.randint(2,3)
            ans = f"{n*m}/{d*m}"
            choices = [ans]
            for _ in range(10):
                w = random.randint(1, d*3-1)
                g2 = math.gcd(w, d*3)
                ws = f"{w//g2}/{d*3//g2}"
                if ws not in choices and ws != ans: choices.append(ws)
                if len(choices) >= 4: break
            while len(choices) < 4:
                nd = random.randint(2,24); nn = random.randint(1,nd-1)
                ws = f"{nn}/{nd}"
                if ws not in choices: choices.append(ws)
            random.shuffle(choices)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"Multiply both numerator and denominator by the same number.",
                    "explanation":f"{n}/{d} = {n}×{m}/{d}×{m} = {ans}"}

    @staticmethod
    def _gen_elementary_place_value(diff):
        if diff == "easy":
            n = random.randint(10,99)
            q = f"Round {n} to the nearest ten."
            ans = round(n, -1)
        elif diff == "medium":
            n = random.randint(100,999)
            q = f"Round {n} to the nearest hundred."
            ans = round(n, -2)
        else:
            n = random.randint(1000,9999)
            q = f"Round {n} to the nearest thousand."
            ans = round(n, -3)
        return {"question":q,"answer":str(ans),
                "choices":ProblemGenerator._int_choices(ans, max(0,ans-1000), ans+1000),
                "hint":"Look at the digit one place to the right of the target place.",
                "explanation":f"Rounding {n} gives {ans}"}

    # ═══════════════ MIDDLE SCHOOL ═══════════════

    @staticmethod
    def _gen_middle_school_frac_dec(diff):
        if diff == "easy":
            d = random.choice([2,4,5,10,20,25,50])
            n = random.randint(1, d-1)
            f = Fraction(n, d)
            dec = float(f)
            q = f"Convert {n}/{d} to a decimal."
            ans = f"{dec:.2f}".rstrip('0').rstrip('.')
            choices = [ans]
            for o in [0.1,0.25,0.5,0.05,-0.1]:
                w = round(dec+o,4)
                if w >= 0: choices.append(f"{w:.2f}".rstrip('0').rstrip('.'))
            choices = list(dict.fromkeys(choices))[:4]
            while len(choices) < 4:
                w = round(random.uniform(0,2),2)
                ws = f"{w:.2f}".rstrip('0').rstrip('.')
                if ws not in choices: choices.append(ws)
            random.shuffle(choices)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"Divide the numerator by the denominator.",
                    "explanation":f"{n} ÷ {d} = {ans}"}
        elif diff == "medium":
            d1, d2 = random.choice([3,4,5,6]), random.choice([3,4,5,6])
            n1, n2 = random.randint(1,d1-1), random.randint(1,d2-1)
            f1, f2 = Fraction(n1,d1), Fraction(n2,d2)
            result = f1 + f2
            q = f"What is {n1}/{d1} + {n2}/{d2}?"
            ans = str(result)
            return {"question":q,"answer":ans,
                    "choices":ProblemGenerator._frac_choices(result),
                    "hint":"Find a common denominator, then add numerators.",
                    "explanation":f"{n1}/{d1} + {n2}/{d2} = {f1} + {f2} = {ans}"}
        else:
            d = random.choice([2,3,4,5,6,8])
            n = random.randint(1, d-1)
            f = Fraction(n, d)
            q = f"What is 1 − {n}/{d}?"
            result = Fraction(1,1) - f
            ans = str(result)
            return {"question":q,"answer":ans,
                    "choices":ProblemGenerator._frac_choices(result),
                    "hint":"Convert 1 to a fraction with the same denominator.",
                    "explanation":f"1 − {n}/{d} = {d}/{d} − {n}/{d} = {ans}"}

    @staticmethod
    def _gen_middle_school_ratios(diff):
        if diff == "easy":
            a, b = random.randint(2,10), random.randint(2,10)
            g = math.gcd(a,b)
            q = f"Simplify the ratio {a}:{b}."
            ans = f"{a//g}:{b//g}"
            choices = [ans]
            for m in [2,3]:
                w = f"{a*m}:{b*m}"
                if w != ans: choices.append(w)
            for _ in range(5):
                m = random.randint(1,5)
                w = f"{a//g*m}:{b//g*m}"
                if w not in choices: choices.append(w)
                if len(choices)>=4: break
            while len(choices)<4:
                w=f"{random.randint(1,10)}:{random.randint(1,10)}"
                if w not in choices: choices.append(w)
            random.shuffle(choices)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"Divide both numbers by their greatest common factor.",
                    "explanation":f"GCD({a},{b}) = {g}, so {a}:{b} = {a//g}:{b//g}"}
        elif diff == "medium":
            a, b = random.randint(2,8), random.randint(2,8)
            scale = random.randint(2,5)
            q = f"If the ratio is {a}:{b} and the first value is {a*scale}, what is the second?"
            ans = b * scale
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,1,ans+15),
                    "hint":"Multiply the second part of the ratio by the same scale factor.",
                    "explanation":f"Scale factor = {a*scale}/{a} = {scale}, so {b} × {scale} = {ans}"}
        else:
            a, b = random.randint(2,10), random.randint(2,10)
            unit = random.choice(["$","km","L","kg"])
            total = a * random.randint(2,6)
            q = f"If {a} items cost {unit}{total}, what is the unit rate per item?"
            ans = Fraction(total, a)
            ans_str = f"{unit}{float(ans):.2f}" if a != 1 else f"{unit}{total}"
            choices = [ans_str]
            for o in [0.5,1,2,-0.5,-1]:
                w = float(ans)+o
                if w>0: choices.append(f"{unit}{w:.2f}")
            choices = list(dict.fromkeys(choices))[:4]
            while len(choices)<4:
                w=random.uniform(0.5,float(ans)+5)
                ws=f"{unit}{w:.2f}"
                if ws not in choices: choices.append(ws)
            random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Divide total cost by the number of items.",
                    "explanation":f"{unit}{total} ÷ {a} = {ans_str}"}

    @staticmethod
    def _gen_middle_school_algebra(diff):
        if diff == "easy":
            x = random.randint(1,10); b = random.randint(1,20)
            a = random.randint(2,5)
            c = a*x + b
            q = f"Solve for x: {a}x + {b} = {c}"
            ans = x
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,0,20),
                    "hint":f"First subtract {b}, then divide by {a}.",
                    "explanation":f"{a}x = {c}-{b} = {c-b}, x = {c-b}/{a} = {ans}"}
        elif diff == "medium":
            x = random.randint(0,10); a = random.randint(2,6)
            b = random.randint(1,15); c = a*x + b
            q = f"Solve for x: {a}x + {b} = {c}"
            ans = x
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,0,25),
                    "hint":"Isolate x by undoing addition/subtraction first, then multiplication.",
                    "explanation":f"{a}x = {c-b}, x = {c-b}/{a} = {ans}"}
        else:
            x = random.randint(1,8); a = random.randint(2,5); b = random.randint(1,10)
            c = a*x - b
            q = f"Solve for x: {a}x - {b} = {c}"
            ans = x
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,0,20),
                    "hint":"Add b to both sides, then divide by a.",
                    "explanation":f"{a}x = {c+b}, x = {c+b}/{a} = {ans}"}

    @staticmethod
    def _gen_middle_school_geometry(diff):
        if diff == "easy":
            l, w = random.randint(3,15), random.randint(3,15)
            q = f"Find the area of a rectangle with length {l} and width {w}."
            ans = l * w
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, ans-10, ans+10),
                    "hint":"Area = length × width.",
                    "explanation":f"Area = {l} × {w} = {ans}"}
        elif diff == "medium":
            b, h = random.randint(3,15), random.randint(3,15)
            q = f"Find the area of a triangle with base {b} and height {h}."
            ans = Fraction(b*h, 2)
            ans_str = str(ans)
            if ans.denominator == 1: ans_str = str(ans.numerator)
            choices = [ans_str]
            for o in [1,2,3,-1]:
                w = b*h//2 + o
                choices.append(str(w))
            choices = list(dict.fromkeys(choices))[:4]
            while len(choices)<4:
                choices.append(str(random.randint(1,b*h)))
            random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Area = ½ × base × height.",
                    "explanation":f"Area = ½ × {b} × {h} = {ans_str}"}
        else:
            s = random.randint(2,10)
            q = f"Find the volume of a cube with side length {s}."
            ans = s**3
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, 1, ans+30),
                    "hint":"Volume = side³.",
                    "explanation":f"Volume = {s}³ = {ans}"}

    # ═══════════════ HIGH SCHOOL ═══════════════

    @staticmethod
    def _gen_high_school_algebra2(diff):
        # Quadratic: x² + bx + c = 0 with integer roots
        r1 = random.randint(-6,6); r2 = random.randint(-6,6)
        b_coeff = -(r1+r2); c_coeff = r1*r2
        if b_coeff > 0:
            eq = f"x² + {b_coeff}x + {c_coeff} = 0"
        elif b_coeff < 0:
            eq = f"x² − {abs(b_coeff)}x + {c_coeff} = 0"
        else:
            eq = f"x² + {c_coeff} = 0"
        if c_coeff < 0:
            eq = eq.replace(f"+ {c_coeff}", f"− {abs(c_coeff)}")

        if diff == "easy":
            q = f"Solve: {eq}.  What is one solution?"
            ans = r1
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,-10,10),
                    "hint":"Try plugging in integer values.",
                    "explanation":f"(x−{r1})(x−{r2})=0, so x={r1} or x={r2}"}
        else:
            q = f"Solve: {eq}.  What is the sum of the solutions?"
            ans = r1 + r2
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,-15,15),
                    "hint":"By Vieta's formulas, sum of roots = −b/a.",
                    "explanation":f"Sum of solutions = {r1} + {r2} = {ans}"}

    @staticmethod
    def _gen_high_school_trig(diff):
        common = {0:("0","0°"), 30:("1/2","30°"), 45:("√2/2","45°"),
                  60:("√3/2","60°"), 90:("1","90°")}
        angle = random.choice(list(common.keys()))
        val, label = common[angle]
        func = random.choice(["sin","cos"])
        if diff == "easy":
            q = f"What is {func}({label})?"
            if func == "sin":
                answers_map = {0:"0", 30:"1/2", 45:"√2/2", 60:"√3/2", 90:"1"}
            else:
                answers_map = {0:"1", 30:"√3/2", 45:"√2/2", 60:"1/2", 90:"0"}
            ans = answers_map[angle]
            all_vals = ["0","1/2","√2/2","√3/2","1"]
            choices = [ans]
            for v in all_vals:
                if v not in choices: choices.append(v)
            choices = choices[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"Recall the unit circle values.",
                    "explanation":f"{func}({label}) = {ans}"}
        else:
            opp = random.randint(1,10); adj = random.randint(1,10)
            hyp = math.sqrt(opp**2 + adj**2)
            q = f"In a right triangle with opposite = {opp} and adjacent = {adj}, what is tan(θ)?"
            f = Fraction(opp, adj)
            ans = str(f)
            return {"question":q,"answer":ans,
                    "choices":ProblemGenerator._frac_choices(f),
                    "hint":"tan(θ) = opposite / adjacent.",
                    "explanation":f"tan(θ) = {opp}/{adj} = {ans}"}

    @staticmethod
    def _gen_high_school_geometry2(diff):
        if diff == "easy":
            a, b = random.randint(3,12), random.randint(3,12)
            c_sq = a**2 + b**2
            c = math.sqrt(c_sq)
            q = f"In a right triangle with legs {a} and {b}, what is c²?"
            ans = c_sq
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, ans-20, ans+20),
                    "hint":"Use the Pythagorean theorem: a² + b² = c².",
                    "explanation":f"{a}² + {b}² = {a**2} + {b**2} = {ans}"}
        elif diff == "medium":
            r = random.randint(3,12)
            q = f"Find the area of a circle with radius {r}. (Use π ≈ 3.14, round to nearest integer)"
            ans = round(3.14 * r**2)
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, max(1,ans-30), ans+30),
                    "hint":"Area = π × r².",
                    "explanation":f"Area = 3.14 × {r}² = 3.14 × {r**2} ≈ {ans}"}
        else:
            r = random.randint(3,10)
            q = f"Find the circumference of a circle with radius {r}. (Use π ≈ 3.14)"
            ans = round(2 * 3.14 * r, 2)
            ans_str = f"{ans:.2f}"
            choices = [ans_str]
            for o in [3,6,-3,10]:
                w = round(ans+o,2)
                choices.append(f"{w:.2f}")
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Circumference = 2πr.",
                    "explanation":f"C = 2 × 3.14 × {r} = {ans_str}"}

    @staticmethod
    def _gen_high_school_precalc(diff):
        if diff == "easy":
            base = random.choice([2,3,5,10])
            exp = random.randint(1,4)
            val = base**exp
            q = f"Solve: log_{base}({val}) = ?"
            ans = exp
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,1,10),
                    "hint":"log_b(x) asks: b to what power equals x?",
                    "explanation":f"{base}^{exp} = {val}, so log_{base}({val}) = {ans}"}
        elif diff == "medium":
            a = random.randint(1,5); r = random.randint(2,4); n = random.randint(3,6)
            nth = a * r**(n-1)
            q = f"In a geometric sequence with a₁={a}, r={r}, find the {n}th term."
            ans = nth
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans, 1, ans+20),
                    "hint":"aₙ = a₁ × r^(n−1).",
                    "explanation":f"a_{n} = {a} × {r}^{n-1} = {a} × {r**(n-1)} = {ans}"}
        else:
            base = random.choice([2,3,10])
            x = random.randint(1,4)
            val = base**x
            q = f"What is log_{base}({val}) + log_{base}({base})?"
            ans = x + 1
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,1,ans+5),
                    "hint":"log_b(b) = 1, and use log addition rules.",
                    "explanation":f"log_{base}({val}) = {x}, log_{base}({base}) = 1, so {x}+1 = {ans}"}

    # ═══════════════ UNDERGRADUATE ═══════════════

    @staticmethod
    def _gen_undergraduate_derivatives(diff):
        if diff == "easy":
            n = random.randint(2,7)
            q = f"Find d/dx [x^{n}]."
            ans_str = f"{n}x^{n-1}" if n-1 != 1 else f"{n}x"
            if n-1 == 0: ans_str = str(n)
            choices = [ans_str]
            for off in [-1,1,2]:
                w_n = n + off
                if w_n >= 1:
                    w = f"{w_n}x^{w_n-1}" if w_n-1 != 1 else f"{w_n}x"
                    if w_n-1 == 0: w = str(w_n)
                    choices.append(w)
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Power rule: d/dx[xⁿ] = nxⁿ⁻¹.",
                    "explanation":f"d/dx[x^{n}] = {n}x^{n-1}"}
        elif diff == "medium":
            n = random.randint(2,5); a = random.randint(2,5)
            q = f"Find d/dx [{a}x^{n}]."
            coeff = a * n
            ans_str = f"{coeff}x^{n-1}" if n-1 != 1 else f"{coeff}x"
            if n-1 == 0: ans_str = str(coeff)
            choices = [ans_str]
            for off in [1,-1,2]:
                w = coeff + off
                ws = f"{w}x^{n-1}" if n-1!=1 else f"{w}x"
                if n-1==0: ws = str(w)
                choices.append(ws)
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Constant multiple rule + power rule.",
                    "explanation":f"d/dx[{a}x^{n}] = {a}·{n}x^{n-1} = {ans_str}"}
        else:
            n = random.randint(2,4)
            q = f"Find d/dx [sin(x^{n})]."
            ans_str = f"{n}x^{n-1}·cos(x^{n})" if n-1!=0 else f"cos(x^{n})"
            if n == 2: ans_str = f"{n}x·cos(x²)"
            choices = [ans_str]
            wrongs = [f"cos(x^{n})", f"{n}cos(x^{n})", f"x^{n-1}·cos(x^{n})", f"−{n}x^{n-1}·sin(x^{n})"]
            for w in wrongs:
                if w not in choices: choices.append(w)
            choices = choices[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Use the chain rule: d/dx[sin(u)] = cos(u)·u'.",
                    "explanation":f"Chain rule: cos(x^{n}) × {n}x^{n-1} = {ans_str}"}

    @staticmethod
    def _gen_undergraduate_integrals(diff):
        if diff == "easy":
            n = random.randint(1,5)
            q = f"Find ∫ x^{n} dx."
            d = n + 1
            ans_str = f"x^{d}/{d} + C"
            choices = [ans_str]
            for off in [1,-1,2]:
                wd = d + off
                if wd > 0: choices.append(f"x^{wd}/{wd} + C")
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Power rule: ∫xⁿ dx = xⁿ⁺¹/(n+1) + C.",
                    "explanation":f"∫x^{n} dx = x^{d}/{d} + C"}
        elif diff == "medium":
            a = random.randint(1,4); b = random.randint(1,5)
            q = f"Find ∫ ({a}x + {b}) dx."
            ax2 = Fraction(a,2)
            ax_str = f"{ax2}x²" if ax2.denominator != 1 else f"{ax2.numerator}x²"
            ans_str = f"{ax_str} + {b}x + C"
            choices = [ans_str]
            for off in [1,2,-1]:
                wa = Fraction(a+off,2)
                ws = f"{wa}x² + {b}x + C" if wa.denominator!=1 else f"{wa.numerator}x² + {b}x + C"
                choices.append(ws)
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Integrate term by term.",
                    "explanation":f"∫{a}x dx = {ax_str}, ∫{b} dx = {b}x, so {ans_str}"}
        else:
            n = random.randint(2,5)
            a = random.randint(1,3); b = random.randint(1,5)
            q = f"Evaluate ∫₀¹ {a}x^{n} dx."
            val = Fraction(a, n+1)
            ans = str(val)
            choices = [ans]
            for off in [Fraction(1,2), Fraction(1,3), Fraction(-1, n+1)]:
                w = val + off
                if w > 0: choices.append(str(w))
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"∫₀¹ xⁿ dx = 1/(n+1).",
                    "explanation":f"[{a}x^{n+1}/{n+1}]₀¹ = {a}/{n+1} = {ans}"}

    @staticmethod
    def _gen_undergraduate_linalg(diff):
        if diff == "easy":
            a,b,c,d = [random.randint(-5,5) for _ in range(4)]
            det = a*d - b*c
            q = f"Find the determinant of [[{a},{b}],[{c},{d}]]."
            ans = det
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,-30,30),
                    "hint":"det = ad − bc.",
                    "explanation":f"det = ({a})({d}) − ({b})({c}) = {a*d} − {b*c} = {ans}"}
        elif diff == "medium":
            a,b,c,d = [random.randint(-4,4) for _ in range(4)]
            det = a*d - b*c
            if det == 0:
                a,b,c,d = 2,1,1,3
                det = 5
            q = f"Find the determinant of [[{a},{b}],[{c},{d}]]. If A⁻¹ exists, what is det(A)?"
            ans = det
            return {"question":q,"answer":str(ans),
                    "choices":ProblemGenerator._int_choices(ans,-20,20),
                    "hint":"det(A⁻¹) = 1/det(A), but the question asks for det(A).",
                    "explanation":f"det(A) = ({a})({d}) − ({b})({c}) = {ans}"}
        else:
            a1,b1 = random.randint(1,5), random.randint(1,5)
            a2,b2 = random.randint(1,5), random.randint(1,5)
            c1 = a1+b1; c2 = a2+b2
            q = f"If A = [[{a1},{b1}],[{a2},{b2}]] and B = [[1,1],[1,1]], what is A+B?"
            r1a,r1b = a1+1,b1+1; r2a,r2b = a2+1,b2+1
            ans = f"[[{r1a},{r1b}],[{r2a},{r2b}]]"
            choices = [ans]
            for _ in range(5):
                o1,o2,o3,o4 = [random.randint(-2,2) for _ in range(4)]
                w = f"[[{r1a+o1},{r1b+o2}],[{r2a+o3},{r2b+o4}]]"
                if w not in choices: choices.append(w)
                if len(choices)>=4: break
            while len(choices)<4:
                w=f"[[{random.randint(1,7)},{random.randint(1,7)}],[{random.randint(1,7)},{random.randint(1,7)}]]"
                if w not in choices: choices.append(w)
            random.shuffle(choices)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"Add corresponding entries.",
                    "explanation":f"[{a1}+1, {b1}+1; {a2}+1, {b2}+1] = {ans}"}

    @staticmethod
    def _gen_undergraduate_statistics(diff):
        if diff == "easy":
            n = random.randint(4,6)
            data = sorted([random.randint(1,20) for _ in range(n)])
            mean = sum(data)/len(data)
            q = f"Find the mean of: {', '.join(map(str,data))}"
            ans = round(mean, 2)
            ans_str = f"{ans:.2f}"
            choices = [ans_str]
            for o in [0.5,1,1.5,-0.5]:
                w = round(ans+o,2)
                choices.append(f"{w:.2f}")
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"Mean = sum of values / number of values.",
                    "explanation":f"Sum = {sum(data)}, Mean = {sum(data)}/{n} = {ans_str}"}
        elif diff == "medium":
            n = random.randint(3,5)
            data = sorted([random.randint(1,10) for _ in range(n)])
            mean = sum(data)/len(data)
            variance = sum((x-mean)**2 for x in data)/len(data)
            std = math.sqrt(variance)
            q = f"Find the population standard deviation of: {', '.join(map(str,data))} (round to 2 decimals)."
            ans = round(std,2); ans_str = f"{ans:.2f}"
            choices = [ans_str]
            for o in [0.5,1,0.3]:
                w = round(std+o,2)
                choices.append(f"{w:.2f}")
            choices = list(dict.fromkeys(choices))[:4]; random.shuffle(choices)
            return {"question":q,"answer":ans_str,"choices":choices,
                    "hint":"σ = √(Σ(xᵢ−μ)²/N).",
                    "explanation":f"Mean={mean:.2f}, Variance={variance:.2f}, σ={ans_str}"}
        else:
            total = random.randint(10,50)
            favorable = random.randint(1, total-1)
            q = f"A bag has {favorable} red and {total-favorable} blue marbles. What is P(red)?"
            f = Fraction(favorable, total)
            ans = str(f)
            choices = ProblemGenerator._frac_choices(f)
            return {"question":q,"answer":ans,"choices":choices,
                    "hint":"P(red) = red marbles / total marbles.",
                    "explanation":f"P(red) = {favorable}/{total} = {ans}"}


# ─────────────────────── PROGRESS TRACKER ─────────────────────

class ProgressTracker:
    def __init__(self):
        self.data = {"total_attempted":0,"total_correct":0,"streak":0,
                     "best_streak":0,"history":[],"topics":{}}
        self._load()

    def _load(self):
        try:
            if SAVE_PATH.exists():
                with open(SAVE_PATH) as f:
                    saved = json.load(f)
                    self.data.update(saved)
        except Exception:
            pass

    def save(self):
        try:
            SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(SAVE_PATH,"w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def record_quiz(self, level, topic, difficulty, score, total, elapsed):
        self.data["total_attempted"] += total
        self.data["total_correct"] += score
        key = f"{level}_{topic}"
        if key not in self.data["topics"]:
            self.data["topics"][key] = {"attempted":0,"correct":0,"best_pct":0}
        t = self.data["topics"][key]
        t["attempted"] += total
        t["correct"] += score
        pct = round(score/total*100) if total else 0
        t["best_pct"] = max(t["best_pct"], pct)
        self.data["history"].append({
            "date": datetime.now().isoformat()[:19],
            "level":level,"topic":topic,"difficulty":difficulty,
            "score":score,"total":total,"pct":pct,"time":elapsed
        })
        if len(self.data["history"]) > 200:
            self.data["history"] = self.data["history"][-200:]
        self.save()

    def update_streak(self, correct):
        if correct:
            self.data["streak"] += 1
            self.data["best_streak"] = max(self.data["best_streak"], self.data["streak"])
        else:
            self.data["streak"] = 0
        self.save()

    @property
    def accuracy(self):
        if self.data["total_attempted"] == 0: return 0
        return round(self.data["total_correct"]/self.data["total_attempted"]*100,1)

    @property
    def total_quizzes(self):
        return len(self.data["history"])


# ──────────────────────── CUSTOM WIDGETS ──────────────────────

class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0; self._max = 100; self._label = ""
        self.setMinimumSize(180,180); self.setMaximumSize(220,220)

    def set_value(self, v, m=100, label=""):
        self._value = v; self._max = m; self._label = label; self.update()

    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(15,15,self.width()-30,self.height()-30)
        p.setPen(QPen(QColor(THEME["border"]),10)); p.drawArc(rect,0,360*16)
        if self._max > 0:
            frac = self._value/self._max
            color = QColor(THEME["success"]) if frac>=0.8 else (QColor(THEME["warning"]) if frac>=0.5 else QColor(THEME["error"]))
            p.setPen(QPen(color,10,Qt.SolidLine,Qt.RoundCap))
            p.drawArc(rect, 90*16, int(-frac*360*16))
        p.setPen(QColor(THEME["text_primary"]))
        p.setFont(QFont("Segoe UI",32,QFont.Bold))
        pct = int(self._value/self._max*100) if self._max else 0
        p.drawText(rect, Qt.AlignCenter, f"{pct}%")
        if self._label:
            p.setFont(QFont("Segoe UI",10)); p.setPen(QColor(THEME["text_secondary"]))
            r2 = QRectF(0, rect.bottom()-5, self.width(), 25)
            p.drawText(r2, Qt.AlignCenter, self._label)
        p.end()


class TopicCard(QFrame):
    clicked = Signal(str, str)  # level, topic_key

    def __init__(self, level, key, name, icon, color, parent=None):
        super().__init__(parent)
        self.level = level; self.key = key; self._color = color
        self.setFixedHeight(100); self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("topicCard")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16,12,16,12)
        top = QHBoxLayout()
        icon_lbl = QLabel(icon); icon_lbl.setFont(QFont("Segoe UI",24))
        top.addWidget(icon_lbl)
        name_lbl = QLabel(name); name_lbl.setFont(QFont("Segoe UI",13,QFont.Bold))
        name_lbl.setStyleSheet(f"color:{THEME['text_primary']};")
        name_lbl.setWordWrap(True)
        top.addWidget(name_lbl,1)
        lay.addLayout(top)
        self.setStyleSheet(f"""
            #topicCard {{ background:{THEME['bg_card']}; border:2px solid {THEME['border']};
                          border-radius:12px; }}
            #topicCard:hover {{ border-color:{color}; background:{THEME['hover']}; }}
        """)

    def mousePressEvent(self, e):
        self.clicked.emit(self.level, self.key)


class AnswerButton(QRadioButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI",13))
        self.setStyleSheet(f"""
            QRadioButton {{ spacing:10px; padding:12px 16px; color:{THEME['text_primary']};
                            background:{THEME['bg_card']}; border:2px solid {THEME['border']};
                            border-radius:10px; }}
            QRadioButton:hover {{ border-color:{THEME['primary']}; background:{THEME['hover']}; }}
            QRadioButton::indicator {{ width:18px; height:18px; }}
            QRadioButton::indicator:checked {{ border-color:{THEME['primary']}; }}
        """)


# ──────────────────────── PAGE WIDGETS ────────────────────────

class HomePage(QWidget):
    level_selected = Signal(str)
    progress_requested = Signal()

    def __init__(self, tracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        lay = QVBoxLayout(self); lay.setContentsMargins(40,30,40,30); lay.setSpacing(20)
        title = QLabel("🧮 MathQuest"); title.setFont(QFont("Segoe UI",36,QFont.Bold))
        title.setStyleSheet(f"color:{THEME['primary']};"); lay.addWidget(title)
        sub = QLabel("Your journey to math mastery starts here!")
        sub.setFont(QFont("Segoe UI",14)); sub.setStyleSheet(f"color:{THEME['text_secondary']};")
        lay.addWidget(sub); lay.addSpacing(10)

        grid = QGridLayout(); grid.setSpacing(16)
        for i, (key, info) in enumerate(LEVELS.items()):
            card = QFrame(); card.setObjectName("levelCard")
            card.setFixedHeight(130); card.setCursor(Qt.PointingHandCursor)
            cl = QVBoxLayout(card); cl.setContentsMargins(20,16,20,16)
            icon = QLabel(info["icon"]); icon.setFont(QFont("Segoe UI",32)); cl.addWidget(icon)
            name = QLabel(info["name"]); name.setFont(QFont("Segoe UI",13,QFont.Bold))
            name.setStyleSheet(f"color:{THEME['text_primary']};"); name.setWordWrap(True)
            cl.addWidget(name)
            card.setStyleSheet(f"""
                #levelCard {{ background:{THEME['bg_card']}; border:2px solid {THEME['border']};
                              border-radius:16px; }}
                #levelCard:hover {{ border-color:{info['color']}; transform:scale(1.02); }}
            """)
            card.mousePressEvent = lambda e, k=key: self.level_selected.emit(k)
            grid.addWidget(card, i//2, i%2)
        lay.addLayout(grid,1)

        # Stats bar
        stats = QFrame(); stats.setObjectName("statsBar")
        sl = QHBoxLayout(stats); sl.setContentsMargins(20,12,20,12)
        for label, val_func in [("Questions", lambda: str(self.tracker.data["total_attempted"])),
                                 ("Accuracy", lambda: f"{self.tracker.accuracy}%"),
                                 ("Best Streak", lambda: f"🔥 {self.tracker.data['best_streak']}"),
                                 ("Quizzes", lambda: str(self.tracker.total_quizzes))]:
            v = QLabel(val_func()); v.setFont(QFont("Segoe UI",16,QFont.Bold))
            v.setStyleSheet(f"color:{THEME['primary']};"); v.setAlignment(Qt.AlignCenter)
            l = QLabel(label); l.setFont(QFont("Segoe UI",10))
            l.setStyleSheet(f"color:{THEME['text_secondary']};"); l.setAlignment(Qt.AlignCenter)
            col = QVBoxLayout(); col.addWidget(v); col.addWidget(l); sl.addLayout(col)
        stats.setStyleSheet(f"#statsBar{{background:{THEME['bg_card']};border-radius:12px;border:1px solid {THEME['border']};}}")
        lay.addWidget(stats)

        pb = QPushButton("📊  View Detailed Progress")
        pb.setFont(QFont("Segoe UI",12)); pb.setCursor(Qt.PointingHandCursor)
        pb.setStyleSheet(f"""QPushButton{{background:{THEME['primary']};color:white;
            border:none;border-radius:10px;padding:12px 24px;}}
            QPushButton:hover{{background:{THEME['primary_dark']};}}""")
        pb.clicked.connect(self.progress_requested.emit); lay.addWidget(pb,0,Qt.AlignCenter)


class TopicPage(QWidget):
    topic_selected = Signal(str, str)
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._level = None
        self.lay = QVBoxLayout(self); self.lay.setContentsMargins(40,30,40,30); self.lay.setSpacing(16)
        self.header = QHBoxLayout()
        self.back_btn = QPushButton("← Back"); self.back_btn.setFont(QFont("Segoe UI",11))
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet(f"color:{THEME['primary']};background:transparent;border:none;padding:6px;")
        self.back_btn.clicked.connect(self.back_requested.emit)
        self.header.addWidget(self.back_btn)
        self.title_lbl = QLabel(); self.title_lbl.setFont(QFont("Segoe UI",28,QFont.Bold))
        self.title_lbl.setStyleSheet(f"color:{THEME['text_primary']};")
        self.header.addWidget(self.title_lbl,1); self.lay.addLayout(self.header)
        self.sub_lbl = QLabel("Choose a topic to practice:")
        self.sub_lbl.setFont(QFont("Segoe UI",12)); self.sub_lbl.setStyleSheet(f"color:{THEME['text_secondary']};")
        self.lay.addWidget(self.sub_lbl)
        self.grid = QGridLayout(); self.grid.setSpacing(16); self.lay.addLayout(self.grid,1)

    def set_level(self, level):
        self._level = level; info = LEVELS[level]
        self.title_lbl.setText(f"{info['icon']}  {info['name']}")
        # Clear grid
        while self.grid.count():
            item = self.grid.takeAt(0); w = item.widget()
            if w: w.deleteLater()
        for i, (key, name, icon) in enumerate(TOPICS[level]):
            color = info["color"]
            card = TopicCard(level, key, name, icon, color)
            card.clicked.connect(self.topic_selected.emit)
            self.grid.addWidget(card, i//2, i%2)


class QuizConfigPage(QWidget):
    start_quiz = Signal(str, str, str, int)  # level, topic, difficulty, num_q
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._level = ""; self._topic = ""
        lay = QVBoxLayout(self); lay.setContentsMargins(40,30,40,30); lay.setSpacing(20)
        lay.setAlignment(Qt.AlignCenter)

        card = QFrame(); card.setObjectName("configCard")
        cl = QVBoxLayout(card); cl.setContentsMargins(32,28,32,28); cl.setSpacing(18)
        self.back_btn2 = QPushButton("← Back"); self.back_btn2.setFont(QFont("Segoe UI",11))
        self.back_btn2.setCursor(Qt.PointingHandCursor)
        self.back_btn2.setStyleSheet(f"color:{THEME['primary']};background:transparent;border:none;padding:6px;")
        self.back_btn2.clicked.connect(self.back_requested.emit)
        cl.addWidget(self.back_btn2,0,Qt.AlignLeft)

        self.title_lbl = QLabel("Quiz Setup"); self.title_lbl.setFont(QFont("Segoe UI",26,QFont.Bold))
        self.title_lbl.setStyleSheet(f"color:{THEME['text_primary']};"); cl.addWidget(self.title_lbl)

        # Difficulty
        cl.addWidget(QLabel("Difficulty:"))
        self.diff_combo = QComboBox(); self.diff_combo.addItems(["Easy","Medium","Hard"])
        self.diff_combo.setFont(QFont("Segoe UI",12))
        self.diff_combo.setStyleSheet(f"padding:10px;border:2px solid {THEME['border']};border-radius:8px;")
        cl.addWidget(self.diff_combo)

        # Num questions
        cl.addWidget(QLabel("Number of Questions:"))
        self.num_spin = QSpinBox(); self.num_spin.setRange(5,30); self.num_spin.setValue(10)
        self.num_spin.setFont(QFont("Segoe UI",12))
        self.num_spin.setStyleSheet(f"padding:10px;border:2px solid {THEME['border']};border-radius:8px;")
        cl.addWidget(self.num_spin)

        self.start_btn = QPushButton("🚀  Start Quiz")
        self.start_btn.setFont(QFont("Segoe UI",14,QFont.Bold)); self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet(f"""QPushButton{{background:{THEME['primary']};color:white;
            border:none;border-radius:12px;padding:14px 32px;}}
            QPushButton:hover{{background:{THEME['primary_dark']};}}""")
        self.start_btn.clicked.connect(self._start)
        cl.addWidget(self.start_btn)

        card.setStyleSheet(f"#configCard{{background:{THEME['bg_card']};border-radius:20px;border:1px solid {THEME['border']};}}")
        card.setMaximumWidth(450); card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        lay.addWidget(card)

    def set_info(self, level, topic):
        self._level = level; self._topic = topic
        tname = dict(TOPICS[level]).get(topic, topic)
        self.title_lbl.setText(f"📝  {tname}")

    def _start(self):
        diff = self.diff_combo.currentText().lower()
        n = self.num_spin.value()
        self.start_quiz.emit(self._level, self._topic, diff, n)


class QuizPage(QWidget):
    quiz_finished = Signal(list, str, str, str, int, float)  # answers, level, topic, diff, total, elapsed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.problems = []; self.answers = []; self.current = 0
        self.start_time = 0; self.elapsed = 0
        self.timer = QTimer(); self.timer.setInterval(1000); self.timer.timeout.connect(self._tick)
        self.secs = 0

        lay = QVBoxLayout(self); lay.setContentsMargins(40,20,40,20); lay.setSpacing(12)

        # Top bar
        top = QHBoxLayout()
        self.qnum_lbl = QLabel(); self.qnum_lbl.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.qnum_lbl.setStyleSheet(f"color:{THEME['primary']};")
        top.addWidget(self.qnum_lbl)
        self.timer_lbl = QLabel("⏱ 0:00"); self.timer_lbl.setFont(QFont("Segoe UI",12))
        self.timer_lbl.setStyleSheet(f"color:{THEME['text_secondary']};")
        top.addWidget(self.timer_lbl,1,Qt.AlignRight)
        lay.addLayout(top)

        # Progress bar
        self.progress = QProgressBar(); self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8); self.progress.setStyleSheet(f"""
            QProgressBar{{background:{THEME['border']};border-radius:4px;border:none;}}
            QProgressBar::chunk{{background:{THEME['primary']};border-radius:4px;}}""")
        lay.addWidget(self.progress)

        # Score
        self.score_lbl = QLabel("Score: 0"); self.score_lbl.setFont(QFont("Segoe UI",11))
        self.score_lbl.setStyleSheet(f"color:{THEME['text_secondary']};")
        lay.addWidget(self.score_lbl)

        # Question area
        self.q_frame = QFrame(); self.q_frame.setObjectName("qFrame")
        ql = QVBoxLayout(self.q_frame); ql.setContentsMargins(24,20,24,20); ql.setSpacing(16)
        self.question_lbl = QLabel(); self.question_lbl.setFont(QFont("Segoe UI",18,QFont.Bold))
        self.question_lbl.setStyleSheet(f"color:{THEME['text_primary']};")
        self.question_lbl.setWordWrap(True); self.question_lbl.setAlignment(Qt.AlignCenter)
        ql.addWidget(self.question_lbl)

        self.choices_group = QButtonGroup(self); self.choice_btns = []
        for i in range(4):
            btn = AnswerButton(""); self.choices_group.addButton(btn,i)
            btn.setVisible(False); ql.addWidget(btn); self.choice_btns.append(btn)
        self.q_frame.setStyleSheet(f"#qFrame{{background:{THEME['bg_card']};border-radius:16px;border:1px solid {THEME['border']};}}")
        lay.addWidget(self.q_frame,1)

        # Feedback
        self.feedback_lbl = QLabel(); self.feedback_lbl.setFont(QFont("Segoe UI",12))
        self.feedback_lbl.setWordWrap(True); self.feedback_lbl.setAlignment(Qt.AlignCenter)
        self.feedback_lbl.setVisible(False); lay.addWidget(self.feedback_lbl)

        # Buttons
        btn_row = QHBoxLayout()
        self.hint_btn = QPushButton("💡 Hint"); self.hint_btn.setFont(QFont("Segoe UI",11))
        self.hint_btn.setCursor(Qt.PointingHandCursor)
        self.hint_btn.setStyleSheet(f"""QPushButton{{background:{THEME['warning']};color:white;
            border:none;border-radius:10px;padding:10px 20px;}}
            QPushButton:hover{{background:#D97706;}}""")
        self.hint_btn.clicked.connect(self._show_hint); btn_row.addWidget(self.hint_btn)
        btn_row.addStretch()
        self.submit_btn = QPushButton("Submit  →"); self.submit_btn.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        self.submit_btn.setStyleSheet(f"""QPushButton{{background:{THEME['primary']};color:white;
            border:none;border-radius:10px;padding:12px 28px;}}
            QPushButton:hover{{background:{THEME['primary_dark']};}}""")
        self.submit_btn.clicked.connect(self._submit); btn_row.addWidget(self.submit_btn)
        self.next_btn = QPushButton("Next  →"); self.next_btn.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setStyleSheet(f"""QPushButton{{background:{THEME['success']};color:white;
            border:none;border-radius:10px;padding:12px 28px;}}
            QPushButton:hover{{background:#059669;}}""")
        self.next_btn.clicked.connect(self._next); self.next_btn.setVisible(False)
        btn_row.addWidget(self.next_btn)
        lay.addLayout(btn_row)

        # Hint display
        self.hint_lbl = QLabel(); self.hint_lbl.setFont(QFont("Segoe UI",11))
        self.hint_lbl.setStyleSheet(f"color:{THEME['warning']};background:#FFFBEB;border-radius:8px;padding:10px;")
        self.hint_lbl.setWordWrap(True); self.hint_lbl.setVisible(False); lay.addWidget(self.hint_lbl)

    def start(self, problems, level, topic, diff):
        self.problems = problems; self.answers = []
        self.current = 0; self.score = 0; self.secs = 0
        self.start_time = time.time()
        self._level = level; self._topic = topic; self._diff = diff
        self.timer.start(); self._show_question()

    def _show_question(self):
        p = self.problems[self.current]
        self.qnum_lbl.setText(f"Question {self.current+1}/{len(self.problems)}")
        self.progress.setValue(int((self.current)/len(self.problems)*100))
        self.question_lbl.setText(p["question"])
        self.feedback_lbl.setVisible(False); self.hint_lbl.setVisible(False)
        self.submit_btn.setVisible(True); self.next_btn.setVisible(False)
        self.hint_btn.setEnabled(True)
        for i, btn in enumerate(self.choice_btns):
            if i < len(p["choices"]):
                btn.setText(p["choices"][i]); btn.setVisible(True); btn.setChecked(False)
                btn.setEnabled(True)
                btn.setStyleSheet(f"""
                    QRadioButton {{ spacing:10px; padding:12px 16px; color:{THEME['text_primary']};
                                    background:{THEME['bg_card']}; border:2px solid {THEME['border']};
                                    border-radius:10px; }}
                    QRadioButton:hover {{ border-color:{THEME['primary']}; background:{THEME['hover']}; }}
                """)
            else:
                btn.setVisible(False)

    def _submit(self):
        checked = self.choices_group.checkedId()
        if checked < 0:
            return
        p = self.problems[self.current]
        chosen = self.choice_btns[checked].text()
        correct = chosen == p["answer"]
        if correct: self.score += 1
        self.answers.append({"chosen":chosen,"correct":correct,"problem":p})
        self.score_lbl.setText(f"Score: {self.score}/{self.current+1}")
        # Show feedback
        for btn in self.choice_btns:
            btn.setEnabled(True)
            if btn.text() == p["answer"]:
                btn.setStyleSheet(f"""
                    QRadioButton {{ spacing:10px; padding:12px 16px; color:white;
                                    background:{THEME['success']}; border:2px solid {THEME['success']};
                                    border-radius:10px; font-weight:bold; }}
                """)
            elif btn.text() == chosen and not correct:
                btn.setStyleSheet(f"""
                    QRadioButton {{ spacing:10px; padding:12px 16px; color:white;
                                    background:{THEME['error']}; border:2px solid {THEME['error']};
                                    border-radius:10px; }}
                """)
            btn.setEnabled(False)
        if correct:
            self.feedback_lbl.setStyleSheet(f"color:{THEME['success']};font-weight:bold;font-size:14px;")
            self.feedback_lbl.setText("✅ Correct!")
        else:
            self.feedback_lbl.setStyleSheet(f"color:{THEME['error']};font-weight:bold;font-size:14px;")
            self.feedback_lbl.setText(f"❌ The answer is {p['answer']}")
        self.feedback_lbl.setVisible(True)
        self.submit_btn.setVisible(False)
        self.next_btn.setVisible(True)
        self.next_btn.setText("Finish  ✓" if self.current == len(self.problems)-1 else "Next  →")
        self.hint_btn.setEnabled(False)

    def _next(self):
        self.current += 1
        if self.current >= len(self.problems):
            self.timer.stop(); self.elapsed = time.time() - self.start_time
            self.quiz_finished.emit(self.answers, self._level, self._topic, self._diff, len(self.problems), self.elapsed)
        else:
            self._show_question()

    def _show_hint(self):
        p = self.problems[self.current]
        self.hint_lbl.setText(f"💡 {p['hint']}")
        self.hint_lbl.setVisible(True)
        self.hint_btn.setEnabled(False)

    def _tick(self):
        self.secs += 1
        m, s = divmod(self.secs, 60)
        self.timer_lbl.setText(f"⏱ {m}:{s:02d}")


class ResultsPage(QWidget):
    home_requested = Signal()
    retry_requested = Signal()

    def __init__(self, tracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker; self._level = ""; self._topic = ""; self._diff = ""; self._num = 10
        lay = QVBoxLayout(self); lay.setContentsMargins(40,30,40,30); lay.setSpacing(20)
        lay.setAlignment(Qt.AlignCenter)

        card = QFrame(); card.setObjectName("resCard")
        cl = QVBoxLayout(card); cl.setContentsMargins(32,28,32,28); cl.setSpacing(16)
        cl.setAlignment(Qt.AlignCenter)

        self.title = QLabel("Quiz Complete! 🎉"); self.title.setFont(QFont("Segoe UI",28,QFont.Bold))
        self.title.setStyleSheet(f"color:{THEME['primary']};"); self.title.setAlignment(Qt.AlignCenter)
        cl.addWidget(self.title)

        self.circle = CircularProgress(); cl.addWidget(self.circle,0,Qt.AlignCenter)

        self.detail_lbl = QLabel(); self.detail_lbl.setFont(QFont("Segoe UI",14))
        self.detail_lbl.setStyleSheet(f"color:{THEME['text_secondary']};")
        self.detail_lbl.setAlignment(Qt.AlignCenter); self.detail_lbl.setWordWrap(True)
        cl.addWidget(self.detail_lbl)

        # Review section
        self.review_area = QScrollArea(); self.review_area.setWidgetResizable(True)
        self.review_area.setMaximumHeight(250)
        self.review_widget = QWidget(); self.review_lay = QVBoxLayout(self.review_widget)
        self.review_lay.setSpacing(8)
        self.review_area.setWidget(self.review_widget)
        self.review_area.setStyleSheet(f"QScrollArea{{border:1px solid {THEME['border']};border-radius:8px;}}")
        cl.addWidget(self.review_area)

        btn_row = QHBoxLayout()
        self.retry_btn = QPushButton("🔄  Try Again"); self.retry_btn.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.retry_btn.setCursor(Qt.PointingHandCursor)
        self.retry_btn.setStyleSheet(f"""QPushButton{{background:{THEME['primary']};color:white;
            border:none;border-radius:10px;padding:12px 24px;}}
            QPushButton:hover{{background:{THEME['primary_dark']};}}""")
        self.retry_btn.clicked.connect(self.retry_requested.emit)
        btn_row.addWidget(self.retry_btn)
        self.home_btn = QPushButton("🏠  Home"); self.home_btn.setFont(QFont("Segoe UI",12,QFont.Bold))
        self.home_btn.setCursor(Qt.PointingHandCursor)
        self.home_btn.setStyleSheet(f"""QPushButton{{background:{THEME['bg_card']};color:{THEME['text_primary']};
            border:2px solid {THEME['border']};border-radius:10px;padding:12px 24px;}}
            QPushButton:hover{{background:{THEME['hover']};}}""")
        self.home_btn.clicked.connect(self.home_requested.emit)
        btn_row.addWidget(self.home_btn)
        cl.addLayout(btn_row)

        card.setStyleSheet(f"#resCard{{background:{THEME['bg_card']};border-radius:20px;border:1px solid {THEME['border']};}}")
        card.setMaximumWidth(550); card.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        lay.addWidget(card)

    def set_results(self, answers, level, topic, diff, total, elapsed):
        self._level = level; self._topic = topic; self._diff = diff; self._num = total
        score = sum(1 for a in answers if a["correct"])
        pct = round(score/total*100) if total else 0
        self.circle.set_value(score, total, f"{score}/{total}")
        if pct >= 80:
            self.title.setText("Excellent! 🌟")
        elif pct >= 60:
            self.title.setText("Good Job! 👍")
        else:
            self.title.setText("Keep Practicing! 💪")
        m, s = divmod(int(elapsed), 60)
        self.detail_lbl.setText(
            f"Score: {score}/{total}  •  Time: {m}:{s:02d}\n"
            f"Level: {LEVELS[level]['name']}  •  Difficulty: {diff.title()}"
        )
        # Record
        self.tracker.record_quiz(level, topic, diff, score, total, elapsed)
        # Build review
        while self.review_lay.count():
            item = self.review_lay.takeAt(0); w = item.widget()
            if w: w.deleteLater()
        for i, a in enumerate(answers):
            p = a["problem"]
            icon = "✅" if a["correct"] else "❌"
            color = THEME["success"] if a["correct"] else THEME["error"]
            lbl = QLabel(f"{icon}  Q{i+1}: {p['question']}  →  Your answer: {a['chosen']}" +
                         ("" if a["correct"] else f"  (Correct: {p['answer']})"))
            lbl.setWordWrap(True); lbl.setFont(QFont("Segoe UI",10))
            lbl.setStyleSheet(f"color:{color};padding:4px;")
            self.review_lay.addWidget(lbl)
        self.review_lay.addStretch()

    def get_retry_info(self):
        return self._level, self._topic, self._diff, self._num


class ProgressPage(QWidget):
    back_requested = Signal()

    def __init__(self, tracker, parent=None):
        super().__init__(parent)
        self.tracker = tracker
        lay = QVBoxLayout(self); lay.setContentsMargins(40,30,40,30); lay.setSpacing(16)

        header = QHBoxLayout()
        back = QPushButton("← Back"); back.setFont(QFont("Segoe UI",11))
        back.setCursor(Qt.PointingHandCursor)
        back.setStyleSheet(f"color:{THEME['primary']};background:transparent;border:none;padding:6px;")
        back.clicked.connect(self.back_requested.emit); header.addWidget(back)
        title = QLabel("📊  Progress Dashboard"); title.setFont(QFont("Segoe UI",24,QFont.Bold))
        title.setStyleSheet(f"color:{THEME['text_primary']};"); header.addWidget(title,1)
        lay.addLayout(header)

        # Stats cards
        stats_row = QHBoxLayout(); stats_row.setSpacing(12)
        for label, val_func, color in [
            ("Total Questions", lambda: str(self.tracker.data["total_attempted"]), THEME["primary"]),
            ("Accuracy", lambda: f"{self.tracker.accuracy}%", THEME["success"]),
            ("Best Streak", lambda: f"🔥 {self.tracker.data['best_streak']}", THEME["warning"]),
            ("Quizzes Done", lambda: str(self.tracker.total_quizzes), THEME["secondary"]),
        ]:
            card = QFrame(); card.setObjectName("statCard")
            cl = QVBoxLayout(card); cl.setContentsMargins(16,12,16,12); cl.setAlignment(Qt.AlignCenter)
            v = QLabel(val_func()); v.setFont(QFont("Segoe UI",20,QFont.Bold))
            v.setStyleSheet(f"color:{color};"); v.setAlignment(Qt.AlignCenter); cl.addWidget(v)
            l = QLabel(label); l.setFont(QFont("Segoe UI",9))
            l.setStyleSheet(f"color:{THEME['text_secondary']};"); l.setAlignment(Qt.AlignCenter); cl.addWidget(l)
            card.setStyleSheet(f"#statCard{{background:{THEME['bg_card']};border-radius:12px;border:1px solid {THEME['border']};}}")
            stats_row.addWidget(card)
        lay.addLayout(stats_row)

        # Topic breakdown
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{border:none;}}")
        inner = QWidget(); il = QVBoxLayout(inner); il.setSpacing(8)
        il.addWidget(QLabel("Topic Breakdown:"))
        for level_key, topics in TOPICS.items():
            level_lbl = QLabel(f"{LEVELS[level_key]['icon']}  {LEVELS[level_key]['name']}")
            level_lbl.setFont(QFont("Segoe UI",12,QFont.Bold))
            level_lbl.setStyleSheet(f"color:{LEVELS[level_key]['color']};margin-top:8px;")
            il.addWidget(level_lbl)
            for tkey, tname, ticon in topics:
                key = f"{level_key}_{tkey}"
                tdata = self.tracker.data["topics"].get(key, {"attempted":0,"correct":0,"best_pct":0})
                row = QHBoxLayout()
                name_l = QLabel(f"  {ticon} {tname}"); name_l.setFont(QFont("Segoe UI",10))
                name_l.setStyleSheet(f"color:{THEME['text_primary']};"); name_l.setMinimumWidth(200)
                row.addWidget(name_l)
                bar = QProgressBar(); bar.setRange(0,100); bar.setValue(tdata["best_pct"])
                bar.setFixedHeight(16); bar.setTextVisible(True)
                bar.setFormat(f"{tdata['best_pct']}% ({tdata['attempted']} questions)")
                bar.setStyleSheet(f"""
                    QProgressBar{{background:{THEME['border']};border-radius:8px;border:none;text-align:center;font-size:9px;}}
                    QProgressBar::chunk{{background:{LEVELS[level_key]['color']};border-radius:8px;}}""")
                row.addWidget(bar,1)
                il.addLayout(row)
        il.addStretch()
        scroll.setWidget(inner)
        lay.addWidget(scroll,1)

        # Reset button
        reset_btn = QPushButton("🗑️  Reset All Progress"); reset_btn.setFont(QFont("Segoe UI",10))
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setStyleSheet(f"""QPushButton{{background:transparent;color:{THEME['error']};
            border:1px solid {THEME['error']};border-radius:8px;padding:8px 16px;}}
            QPushButton:hover{{background:#FEE2E2;}}""")
        def do_reset():
            self.tracker.data = {"total_attempted":0,"total_correct":0,"streak":0,
                                 "best_streak":0,"history":[],"topics":{}}
            self.tracker.save(); self.refresh()
        reset_btn.clicked.connect(do_reset)
        lay.addWidget(reset_btn,0,Qt.AlignRight)

    def refresh(self):
        # Rebuild by re-initializing (simple approach)
        pass


# ──────────────────────── MAIN WINDOW ─────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathQuest — Math Learning App")
        self.setMinimumSize(1100, 750)
        self.resize(1200, 800)

        self.tracker = ProgressTracker()
        self.current_level = ""
        self.current_topic = ""

        # Central widget
        central = QWidget(); self.setCentralWidget(central)
        main_lay = QHBoxLayout(central); main_lay.setContentsMargins(0,0,0,0); main_lay.setSpacing(0)

        # Sidebar
        sidebar = QFrame(); sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sl = QVBoxLayout(sidebar); sl.setContentsMargins(12,20,12,20); sl.setSpacing(6)

        logo = QLabel("🧮 MathQuest"); logo.setFont(QFont("Segoe UI",18,QFont.Bold))
        logo.setStyleSheet(f"color:white;padding:8px;"); sl.addWidget(logo)
        sl.addSpacing(12)

        self.nav_btns = {}
        nav_items = [("home","🏠  Home","")] + \
                     [(k, f"{v['icon']}  {v['name']}", v['color']) for k,v in LEVELS.items()] + \
                     [("progress","📊  Progress","")]
        for key, label, color in nav_items:
            btn = QPushButton(label); btn.setFont(QFont("Segoe UI",11))
            btn.setCursor(Qt.PointingHandCursor); btn.setObjectName(f"nav_{key}")
            btn.setStyleSheet(f"""
                QPushButton{{color:{THEME['text_light']};background:transparent;
                    border:none;border-radius:8px;padding:10px 14px;text-align:left;}}
                QPushButton:hover{{background:rgba(255,255,255,0.1);}}
            """)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            sl.addWidget(btn); self.nav_btns[key] = btn
        sl.addStretch()

        version = QLabel("v1.0 • Made with PySide6")
        version.setFont(QFont("Segoe UI",8)); version.setStyleSheet("color:rgba(255,255,255,0.4);")
        sl.addWidget(version)

        sidebar.setStyleSheet(f"#sidebar{{background:{THEME['bg_sidebar']};}}")
        main_lay.addWidget(sidebar)

        # Content area
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{THEME['bg_main']};")
        main_lay.addWidget(self.stack,1)

        # Pages
        self.home_page = HomePage(self.tracker)
        self.topic_page = TopicPage()
        self.config_page = QuizConfigPage()
        self.quiz_page = QuizPage()
        self.results_page = ResultsPage(self.tracker)
        self.progress_page = ProgressPage(self.tracker)

        for p in [self.home_page, self.topic_page, self.config_page,
                   self.quiz_page, self.results_page, self.progress_page]:
            self.stack.addWidget(p)

        # Signals
        self.home_page.level_selected.connect(self._on_level_selected)
        self.home_page.progress_requested.connect(lambda: self._navigate("progress"))
        self.topic_page.topic_selected.connect(self._on_topic_selected)
        self.topic_page.back_requested.connect(lambda: self._navigate("home"))
        self.config_page.back_requested.connect(lambda: self._navigate("topics"))
        self.config_page.start_quiz.connect(self._start_quiz)
        self.quiz_page.quiz_finished.connect(self._on_quiz_finished)
        self.results_page.home_requested.connect(lambda: self._navigate("home"))
        self.results_page.retry_requested.connect(self._retry_quiz)
        self.progress_page.back_requested.connect(lambda: self._navigate("home"))

        self._navigate("home")
        self._apply_global_style()

    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{ background:{THEME['bg_main']}; }}
            QLabel {{ color:{THEME['text_primary']}; }}
            QComboBox {{ background:{THEME['bg_card']}; color:{THEME['text_primary']};
                         border:2px solid {THEME['border']}; border-radius:8px; padding:8px; }}
            QSpinBox {{ background:{THEME['bg_card']}; color:{THEME['text_primary']};
                        border:2px solid {THEME['border']}; border-radius:8px; padding:8px; }}
            QScrollBar:vertical {{ background:{THEME['bg_main']}; width:10px; border-radius:5px; }}
            QScrollBar::handle:vertical {{ background:{THEME['border']}; border-radius:5px; min-height:20px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height:0px; }}
        """)

    def _navigate(self, key):
        # Update sidebar highlighting
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.setStyleSheet(f"""
                    QPushButton{{color:white;background:rgba(255,255,255,0.15);
                        border:none;border-radius:8px;padding:10px 14px;text-align:left;}}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton{{color:{THEME['text_light']};background:transparent;
                        border:none;border-radius:8px;padding:10px 14px;text-align:left;}}
                    QPushButton:hover{{background:rgba(255,255,255,0.1);}}
                """)
        if key == "home":
            self.stack.setCurrentIndex(0)
        elif key == "progress":
            # Rebuild progress page
            self.stack.removeWidget(self.progress_page)
            self.progress_page = ProgressPage(self.tracker)
            self.progress_page.back_requested.connect(lambda: self._navigate("home"))
            self.stack.addWidget(self.progress_page)
            self.stack.setCurrentWidget(self.progress_page)
        elif key in LEVELS:
            self.current_level = key
            self.topic_page.set_level(key)
            self.stack.setCurrentWidget(self.topic_page)
        elif key == "topics":
            self.stack.setCurrentWidget(self.topic_page)

    def _on_level_selected(self, level):
        self.current_level = level
        self.topic_page.set_level(level)
        self.stack.setCurrentWidget(self.topic_page)
        self._highlight_nav(level)

    def _on_topic_selected(self, level, topic):
        self.current_level = level; self.current_topic = topic
        self.config_page.set_info(level, topic)
        self.stack.setCurrentWidget(self.config_page)

    def _start_quiz(self, level, topic, diff, num_q):
        gen = ProblemGenerator
        problems = [gen.generate(level, topic, diff) for _ in range(num_q)]
        self.quiz_page.start(problems, level, topic, diff)

        # Update topic page title with quiz info
        tname = dict(TOPICS[level]).get(topic, topic)
        self.quiz_page.setWindowTitle(f"Quiz: {tname}")
        self.stack.setCurrentWidget(self.quiz_page)

    def _on_quiz_finished(self, answers, level, topic, diff, total, elapsed):
        self.results_page.set_results(answers, level, topic, diff, total, elapsed)
        self.stack.setCurrentWidget(self.results_page)

    def _retry_quiz(self):
        level, topic, diff, num = self.results_page.get_retry_info()
        self._start_quiz(level, topic, diff, num)

    def _highlight_nav(self, key):
        for k, btn in self.nav_btns.items():
            if k == key:
                btn.setStyleSheet(f"""
                    QPushButton{{color:white;background:rgba(255,255,255,0.15);
                        border:none;border-radius:8px;padding:10px 14px;text-align:left;}}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton{{color:{THEME['text_light']};background:transparent;
                        border:none;border-radius:8px;padding:10px 14px;text-align:left;}}
                    QPushButton:hover{{background:rgba(255,255,255,0.1);}}
                """)


# ──────────────────────── ENTRY POINT ─────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()