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
    ' ': 0.201, '!': 0.241, '"': 0.436, '#': 0.738, '$': 0.601, '%': 0.792,
    '&': 0.683, "'": 0.251, '(': 0.412, ')': 0.412, '*': 0.475, '+': 0.6,
    ',': 0.25, '-': 0.458, '.': 0.25, '/': 0.367, '0': 0.684, '1': 0.349,
    '2': 0.6, '3': 0.591, '4': 0.673, '5': 0.586, '6': 0.6, '7': 0.61,
    '8': 0.597, '9': 0.633, ':': 0.25, ';': 0.25, '=': 0.6, '?': 0.526,
    'A': 0.755, 'B': 0.69, 'C': 0.704, 'D': 0.737, 'E': 0.644, 'F': 0.639,
    'G': 0.793, 'H': 0.738, 'I': 0.272, 'J': 0.625, 'K': 0.672, 'L': 0.628,
    'M': 0.881, 'N': 0.748, 'O': 0.812, 'P': 0.68, 'Q': 0.812, 'R': 0.678,
    'S': 0.641, 'T': 0.66, 'U': 0.724, 'V': 0.745, 'W': 0.931, 'X': 0.711,
    'Y': 0.719, 'Z': 0.625, '[': 0.394, ']': 0.394, 'a': 0.555, 'b': 0.632,
    'c': 0.518, 'd': 0.632, 'e': 0.589, 'f': 0.433, 'g': 0.628, 'h': 0.594,
    'i': 0.245, 'j': 0.245, 'k': 0.568, 'l': 0.245, 'm': 0.905, 'n': 0.594,
    'o': 0.616, 'p': 0.632, 'q': 0.632, 'r': 0.408, 's': 0.491, 't': 0.434,
    'u': 0.594, 'v': 0.603, 'w': 0.78, 'x': 0.568, 'y': 0.589, 'z': 0.506,
    '²': 0.307, '³': 0.329, '¹': 0.195, '×': 0.6, '÷': 0.6, 'ˢ': 0.381,
    'ᵂ': 0.694, 'ᵈ': 0.479, 'ᶜ': 0.413, 'ᶠ': 0.377, '₀': 0.438, '₁': 0.438,
    '₂': 0.438, '₃': 0.438, '₄': 0.438, '₅': 0.438, 'ₐ': 0.457, '→': 0.837,
    '−': 0.6, '≤': 0.837, '≥': 0.837,
}

# Anything not measured takes the widest of its class, so an unlisted
# character is over-counted rather than clipped.
EM_FALLBACK = {"upper": 0.931, "lower": 0.905, "digit": 0.684, "other": 0.837}


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
