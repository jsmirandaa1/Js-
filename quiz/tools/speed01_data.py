# SPEED QUIZ (formato TikTok): 8 perguntas, timer de 3s, dificuldade subindo, 1 HARD no meio e FINAL BOSS no fim.
# Cada pergunta: (vídeo de origem, índice da pergunta, nível, pergunta falada, resposta falada)
# nível: E = fácil, M = médio, H = "HARD QUESTION", B = "FINAL BOSS"
TIMER = {"E": 3, "M": 3, "H": 4, "B": 5}
SPEED = [
  dict(hook="ONLY 2% GET 8/8", hook_v="Only two percent get all eight. Go!", qs=[
    (1, 0, "E", "Which planet is known as the Red Planet?", "Mars!"),
    (2, 4, "E", "What's the chemical symbol for oxygen?", "O!"),
    (1, 8, "M", "What's the capital of Australia?", "Canberra!"),
    (2, 6, "M", "How many chambers does the human heart have?", "Four!"),
    (3, 15, "H", "Hard one! What does a light-year measure?", "Distance!"),
    (1, 11, "M", "Which planet is famous for its rings?", "Saturn!"),
    (3, 6, "M", "What's the currency of Japan?", "The yen!"),
    (2, 9, "B", "Final boss! Which part of the brain controls balance?", "The cerebellum!"),
  ]),
  dict(hook="90% FAIL THE LAST ONE", hook_v="Ninety percent fail the last one. Let's go!", qs=[
    (1, 2, "E", "How many sides does a hexagon have?", "Six!"),
    (3, 9, "E", "What's the fastest land animal?", "The cheetah!"),
    (1, 5, "M", "Where are the Great Pyramids of Giza?", "Egypt!"),
    (2, 8, "M", "What's the main gas in Earth's atmosphere?", "Nitrogen!"),
    (1, 10, "H", "Hard one! How many hearts does an octopus have?", "Three!"),
    (3, 17, "M", "Which country is shaped like a boot?", "Italy!"),
    (1, 7, "M", "How many keys does a standard piano have?", "Eighty-eight!"),
    (3, 29, "B", "Final boss! Which language has the most native speakers?", "Mandarin Chinese!"),
  ]),
  dict(hook="GENIUS TEST: 8/8?", hook_v="Genius test. Eight questions. Three seconds each. Go!", qs=[
    (1, 1, "E", "What's the largest ocean on Earth?", "The Pacific!"),
    (2, 0, "E", "What's the closest planet to the Sun?", "Mercury!"),
    (1, 4, "M", "What's the chemical symbol for gold?", "A U!"),
    (3, 7, "M", "How many bones are in an adult human body?", "Two hundred six!"),
    (2, 3, "H", "Hard one! Which planet has the strongest winds?", "Neptune!"),
    (3, 12, "M", "Where is the Mona Lisa displayed?", "The Louvre!"),
    (1, 12, "M", "What year did humans first land on the Moon?", "Nineteen sixty-nine!"),
    (3, 26, "B", "Final boss! What measures atmospheric pressure?", "A barometer!"),
  ]),
  dict(hook="SMARTER THAN 98%?", hook_v="Are you smarter than ninety-eight percent? Prove it!", qs=[
    (2, 5, "E", "Which animal changes its skin color?", "The chameleon!"),
    (3, 8, "E", "At what temperature does water boil, in Celsius?", "One hundred degrees!"),
    (1, 6, "M", "Which of these is a prime number?", "Two!"),
    (2, 11, "M", "What force keeps planets in orbit?", "Gravity!"),
    (1, 9, "H", "Hard one! What's the chemical symbol for sodium?", "N A!"),
    (3, 14, "M", "What's the largest hot desert in the world?", "The Sahara!"),
    (2, 10, "M", "Which mammal lays eggs?", "The platypus!"),
    (3, 16, "B", "Final boss! Which metal is liquid at room temperature?", "Mercury!"),
  ]),
]
OUTRO_V = "How many did you get? Comment your score!"
PHONEME_A = {"sp2_a2"}   # "A U!" -> letra A
