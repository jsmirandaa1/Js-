# GUESS THE FOOD BY ITS SHADOW — 100 comidas/bebidas em 4 níveis (emojis 3D Fluent, MIT). (arquivo, nome na tela, nome falado)
def _a(*xs): return [x if isinstance(x, tuple) else (x, x, x) for x in xs]
LEVELS = [
    ("EASY", (80, 200, 120), _a(("Red apple", "Apple", "Apple"), "Banana", "Grapes", "Watermelon", "Strawberry", "Cherries", "Pineapple", "Pear", "Carrot",
        ("Ear of corn", "Corn", "Corn"), "Broccoli", "Mushroom", "Hamburger", "French fries", "Pizza", "Hot dog", "Popcorn", "Birthday cake", "Cupcake",
        "Lollipop", ("Doughnut", "Donut", "Donut"), ("Soft ice cream", "Ice Cream Cone", "Ice cream cone"), "Egg", "Teapot", ("Hot pepper", "Chili Pepper", "Chili pepper"))),
    ("MEDIUM", (240, 200, 60), _a("Lemon", ("Tangerine", "Orange", "Orange"), "Mango", "Peach", "Tomato", "Eggplant", "Bell pepper", "Cucumber", "Garlic",
        "Peanuts", "Bread", "Croissant", "Pretzel", "Bagel", "Pancakes", "Waffle", ("Cheese wedge", "Cheese", "Cheese"), ("Poultry leg", "Chicken Leg", "Chicken leg"),
        "Bacon", "Taco", "Burrito", "Spaghetti", ("Hot beverage", "Coffee", "Coffee"), ("Beer mug", "Beer", "Beer"), ("Cocktail glass", "Cocktail", "Cocktail"))),
    ("HARD", (255, 140, 50), _a("Avocado", "Onion", "Potato", ("Baguette bread", "Baguette", "Baguette"), "Meat on bone", "Sandwich", "Sushi", "Fried shrimp",
        ("Steaming bowl", "Ramen", "Ramen"), ("Shortcake", "Slice of Cake", "Slice of cake"), "Candy", "Chocolate bar", "Shaved ice", ("Ice cream", "Ice Cream Bowl", "Ice cream bowl"),
        ("Honey pot", "Honey", "Honey"), ("Cooking", "Fried Egg", "Fried egg"), "Butter", "Salt", "Bubble tea", "Tropical drink", ("Cup with straw", "Soda", "Soda"),
        "Blueberries", "Melon", "Lobster", "Hot dog" if False else ("Pie", "Pie", "Pie"))),
    ("IMPOSSIBLE", (240, 60, 70), _a(("Kiwi fruit", "Kiwi", "Kiwi"), "Coconut", ("Leafy green", "Lettuce", "Lettuce"), "Chestnut", ("Cooked rice", "Rice", "Rice"),
        "Dumpling", "Fortune cookie", "Bento box", "Rice ball", ("Custard", "Pudding", "Pudding"), ("Canned food", "Canned Food", "Canned food"), "Olive",
        "Falafel", ("Pea pod", "Peas", "Peas"), "Beans", ("Roasted sweet potato", "Sweet Potato", "Sweet potato"), ("Ginger root", "Ginger", "Ginger"), "Crab",
        "Shrimp", "Squid", "Dango", ("Teacup without handle", "Green Tea", "Green tea"), ("Cut of meat", "Steak", "Steak"), ("Glass of milk", "Milk", "Milk"), "Moon cake")),
]
TITLE1, TITLE2 = "GUESS 100 FOODS", "BY THEIR SHADOW"
LABEL, UNIT = "GUESS THE FOOD", "FOODS"
INTRO_V = "Can you guess one hundred foods by their shadow? Three seconds each. From easy to impossible. Let's go!"
LEVEL_V = ["Level one: easy!", "Level two: medium!", "Level three: hard!", "Level four: impossible!"]
OUTRO_V = "How many foods did you get right? Comment your score, and subscribe to BrainRush Quiz for more challenges!"
SHORT_END_V = "How many did you get? Comment your score!"
GUESS_T, REVEAL_T = 3.0, 2.0
BANDS = [("0–25", "SNACK ROOKIE"), ("26–50", "FOOD LOVER"), ("51–75", "MASTER CHEF"), ("76–99", "FOOD GENIUS"), ("100", "BRAINRUSH LEGEND")]
SHORT_HOOKS = ["GUESS THE FOOD BY ITS SHADOW", "ONLY 1% GET THEM ALL", "CAN YOU GUESS THEM ALL?", "90% FAIL THE LAST ONE", "GUESS THE SHADOW IN 3 SECONDS",
               "FOOD QUIZ: EASY TO IMPOSSIBLE", "ONLY FOODIES GET THEM ALL", "GUESS THE FOOD IN 3 SECONDS", "SMARTER THAN 98%?", "IMPOSSIBLE FOOD QUIZ"]
CLIFF_FROM = 99   # SEM cliffhanger (teste A/B contra a série dos animais)
