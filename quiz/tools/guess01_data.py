# GUESS THE ANIMAL BY ITS SHADOW — 100 animais em 4 níveis (emojis 3D Fluent, MIT)
# (arquivo do emoji, nome na tela, nome falado)
def _a(*names):
    out = []
    for n in names:
        f, show, say = (n if isinstance(n, tuple) else (n, n, n))
        out.append((f, show, say))
    return out
LEVELS = [
    ("EASY", (80, 200, 120), _a("Dog", "Cat", "Cow", "Pig", "Horse", "Elephant", "Giraffe", "Rabbit", "Fish", "Penguin", "Snake", "Turtle", "Butterfly",
                               "Zebra", "Dolphin", "Kangaroo", "Camel", "Crocodile", "Shark", "Flamingo", "Snail", "Crab", "Spider", "Swan", "Bat")),
    ("MEDIUM", (240, 200, 60), _a("Chicken", "Duck", "Monkey", "Owl", "Whale", ("Ewe", "Sheep", "Sheep"), "Mouse", "Octopus", "Peacock", "Parrot", "Hedgehog",
                                  ("Chipmunk", "Squirrel", "Squirrel"), "Lobster", "Eagle", "Deer", "Goat", ("Lady beetle", "Ladybug", "Ladybug"), "Ant", "Gorilla",
                                  "Rhinoceros", "Hippopotamus", "Llama", "Scorpion", "Mosquito", "Moose")),
    ("HARD", (255, 140, 50), _a("Lion", "Frog", "Bear", "Koala", "Panda", ("Honeybee", "Bee", "Bee"), "Sloth", "Otter", "Skunk", "Badger", "Beaver", "Bison",
                                "Mammoth", "Orangutan", "Raccoon", "Seal", "Squid", "Shrimp", "Turkey", "Dodo", "Donkey", ("Blowfish", "Pufferfish", "Pufferfish"),
                                "Jellyfish", "Cricket", "Beetle")),
    ("IMPOSSIBLE", (240, 60, 70), _a("Rat", "Ram", "Ox", "Water buffalo", ("Boar", "Wild Boar", "Wild boar"), "Wolf", "Fox", "Poodle", "Leopard", "Tiger",
                                     "Rooster", "Dove", "Goose", "Cockroach", "Worm", "Fly", ("Two-hump camel", "Bactrian Camel", "Bactrian camel"),
                                     ("Sauropod", "Dinosaur", "Dinosaur"), "Tropical fish", "Polar bear", "Bird", "Hamster", "Lizard", "Oyster",
                                     ("Hatching chick", "Baby Chick", "Baby chick"))),
]
TITLE = "GUESS 100 ANIMALS BY THEIR SHADOW"
INTRO_V = "Can you guess one hundred animals by their shadow? Three seconds each. From easy to impossible. Let's go!"
LEVEL_V = ["Level one: easy!", "Level two: medium!", "Level three: hard!", "Level four: impossible!"]
OUTRO_V = "How many did you get right? Comment your score, and subscribe to BrainRush Quiz for more challenges!"
SHORT_END_V = "How many did you get? Comment your score!"
GUESS_T, REVEAL_T = 3.0, 2.0
BANDS = [("0–25", "BEGINNER"), ("26–50", "ANIMAL FAN"), ("51–75", "EXPERT"), ("76–99", "GENIUS"), ("100", "BRAINRUSH LEGEND")]
SHORT_HOOKS = ["GUESS THE ANIMAL BY ITS SHADOW", "ONLY 1% GET THEM ALL", "CAN YOU GUESS THEM ALL?", "90% FAIL THE LAST ONE", "GUESS THE SHADOW IN 3 SECONDS",
               "EASY TO IMPOSSIBLE", "ONLY GENIUSES GET THEM ALL", "GUESS THE ANIMAL IN 3 SECONDS", "SMARTER THAN 98%?", "IMPOSSIBLE ANIMAL QUIZ"]
CLIFF_FROM = 2   # cliffhanger a partir do Part 3 (Part 1 e 2 já foram postados sem)
