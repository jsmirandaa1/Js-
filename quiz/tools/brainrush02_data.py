# Dados do vídeo 02 — BrainRush Quiz (15 Science & Nature Questions)
TITLE = "15 Science & Nature Questions — Can You Beat This Quiz?"
# cenas de abertura: (nome, texto, tipo de cena)
INTRO = [
    ("intro2", "Welcome back to BrainRush Quiz!", "intro2"),
    ("intro3", "Today, we're testing your knowledge of science and nature. From the human body to outer space, these fifteen questions will challenge what you think you know. You'll have just seven seconds to answer each question. Keep track of your score, and don't forget to comment your final result below. Are you ready? Let's begin!", "intro3"),
]
NUMS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen"]
CTA = ["You have seven seconds!", "Seven seconds. What's your answer?", "Think fast!", "Make your choice!", "Seven seconds!", "Choose carefully!",
       "Lock in your answer!", "Don't overthink it!", "What's your answer?", "Seven seconds. Go!", "What's your guess?", "Think carefully!",
       "Seven seconds to answer!", "Lock it in!", "This is your final chance. Seven seconds!"]
# (categoria, pergunta, opções, índice certo, pergunta falada SEM o "Question number X", leitura das opções, explicação, keyword)
_Q = [
 ("SPACE", "WHAT IS THE CLOSEST PLANET TO THE SUN?", ["Venus", "Mercury", "Mars", "Earth"], 1,
  "What is the closest planet to the Sun?", None,
  "Mercury is the closest planet to the Sun. It completes one orbit in just eighty-eight Earth days!", "88 DAYS"),
 ("PLANTS", "WHICH GAS DO PLANTS ABSORB DURING PHOTOSYNTHESIS?", ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], 2,
  "Which gas do plants absorb from the atmosphere during photosynthesis?", None,
  "Plants absorb carbon dioxide and use sunlight and water to produce sugars, releasing oxygen as a byproduct.", "CO2"),
 ("HUMAN BODY", "WHAT IS THE LARGEST ORGAN OF THE HUMAN BODY?", ["Liver", "Brain", "Lungs", "Skin"], 3,
  "What is the largest organ of the human body?", None,
  "Your skin is the largest organ of your body. It protects you, helps regulate temperature, and allows you to feel touch.", "SKIN"),
 ("SPACE", "WHICH PLANET HAS THE STRONGEST WINDS IN OUR SOLAR SYSTEM?", ["Neptune", "Saturn", "Jupiter", "Uranus"], 0,
  "Which planet is known for having the strongest winds in our solar system?", None,
  "Neptune has incredibly powerful winds that can reach speeds of over two thousand kilometers per hour!", "2,000+ KM/H"),
 ("CHEMISTRY", "WHAT IS THE CHEMICAL SYMBOL FOR OXYGEN?", ["Ox", "O", "Og", "Oy"], 1,
  "What is the chemical symbol for oxygen?", "A: O X. B: O. C: O G. Or D: O Y.",
  "The chemical symbol for oxygen is O. Oxygen is essential for human respiration and supports combustion.", "O"),
 ("ANIMALS", "WHICH ANIMAL CHANGES ITS SKIN COLOR TO BLEND INTO ITS SURROUNDINGS?", ["Cheetah", "Chameleon", "Kangaroo", "Zebra"], 1,
  "Which animal is famous for changing its skin color to blend into its surroundings?", None,
  "Chameleons can change their skin color using specialized cells. They use these changes for communication, temperature regulation, and camouflage.", "CAMOUFLAGE"),
 ("HUMAN BODY", "HOW MANY CHAMBERS DOES A HUMAN HEART HAVE?", ["Two", "Three", "Four", "Five"], 2,
  "How many chambers does a human heart have?", None,
  "The human heart has four chambers: two atria and two ventricles. Together, they keep blood circulating throughout the body.", "4 CHAMBERS"),
 ("EARTH SCIENCE", "WHAT IS THE HARDEST NATURALLY OCCURRING SUBSTANCE ON EARTH?", ["Quartz", "Diamond", "Granite", "Iron"], 1,
  "What is the hardest naturally occurring substance on Earth?", None,
  "Diamond is the hardest naturally occurring mineral on the Mohs hardness scale. It can scratch almost every other natural mineral.", "MOHS 10"),
 ("EARTH SCIENCE", "WHAT IS THE MAIN GAS FOUND IN EARTH'S ATMOSPHERE?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], 2,
  "What is the main gas found in Earth's atmosphere?", None,
  "Nitrogen makes up approximately seventy-eight percent of Earth's atmosphere, making it the most abundant atmospheric gas.", "78%"),
 ("HUMAN BODY", "WHICH PART OF THE BRAIN CONTROLS BALANCE AND COORDINATION?", ["Cerebellum", "Hypothalamus", "Brainstem", "Frontal lobe"], 0,
  "Which part of the human brain is mainly responsible for balance and coordination?", None,
  "The cerebellum helps coordinate voluntary movements, balance, posture, and motor learning.", "CEREBELLUM"),
 ("ANIMALS", "WHICH OF THESE ANIMALS IS A MAMMAL THAT LAYS EGGS?", ["Dolphin", "Platypus", "Penguin", "Seal"], 1,
  "Which of these animals is a mammal that lays eggs?", None,
  "The platypus is one of the few mammals that lay eggs. These unusual mammals are native to Australia.", "PLATYPUS"),
 ("PHYSICS", "WHAT FORCE KEEPS PLANETS IN ORBIT AROUND THE SUN?", ["Magnetism", "Friction", "Gravity", "Electricity"], 2,
  "What force keeps planets in orbit around the Sun?", None,
  "Gravity is the force of attraction between objects with mass. The Sun's gravity keeps the planets in their orbits.", "GRAVITY"),
 ("HUMAN BODY", "WHICH VITAMIN CAN YOUR BODY PRODUCE FROM SUNLIGHT?", ["Vitamin A", "Vitamin C", "Vitamin D", "Vitamin B12"], 2,
  "Which vitamin can the human body produce when the skin is exposed to sunlight?", "A: Vitamin A. B: Vitamin C. C: Vitamin D. Or D: Vitamin B twelve.",
  "When exposed to ultraviolet B radiation from sunlight, the skin can produce vitamin D, which helps the body absorb calcium.", "VITAMIN D"),
 ("EARTH SCIENCE", "WHAT IS IT CALLED WHEN LIQUID WATER TURNS INTO VAPOR?", ["Condensation", "Evaporation", "Freezing", "Melting"], 1,
  "What is the name of the process in which liquid water changes into water vapor?", None,
  "Evaporation happens when liquid water gains enough energy to become water vapor. It's an important part of the water cycle.", "EVAPORATION"),
 ("FINAL CHALLENGE", "WHICH STAR IS CLOSEST TO EARTH?", ["Sirius", "Polaris", "The Sun", "Proxima Centauri"], 2,
  "Which star is closest to Earth?", None,
  "The Sun is the closest star to Earth, at an average distance of about one hundred fifty million kilometers. Proxima Centauri is the closest star beyond our solar system.", "150 MILLION KM"),
]
def _opts(o, read):
    return read or f"A: {o[0]}. B: {o[1]}. C: {o[2]}. Or D: {o[3]}."
