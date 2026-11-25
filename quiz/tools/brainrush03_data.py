# Dados do vídeo 03 — BrainRush Quiz (30 General Knowledge Questions, 5 rounds)
TITLE = "30 General Knowledge Questions — Can You Score 30/30?"
INTRO = [("intro3", "Thirty questions. Seven seconds each. Think you're a genius? Prove it! Let's go!", "intro3")]
NUMS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five",
        "twenty-six", "twenty-seven", "twenty-eight", "twenty-nine", "thirty"]
ROUNDS = {0: ("ROUND 1 • EASY", "Round one: easy!"), 6: ("ROUND 2 • MEDIUM", "Round two: medium!"), 12: ("ROUND 3 • GETTING HARDER", "Round three: getting harder!"),
          18: ("ROUND 4 • CHALLENGE", "Round four: challenge!"), 24: ("ROUND 5 • EXPERT", "Round five: expert level!")}
CTA = ["You have seven seconds!", "Think fast!", "Seven seconds!", "Make your choice!", "What's your answer?", "Go!"]
# (pergunta na tela, opções, certo, pergunta falada, leitura das opções ou None, explicação falada)
_Q = [
 ("WHICH IS THE LARGEST OCEAN ON EARTH?", ["Atlantic Ocean", "Indian Ocean", "Pacific Ocean", "Arctic Ocean"], 2, "Which is the largest ocean on Earth?", None,
  "The Pacific Ocean is the largest and deepest ocean on Earth, covering more area than all the continents combined."),
 ("WHAT IS THE CHEMICAL SYMBOL FOR GOLD?", ["Ag", "Au", "Fe", "Go"], 1, "What is the chemical symbol for gold?", "A: A G. B: A U. C: F E. Or D: G O.",
  "The symbol A U comes from the Latin word aurum, which means gold."),
 ("WHAT IS THE CAPITAL CITY OF AUSTRALIA?", ["Sydney", "Melbourne", "Brisbane", "Canberra"], 3, "What is the capital city of Australia?", None,
  "Canberra is Australia's capital. Many people mistakenly think it's Sydney or Melbourne."),
 ("HOW MANY SIDES DOES A HEXAGON HAVE?", ["Five", "Six", "Seven", "Eight"], 1, "How many sides does a hexagon have?", None,
  "A hexagon is a polygon with six sides and six angles."),
 ("WHO WROTE THE FAMOUS PLAY \"ROMEO AND JULIET\"?", ["Charles Dickens", "William Shakespeare", "Mark Twain", "Jane Austen"], 1, "Who wrote the famous play Romeo and Juliet?", None,
  "William Shakespeare wrote Romeo and Juliet, one of the most famous tragedies in English literature."),
 ("WHICH PLANET IS FAMOUS FOR ITS PROMINENT RING SYSTEM?", ["Mars", "Venus", "Saturn", "Mercury"], 2, "Which planet is famous for its prominent ring system?", None,
  "Saturn has an enormous ring system made mostly of ice particles, rock, and dust."),
 ("WHAT IS THE OFFICIAL CURRENCY OF JAPAN?", ["Yuan", "Won", "Yen", "Baht"], 2, "What is the official currency of Japan?", None,
  "The Japanese yen is the official currency of Japan and one of the world's major currencies."),
 ("HOW MANY BONES ARE IN AN ADULT HUMAN BODY?", ["186", "196", "206", "216"], 2, "How many bones are typically found in an adult human body?",
  "A: One hundred eighty-six. B: One hundred ninety-six. C: Two hundred six. Or D: Two hundred sixteen.",
  "Most adults have two hundred six bones. Babies are born with more bones, many of which fuse as they grow."),
 ("AT SEA LEVEL, WHAT IS THE BOILING POINT OF WATER IN CELSIUS?", ["50°C", "75°C", "100°C", "125°C"], 2, "At sea level, what is the boiling point of water in Celsius?",
  "A: Fifty degrees. B: Seventy-five degrees. C: One hundred degrees. Or D: One hundred twenty-five degrees.",
  "Pure water boils at one hundred degrees Celsius, or two hundred twelve degrees Fahrenheit, at standard atmospheric pressure."),
 ("WHICH IS THE FASTEST LAND ANIMAL?", ["Lion", "Cheetah", "Horse", "Leopard"], 1, "Which animal is the fastest land animal?", None,
  "The cheetah can reach speeds of around sixty to seventy miles per hour in short bursts."),
 ("IN WHICH COUNTRY IS THE GREAT WALL LOCATED?", ["India", "Japan", "China", "Mongolia"], 2, "In which country is the Great Wall located?", None,
  "The Great Wall is a vast network of fortifications built across northern China over many centuries."),
 ("WHICH GAS DO PLANTS ABSORB DURING PHOTOSYNTHESIS?", ["Oxygen", "Nitrogen", "Carbon dioxide", "Hydrogen"], 2, "Which gas do plants absorb from the atmosphere during photosynthesis?", None,
  "Plants absorb carbon dioxide and use sunlight and water to produce sugars during photosynthesis."),
 ("WHERE CAN YOU FIND THE MONA LISA?", ["British Museum", "Louvre Museum", "Vatican Museums", "Prado Museum"], 1, "Where can you find Leonardo da Vinci's famous painting, the Mona Lisa?", None,
  "The Mona Lisa is displayed at the Louvre Museum in Paris, France."),
 ("WHAT IS THE SMALLEST PRIME NUMBER?", ["0", "1", "2", "3"], 2, "What is the smallest prime number?", "A: Zero. B: One. C: Two. Or D: Three.",
  "Two is the smallest prime number, and the only even prime number, because its only positive divisors are one and two."),
 ("WHAT IS THE LARGEST HOT DESERT IN THE WORLD?", ["Arabian Desert", "Gobi Desert", "Sahara Desert", "Kalahari Desert"], 2, "What is the largest hot desert in the world?", None,
  "The Sahara is the world's largest hot desert, covering much of North Africa."),
 ("WHAT DOES A LIGHT-YEAR MEASURE?", ["Time", "Distance", "Brightness", "Temperature"], 1, "What does a light-year measure?", None,
  "A light-year is the distance light travels in one year, approximately five point eight eight trillion miles."),
 ("WHICH METAL IS LIQUID AT ROOM TEMPERATURE?", ["Iron", "Aluminum", "Mercury", "Copper"], 2, "Which metal is liquid at typical room temperature?", None,
  "Mercury is a metal that remains liquid at typical room temperatures, unlike most other metals."),
 ("WHICH EUROPEAN COUNTRY IS SHAPED LIKE A BOOT?", ["Greece", "Italy", "Portugal", "Croatia"], 1, "Which European country is commonly described as being shaped like a boot?", None,
  "Italy's distinctive peninsula resembles a boot extending into the Mediterranean Sea."),
 ("WHO WAS THE FIRST PERSON TO WALK ON THE MOON?", ["Buzz Aldrin", "Yuri Gagarin", "Neil Armstrong", "Michael Collins"], 2, "Who was the first person to walk on the Moon?", None,
  "Neil Armstrong stepped onto the Moon on July twentieth, nineteen sixty-nine, during NASA's Apollo eleven mission."),
 ("HOW MANY CHAMBERS DOES A HUMAN HEART HAVE?", ["Two", "Three", "Four", "Five"], 2, "How many chambers does a human heart have?", None,
  "The human heart has four chambers: two atria and two ventricles."),
 ("WHAT IS THE SQUARE ROOT OF 144?", ["10", "11", "12", "14"], 2, "What is the square root of one hundred forty-four?", "A: Ten. B: Eleven. C: Twelve. Or D: Fourteen.",
  "Twelve multiplied by twelve equals one hundred forty-four, so its square root is twelve."),
 ("WHAT IS THE LARGEST ANIMAL ON EARTH?", ["African elephant", "Whale shark", "Blue whale", "Giant squid"], 2, "What is the largest animal on Earth?", None,
  "The blue whale is the largest known animal ever to have lived on Earth."),
 ("WHAT IS THE OFFICIAL CURRENCY OF SWITZERLAND?", ["Euro", "Swiss franc", "Swiss mark", "Krona"], 1, "What is the official currency of Switzerland?", None,
  "Switzerland uses the Swiss franc, abbreviated C H F, as its official currency."),
 ("WHAT IS THE SHAPE OF A DNA MOLECULE CALLED?", ["Single spiral", "Double helix", "Flat rectangle", "Triple helix"], 1, "What is the shape of a DNA molecule commonly described as?", None,
  "DNA consists of two strands twisted around each other, forming a double helix structure."),
 ("HOW MANY CONTINENTS ARE TRADITIONALLY RECOGNIZED?", ["Five", "Six", "Seven", "Eight"], 2, "How many traditionally recognized continents are there?", None,
  "The commonly taught seven continent model includes Africa, Antarctica, Asia, Europe, North America, South America, and Australia."),
 ("WHICH MOUNTAIN IS THE HIGHEST ABOVE SEA LEVEL?", ["K2", "Mount Kilimanjaro", "Mount Everest", "Denali"], 2, "Which mountain is the highest above sea level?", "A: K two. B: Mount Kilimanjaro. C: Mount Everest. Or D: Denali.",
  "Mount Everest reaches approximately twenty-nine thousand and thirty-two feet, or eight thousand eight hundred forty-nine meters, above sea level."),
 ("WHICH INSTRUMENT MEASURES ATMOSPHERIC PRESSURE?", ["Thermometer", "Barometer", "Hygrometer", "Anemometer"], 1, "Which instrument is used to measure atmospheric pressure?", None,
  "A barometer measures atmospheric pressure, and is commonly used in weather forecasting."),
 ("WHICH SPACECRAFT CARRIED ASTRONAUTS TO THE MOON IN 1969?", ["Apollo 8", "Apollo 10", "Apollo 11", "Apollo 13"], 2, "Which spacecraft carried astronauts to the Moon in nineteen sixty-nine?",
  "A: Apollo eight. B: Apollo ten. C: Apollo eleven. Or D: Apollo thirteen.",
  "Apollo eleven was the NASA mission that achieved the first crewed Moon landing in July, nineteen sixty-nine."),
 ("APPROXIMATELY HOW FAST DOES LIGHT TRAVEL IN A VACUUM?", ["30,000 km/s", "150,000 km/s", "300,000 km/s", "500,000 km/s"], 2, "Approximately how fast does light travel in a vacuum?",
  "A: Thirty thousand. B: One hundred fifty thousand. C: Three hundred thousand. Or D: Five hundred thousand kilometers per second.",
  "Light travels at approximately two hundred ninety-nine thousand, seven hundred ninety-two kilometers per second in a vacuum."),
 ("WHICH LANGUAGE HAS THE MOST NATIVE SPEAKERS?", ["English", "Spanish", "Mandarin Chinese", "Hindi"], 2, "Which language has the largest number of native speakers worldwide?", None,
  "Mandarin Chinese has more native speakers than any other individual language in the world."),
]
def _opts(o, read): return read or f"A: {o[0]}. B: {o[1]}. C: {o[2]}. Or D: {o[3]}."
def _cat(i):
    k = max(r for r in ROUNDS if r <= i); return ROUNDS[k][0] if i != 29 else "FINAL QUESTION"
