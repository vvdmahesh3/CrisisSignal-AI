"""
CrisisSignal AI — ML Training Data
Labeled examples for the TF-IDF + LinearSVC classifier.

Phase 2.1: Each example is (text, label). Labels match CATEGORY_KEYWORDS
in ai_engine.py: fire, medical, theft, violence, infra, general.

The classifier learns from these examples so that natural-language
paraphrases ("something burning upstairs") are classified correctly
even when they miss the exact keyword list.

To retrain: run `flask train-classifier`
"""

TRAINING_DATA = [

    # ── FIRE ──────────────────────────────────────────────────
    ("There is smoke coming from the kitchen area", "fire"),
    ("I can smell something burning near the staircase", "fire"),
    ("Flames visible on the third floor of hostel block C", "fire"),
    ("Heavy smoke in the corridor cannot breathe properly", "fire"),
    ("Something is on fire near the parking lot help", "fire"),
    ("The lab is burning people are running outside", "fire"),
    ("Saw sparks and smoke from the electrical panel", "fire"),
    ("Fire alarm going off smoke visible in the hallway", "fire"),
    ("Burning smell from upstairs room might be serious", "fire"),
    ("There is a blaze at the back of the building", "fire"),
    ("Ash falling from ceiling something is burning above", "fire"),
    ("Smoke filling the corridor people evacuating now", "fire"),
    ("Kitchen caught fire someone call for help", "fire"),
    ("Electrical short circuit caused a fire in room 204", "fire"),
    ("Fire spreading to adjacent rooms in the hostel block", "fire"),
    ("I see flames coming through the window on floor 2", "fire"),
    ("Something burning upstairs very strong smell of smoke", "fire"),
    ("The canteen stove exploded fire everywhere", "fire"),
    ("Hostel room is burning smoke is very thick", "fire"),
    ("Emergency fire in the library reading room", "fire"),
    ("The auditorium curtain caught fire it is spreading", "fire"),
    ("Generator room is on fire black smoke everywhere", "fire"),

    # ── MEDICAL ───────────────────────────────────────────────
    ("Person lying on the ground not moving", "medical"),
    ("Someone fainted near the library entrance", "medical"),
    ("Student collapsed on the staircase needs help now", "medical"),
    ("Person unconscious at the canteen area", "medical"),
    ("There is a lot of blood someone is injured badly", "medical"),
    ("Someone fell from the first floor needs ambulance", "medical"),
    ("Person having seizure in the classroom call doctor", "medical"),
    ("Student is not breathing need medical help urgently", "medical"),
    ("Heart attack patient near main gate please hurry", "medical"),
    ("Injury at the sports ground player cannot walk", "medical"),
    ("Someone is bleeding heavily near hostel block B", "medical"),
    ("Old person collapsed at the entrance unconscious", "medical"),
    ("Need ambulance immediately person not responding", "medical"),
    ("Accident near parking lot person is injured", "medical"),
    ("Student having trouble breathing in classroom 3B", "medical"),
    ("Person found unconscious in bathroom please send help", "medical"),
    ("Severe allergic reaction happening right now in cafeteria", "medical"),
    ("Child injured at the playground needs doctor", "medical"),
    ("Someone is having a stroke near the admin block", "medical"),
    ("Person collapsed during morning assembly urgent help needed", "medical"),
    ("Gym accident person has broken arm needs immediate help", "medical"),
    ("Staff member fainted in the office room 101", "medical"),

    # ── THEFT ─────────────────────────────────────────────────
    ("My laptop was stolen from the library", "theft"),
    ("Bag snatched near the bus stop", "theft"),
    ("Someone broke into the room while I was away", "theft"),
    ("Pickpocket incident at the canteen very crowded", "theft"),
    ("Bicycle stolen from parking near block A", "theft"),
    ("Mobile phone snatched by someone on a bike", "theft"),
    ("Unauthorized person seen taking items from hostel room", "theft"),
    ("Cash stolen from locker in the gym", "theft"),
    ("Robber seen running away from the back gate area", "theft"),
    ("My wallet is missing someone stole it at the event", "theft"),
    ("Bag missing from classroom someone took it", "theft"),
    ("Security camera footage shows someone stealing equipment", "theft"),
    ("Lab equipment has been looted overnight", "theft"),
    ("Burglar spotted entering building through broken window", "theft"),
    ("Student complained phone missing from library desk", "theft"),
    ("Items stolen from the storeroom lock is broken", "theft"),
    ("Someone snatched gold chain near the ATM machine", "theft"),
    ("Shop at the corner was robbed early this morning", "theft"),

    # ── VIOLENCE ──────────────────────────────────────────────
    ("Fight happening between two groups near the main gate", "violence"),
    ("Someone has a knife outside the hostel threatening people", "violence"),
    ("Physical assault near the cafeteria student is injured", "violence"),
    ("Group of people attacking a student near block D", "violence"),
    ("Heard gunshots near the back of the campus", "violence"),
    ("Two people fighting with weapons in the parking lot", "violence"),
    ("Student being beaten by outsiders at the side entrance", "violence"),
    ("Stabbing incident reported near the library garden", "violence"),
    ("Aggressive person threatening staff with weapon", "violence"),
    ("Mob fighting on the road in front of the campus gate", "violence"),
    ("Someone attacked the security guard and ran away", "violence"),
    ("Domestic dispute turned violent near the residences", "violence"),
    ("Man threatening people with a rod near the gate", "violence"),
    ("Multiple people involved in a fight need police", "violence"),
    ("Witness to an assault near the sports ground right now", "violence"),
    ("Person with gun seen near the administration block", "violence"),
    ("Ragging incident going on in room 305 someone is being hurt", "violence"),

    # ── INFRASTRUCTURE ────────────────────────────────────────
    ("Water leaking from the ceiling in room 202", "infra"),
    ("Power cut in the entire hostel block no electricity", "infra"),
    ("Elevator stuck between floors person trapped inside", "infra"),
    ("Gas leak smell coming from the kitchen pipeline", "infra"),
    ("Short circuit in the lab caused sparks and smoke smell", "infra"),
    ("Major flood in the basement water level rising", "infra"),
    ("Ceiling crack getting wider looks very dangerous", "infra"),
    ("Sewage overflow near the sports complex very bad smell", "infra"),
    ("Water pipeline burst on second floor everything flooded", "infra"),
    ("Internet and power both down in block B since 2 hours", "infra"),
    ("Transformer tripped power out in half the campus", "infra"),
    ("Broken staircase railing dangerous for students", "infra"),
    ("AC unit leaking water onto electrical switchboard", "infra"),
    ("Gas smell very strong near cooking area please check", "infra"),
    ("Lift not working person with disability stuck on floor 4", "infra"),
    ("Road cave-in near the hostel block area dangerous", "infra"),
    ("Plumbing issue severe flood in the ground floor corridor", "infra"),

    # ── GENERAL (unclassified/noise/low signal) ───────────────
    ("I think I saw something weird near the gate", "general"),
    ("Not sure if this is an issue but something looks off", "general"),
    ("Strange noise coming from the storage room", "general"),
    ("Suspicious person walking around the campus", "general"),
    ("Unusual activity near the admin block", "general"),
    ("Lost my keys near the cafeteria", "general"),
    ("Stray dogs near the entrance could be a problem", "general"),
    ("Power went off briefly but came back think it's fine", "general"),
    ("Someone left food on the stairs not sure if problem", "general"),
    ("Noticed someone unfamiliar in the hallway", "general"),
    ("Unattended bag on the bench near the garden", "general"),
    ("Strange smell in the corridor not sure what it is", "general"),
    ("Student argument getting slightly heated in the quad", "general"),
    ("Maintenance work making a lot of noise late at night", "general"),
]
