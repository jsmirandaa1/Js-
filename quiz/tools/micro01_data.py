# MICRO (TikTok): vídeos de ~12s, pergunta/desafio no 1º frame.
# RIDDLES: (pergunta na tela, pergunta falada, [(opção, emoji)], índice certo, resposta falada)
RIDDLES = [
    ("WHAT HAS KEYS BUT CAN'T OPEN LOCKS?", "What has keys, but can't open locks?",
     [("A door", "door"), ("A piano", "musical_keyboard"), ("A map", "world_map")], 1, "A piano!"),
    ("WHAT HAS HANDS BUT CAN'T CLAP?", "What has hands, but can't clap?",
     [("A clock", "mantelpiece_clock"), ("A robot", "robot"), ("Gloves", "gloves")], 0, "A clock!"),
    ("HOW MANY MONTHS HAVE 28 DAYS?", "How many months have twenty-eight days?",
     [("Only 1", "spiral_calendar"), ("2", "spiral_calendar"), ("All 12", "spiral_calendar")], 2, "All twelve of them!"),
    ("WHAT CAN YOU CATCH BUT NOT THROW?", "What can you catch, but not throw?",
     [("A ball", "soccer_ball"), ("A cold", "sneezing_face"), ("A fish", "fish")], 1, "A cold!"),
    ("WHAT GOES UP BUT NEVER COMES DOWN?", "What goes up, but never comes down?",
     [("A balloon", "balloon"), ("A rocket", "rocket"), ("Your age", "birthday_cake")], 2, "Your age!"),
    ("WHAT WEIGHS MORE: A POUND OF FEATHERS OR A POUND OF ROCKS?", "What weighs more? A pound of feathers, or a pound of rocks?",
     [("Feathers", "feather"), ("Rocks", "rock"), ("Same weight", "balance_scale")], 2, "Same weight! A pound is a pound."),
]
# ODD ONE OUT: (símbolo repetido, símbolo diferente, linhas, colunas, segundos)
ODD = [
    ("NM", "MN", 9, 6, 8),
    ("69", "96", 10, 6, 8),
    ("bd", "bp", 10, 6, 8),
    ("88", "8B", 11, 6, 9),
    ("EF", "EP", 11, 6, 9),
    ("OO", "OQ", 12, 7, 10),
]
LINES = {"riddle_end": "Did you get it? Comment your answer!", "odd_intro": "Find the odd one out!", "odd_end": "Did you find it? Comment your time!"}