KW = [""] * 30
QS = [(_cat(i), q, o, k, f"{ask} {_opts(o, rd)} {CTA[i % len(CTA)] if i != 29 else 'This is your final chance. Seven seconds!'}", ans, KW[i])
      for i, (q, o, k, ask, rd, ans) in enumerate(_Q)]
PRE = []
for i in range(30):
    p = f"Question number {NUMS[i]}!"
    if i in ROUNDS: p = ROUNDS[i][1] + " " + p
    if i == 29: p = "Final question! Number thirty!"
    PRE.append(p)
LETTER_A = {"q02_ask", "q02_ans"}  # "A G", "A U"
SCORE = None
OUTRO = ("outro", "What's your score? Comment below! And subscribe to BrainRush Quiz for more challenges. Think fast. Know more!")
BANDS = []
SHORTS = [
    dict(qs=[0, 1, 2], hook="ONLY 1% GET 3/3", hook_v="Only one percent of people get all three right. Let's see if you can!"),
    dict(qs=[3, 4, 5], hook="CAN YOU GET 3/3?", hook_v="Three questions. Seven seconds each. Can you get them all?"),
    dict(qs=[6, 7, 8], hook="90% FAIL QUESTION 3", hook_v="Ninety percent of people fail question number three. Are you one of them?"),
    dict(qs=[9, 10, 11], hook="GENIUS TEST: 3/3?", hook_v="Only real geniuses get all three. Let's find out!"),
    dict(qs=[12, 13, 14], hook="SMARTER THAN 90%?", hook_v="Are you smarter than ninety percent of people? Prove it!"),
    dict(qs=[15, 16, 17], hook="MOST PEOPLE FAIL #2", hook_v="Most people get question two wrong. Will you?"),
    dict(qs=[18, 19, 20], hook="ONLY 1% GET 3/3", hook_v="Only one percent of people get all three. Ready?"),
    dict(qs=[21, 22, 23], hook="CAN YOU GET 3/3?", hook_v="Three questions. Seven seconds each. Let's see what you know!"),
    dict(qs=[24, 25, 26], hook="EXPERT LEVEL QUIZ", hook_v="Expert level. Only real geniuses get all three. Let's go!"),
    dict(qs=[27, 28, 29], hook="FINAL BOSS QUIZ", hook_v="The final three. These are the hardest ones. Ready?"),
]
