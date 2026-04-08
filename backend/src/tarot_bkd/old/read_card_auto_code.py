import os

filedict = os.path.dirname(os.path.abspath(__file__))

# Dictionary to hold tarot card info
tarot_cards = {}

with open(f"{filedict}\\rider_waite_cards.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()

new_lines = []
for line in lines:
    # Check for card title
    if "self.is_reversed = False" in line:
        line = '        self.orientation = "upright"\n'
        pass
    new_lines.append(line)

    pass

ROMAN = [
    (1000, "M"),
    ( 900, "CM"),
    ( 500, "D"),
    ( 400, "CD"),
    ( 100, "C"),
    (  90, "XC"),
    (  50, "L"),
    (  40, "XL"),
    (  10, "X"),
    (   9, "IX"),
    (   5, "V"),
    (   4, "IV"),
    (   1, "I"),
]


def int_to_roman(number):
    if number == 0:
        return 0
    result = []
    for (arabic, roman) in ROMAN:
        (factor, number) = divmod(number, arabic)
        result.append(roman * factor)
        if number == 0:
            break
    return "".join(result)


with open(f"{filedict}\\generated_cards.txt", 'w', encoding='utf-8') as file:
    for line in new_lines:
        file.write(line)
        pass

pass
