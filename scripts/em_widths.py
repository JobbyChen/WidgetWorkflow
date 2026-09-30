# -*- coding: utf-8 -*-
"""How wide a character is, in em, in Red Hat Display.

Measured in Chromium over a rendered widget with `getComputedTextLength`, ten
copies of each character between two H's so the side bearings cancel. Weights
700 and 800 at sizes 12, 13 and 14 agree to 0.0002 em, so one table serves
every label the engine draws; a plain 10.5px tick runs about 11% narrower,
which this over-states and therefore never clips.

Before this the model was an average per *case*, and it was 20% narrow for
"S + Quota" -- a Q, a W or a + is half again the width of an average capital,
and a margin sized from the average cuts off the label it was sized for. The
width model was wrong three times before it was measured per character rather
than per class.

`python scripts/em_widths.py --js` prints the engine's copy of this table. The
engine carries its own because it sizes its margins in the browser: run the
flag and paste, never retype, and `scripts/test_check_file.py` fails if the
two ever drift apart.
"""

EM = {
    ' ': 0.348, '!': 0.456, '"': 0.52, '#': 0.837, '$': 0.695, '%': 1.001,
    '&': 0.871, "'": 0.306, '(': 0.457, ')': 0.457, '*': 0.522, '+': 0.837,
    ',': 0.38, '-': 0.415, '.': 0.38, '/': 0.365, '0': 0.695, '1': 0.695,
    '2': 0.695, '3': 0.695, '4': 0.695, '5': 0.695, '6': 0.695, '7': 0.695,
    '8': 0.695, '9': 0.695, ':': 0.4, ';': 0.4, '=': 0.837, '?': 0.58,
    'A': 0.773, 'B': 0.761, 'C': 0.733, 'D': 0.829, 'E': 0.682, 'F': 0.682,
    'G': 0.82, 'H': 0.836, 'I': 0.372, 'J': 0.372, 'K': 0.774, 'L': 0.637,
    'M': 0.994, 'N': 0.836, 'O': 0.849, 'P': 0.732, 'Q': 0.849, 'R': 0.769,
    'S': 0.679, 'T': 0.702, 'U': 0.811, 'V': 0.773, 'W': 1.102, 'X': 0.77,
    'Y': 0.723, 'Z': 0.724, '[': 0.457, ']': 0.457, 'a': 0.674, 'b': 0.715,
    'c': 0.592, 'd': 0.715, 'e': 0.678, 'f': 0.405, 'g': 0.715, 'h': 0.711,
    'i': 0.343, 'j': 0.343, 'k': 0.664, 'l': 0.343, 'm': 1.041, 'n': 0.711,
    'o': 0.686, 'p': 0.715, 'q': 0.715, 'r': 0.493, 's': 0.595, 't': 0.478,
    'u': 0.711, 'v': 0.651, 'w': 0.923, 'x': 0.644, 'y': 0.651, 'z': 0.582,
    '²': 0.438, '³': 0.438, '¹': 0.438, '×': 0.837, '÷': 0.837, 'ˢ': 0.381,
    'ᵂ': 0.694, 'ᵈ': 0.479, 'ᶜ': 0.413, 'ᶠ': 0.377, '₀': 0.438, '₁': 0.438,
    '₂': 0.438, '₃': 0.438, '₄': 0.438, '₅': 0.438, 'ₐ': 0.457, '→': 0.837,
    '−': 0.837, '≤': 0.837, '≥': 0.837,
}

# Anything not measured takes the widest of its class, so an unlisted
# character is over-counted rather than clipped.
EM_FALLBACK = {"upper": 1.102, "lower": 1.041, "digit": 0.695, "other": 1.001}


def em_width(text):
    """A string's width in em."""
    w = 0.0
    for ch in str(text):
        if ch in EM:
            w += EM[ch]
        elif ch.isupper():
            w += EM_FALLBACK["upper"]
        elif ch.islower():
            w += EM_FALLBACK["lower"]
        elif ch.isdigit():
            w += EM_FALLBACK["digit"]
        else:
            w += EM_FALLBACK["other"]
    return w


def js_literal():
    """The same table, as the engine writes it."""
    out, line = [], "      "
    for k in sorted(EM):
        key = k if (k.isalnum() and ord(k) < 128) else ("'" + k.replace("'", "\\'") + "'")
        piece = key + ":" + (("%.3f" % EM[k]).rstrip("0").lstrip("0")) + ","
        if len(line) + len(piece) > 76:
            out.append(line)
            line = "      "
        line += piece
    out.append(line)
    return "{\n" + "\n".join(out).rstrip(",") + "}"


if __name__ == "__main__":
    import sys
    if "--js" in sys.argv:
        print(js_literal())
    else:
        for a in sys.argv[1:]:
            print("%s  %.3f em" % (a, em_width(a)))