# formato igual ao vídeo 01: (cat, pergunta, opções, certo, fala_pergunta, fala_resposta, keyword)
QS = [(c, q, o, k, f"{ask} {_opts(o, rd)} {CTA[i]}", ans, kw) for i, (c, q, o, k, ask, rd, ans, kw) in enumerate(_Q)]
# "Question number X!" é gravado separado (os shorts não usam)
PRE = [f"Question number {n}!" for n in NUMS[:14]] + ["Final question! Number fifteen!"]
LETTER_A = {"q13_ask"}   # "Vitamin A" — força a pronúncia da letra A
SCORE = ("score", "That's the end of the challenge! Now, let's see how you did. Zero to five correct: Keep learning! Six to ten correct: Solid knowledge! Eleven to thirteen correct: Brain power! Fourteen correct: Impressive! And if you got all fifteen correct, you're a true BrainRush legend!")
SCORE_KEYS = ["zero", "six", "eleven", "fourteen", "all"]
OUTRO = ("outro", "Comment your score below, and challenge a friend to beat it. Subscribe to BrainRush Quiz for more challenges. Think fast. Know more!")
BANDS = [("0–5", "KEEP LEARNING"), ("6–10", "SOLID KNOWLEDGE"), ("11–13", "BRAIN POWER"), ("14", "IMPRESSIVE"), ("15", "BRAINRUSH LEGEND")]
# shorts: (perguntas, texto do gancho, gancho falado)
SHORTS = [
    dict(qs=[0, 3, 7], hook="ONLY GENIUSES GET 3/3", hook_v="Only geniuses get all three of these right. Let's see if you're one of them!"),
    dict(qs=[2, 6, 9], hook="HUMAN BODY QUIZ: 3/3?", hook_v="How well do you know your own body? Three questions. Seven seconds each."),
    dict(qs=[5, 10, 14], hook="90% FAIL QUESTION 3", hook_v="Ninety percent of people fail question number three. Can you beat it?"),
]
