# GUESS 100 FLAGS — Easy → Impossible (bandeiras: flag-icons, MIT). Itens: (código ISO, nome na tela, nome falado)
MODE = "flag"
def _a(*xs): return [x if isinstance(x, tuple) and len(x) == 3 else (x[0], x[1], x[1]) for x in xs]
LEVELS = [
    ("EASY", (80, 200, 120), _a(("us", "United States"), ("gb", "United Kingdom"), ("ca", "Canada"), ("br", "Brazil"), ("jp", "Japan"), ("cn", "China"),
        ("fr", "France"), ("de", "Germany"), ("it", "Italy"), ("es", "Spain"), ("mx", "Mexico"), ("in", "India"), ("au", "Australia"), ("kr", "South Korea"),
        ("ar", "Argentina"), ("ch", "Switzerland"), ("se", "Sweden"), ("gr", "Greece"), ("pt", "Portugal"), ("tr", "Turkey"), ("eg", "Egypt"),
        ("ie", "Ireland"), ("nl", "Netherlands"), ("jm", "Jamaica"), ("ru", "Russia"))),
    ("MEDIUM", (240, 200, 60), _a(("be", "Belgium"), ("at", "Austria"), ("pl", "Poland"), ("dk", "Denmark"), ("no", "Norway"), ("fi", "Finland"),
        ("nz", "New Zealand"), ("co", "Colombia"), ("cl", "Chile"), ("pe", "Peru"), ("ve", "Venezuela"), ("cu", "Cuba"), ("sa", "Saudi Arabia"),
        ("za", "South Africa"), ("ng", "Nigeria"), ("ke", "Kenya"), ("th", "Thailand"), ("vn", "Vietnam"), ("ph", "Philippines"), ("id", "Indonesia"),
        ("my", "Malaysia"), ("pk", "Pakistan"), ("ua", "Ukraine"), ("cz", "Czech Republic"), ("hu", "Hungary"))),
    ("HARD", (255, 140, 50), _a(("hr", "Croatia"), ("rs", "Serbia"), ("ro", "Romania"), ("bg", "Bulgaria"), ("sk", "Slovakia"), ("si", "Slovenia"),
        ("ee", "Estonia"), ("lv", "Latvia"), ("lt", "Lithuania"), ("is", "Iceland"), ("ma", "Morocco"), ("dz", "Algeria"), ("tn", "Tunisia"),
        ("et", "Ethiopia"), ("gh", "Ghana"), ("sn", "Senegal"), ("cm", "Cameroon"), ("uy", "Uruguay"), ("py", "Paraguay"), ("bo", "Bolivia"),
        ("ec", "Ecuador"), ("cr", "Costa Rica"), ("pa", "Panama"), ("np", "Nepal"), ("lk", "Sri Lanka"))),
    ("IMPOSSIBLE", (240, 60, 70), _a(("td", "Chad"), ("mc", "Monaco"), ("ci", "Ivory Coast"), ("lu", "Luxembourg"), ("ml", "Mali"), ("gn", "Guinea"),
        ("bj", "Benin"), ("bf", "Burkina Faso"), ("ne", "Niger"), ("sl", "Sierra Leone"), ("tt", "Trinidad and Tobago"), ("kz", "Kazakhstan"),
        ("kg", "Kyrgyzstan"), ("uz", "Uzbekistan"), ("tj", "Tajikistan"), ("mn", "Mongolia"), ("bt", "Bhutan"), ("mz", "Mozambique"), ("zm", "Zambia"),
        ("zw", "Zimbabwe"), ("bw", "Botswana"), ("na", "Namibia"), ("ls", "Lesotho"), ("sz", "Eswatini"), ("vu", "Vanuatu"))),
]
TITLE1, TITLE2 = "GUESS 100 FLAGS", "OF THE WORLD"
LABEL, UNIT = "GUESS THE COUNTRY", "FLAGS"
INTRO_V = "Can you guess one hundred flags of the world? Three seconds each. From easy to impossible. Let's go!"
LEVEL_V = ["Level one: easy!", "Level two: medium!", "Level three: hard!", "Level four: impossible!"]
OUTRO_V = "How many flags did you get right? Comment your score, and subscribe to BrainRush Quiz for more challenges!"
SHORT_END_V = "How many did you get? Comment your score!"
GUESS_T, REVEAL_T = 3.0, 2.0
BANDS = [("0–25", "TOURIST"), ("26–50", "TRAVELER"), ("51–75", "EXPLORER"), ("76–99", "GEOGRAPHY GENIUS"), ("100", "BRAINRUSH LEGEND")]
SHORT_HOOKS = ["GUESS THE FLAG IN 3 SECONDS", "ONLY 1% GET THEM ALL", "CAN YOU NAME THEM ALL?", "90% FAIL THE LAST ONE", "FLAG QUIZ: EASY TO IMPOSSIBLE",
               "GEOGRAPHY GENIUS TEST", "ONLY GENIUSES GET THEM ALL", "GUESS THE COUNTRY", "SMARTER THAN 98%?", "IMPOSSIBLE FLAG QUIZ"]
CLIFF_FROM = 0   # cliffhanger desde o Part 1
