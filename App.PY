import streamlit as st
import random
import time
import pandas as pd

# ==============================================================================
# ZONE 1: CONFIGURATION & STATIC DATA (The Universe)
# ==============================================================================
try:
    st.set_page_config(page_title="College Football Mogul V7.8", page_icon="🏈", layout="wide")
except:
    pass

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }

    /* DASHBOARD WIDGETS */
    .security-box { background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px; }
    .security-safe { color: #28a745; font-weight: bold; }
    .security-warm { color: #fd7e14; font-weight: bold; }
    .security-hot { color: #dc3545; font-weight: bold; }

    /* FINANCIAL REPORT BOX */
    .finance-alert { background-color: #d1e7dd; color: #0f5132; border: 1px solid #badbcc; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-weight: bold; }
    .nil-alert { background-color: #cff4fc; color: #055160; border: 1px solid #b6effb; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center; font-size: 1.2em; font-weight: bold; }

    /* GAME CARDS */
    .game-card { padding: 10px; border-radius: 8px; margin-bottom: 12px; border: 1px solid #ddd; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .game-card-win { border-left: 5px solid #28a745; }
    .game-card-loss { border-left: 5px solid #dc3545; }
    .game-card-pending { border-left: 5px solid #6c757d; background: #f8f9fa; }
    .game-card-rival { border: 2px solid #ffc107 !important; background-color: #fffbf0 !important; }

    .card-header { display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px;}
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; font-size: 0.85em; }
    .stat-row { display: flex; justify-content: space-between; }

    /* STAFF CARDS */
    .staff-card { background: white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    .staff-role { font-size: 0.8em; color: #666; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
    .staff-name { font-size: 1.1em; font-weight: 800; color: #333; }
    .badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75em; font-weight: bold; margin-right: 5px; display: inline-block;}
    .badge-tier-s { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    .badge-tier-a { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .badge-tier-f { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    .badge-trait { background: #e2e3e5; color: #383d41; }

    .recruiting-intel { background-color: #e0f7fa; border-left: 5px solid #006064; padding: 15px; margin-bottom: 12px; border-radius: 4px; }
    .bracket-box { background-color: #2c3e50; color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 10px; }
    .bracket-row { display: flex; justify-content: space-between; padding: 5px; border-bottom: 1px solid #444; }
    .news-box { background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .news-item { padding: 6px 0; border-bottom: 1px solid #f1f1f1; }
    .news-item:last-child { border-bottom: none; }
    </style>
""", unsafe_allow_html=True)

POSITIONS = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"]
REGION_STRENGTH = {"South": 1.08, "Midwest": 1.05, "West": 1.05, "North": 1.02}
SCHEMES = {"Offense": ["Air Raid", "Smashmouth", "Pro Style"], "Defense": ["3-3-5 Cloud", "4-4 Heavy", "Man Coverage"]}
COUNTERS = {
    "Air Raid": "3-3-5 Cloud",
    "Smashmouth": "4-4 Heavy",
    "Pro Style": "Man Coverage",
    "3-3-5 Cloud": "Smashmouth",
    "4-4 Heavy": "Air Raid",
    "Man Coverage": "Pro Style"
}
TRAITS = ["❄️ Clutch", "🚀 Speedster", "🧠 General", "😤 Enforcer"]
COACH_TRAITS = {"None": "None", "Recruiter": "+10% Recruiting", "Tactician": "+3 Game Boost",
                "Air Raid": "+2 Scheme", "Smashmouth": "+2 Scheme", "Pro Style": "+2 Scheme"}
BOWL_MAPPING = {
    "Elite": ["Rose Bowl", "Sugar Bowl", "Orange Bowl", "Cotton Bowl", "Peach Bowl", "Fiesta Bowl"],
    "High": ["Citrus Bowl", "Alamo Bowl", "Pop-Tarts Bowl", "Gator Bowl"],
    "Mid": ["Liberty Bowl", "Music City Bowl", "Las Vegas Bowl"],
    "Low": ["Gasparilla Bowl", "Boca Raton Bowl", "Potato Bowl"]
}

TEAMS_DB = {
    "Georgia": {"color": "#BA0C2F"}, "Alabama": {"color": "#9E1B32"}, "Ohio State": {"color": "#BB0000"},
    "Michigan": {"color": "#00274C"}, "Texas": {"color": "#BF5700"}, "Oklahoma": {"color": "#841617"},
    "Oregon": {"color": "#154733"}, "Washington": {"color": "#4B2E83"}, "Florida St": {"color": "#782F40"},
    "Miami": {"color": "#005030"}, "Penn State": {"color": "#041E42"}, "Notre Dame": {"color": "#0C2340"},
    "LSU": {"color": "#461D7C"}, "Ole Miss": {"color": "#CE1126"}, "Tennessee": {"color": "#FF8200"},
    "Auburn": {"color": "#0C2340"}, "Indiana": {"color": "#990000"}, "Purdue": {"color": "#CEB888"},
    "Colorado": {"color": "#CFB87C"}, "USC": {"color": "#990000"}, "Boise State": {"color": "#0033A0"},
    "San Jose State": {"color": "#0055A2"}
}

REAL_WORLD_INIT = {
    "Indiana": {"Prestige": 99, "Talent": 86, "Tier": 1, "Rival": "Purdue"},
    "Ohio State": {"Prestige": 95, "Talent": 94, "Tier": 1, "Rival": "Michigan"},
    "Miami": {"Prestige": 94, "Talent": 89, "Tier": 1, "Rival": "Florida St"},
    "Oregon": {"Prestige": 93, "Talent": 92, "Tier": 1, "Rival": "Washington"},
    "Georgia": {"Prestige": 92, "Talent": 96, "Tier": 1, "Rival": "Florida"},
    "Ole Miss": {"Prestige": 91, "Talent": 88, "Tier": 1, "Rival": "Mississippi St"},
    "Texas Tech": {"Prestige": 90, "Talent": 84, "Tier": 2, "Rival": "Baylor"},
    "Texas A&M": {"Prestige": 89, "Talent": 91, "Tier": 2, "Rival": "Texas"},
    "Alabama": {"Prestige": 85, "Talent": 95, "Tier": 1, "Rival": "Auburn"},
    "Notre Dame": {"Prestige": 87, "Talent": 90, "Tier": 1, "Rival": "USC"},
    "BYU": {"Prestige": 86, "Talent": 82, "Tier": 2, "Rival": "Utah"},
    "Texas": {"Prestige": 84, "Talent": 97, "Tier": 1, "Rival": "Oklahoma"},
    "Oklahoma": {"Prestige": 83, "Talent": 90, "Tier": 2, "Rival": "Texas"},
    "Utah": {"Prestige": 82, "Talent": 85, "Tier": 2, "Rival": "BYU"},
    "Vanderbilt": {"Prestige": 80, "Talent": 78, "Tier": 3, "Rival": "Tennessee"},
    "USC": {"Prestige": 79, "Talent": 89, "Tier": 2, "Rival": "Notre Dame"},
    "Michigan": {"Prestige": 78, "Talent": 91, "Tier": 2, "Rival": "Ohio State"},
    "Penn State": {"Prestige": 77, "Talent": 88, "Tier": 2, "Rival": "Ohio State"},
    "LSU": {"Prestige": 76, "Talent": 92, "Tier": 2, "Rival": "Alabama"},
    "Florida St": {"Prestige": 70, "Talent": 87, "Tier": 3, "Rival": "Miami"},
    "Colorado": {"Prestige": 75, "Talent": 85, "Tier": 2, "Rival": "Nebraska"},
    "Boise State": {"Prestige": 72, "Talent": 79, "Tier": 3, "Rival": "Fresno St"},
    "Tulane": {"Prestige": 74, "Talent": 77, "Tier": 3, "Rival": "LSU"}
}

CONFERENCES = {
    "SEC": ["Georgia", "Alabama", "Texas", "LSU", "Tennessee", "Oklahoma", "Auburn", "Texas A&M", "Ole Miss", "Vanderbilt", "Florida", "Mississippi St"],
    "Big Ten": ["Ohio State", "Oregon", "Penn State", "Michigan", "USC", "Wisconsin", "Iowa", "Washington", "Indiana", "Nebraska", "Purdue"],
    "ACC": ["Florida St", "Clemson", "Miami", "Stanford", "Cal", "Louisville", "UNC", "Virginia Tech", "SMU"],
    "Big 12": ["Utah", "TCU", "Baylor", "Texas Tech", "Arizona State", "Colorado", "Kansas State", "Oklahoma St", "BYU", "Arizona"],
    "G5": ["Boise State", "San Jose State", "San Diego St", "Nevada", "Wyoming", "Air Force", "Colorado St", "Fresno St", "Tulane", "Memphis", "Navy", "Army"]
}
ALL_TEAMS = [t for c in CONFERENCES.values() for t in c]

# ==============================================================================
# ZONE 2: HELPER FUNCTIONS
# ==============================================================================
def helper_format_cash(amount):
    return f"${amount/1000000:.1f}M" if amount >= 1000000 else f"${int(amount/1000)}K"

def generate_name():
    first = ["Marcus", "Trey", "Deion", "Caleb", "Jalen", "Bo", "Ty", "Zay", "Kool-Aid", "Tank", "Arch", "Shedeur", "Quinn", "Travis", "Ashton"]
    last = ["King", "Sanders", "Ewers", "Milroe", "Hunter", "Bond", "Nix", "Penix", "Bowers", "Manning", "Gabriel", "Beck", "Jeanty", "Judkins"]
    return f"{random.choice(first)} {random.choice(last)}"

def generate_coach_name():
    first = ["Kirby", "Nick", "Ryan", "Lane", "Dabo", "Lincoln", "Steve", "Chip", "Deion", "Marcus", "Dan", "Kalen"]
    last = ["Smart", "Saban", "Day", "Kiffin", "Swinney", "Riley", "Sarkisian", "Kelly", "Sanders", "Freeman", "Lanning", "DeBoer"]
    return f"{random.choice(first)} {random.choice(last)}"

def get_letter_grade(val):
    if val >= 9: return "A+"
    elif val >= 8: return "A"
    elif val >= 7: return "B"
    elif val >= 5: return "C"
    elif val >= 3: return "D"
    else: return "F"

def calculate_saban_score(career_stats, prestige):
    return int((career_stats['w'] * 1) + (career_stats['bowl_w'] * 5) + (career_stats['titles'] * 50) + (prestige * 0.5))

def get_bowl_name(rank):
    if rank <= 12: return "CFP Playoff"
    elif rank <= 25: return random.choice(BOWL_MAPPING["Elite"])
    elif rank <= 40: return random.choice(BOWL_MAPPING["High"])
    elif rank <= 80: return random.choice(BOWL_MAPPING["Mid"])
    else: return random.choice(BOWL_MAPPING["Low"])

def get_conference(team: str) -> str:
    for conf, teams in CONFERENCES.items():
        if team in teams:
            return conf
    return "G5"

def role_rating(cand: dict, role: str) -> int:
    if role in ["HC", "OC"]:
        return cand.get("off", 1)
    if role == "DC":
        return cand.get("def", 1)
    if role == "Scout":
        return cand.get("recruit", 1)
    return cand.get("off", 1)

def compute_team_needs(roster: dict, k: int = 3) -> list:
    sorted_pos = sorted(roster.items(), key=lambda x: x[1])
    return [p for p, _ in sorted_pos[:k]]

def generate_star_player(position, tier):
    return {"id": random.randint(10000, 99999), "name": generate_name(), "pos": position,
            "rating": min(99, 85 + random.randint(0, 10)), "year": "Fr", "trait": random.choice(TRAITS)}

def generate_ga_coach(role):
    return {"name": f"GA {generate_name()}", "role": role, "off": random.randint(1, 3),
            "def": random.randint(1, 3), "recruit": random.randint(1, 2), "trait": "None",
            "salary": 50000, "history": "Former Player", "scouted": True}

def add_news(text: str):
    if "news" not in st.session_state:
        st.session_state.news = []
    st.session_state.news.insert(0, f"{st.session_state.year}: {text}")
    st.session_state.news = st.session_state.news[:12]

# ==============================================================================
# ZONE 3: THE ENGINE (Math & Logic)
# ==============================================================================
def engine_calculate_revenue(tier, marketing_lvl, inflation):
    if not tier: tier = 3
    base = {1: 40000000, 2: 25000000, 3: 10000000, 4: 5000000}.get(tier, 5000000)
    marketing_bonus = marketing_lvl * 2000000
    total = (base + marketing_bonus) * inflation
    return int(total)

def engine_generate_coach(role, tier):
    cost = random.randint(4000000, 8000000) if tier == 1 else random.randint(500000, 3500000)
    trait_pool = list(COACH_TRAITS.keys())
    if role == "OC":
        trait_pool = ["Air Raid", "Smashmouth", "Pro Style", "Recruiter", "Tactician"]
    base = 8 if tier == 1 else (5 if tier == 2 else 1)
    return {"name": generate_coach_name(), "role": role,
            "off": min(10, base + random.randint(0, 3)),
            "def": min(10, base + random.randint(0, 3)),
            "recruit": min(10, base + random.randint(0, 3)),
            "trait": random.choice(trait_pool),
            "salary": cost, "history": "External Hire", "scouted": False}

def engine_generate_roster(tier, base_ovr=None):
    base = base_ovr if base_ovr else (90 if tier == 1 else 74)
    roster = {}
    for p in POSITIONS:
        roster[p] = min(99, max(40, base + random.randint(-4, 4)))
    return roster

def engine_generate_schedule(my_team, my_conf, rival):
    conf_foes = [t for t in CONFERENCES.get(my_conf, CONFERENCES['G5']) if t != my_team]
    schedule = random.sample(conf_foes, min(8, len(conf_foes)))
    needed = 12 - len(schedule)
    non_conf = [t for t in ALL_TEAMS if t not in CONFERENCES.get(my_conf, []) and t != my_team]
    schedule += random.sample(non_conf, min(len(non_conf), needed))

    if rival in ALL_TEAMS:
        if rival in schedule:
            schedule.remove(rival)
        schedule.append(rival)
    else:
        random.shuffle(schedule)

    while len(schedule) > 12:
        schedule.pop(0)
    return schedule

def engine_play_game(my_rating, opp_rating, staff, schemes, opp_schemes, game_plan, opp_coaches, is_home, is_rival, fac_lvl, my_roster):
    # 1. Roster Talent
    my_off = (my_roster["QB"] * 0.3) + (my_roster["OL"] * 0.25) + ((my_roster["RB"] + my_roster["WR"]) / 2 * 0.45)
    my_def = sum(my_roster[p] for p in ["DL", "LB", "DB"]) / 3

    talent_gap = (my_rating**2 - opp_rating**2) / 125.0

    # 2. Scheme
    scheme_bonus = 0
    if COUNTERS.get(opp_schemes.get('Def', "Man Coverage"), "Pro Style") == schemes.get('Off', "Pro Style"):
        scheme_bonus += 4
    elif COUNTERS.get(schemes.get('Off', "Pro Style"), "Man Coverage") == opp_schemes.get('Def', "Man Coverage"):
        scheme_bonus -= 4

    # 3. Coaching (1.1x)
    my_oc = staff.get('OC', {'off': 3}).get('off', 3)
    my_dc = staff.get('DC', {'def': 3}).get('def', 3)
    opp_oc = opp_coaches.get('OC', 5)
    opp_dc = opp_coaches.get('DC', 5)

    def get_tier_bonus(rating):
        if rating >= 8: return 3
        elif rating <= 4: return -3
        return 0

    coaching_net = ((get_tier_bonus(my_oc) - get_tier_bonus(opp_dc)) * 1.1) + ((get_tier_bonus(my_dc) - get_tier_bonus(opp_oc)) * 1.1)

    # Staff trait impacts (lightweight but meaningful)
    hc_trait = staff.get("HC", {}).get("trait", "None")
    if hc_trait == "Tactician":
        coaching_net += 1.5

    if staff.get("OC", {}).get("trait") in ["Air Raid", "Smashmouth", "Pro Style"] and staff.get("OC", {}).get("trait") == schemes.get("Off"):
        scheme_bonus += 2
    if staff.get("DC", {}).get("trait") in ["Air Raid", "Smashmouth", "Pro Style"] and staff.get("DC", {}).get("trait") == schemes.get("Off"):
        scheme_bonus += 1  # small bump (DC helps overall identity)

    # 4. Home field (smooth)
    home_bonus = 0
    if is_home:
        home_bonus = max(0, round((fac_lvl - 1) / 3))  # 0..3ish
    else:
        # small chance of "hostile road" effect
        if random.random() < 0.25:
            home_bonus = -max(0, round((fac_lvl - 1) / 4))

    # 5. Variance
    var_mult = 2.0 if is_rival else 1.0
    if game_plan == "Aggressive":
        var_mult *= 1.5
    elif game_plan == "Conservative":
        var_mult *= 0.75

    # 6. Monte Carlo (100x)
    sims = []
    for _ in range(100):
        luck = random.gauss(0, 3.0 * var_mult)
        sims.append(talent_gap + scheme_bonus + coaching_net + home_bonus + luck)

    margin = sum(sims) / len(sims)

    # Score model (more football-ish)
    total_points = int(max(20, min(85, random.gauss(55, 10))))
    spread = max(-24, min(24, margin))
    my_score = int(round((total_points / 2) + (spread / 2)))
    opp_score = int(total_points - my_score)
    my_score = max(0, min(70, my_score))
    opp_score = max(0, min(70, opp_score))

    visual_my_off = int(my_off + get_tier_bonus(my_oc))
    visual_my_def = int(my_def + get_tier_bonus(my_dc))

    return {
        "result": "W" if margin > 0 else "L",
        "score": f"{my_score}-{opp_score}",
        "stats": {
            "qb_duel": [int(my_roster["QB"]), int(opp_rating)],
            "off_vs_def": [visual_my_off, int(opp_rating + get_tier_bonus(opp_dc))],
            "def_vs_off": [visual_my_def, int(opp_rating + get_tier_bonus(opp_oc))],
            "staff": [f"{my_oc}/{my_dc}", f"{opp_oc}/{opp_dc}"],
            "raw_roster": int((my_off + my_def) / 2)
        }
    }

def engine_evolve_universe(opponents_db):
    for team, data in opponents_db.items():
        wins = int((data['OVR'] / 100) * 12) + random.randint(-2, 2)
        wins = max(0, min(12, wins))

        change = 0
        if wins >= 10: change = 3
        elif wins <= 4: change = -3
        data['Prestige'] = max(20, min(99, data['Prestige'] + change))

        if data['Prestige'] > 80 and wins < 6:  # Fire
            data['Coaches'] = {"OC": random.randint(7, 9), "DC": random.randint(7, 9)}
        elif data['Prestige'] < 70 and wins > 9:  # Poach
            data['Coaches'] = {"OC": random.randint(3, 6), "DC": random.randint(3, 6)}

        base_ovr = int(data['Prestige'] * 0.9)
        data['OVR'] = base_ovr + random.randint(-3, 3)
    return opponents_db

def engine_generate_portal_players():
    players = []
    for _ in range(3):
        players.append({"name": f"{generate_name()}", "pos": random.choice(POSITIONS), "rating": random.randint(90, 99),
                        "cost": random.randint(3000000, 6000000), "trait": random.choice(TRAITS), "year": "Sr"})
    for _ in range(3):
        players.append({"name": f"{generate_name()}", "pos": random.choice(POSITIONS), "rating": random.randint(80, 89),
                        "cost": random.randint(1000000, 2500000), "trait": random.choice(TRAITS), "year": "Sr"})
    for _ in range(4):
        players.append({"name": f"{generate_name()}", "pos": random.choice(POSITIONS), "rating": random.randint(70, 78),
                        "cost": random.randint(150000, 500000), "trait": "None", "year": "Jr"})
    return players

def process_recruiting(budget, allocations, staff, prestige, inflation):
    results = {"roster_updates": {}, "gems": [], "cost": sum(allocations.values()), "booster_bonus": 0}
    if results["cost"] > budget:
        return None

    scout_rate = staff.get('Scout', {'recruit': 1}).get('recruit', 1)

    cost_mult = 1.2
    if scout_rate >= 8:
        cost_mult = 0.8
    elif scout_rate >= 5:
        cost_mult = 1.0

    base_cost = 800000 * inflation * cost_mult

    home_region = st.session_state.home_region
    hot_positions = st.session_state.hotspots.get(home_region, [])
    needs = st.session_state.get("team_needs", [])

    for pos, amount in allocations.items():
        # If you ignore a position, it backslides a bit
        if amount < base_cost * 0.5:
            change = -random.randint(2, 6)
            results["roster_updates"][pos] = change
            continue

        pipeline_bonus = 1.15 if pos in hot_positions else 1.0
        need_bonus = 1.25 if pos in needs else 0.90  # reward needs; mild penalty off-need

        spend_ratio = max(0.0, amount / base_cost)
        dim = spend_ratio ** 0.85  # diminishing returns

        prestige_factor = max(0.85, min(1.15, (prestige / 75) ** 0.35))

        change = dim * pipeline_bonus * need_bonus * prestige_factor
        change = max(-6, min(12, change))  # cap

        # Gems
        gem_chance = 0.10
        if pos in needs: gem_chance += 0.07
        if pos in hot_positions: gem_chance += 0.05
        if staff.get("HC", {}).get("trait") == "Recruiter": gem_chance += 0.03
        if amount > base_cost * 1.2 and random.random() < gem_chance:
            change += 5
            new_star = generate_star_player(pos, 1)
            new_star['name'] += " (GEM)"
            results["gems"].append(new_star)
            results["booster_bonus"] += 250000

        # Recruiter trait improves yields a bit
        if staff.get("HC", {}).get("trait") == "Recruiter":
            change *= 1.08

        results["roster_updates"][pos] = change

    return results

# ==============================================================================
# ZONE 4: STATE MANAGEMENT & BRACKET LOGIC
# ==============================================================================
def initialize_game_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = 'SETUP'
        st.session_state.year = 2026
        st.session_state.budget = 0
        st.session_state.prestige = 50
        st.session_state.job_security = 80
        st.session_state.expected_wins = 6
        st.session_state.tenure = 1
        st.session_state.roster = {p: 75 for p in POSITIONS}
        st.session_state.active_transfers = {p: False for p in POSITIONS}
        st.session_state.stars = []
        st.session_state.staff = {}
        st.session_state.facilities = {"Marketing": 1, "Training": 1, "Stadium": 1}
        st.session_state.history = []
        st.session_state.record = {"w": 0, "l": 0}
        st.session_state.opponents_db = {}
        st.session_state.my_schemes = {"Off": "Pro Style", "Def": "Man Coverage"}
        st.session_state.career_stats = {"w": 0, "l": 0, "bowl_w": 0, "bowl_l": 0, "titles": 0}
        st.session_state.season_logs = []
        st.session_state.schedule = []
        st.session_state.season_simulated = False  # now means "season finished"
        st.session_state.hotspots = {}
        st.session_state.portal_players = []
        st.session_state.candidates = {}
        st.session_state.postseason_data = {"Type": None, "Rank": 0, "Round": 0, "Matches": []}
        st.session_state.revenue_report = None
        st.session_state.inflation = 1.0
        st.session_state.team_needs = []
        st.session_state.game_plan = "Normal"
        st.session_state.week_index = 0
        st.session_state.news = []

    # SAFETY CHECKS
    if 'inflation' not in st.session_state: st.session_state.inflation = 1.0
    if 'revenue_report' not in st.session_state: st.session_state.revenue_report = None
    if 'postseason_data' not in st.session_state: st.session_state.postseason_data = {"Type": None, "Rank": 0, "Round": 0, "Matches": []}
    if 'team_needs' not in st.session_state: st.session_state.team_needs = []
    if 'game_plan' not in st.session_state: st.session_state.game_plan = "Normal"
    if 'week_index' not in st.session_state: st.session_state.week_index = 0
    if 'news' not in st.session_state: st.session_state.news = []

def generate_hotspots():
    hotspots = {}
    for reg in REGION_STRENGTH.keys():
        hotspots[reg] = random.sample(POSITIONS, 2)
    return hotspots

def init_playoff_bracket(user_rank, user_team_name):
    # Determine the top 12 teams (exclude user to prevent duplicate)
    sorted_ai = [(t, d) for t, d in st.session_state.opponents_db.items() if t != user_team_name]
    sorted_ai = sorted(sorted_ai, key=lambda x: x[1]['OVR'], reverse=True)

    top_12 = []
    ai_idx = 0
    for r in range(1, 13):
        if r == user_rank:
            top_12.append(user_team_name)
        else:
            top_12.append(sorted_ai[ai_idx][0])
            ai_idx += 1

    r1_matches = [
        {"high": 5, "low": 12, "t1": top_12[4], "t2": top_12[11], "winner": None},
        {"high": 6, "low": 11, "t1": top_12[5], "t2": top_12[10], "winner": None},
        {"high": 7, "low": 10, "t1": top_12[6], "t2": top_12[9], "winner": None},
        {"high": 8, "low": 9,  "t1": top_12[7], "t2": top_12[8], "winner": None}
    ]
    qf_seeds = [top_12[0], top_12[1], top_12[2], top_12[3]]
    return {"Type": "CFP", "Round": 1, "Matches": r1_matches, "Seeds": top_12, "QF_Seeds": qf_seeds, "UserAlive": True, "Rank": user_rank}

initialize_game_state()

# ==============================================================================
# ZONE 5: UI CONTROLLERS
# ==============================================================================
def run_setup():
    st.title("🏆 College Football Mogul V7.8")
    st.markdown("### Dynasty Mode (Jan 2026)")
    c1, c2 = st.columns(2)
    name = c1.text_input("AD Name", "Coach Prime")
    diff = c2.selectbox("Difficulty", ["Normal", "Hard", "Easy"])

    sorted_teams = sorted(REAL_WORLD_INIT.keys()) + sorted([t for t in ALL_TEAMS if t not in REAL_WORLD_INIT])
    team = st.selectbox("Select Team", sorted_teams)

    if team in REAL_WORLD_INIT:
        d = REAL_WORLD_INIT[team]
        tier = d['Tier']
        budget = 25000000 if tier == 1 else (15000000 if tier == 2 else 5000000)
        conf = get_conference(team)
        rival = d.get('Rival', 'Rival')
    else:
        tier, budget, conf, rival = 3, 5000000, get_conference(team), "Rival"

    expect = 10 if tier == 1 else (8 if tier == 2 else (6 if tier == 3 else 4))
    st.info(f"**{team}** | Conf: {conf} | Tier: {tier} | Budget: {helper_format_cash(budget)} | Rival: {rival}")
    st.caption(f"Expectation: {expect}+ Wins")

    if st.button("Start Dynasty", type="primary"):
        st.session_state.ad_name = name
        st.session_state.team_name = team
        st.session_state.team_color = TEAMS_DB.get(team, {}).get('color', '#333333')
        st.session_state.team_conf = conf
        st.session_state.team_rival = rival
        st.session_state.home_region = "South"
        st.session_state.expected_wins = expect
        st.session_state.school_tier = tier
        st.session_state.budget = int(budget * (0.75 if diff == "Hard" else 1.25 if diff == "Easy" else 1.0))
        st.session_state.roster = engine_generate_roster(tier, REAL_WORLD_INIT.get(team, {}).get('Talent'))
        st.session_state.prestige = REAL_WORLD_INIT.get(team, {}).get('Prestige', 60)
        st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)

        # Staff
        st.session_state.staff = {}
        for r in ["HC", "OC", "DC", "Scout"]:
            st.session_state.staff[r] = engine_generate_coach(r, tier)

        val = 10 if tier == 1 else 5
        st.session_state.facilities = {"Marketing": val, "Training": val, "Stadium": val}

        # Universe
        st.session_state.opponents_db = {}
        for opp in ALL_TEAMS:
            if opp in REAL_WORLD_INIT:
                data = REAL_WORLD_INIT[opp]
                st.session_state.opponents_db[opp] = {
                    "Prestige": data['Prestige'], "OVR": data['Talent'],
                    "Off": random.choice(list(SCHEMES["Offense"])),
                    "Def": random.choice(list(SCHEMES["Defense"])),
                    "Coaches": {"OC": random.randint(5, 9), "DC": random.randint(5, 9)}
                }
            else:
                pres = 85 if opp in CONFERENCES['SEC'] else 65
                ovr = 82 if opp in CONFERENCES['SEC'] else 70
                st.session_state.opponents_db[opp] = {
                    "Prestige": pres, "OVR": ovr, "Off": "Pro Style", "Def": "Man Coverage",
                    "Coaches": {"OC": 5, "DC": 5}
                }

        st.session_state.hotspots = generate_hotspots()
        st.session_state.schedule = engine_generate_schedule(team, conf, rival)

        # Season state (weekly play)
        st.session_state.week_index = 0
        st.session_state.record = {"w": 0, "l": 0}
        st.session_state.season_logs = []
        st.session_state.season_simulated = False

        st.session_state.game_state = 'DASHBOARD'
        add_news(f"{team} hires {st.session_state.staff['HC']['name']} as HC.")
        st.rerun()

def show_dashboard():
    thresh = 0 if st.session_state.tenure <= 2 else 30
    if st.session_state.job_security < thresh:
        st.session_state.game_state = "FIRED"
        st.rerun()

    if st.session_state.revenue_report:
        st.markdown(f"<div class='finance-alert'>💰 FINANCIAL REPORT<br>{st.session_state.revenue_report}</div>", unsafe_allow_html=True)

    sec = st.session_state.job_security
    sec_cls = "security-safe" if sec > 75 else ("security-warm" if sec > 40 else "security-hot")
    st.markdown(f"<div class='security-box'>Year {st.session_state.tenure} | Security: <span class='{sec_cls}'>{sec}%</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background-color: {st.session_state.team_color}; padding: 10px; border-radius: 5px; color: white;'><h2>{st.session_state.team_name}</h2></div>", unsafe_allow_html=True)

    raw_roster_val = int(sum(st.session_state.roster.values()) / 7)
    curr_ovr = int((st.session_state.roster['QB'] * 0.3) +
                   (st.session_state.roster['OL'] * 0.25) +
                   ((st.session_state.roster['RB'] + st.session_state.roster['WR']) / 2 * 0.45) +
                   (st.session_state.facilities['Training'] * 0.5))
    st.session_state.team_rating = curr_ovr

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Budget", helper_format_cash(st.session_state.budget))
    c2.metric("Team OVR", curr_ovr, f"Raw Talent: {raw_roster_val}")
    c3.metric("Record", f"{st.session_state.record['w']}-{st.session_state.record['l']}")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    c4.metric("Legacy Score", saban, f"Titles: {st.session_state.career_stats['titles']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Strategy", "Staff", "Facilities", "Season (Weekly)", "Legacy"])

    with tab1:
        c1, c2 = st.columns(2)
        st.session_state.my_schemes["Off"] = c1.selectbox("Offense", SCHEMES["Offense"])
        st.session_state.my_schemes["Def"] = c2.selectbox("Defense", SCHEMES["Defense"])
        st.write("Unit Strength")
        for p, v in st.session_state.roster.items():
            lab = f"{p}: {int(v)}" + (" (RENTAL)" if st.session_state.active_transfers.get(p) else "")
            st.progress(min(1.0, v / 100), lab)

    with tab2:
        st.markdown("### 🧢 Current Staff")
        cols = st.columns(4)
        roles = ["HC", "OC", "DC", "Scout"]
        for i, role in enumerate(roles):
            with cols[i]:
                if role in st.session_state.staff:
                    c = st.session_state.staff[role]
                    rtg = role_rating(c, role)
                    badge_cls = "badge-tier-s" if rtg >= 8 else ("badge-tier-a" if rtg >= 5 else "badge-tier-f")
                    st.markdown(f"""
                    <div class='staff-card'>
                        <div class='staff-role'>{role}</div>
                        <div class='staff-name'>{c['name']}</div>
                        <div><span class='badge {badge_cls}'>RATING: {rtg}</span> <span class='badge badge-trait'>{c.get('trait','None')}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Fire", key=f"fire_{role}"):
                        add_news(f"{st.session_state.team_name} parts ways with {c['name']} ({role}).")
                        del st.session_state.staff[role]
                        st.rerun()
                else:
                    st.warning(f"{role} VACANT")
        st.divider()
        st.markdown("### 📋 Job Market")
        vacancies = [r for r in roles if r not in st.session_state.staff]
        if vacancies:
            for role in vacancies:
                if role not in st.session_state.candidates:
                    st.session_state.candidates[role] = [engine_generate_coach(role, random.randint(1, 3)) for _ in range(3)]

                cols = st.columns(3)
                for i, cand in enumerate(st.session_state.candidates[role]):
                    with cols[i]:
                        rr = role_rating(cand, role)
                        vis_rate = f"{rr}" if cand['scouted'] else f"{get_letter_grade(rr)}"
                        vis_trait = cand['trait'] if cand['scouted'] else "???"
                        st.markdown(f"""
                        <div class='staff-card'>
                            <div class='staff-name'>{cand['name']}</div>
                            <div style='font-size:0.8em'>{cand['history']}</div>
                            <div style='margin:5px 0'><span class='badge badge-trait'>{role} OVR: {vis_rate}</span> <span class='badge badge-trait'>Trait: {vis_trait}</span></div>
                            <div style='font-weight:bold'>{helper_format_cash(cand['salary'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("Hire", key=f"h_{role}_{i}"):
                            if st.session_state.budget >= cand['salary']:
                                st.session_state.budget -= cand['salary']
                                st.session_state.staff[role] = cand
                                add_news(f"{st.session_state.team_name} hires {cand['name']} as {role}.")
                                del st.session_state.candidates[role]
                                st.rerun()
                        if not cand['scouted'] and b2.button("Scout ($25k)", key=f"sc_{role}_{i}"):
                            if st.session_state.budget >= 25000:
                                st.session_state.budget -= 25000
                                cand['scouted'] = True
                                st.rerun()

                if st.button(f"Promote GA (Free)", key=f"ga_{role}"):
                    ga = generate_ga_coach(role)
                    st.session_state.staff[role] = ga
                    add_news(f"{st.session_state.team_name} promotes {ga['name']} to {role}.")
                    st.rerun()

    with tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Marketing", st.session_state.facilities['Marketing'], delta="Rev: +$2M/yr")
            if st.button("Upgrade ($1M)", key="um"):
                if st.session_state.budget >= 1000000:
                    st.session_state.budget -= 1000000
                    st.session_state.facilities['Marketing'] += 1
                    add_news("Marketing department upgraded. Boosters are pleased.")
                    st.rerun()
        with c2:
            st.metric("Training", st.session_state.facilities['Training'], delta="OVR Boost")
            if st.button("Upgrade ($3M)", key="ut"):
                if st.session_state.budget >= 3000000:
                    st.session_state.budget -= 3000000
                    st.session_state.facilities['Training'] += 1
                    add_news("Training facility upgraded. Players recover faster.")
                    st.rerun()
        with c3:
            st.metric("Stadium", st.session_state.facilities['Stadium'], delta="Prestige / Home Field")
            if st.button("Upgrade ($10M)", key="us"):
                if st.session_state.budget >= 10000000:
                    st.session_state.budget -= 10000000
                    st.session_state.facilities['Stadium'] += 1
                    st.session_state.prestige = min(99, st.session_state.prestige + 1)
                    add_news("Stadium upgraded. Home field advantage grows.")
                    st.rerun()

    with tab4:
        if len(st.session_state.staff) < 4:
            st.error("Fill Staff First!")
            return

        if not st.session_state.schedule:
            st.session_state.schedule = engine_generate_schedule(st.session_state.team_name, st.session_state.team_conf, st.session_state.team_rival)

        # Weekly decision UI (UI/UX #5)
        st.session_state.game_plan = st.selectbox("Weekly Gameplan", ["Conservative", "Normal", "Aggressive"], index=["Conservative", "Normal", "Aggressive"].index(st.session_state.game_plan))

        # Schedule view with played/pending
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Weeks 1–6")
            for i in range(6):
                opp = st.session_state.schedule[i]
                played = next((x for x in st.session_state.season_logs if x["Week"] == i + 1), None)
                is_rival = opp == st.session_state.team_rival
                if played:
                    res = "W" if played["Score"].startswith("W") else "L"
                    css = "game-card-win" if res == "W" else "game-card-loss"
                    st.markdown(f"<div class='game-card {css}'>Week {i+1}: {played['Score']} vs {opp}</div>", unsafe_allow_html=True)
                else:
                    css = "game-card-rival" if is_rival else "game-card-pending"
                    st.markdown(f"<div class='game-card {css}'>Week {i+1} vs {opp}</div>", unsafe_allow_html=True)

        with c2:
            st.caption("Weeks 7–12")
            for i in range(6, 12):
                opp = st.session_state.schedule[i]
                played = next((x for x in st.session_state.season_logs if x["Week"] == i + 1), None)
                is_rival = opp == st.session_state.team_rival
                if played:
                    res = "W" if played["Score"].startswith("W") else "L"
                    css = "game-card-win" if res == "W" else "game-card-loss"
                    st.markdown(f"<div class='game-card {css}'>Week {i+1}: {played['Score']} vs {opp}</div>", unsafe_allow_html=True)
                else:
                    css = "game-card-rival" if is_rival else "game-card-pending"
                    st.markdown(f"<div class='game-card {css}'>Week {i+1} vs {opp}</div>", unsafe_allow_html=True)

        st.divider()

        # News Feed sidebar-ish
        st.markdown("### 🗞️ News Feed")
        with st.container():
            st.markdown("<div class='news-box'>", unsafe_allow_html=True)
            if st.session_state.news:
                for n in st.session_state.news[:8]:
                    st.markdown(f"<div class='news-item'>• {n}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='news-item'>• No headlines yet.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # Weekly Play Control
        if not st.session_state.season_simulated:
            wk = st.session_state.week_index
            if wk < 12:
                opp = st.session_state.schedule[wk]
                opp_data = st.session_state.opponents_db.get(opp, {"OVR": 80, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}})
                is_riv = (opp == st.session_state.team_rival)

                st.subheader(f"Next Game: Week {wk+1} vs {opp} (OVR: {opp_data['OVR']})")
                if is_riv:
                    st.warning("RIVALRY WEEK: More chaos, bigger stakes!")

                colA, colB = st.columns(2)
                if colA.button("🏈 PLAY WEEK", type="primary"):
                    res = engine_play_game(
                        st.session_state.team_rating, opp_data['OVR'],
                        st.session_state.staff, st.session_state.my_schemes,
                        {"Off": opp_data['Off'], "Def": opp_data['Def']},
                        st.session_state.game_plan,
                        opp_data.get('Coaches', {"OC": 5, "DC": 5}),
                        is_home=(wk % 2 == 0),
                        is_rival=is_riv,
                        fac_lvl=st.session_state.facilities['Stadium'],
                        my_roster=st.session_state.roster
                    )

                    # Update record + security
                    if res['result'] == "W":
                        st.session_state.record["w"] += 1
                        st.session_state.career_stats["w"] += 1
                        st.session_state.job_security = min(100, st.session_state.job_security + (5 if is_riv else 2))
                        add_news(f"{st.session_state.team_name} wins Week {wk+1} vs {opp} ({res['score']}).")
                    else:
                        st.session_state.record["l"] += 1
                        st.session_state.career_stats["l"] += 1
                        pen = 2 if st.session_state.tenure <= 2 else 5
                        st.session_state.job_security = max(0, st.session_state.job_security - pen)
                        add_news(f"{st.session_state.team_name} loses Week {wk+1} vs {opp} ({res['score']}).")

                    st.session_state.season_logs.append({
                        "Week": wk + 1,
                        "Opponent": opp,
                        "Score": f"{res['result']} {res['score']}",
                        "Stats": res['stats']
                    })

                    # Advance week
                    st.session_state.week_index += 1

                    # End of regular season
                    if st.session_state.week_index >= 12:
                        st.session_state.season_simulated = True
                        add_news(f"Regular season ends at {st.session_state.record['w']}-{st.session_state.record['l']}.")
                    st.rerun()

                if colB.button("⏩ SIM REST OF SEASON"):
                    # Fast-sim remaining weeks but still "weekly logic"
                    while not st.session_state.season_simulated:
                        wk2 = st.session_state.week_index
                        if wk2 >= 12:
                            st.session_state.season_simulated = True
                            break
                        opp2 = st.session_state.schedule[wk2]
                        opp_data2 = st.session_state.opponents_db.get(opp2, {"OVR": 80, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}})
                        is_riv2 = (opp2 == st.session_state.team_rival)
                        res2 = engine_play_game(
                            st.session_state.team_rating, opp_data2['OVR'],
                            st.session_state.staff, st.session_state.my_schemes,
                            {"Off": opp_data2['Off'], "Def": opp_data2['Def']},
                            st.session_state.game_plan,
                            opp_data2.get('Coaches', {"OC": 5, "DC": 5}),
                            is_home=(wk2 % 2 == 0),
                            is_rival=is_riv2,
                            fac_lvl=st.session_state.facilities['Stadium'],
                            my_roster=st.session_state.roster
                        )
                        if res2['result'] == "W":
                            st.session_state.record["w"] += 1
                            st.session_state.career_stats["w"] += 1
                            st.session_state.job_security = min(100, st.session_state.job_security + (5 if is_riv2 else 2))
                        else:
                            st.session_state.record["l"] += 1
                            st.session_state.career_stats["l"] += 1
                            pen = 2 if st.session_state.tenure <= 2 else 5
                            st.session_state.job_security = max(0, st.session_state.job_security - pen)

                        st.session_state.season_logs.append({
                            "Week": wk2 + 1,
                            "Opponent": opp2,
                            "Score": f"{res2['result']} {res2['score']}",
                            "Stats": res2['stats']
                        })
                        st.session_state.week_index += 1

                    add_news(f"Regular season ends at {st.session_state.record['w']}-{st.session_state.record['l']}.")
                    st.rerun()

            else:
                st.session_state.season_simulated = True

        # Post-season access
        if st.session_state.season_simulated:
            st.write("### Season Results (Recap)")
            for log in st.session_state.season_logs:
                res = "W" if log['Score'].startswith("W") else "L"
                css = "game-card-win" if res == "W" else "game-card-loss"
                s = log['Stats']
                st.markdown(f"""
                <div class='game-card {css}'>
                    <div class='card-header'><span class='card-score'>{log['Score']}</span><span>vs {log['Opponent']}</span></div>
                    <div class='stat-grid'>
                        <div class='stat-row'><span class='stat-label'>🔥 QB Duel</span><span>{s['qb_duel'][0]} vs {s['qb_duel'][1]}</span></div>
                        <div class='stat-row'><span class='stat-label'>⚔️ Off vs Def</span><span>{s['off_vs_def'][0]} vs {s['off_vs_def'][1]}</span></div>
                        <div class='stat-row'><span class='stat-label'>🛡️ Def vs Off</span><span>{s['def_vs_off'][0]} vs {s['def_vs_off'][1]}</span></div>
                        <div class='stat-row'><span class='stat-label'>🧠 Staff</span><span>{s['staff'][0]} vs {s['staff'][1]}</span></div>
                        <div class='stat-row'><span class='stat-label'>💪 Raw Talent</span><span>{s['raw_roster']}</span></div>
                    </div>
                </div>""", unsafe_allow_html=True)

            if st.button("Proceed to Postseason"):
                wins = st.session_state.record['w']
                rank = 130 - (wins * 10)
                if rank < 1: rank = 1

                if rank <= 12:
                    st.session_state.postseason_data = init_playoff_bracket(rank, st.session_state.team_name)
                else:
                    bowl = get_bowl_name(rank)
                    candidates = [t for t in ALL_TEAMS if t != st.session_state.team_name]
                    opp = random.choice(candidates)
                    st.session_state.postseason_data = {"Type": "BOWL", "Bowl": bowl, "Rank": rank,
                                                        "Opponent": opp, "OppData": st.session_state.opponents_db[opp]}
                st.session_state.game_state = "POSTSEASON"
                st.rerun()

    with tab5:
        st.subheader("🏛️ Trophy Case")
        cs = st.session_state.career_stats
        st.write(f"**Titles:** {cs['titles']}  |  **Bowl W-L:** {cs['bowl_w']}-{cs['bowl_l']}  |  **Career W-L:** {cs['w']}-{cs['l']}")
        st.write(f"**Current Prestige:** {st.session_state.prestige}")
        st.write(f"**Legacy (Saban) Score:** {calculate_saban_score(cs, st.session_state.prestige)}")
        st.divider()
        st.subheader("📚 Season History")
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
        else:
            st.info("No completed seasons yet. Win some hardware!")

def show_postseason():
    st.title("Postseason Hub")
    data = st.session_state.postseason_data

    if data['Type'] == "BOWL":
        st.markdown(f"<div class='bracket-box'><h3>{data['Bowl']}</h3><h1>VS {data['Opponent']}</h1></div>", unsafe_allow_html=True)
        if st.button("PLAY BOWL GAME 🏈", type="primary"):
            opp_data = data['OppData']
            res = engine_play_game(
                st.session_state.team_rating,
                opp_data['OVR'],
                st.session_state.staff,
                st.session_state.my_schemes,
                {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                st.session_state.game_plan,
                opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                False, False, 10, st.session_state.roster
            )

            wins = st.session_state.record['w'] + (1 if res['result'] == "W" else 0)
            losses = st.session_state.record['l'] + (1 if res['result'] == "L" else 0)

            if res['result'] == "W":
                st.session_state.budget += 2000000
                st.toast("🎳 BOWL WIN BONUS: $2M")
                st.session_state.career_stats['bowl_w'] += 1
                add_news(f"{st.session_state.team_name} wins {data['Bowl']}! ({res['score']})")
            else:
                st.session_state.career_stats['bowl_l'] += 1
                add_news(f"{st.session_state.team_name} falls in {data['Bowl']} ({res['score']})")

            delta = wins - st.session_state.expected_wins
            if delta > 0:
                st.session_state.budget += delta * 1000000
            elif delta < 0:
                st.session_state.budget -= abs(delta) * 500000

            hist = {"Year": st.session_state.year, "Record": f"{wins}-{losses}", "Rank": f"#{data['Rank']}", "Bowl": data['Bowl']}
            st.session_state.history.append(hist)
            st.session_state.game_state = "SUMMARY"
            st.rerun()

    elif data['Type'] == "CFP":
        st.header(f"CFP Round: {['Opening Rd', 'Quarterfinals', 'Semifinals', 'Championship'][data['Round'] - 1]}")

        st.write("--- Bracket Status ---")
        for m in data['Matches']:
            if m.get('winner'):
                res_txt = f"✅ {m['winner']} advances"
            else:
                res_txt = f"{m['t1']} vs {m['t2']}"
            st.markdown(f"<div class='bracket-row'>{res_txt}</div>", unsafe_allow_html=True)

        user_match = None
        for m in data['Matches']:
            if m['t1'] == st.session_state.team_name or m['t2'] == st.session_state.team_name:
                user_match = m
                break

        if data['UserAlive'] and user_match:
            opp = user_match['t2'] if user_match['t1'] == st.session_state.team_name else user_match['t1']
            opp_data = st.session_state.opponents_db.get(opp, {"OVR": 88, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}})
            opp_ovr = opp_data["OVR"]

            st.info(f"Your Matchup: vs {opp} (OVR: {opp_ovr})")
            if st.button("PLAY PLAYOFF GAME 🏈", type="primary"):
                res = engine_play_game(
                    st.session_state.team_rating,
                    opp_ovr,
                    st.session_state.staff,
                    st.session_state.my_schemes,
                    {"Off": opp_data["Off"], "Def": opp_data["Def"]},
                    st.session_state.game_plan,
                    opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                    False, False, 10, st.session_state.roster
                )

                next_round_teams = []
                for m in data['Matches']:
                    if m == user_match:
                        if res['result'] == "W":
                            m['winner'] = st.session_state.team_name
                            next_round_teams.append(st.session_state.team_name)
                            st.toast("VICTORY! Advancing...")
                            add_news(f"{st.session_state.team_name} advances in the CFP!")
                        else:
                            m['winner'] = opp
                            next_round_teams.append(opp)
                            st.session_state.postseason_data['UserAlive'] = False
                            st.error(f"Eliminated by {opp}")
                            add_news(f"{st.session_state.team_name} is eliminated by {opp}.")
                    else:
                        winner = random.choice([m['t1'], m['t2']])
                        m['winner'] = winner
                        next_round_teams.append(winner)

                time.sleep(1)

                if st.session_state.postseason_data['UserAlive']:
                    if data['Round'] == 4:
                        st.session_state.budget += 50000000
                        st.session_state.career_stats['titles'] += 1
                        st.balloons()
                        st.success("NATIONAL CHAMPIONS!")
                        add_news(f"{st.session_state.team_name} wins the NATIONAL TITLE!")
                        time.sleep(1)
                        hist = {"Year": st.session_state.year, "Record": "CHAMPS", "Rank": "#1", "Bowl": "National Title"}
                        st.session_state.history.append(hist)
                        st.session_state.game_state = "SUMMARY"
                        st.rerun()
                    else:
                        new_matches = []
                        if data['Round'] == 1:
                            seeds = data['QF_Seeds']
                            for i in range(4):
                                new_matches.append({"t1": seeds[i], "t2": next_round_teams[3 - i], "winner": None})
                        elif data['Round'] == 2:
                            new_matches.append({"t1": next_round_teams[0], "t2": next_round_teams[3], "winner": None})
                            new_matches.append({"t1": next_round_teams[1], "t2": next_round_teams[2], "winner": None})
                        elif data['Round'] == 3:
                            new_matches.append({"t1": next_round_teams[0], "t2": next_round_teams[1], "winner": None})

                        st.session_state.postseason_data['Round'] += 1
                        st.session_state.postseason_data['Matches'] = new_matches
                        st.rerun()
                else:
                    hist = {"Year": st.session_state.year, "Record": "Playoff Loss", "Rank": f"#{data.get('Rank', '?')}", "Bowl": "CFP"}
                    st.session_state.history.append(hist)
                    st.session_state.game_state = "SUMMARY"
                    st.rerun()

        elif data['UserAlive'] and not user_match:
            st.success("You have a BYE week.")
            if st.button("Simulate Round"):
                next_round_teams = []
                for m in data['Matches']:
                    winner = random.choice([m['t1'], m['t2']])
                    m['winner'] = winner
                    next_round_teams.append(winner)

                if data['Round'] == 1:
                    seeds = data['QF_Seeds']
                    new_matches = []
                    for i in range(4):
                        new_matches.append({"t1": seeds[i], "t2": next_round_teams[3 - i], "winner": None})
                    st.session_state.postseason_data['Round'] += 1
                    st.session_state.postseason_data['Matches'] = new_matches
                    st.rerun()

def show_year_summary():
    st.title(f"{st.session_state.year} Summary")
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
    else:
        st.info("No season history yet.")

    # Trophy Case (UI/UX #4)
    st.subheader("🏛️ Trophy Case")
    cs = st.session_state.career_stats
    st.write(f"**Career W-L:** {cs['w']}-{cs['l']}  |  **Bowl W-L:** {cs['bowl_w']}-{cs['bowl_l']}  |  **Titles:** {cs['titles']}")
    st.write(f"**Legacy (Saban) Score:** {calculate_saban_score(cs, st.session_state.prestige)}")

    st.markdown(f"<div class='nil-alert'>💰 WAR CHEST AVAILABLE FOR NIL: {helper_format_cash(st.session_state.budget)}</div>", unsafe_allow_html=True)

    if st.button("Enter Portal", type="primary"):
        st.session_state.portal_players = engine_generate_portal_players()
        st.session_state.game_state = "PORTAL"
        st.rerun()

def show_portal():
    st.title("Transfer Portal")
    st.write(f"Budget: {helper_format_cash(st.session_state.budget)}")

    for i, p in enumerate(list(st.session_state.portal_players)):
        c1, c2 = st.columns([3, 1])
        c1.write(f"{p['pos']} {p['name']} ({p['rating']}) - {helper_format_cash(p['cost'])}")
        if c2.button("Sign", key=f"p_{i}"):
            if st.session_state.budget >= p['cost']:
                st.session_state.budget -= p['cost']
                st.session_state.roster[p['pos']] = p['rating']
                st.session_state.active_transfers[p['pos']] = True
                st.session_state.portal_players.pop(i)
                add_news(f"{st.session_state.team_name} signs portal {p['pos']} {p['name']} ({p['rating']}).")
                st.rerun()

    if st.button("Go to Recruiting"):
        st.session_state.game_state = "RECRUITING"
        st.rerun()

def show_recruiting():
    st.title("High School Recruiting")
    st.write(f"Budget: {helper_format_cash(st.session_state.budget)}")

    hot = st.session_state.hotspots.get(st.session_state.home_region, [])
    needs = st.session_state.get("team_needs", [])

    st.markdown(f"<div class='recruiting-intel'>Pipeline Bonus ({st.session_state.home_region}): {', '.join(hot)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='recruiting-intel'>Team Needs: <b>{', '.join(needs)}</b></div>", unsafe_allow_html=True)

    allocs = {}
    curr = 0
    for p in POSITIONS:
        label = f"{p}" + (" ✅ NEED" if p in needs else "")
        allocs[p] = st.number_input(label, 0, 10000000, 0, step=100000, key=f"alloc_{p}")
        curr += allocs[p]

    st.metric("Remaining", helper_format_cash(st.session_state.budget - curr))

    if st.button("Finalize Class", type="primary"):
        res = process_recruiting(st.session_state.budget, allocs, st.session_state.staff, st.session_state.prestige, st.session_state.inflation)
        if res:
            st.session_state.budget -= res['cost']

            if res['booster_bonus'] > 0:
                st.session_state.budget += res['booster_bonus']
                st.toast(f"💎 Gem Discovery Bonus: {helper_format_cash(res['booster_bonus'])}")
                add_news("Boosters celebrate a surprise GEM commit!")

            for p, g in res['roster_updates'].items():
                loss = 12 if st.session_state.active_transfers[p] else random.randint(2, 5)
                st.session_state.active_transfers[p] = False
                st.session_state.roster[p] = max(40, min(99, st.session_state.roster[p] - loss + g))

            # Update needs for next year
            st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)

            # Annual Revenue Payout
            rev = engine_calculate_revenue(st.session_state.school_tier, st.session_state.facilities['Marketing'], st.session_state.inflation)
            st.session_state.budget += rev
            st.session_state.revenue_report = f"Season Budget Injection: +{helper_format_cash(rev)}"

            st.session_state.opponents_db = engine_evolve_universe(st.session_state.opponents_db)

            # Advance year
            st.session_state.year += 1
            st.session_state.tenure += 1
            st.session_state.inflation *= 1.05
            st.session_state.schedule = engine_generate_schedule(st.session_state.team_name, st.session_state.team_conf, st.session_state.team_rival)
            st.session_state.hotspots = generate_hotspots()

            # Reset season for weekly play
            st.session_state.week_index = 0
            st.session_state.record = {"w": 0, "l": 0}
            st.session_state.season_logs = []
            st.session_state.season_simulated = False

            add_news(f"New season begins. Needs: {', '.join(st.session_state.team_needs)}.")
            time.sleep(0.5)
            st.session_state.game_state = "DASHBOARD"
            st.rerun()
        else:
            st.error("Over Budget")

def show_fired():
    st.error("FIRED! Your tenure has ended.")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    st.write(f"Final Legacy (Saban) Score: **{saban}**")
    if st.button("Restart Career"):
        st.session_state.clear()
        st.rerun()

def show_retirement():
    st.title("Retirement")
    st.write("Thanks for playing!")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    st.write(f"Final Legacy (Saban) Score: **{saban}**")
    if st.button("Restart Career"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# ROUTER
# ==============================================================================
if st.session_state.game_state == 'SETUP':
    run_setup()
elif st.session_state.game_state == 'FIRED':
    show_fired()
elif st.session_state.game_state == 'DASHBOARD':
    show_dashboard()
elif st.session_state.game_state == 'POSTSEASON':
    show_postseason()
elif st.session_state.game_state == 'SUMMARY':
    show_year_summary()
elif st.session_state.game_state == 'PORTAL':
    show_portal()
elif st.session_state.game_state == 'RECRUITING':
    show_recruiting()
elif st.session_state.game_state == 'RETIREMENT':
    show_retirement()
