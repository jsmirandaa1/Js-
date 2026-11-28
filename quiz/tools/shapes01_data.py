# GUESS THE COUNTRY BY ITS SHAPE — 100 países (formato: world-atlas; bandeira na revelação: flag-icons). (id numérico|alpha2, nome na tela, nome falado)
MODE = "shape"
_E = [("380","it","Italy"),("840","us","United States"),("076","br","Brazil"),("036","au","Australia"),("356","in","India"),("392","jp","Japan"),("826","gb","United Kingdom"),
      ("250","fr","France"),("724","es","Spain"),("484","mx","Mexico"),("124","ca","Canada"),("152","cl","Chile"),("032","ar","Argentina"),("156","cn","China"),("643","ru","Russia"),
      ("818","eg","Egypt"),("710","za","South Africa"),("450","mg","Madagascar"),("192","cu","Cuba"),("352","is","Iceland"),("554","nz","New Zealand"),("682","sa","Saudi Arabia"),
      ("792","tr","Turkey"),("300","gr","Greece"),("372","ie","Ireland")]
_M = [("276","de","Germany"),("578","no","Norway"),("752","se","Sweden"),("246","fi","Finland"),("620","pt","Portugal"),("604","pe","Peru"),("170","co","Colombia"),("862","ve","Venezuela"),
      ("360","id","Indonesia"),("608","ph","Philippines"),("704","vn","Vietnam"),("764","th","Thailand"),("410","kr","South Korea"),("804","ua","Ukraine"),("616","pl","Poland"),
      ("566","ng","Nigeria"),("504","ma","Morocco"),("586","pk","Pakistan"),("364","ir","Iran"),("144","lk","Sri Lanka"),("706","so","Somalia"),("496","mn","Mongolia"),
      ("398","kz","Kazakhstan"),("598","pg","Papua New Guinea"),("388","jm","Jamaica")]
_H = [("404","ke","Kenya"),("231","et","Ethiopia"),("368","iq","Iraq"),("004","af","Afghanistan"),("760","sy","Syria"),("434","ly","Libya"),("012","dz","Algeria"),("729","sd","Sudan"),
      ("068","bo","Bolivia"),("600","py","Paraguay"),("858","uy","Uruguay"),("218","ec","Ecuador"),("120","cm","Cameroon"),("024","ao","Angola"),("516","na","Namibia"),("834","tz","Tanzania"),
      ("040","at","Austria"),("756","ch","Switzerland"),("528","nl","Netherlands"),("208","dk","Denmark"),("191","hr","Croatia"),("591","pa","Panama"),("116","kh","Cambodia"),
      ("408","kp","North Korea"),("524","np","Nepal")]
_I = [("148","td","Chad"),("466","ml","Mali"),("562","ne","Niger"),("072","bw","Botswana"),("894","zm","Zambia"),("716","zw","Zimbabwe"),("508","mz","Mozambique"),("800","ug","Uganda"),
      ("288","gh","Ghana"),("384","ci","Ivory Coast"),("478","mr","Mauritania"),("642","ro","Romania"),("348","hu","Hungary"),("112","by","Belarus"),("428","lv","Latvia"),("268","ge","Georgia"),
      ("860","uz","Uzbekistan"),("417","kg","Kyrgyzstan"),("418","la","Laos"),("050","bd","Bangladesh"),("104","mm","Myanmar"),("266","ga","Gabon"),("140","cf","Central African Republic"),
      ("854","bf","Burkina Faso"),("064","bt","Bhutan")]
_f = lambda arr: [(f"{i}|{a}", n, n) for i, a, n in arr]
LEVELS = [("EASY", (80, 200, 120), _f(_E)), ("MEDIUM", (240, 200, 60), _f(_M)), ("HARD", (255, 140, 50), _f(_H)), ("IMPOSSIBLE", (240, 60, 70), _f(_I))]
TITLE1, TITLE2 = "GUESS 100 COUNTRIES", "BY THEIR SHAPE"
LABEL, UNIT = "GUESS THE COUNTRY", "COUNTRIES"
INTRO_V = "Can you guess one hundred countries by their shape? Three seconds each. From easy to impossible. Let's go!"
LEVEL_V = ["Level one: easy!", "Level two: medium! If you got twenty or more so far, you're in the top ten percent!",
           "Level three: hard! Only a few people make it this far.", "Level four: impossible! Only three percent get these right. Good luck!"]
CHECKPOINTS = [None, "GOT 20+ IN LEVEL 1? TOP 10%!", "ONLY A FEW MAKE IT THIS FAR", "ONLY 3% GET THESE RIGHT"]
OUTRO_V = "How many countries did you get right? Comment your score, and subscribe to BrainRush Quiz for more challenges!"
SHORT_END_V = "How many did you get? Comment your score!"
GUESS_T, REVEAL_T = 3.0, 2.0
BANDS = [("0–25", "TOURIST"), ("26–50", "TRAVELER"), ("51–75", "EXPLORER"), ("76–99", "GEOGRAPHY GENIUS"), ("100", "BRAINRUSH LEGEND")]
SHORT_HOOKS = ["GUESS THE COUNTRY BY ITS SHAPE", "ONLY 1% GET THEM ALL", "CAN YOU NAME THEM ALL?", "90% FAIL THE LAST ONE", "GUESS THE SHAPE IN 3 SECONDS",
               "GEOGRAPHY GENIUS TEST", "ONLY GENIUSES GET THEM ALL", "GUESS THE COUNTRY IN 3 SECONDS", "SMARTER THAN 98%?", "IMPOSSIBLE GEOGRAPHY QUIZ"]
CLIFF_FROM = 0   # com cliffhanger (como as bandeiras)
