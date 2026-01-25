import streamlit as st
import random
import time
import pandas as pd
import json
import datetime
import math

# ==============================================================================
# COLLEGE FOOTBALL MOGUL V20
# 1) Fixed Missing Function: show_offseason_nil_v8 is back.
# 2) War Room HS Outreach: Dollar-based allocation (No sliders).
# 3) True CFP Seeding: Quarterfinals re-seed based on Round 1 winners.
# 4) Deterministic AI: Simulations are consistent on refresh.
# ==============================================================================

STATE_VERSION = 20

# Only allow these keys to be loaded from JSON (Security/Stability)
ALLOWED_SAVE_KEYS = {
    "state_version", "game_state", "year", "budget", "prestige", "job_security",
    "expected_wins", "tenure", "roster", "active_transfers", "stars", "staff",
    "facilities", "history", "record", "opponents_db", "my_schemes",
    "career_stats", "season_logs", "schedule", "season_simulated",
    "hotspots", "candidates", "postseason_data", "revenue_report", "inflation",
    "team_needs", "game_plan", "week_index", "news", "offseason_step",
    "nil_class", "hs_total_spend", "hs_shares", "hs_spend_by_pos",
    "hs_alloc_by_pos", "top8", "top8_resolved", "trophies", "conf_revenue_boost_mult",
    "pending_invite", "season_end_ready", "booster_rating", "ai_records",
    "selection_sunday_results", "ad_name", "team_name", "team_color",
    "team_conf", "team_rival", "home_region", "school_tier",
    "team_off", "team_def", "team_rating", "last_postseason_result",
    "achievements", "milestone_log", "conferences_map"
}

# ==============================================================================
# ZONE 1: CONFIGURATION & STATIC DATA
# ==============================================================================
try:
    st.set_page_config(page_title="CFB Mogul V19.1", page_icon="🏈", layout="wide")
except Exception:
    pass

st.markdown("""
<style>
/* GLOBAL & BUTTONS */
.stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }

/* THEME-PROOFING */
.game-card, .staff-card, .news-box, .security-box, .trophy-tile, .rank-row, .resume-box {
    color: #111111 !important;
}

/* CONTAINERS */
.security-box { background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #ddd; text-align: center; margin-bottom: 10px; }
.security-safe { color: #28a745; font-weight: bold; }
.security-warm { color: #fd7e14; font-weight: bold; }
.security-hot { color: #dc3545; font-weight: bold; }

.finance-alert { background-color: #d1e7dd; color: #0f5132 !important; border: 1px solid #badbcc; padding: 15px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-weight: bold; }
.nil-alert { background-color: #cff4fc; color: #055160 !important; border: 1px solid #b6effb; padding: 18px; border-radius: 8px; margin-bottom: 16px; text-align: center; font-size: 1.1em; font-weight: bold; }

/* GAME CARDS */
.game-card { padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ddd; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.game-card-win { border-left: 5px solid #28a745; }
.game-card-loss { border-left: 5px solid #dc3545; }
.game-card-pending { border-left: 5px solid #6c757d; background: #f8f9fa; }
.game-card-rival { border: 2px solid #ffc107 !important; background-color: #fffbf0 !important; }

.card-header { display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 5px;}
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.85em; }
.stat-row { display: flex; justify-content: space-between; }

/* STAFF CARDS */
.staff-card { background: white; border: 1px solid #e0e0e0; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
.staff-role { font-size: 0.8em; color: #666; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.staff-name { font-size: 1.1em; font-weight: 800; color: #333; }

/* BADGES */
.badge { padding: 2px 6px; border-radius: 4px; font-size: 0.75em; font-weight: bold; margin-right: 5px; display: inline-block;}
.badge-tier-s { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
.badge-tier-a { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.badge-tier-f { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
.badge-trait { background: #e2e3e5; color: #383d41; }

/* RECRUITING & NEWS */
.recruiting-intel { background-color: #e0f7fa; color: #006064 !important; border-left: 5px solid #006064; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
.bracket-box { background-color: #2c3e50; color: white !important; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 10px; }
.bracket-row { display: flex; justify-content: space-between; padding: 6px; border-bottom: 1px solid #444; }

.news-box { background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.news-item { padding: 6px 0; border-bottom: 1px solid #f1f1f1; }
.news-item:last-child { border-bottom: none; }

.small-muted { font-size: 0.85em; color: #666; }

/* TROPHIES & NEWSPAPER */
.trophy-strip { font-size: 1.4em; line-height: 1.6em; }
.trophy-tile { background: #fff; border: 1px solid #eee; border-radius: 10px; padding: 10px; }

.newspaper-head { font-family: 'Georgia', serif; font-size: 2em; text-align: center; border-bottom: 3px double #333; padding-bottom: 10px; margin-bottom: 20px; color: #2c3e50; background: #fdfbf7; padding: 15px; border-radius: 5px; }
.newspaper-sub { font-family: 'Georgia', serif; font-style: italic; text-align: center; color: #555; margin-bottom: 20px; }

.booster-meter-container { background: #eee; height: 20px; border-radius: 10px; margin-top: 5px; overflow: hidden; border: 1px solid #ccc; }
.booster-meter-fill { height: 100%; transition: width 0.5s; }

/* RANKINGS TABLE */
.rank-row { background: white; padding: 8px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.rank-row-user { background: #e3f2fd !important; border-left: 5px solid #2196f3; font-weight: bold; }
.rank-num { width: 40px; font-weight: bold; color: #555; }
.rank-team { flex-grow: 1; }
.rank-rec { width: 80px; text-align: right; }

/* RESUME BOX */
.resume-box { background-color: #fff; border: 2px solid #333; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
.resume-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center; }
.resume-label { font-size: 0.8em; text-transform: uppercase; color: #666; letter-spacing: 1px; }
.resume-val { font-size: 1.2em; font-weight: bold; }
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
COACH_TRAITS = {
    "None": "None",
    "Recruiter": "+10% Recruiting",
    "Tactician": "+3 Game Boost",
    "Air Raid": "+2 Scheme",
    "Smashmouth": "+2 Scheme",
    "Pro Style": "+2 Scheme"
}
BOWL_MAPPING = {
    "Elite": ["Rose Bowl", "Sugar Bowl", "Orange Bowl", "Cotton Bowl", "Peach Bowl", "Fiesta Bowl"],
    "High": ["Citrus Bowl", "Alamo Bowl", "Pop-Tarts Bowl", "Gator Bowl"],
    "Mid": ["Liberty Bowl", "Music City Bowl", "Las Vegas Bowl"],
    "Low": ["Gasparilla Bowl", "Boca Raton Bowl", "Potato Bowl"]
}

TROPHY_ICONS = {
    "National Title": "🏆",
    "CFP": "🏆",
    "Rose Bowl": "🌹",
    "Sugar Bowl": "🍬",
    "Orange Bowl": "🍊",
    "Cotton Bowl": "🤠",
    "Peach Bowl": "🍑",
    "Fiesta Bowl": "🎉",
    "Citrus Bowl": "🍋",
    "Alamo Bowl": "🏰",
    "Pop-Tarts Bowl": "🍪",
    "Gator Bowl": "🐊",
    "Liberty Bowl": "🗽",
    "Music City Bowl": "🎸",
    "Las Vegas Bowl": "🎰",
    "Gasparilla Bowl": "🏴‍☠️",
    "Boca Raton Bowl": "🌴",
    "Potato Bowl": "🥔",
    "Bowl Win": "🎳"
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
CONF_POWER = {"SEC": 1.10, "Big Ten": 1.08, "ACC": 1.04, "Big 12": 1.03, "G5": 0.95}

# ==============================================================================
# ZONE 2: HELPERS
# ==============================================================================
def helper_format_cash(amount: int) -> str:
    try:
        amount = int(amount)
    except Exception:
        amount = 0
    return f"${amount/1_000_000:.1f}M" if amount >= 1_000_000 else f"${int(amount/1_000)}K"

def safe_int(value, default=0):
    """Safely convert any value to int with fallback"""
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Safely convert any value to float with fallback"""
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

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
    return int((career_stats["w"] * 1) + (career_stats["bowl_w"] * 5) + (career_stats["titles"] * 50) + (prestige * 0.5))

def get_bowl_name(rank):
    if rank <= 12: return "CFP Playoff"
    elif rank <= 25: return random.choice(BOWL_MAPPING["Elite"])
    elif rank <= 40: return random.choice(BOWL_MAPPING["High"])
    elif rank <= 80: return random.choice(BOWL_MAPPING["Mid"])
    else: return random.choice(BOWL_MAPPING["Low"])

def get_conferences_map() -> dict:
    """Return the mutable conferences map stored in session_state."""
    if "conferences_map" not in st.session_state or not isinstance(st.session_state.conferences_map, dict):
        st.session_state.conferences_map = {k: list(v) for k, v in CONFERENCES.items()}
    return st.session_state.conferences_map

def get_conference(team: str) -> str:
    """Dynamic lookup for V18."""
    conf_map = get_conferences_map()
    for conf, teams in conf_map.items():
        if team in (teams or []):
            return conf
    return "G5"

def role_rating(cand: dict, role: str) -> int:
    if role in ["HC", "OC"]:
        return int(cand.get("off", 1))
    if role == "DC":
        return int(cand.get("def", 1))
    if role == "Scout":
        return int(cand.get("recruit", 1))
    return int(cand.get("off", 1))

def compute_team_needs(roster: dict, k: int = 3) -> list:
    # V15 FIX: Safe getter for roster dict
    r = {p: int((roster or {}).get(p, 75) or 75) for p in POSITIONS}
    sorted_pos = sorted(r.items(), key=lambda x: x[1])
    return [p for p, _ in sorted_pos[:k]]

def generate_star_player(position, tier):
    base = 85 if tier <= 2 else 80
    return {
        "id": random.randint(10000, 99999),
        "name": generate_name(),
        "pos": position,
        "rating": min(99, base + random.randint(5, 14)),
        "year": "Fr",
        "trait": random.choice(TRAITS)
    }

def generate_ga_coach(role):
    return {
        "name": f"GA {generate_name()}",
        "role": role,
        "off": random.randint(1, 3),
        "def": random.randint(1, 3),
        "recruit": random.randint(1, 2),
        "trait": "None",
        "salary": 50000,
        "history": "Former Player",
        "scouted": True
    }

def add_news(text: str):
    if "news" not in st.session_state:
        st.session_state.news = []
    st.session_state.news.insert(0, f"{st.session_state.year}: {text}")
    st.session_state.news = st.session_state.news[:12]

def trophy_icon(name: str) -> str:
    return TROPHY_ICONS.get(name, TROPHY_ICONS.get("Bowl Win", "🎳"))

def award_trophy(trophy_name: str):
    if "trophies" not in st.session_state:
        st.session_state.trophies = []
    st.session_state.trophies.append({
        "Year": st.session_state.year,
        "Name": trophy_name,
        "Icon": trophy_icon(trophy_name)
    })

def render_trophy_gallery(title_text: str = "🏆 Trophy Gallery"):
    # Render a simple trophy gallery from st.session_state.trophies.
    st.subheader(title_text)
    trophies = st.session_state.get("trophies", []) or []
    
    if not trophies:
        st.info("No trophies yet. Win a bowl or a title to start your case.")
        return

    trophies_sorted = sorted(trophies, key=lambda x: int(x.get("Year", 0)), reverse=True)
    cols = st.columns(4)
    for i, t in enumerate(trophies_sorted[:24]):
        with cols[i % 4]:
            icon = t.get("Icon", "🏆")
            name = t.get("Name", "Trophy")
            year = t.get("Year", "?")
            st.markdown(
                f"<div class='trophy-tile'><div style='font-size:2em'>{icon}</div>"
                f"<div style='font-weight:800'>{name}</div>"
                f"<div class='small-muted'>Year {year}</div></div>",
                unsafe_allow_html=True
            )

def normalize_shares(shares: dict):
    def _val(pos):
        try:
            return max(0.0, float(shares.get(pos, 0.0)))
        except Exception:
            return 0.0
    total = sum(_val(p) for p in POSITIONS)
    if total <= 0:
        return {p: 100.0 / len(POSITIONS) for p in POSITIONS}
    return {p: (_val(p) / total) * 100.0 for p in POSITIONS}

# V16: Restored generate_hotspots
def generate_hotspots():
   """
   Returns a dict: Region -> list of 'hot' positions.
   Used by HS Outreach pipeline bonuses (home_region).
   """
   regions = list(REGION_STRENGTH.keys()) or ["South", "Midwest", "West", "North"]

   weighted = {
       "South":  ["RB", "WR", "DL", "LB", "QB", "DB", "OL"],
       "Midwest":["OL", "LB", "DL", "RB", "QB", "DB", "WR"],
       "West":   ["QB", "WR", "DB", "RB", "OL", "DL", "LB"],
       "North":  ["DL", "LB", "OL", "DB", "RB", "WR", "QB"],
   }

   out = {}
   for r in regions:
       pool = weighted.get(r, POSITIONS)
       # Pick 2–3 unique positions
       k = 3 if random.random() < 0.55 else 2
       picks = []
       while len(picks) < k:
           cand = random.choice(pool)
           if cand not in picks:
               picks.append(cand)
       out[r] = picks
   return out

def compute_recruiting_class_grade():
    """
    Grade based on NIL signed tiers, Top-8 commits, and Gems found.
    Returns: (grade_letter, numeric_score, breakdown_dict)
    """
    nil = st.session_state.get("nil_class", []) or []
    top8 = st.session_state.get("top8", []) or []
    stars = st.session_state.get("stars", []) or []

    # NIL points
    tier_points = 0
    tier_counts = {1: 0, 2: 0, 3: 0}
    for p in nil:
        if p.get("status") == "SIGNED":
            tier = int(p.get("tier", 3))
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            tier_points += {1: 12, 2: 7, 3: 3}.get(tier, 3)

    # Top-8 commits points
    top8_commits = [r for r in top8 if r.get("status") == "COMMITTED"]
    top8_points = len(top8_commits) * 10

    # Gems found points
    gem_count = 0
    for s in stars:
        nm = str(s.get("name", ""))
        if "(GEM)" in nm:
            gem_count += 1
    gem_points = gem_count * 6

    score = tier_points + top8_points + gem_points

    if score >= 70: grade = "A+"
    elif score >= 55: grade = "A"
    elif score >= 42: grade = "B"
    elif score >= 30: grade = "C"
    elif score >= 18: grade = "D"
    else: grade = "F"

    breakdown = {
        "score": score,
        "nil_signed": sum(tier_counts.values()),
        "tier_counts": tier_counts,
        "top8_commits": len(top8_commits),
        "gems_found": gem_count,
        "points": {"nil": tier_points, "top8": top8_points, "gems": gem_points}
    }
    return grade, score, breakdown

def get_season_metrics():
    # Calculate Best Win, Worst Loss, SOS (safe on empty/missing logs)
    logs = st.session_state.get("season_logs", []) or []
    if not logs:
        return 0, "None", "None"

    wins_ovr = []
    loss_ovr = []
    sos_accum = 0

    opponents_db = st.session_state.get("opponents_db", {}) or {}

    for log in logs:
        opp_name = log.get("Opponent", "Unknown")
        opp_ovr_log = int(log.get("OppOVR", 0) or 0)

        opp_data = opponents_db.get(opp_name, {"Prestige": 60, "OVR": 75})
        pres = int(opp_data.get("Prestige", 60) or 60)
        ovr = opp_ovr_log if opp_ovr_log > 0 else int(opp_data.get("OVR", 75) or 75)

        sos_accum += pres
        if "@" in str(log.get("Loc", "")):
            sos_accum += 5

        score = str(log.get("Score", ""))
        if score.startswith("W"):
            wins_ovr.append((ovr, opp_name))
        elif score.startswith("L"):
            loss_ovr.append((ovr, opp_name))

    avg_sos = int(sos_accum / max(1, len(logs)))
    best_win = max(wins_ovr, key=lambda x: x[0])[1] if wins_ovr else "None"
    worst_loss = min(loss_ovr, key=lambda x: x[0])[1] if loss_ovr else "None"

    return avg_sos, best_win, worst_loss

def build_season_summary_dict():
    wins = int(st.session_state.record.get("w", 0))
    losses = int(st.session_state.record.get("l", 0))

    avg_sos, best_win, worst_loss = get_season_metrics()

    this_year_hist = next((h for h in st.session_state.history if h.get("Year") == st.session_state.year), None)
    final_rank = this_year_hist.get("Rank", "Unranked") if this_year_hist else "Unranked"
    postseason = this_year_hist.get("Bowl", "No Bowl") if this_year_hist else "No Bowl"

    expected = int(st.session_state.expected_wins)
    delta = wins - expected

    return {
        "Year": st.session_state.year,
        "Team": st.session_state.team_name,
        "Conf": st.session_state.team_conf,
        "Record": f"{wins}-{losses}",
        "FinalRank": final_rank,
        "Postseason": postseason,
        "ExpectedWins": expected,
        "Delta": delta,
        "SOS": int(avg_sos),
        "BestWin": best_win,
        "WorstLoss": worst_loss,
    }

def render_dynasty_timeline(max_items: int = 25):
    # Legacy tab timeline, sorted newest first.
    st.subheader("🕰️ Dynasty Timeline")

    items = []

    # NEWS entries often look like: "2028: Some headline"
    for n in (st.session_state.get("news", []) or []):
        year = 0
        try:
            year = int(str(n).split(":")[0].strip())
        except Exception:
            year = int(st.session_state.get("year", 0) or 0)
        items.append({"year": year, "kind": "NEWS", "text": str(n).strip()})

    # HISTORY rows
    for h in (st.session_state.get("history", []) or []):
        yr = int(h.get("Year", 0) or 0)
        rec = h.get("Record", "?")
        rk = h.get("Rank", "NR")
        bowl = h.get("Bowl", "None")
        rg = h.get("RecruitingGrade", None)
        rg_txt = f" | 📦 Recruiting: {rg}" if rg else ""
        items.append({"year": yr, "kind": "HIST", "text": f"{yr}: Finished {rec}, Rank {rk}, Postseason: {bowl}{rg_txt}"})

    if not items:
        st.markdown("<div class='news-box'><div class='news-item'>• No timeline events yet.</div></div>", unsafe_allow_html=True)
        return

    # Sort newest first; for same year, show NEWS (0) before HIST (1)
    kind_order = {"NEWS": 0, "HIST": 1}
    items.sort(key=lambda x: (-x["year"], kind_order.get(x["kind"], 9)))

    st.markdown("<div class='news-box'>", unsafe_allow_html=True)
    for it in items[:max_items]:
        st.markdown(f"<div class='news-item'>• {it['text']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# V18 FIX: Defined EARLY so Router doesn't crash on name lookup
def show_offseason():
    """V20 FIX: This function was completely missing in V19.1"""
    sync_team_ratings()
    year = safe_int(st.session_state.get("year", 2026), 2026)
    st.title(f"🏈 Offseason {year}")
    
    budget = safe_int(st.session_state.get("budget", 0), 0)
    prestige = safe_int(st.session_state.get("prestige", 60), 60)
    st.markdown(
        f"<div class='nil-alert'>Budget: <b>{helper_format_cash(budget)}</b> | "
        f"Prestige: <b>{prestige}</b></div>",
        unsafe_allow_html=True
    )
    
    step = safe_int(st.session_state.get("offseason_step", 1), 1)
    
    # Step 1: NIL Prospects
    if step == 1:
        show_offseason_nil_v8()
        st.divider()
        if st.button("Continue to HS Outreach →", type="primary"):
            st.session_state.offseason_step = 2
            st.rerun()
    
    # Step 2: HS Outreach
    elif step == 2:
        show_offseason_hs_outreach()
        st.divider()
        if st.button("Continue to Top-8 Battles →", type="primary"):
            st.session_state.offseason_step = 3
            st.rerun()
    
    # Step 3: Top-8 Battles
    elif step == 3:
        show_offseason_top8_v8()
        st.divider()
        if st.button("Finish Recruiting & Advance Season →", type="primary"):
            # Calculate recruiting grade
            grade, score, breakdown = compute_recruiting_class_grade()
            
            # Record in history
            last_hist = st.session_state.history[-1] if st.session_state.history else None
            if last_hist and safe_int(last_hist.get("Year", 0), 0) == year:
                last_hist["RecruitingGrade"] = grade
            
            add_news(f"Recruiting class grade: {grade} ({score} pts)")
            
            # Year advancement
            st.session_state.year += 1
            st.session_state.tenure += 1
            st.session_state.inflation = safe_float(st.session_state.get("inflation", 1.0), 1.0) * 1.02
            
            # Evolve universe
            st.session_state.opponents_db = engine_evolve_universe(st.session_state.opponents_db)
            
            # Conference realignment
            invite = maybe_generate_conference_invite()
            if not invite:
                ai_conference_swap_lightweight()
            
            # Reset season state
            st.session_state.schedule = engine_generate_schedule(
                st.session_state.team_name, 
                st.session_state.team_conf, 
                st.session_state.team_rival
            )
            st.session_state.week_index = 0
            st.session_state.record = {"w": 0, "l": 0}
            st.session_state.season_logs = []
            st.session_state.season_simulated = False
            st.session_state.season_end_ready = False
            st.session_state.revenue_report = None
            
            # Reset recruiting
            st.session_state.nil_class = []
            st.session_state.hs_total_spend = 0
            st.session_state.hs_alloc_by_pos = {p: 0 for p in POSITIONS}
            st.session_state.top8 = []
            st.session_state.top8_resolved = set()
            st.session_state.offseason_step = 1
            
            # Update needs and hotspots
            st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)
            st.session_state.hotspots = generate_hotspots()
            
            sync_team_ratings()
            
            st.session_state.game_state = "DASHBOARD"
            add_news(f"Year {st.session_state.year} begins!")
            st.rerun()

def show_fired():
    st.error("FIRED! Your tenure has ended.")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    st.write(f"Final Legacy (Saban) Score: **{saban}**")
    render_trophy_gallery("🏛️ Your Trophy Gallery (Career)")
    if st.button("Restart Career"):
        st.session_state.clear()
        st.rerun()

def show_retirement():
    st.title("Retirement")
    st.write("Thanks for playing!")
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    st.write(f"Final Legacy (Saban) Score: **{saban}**")
    render_trophy_gallery("🏛️ Your Trophy Gallery (Career)")
    if st.button("Restart Career"):
        st.session_state.clear()
        st.rerun()

# ==============================================================================
# ZONE 3: ENGINE
# ==============================================================================
def engine_calculate_revenue(tier, marketing_lvl, inflation):
    if not tier:
        tier = 3
    base = {1: 40_000_000, 2: 25_000_000, 3: 10_000_000, 4: 5_000_000}.get(tier, 5_000_000)
    marketing_bonus = int(marketing_lvl) * 2_000_000
    total = (base + marketing_bonus) * float(inflation)
    conf_boost = float(st.session_state.get("conf_revenue_boost_mult", 1.0))
    total *= conf_boost
    return int(total)

def engine_generate_coach(role, tier):
    cost = random.randint(4_000_000, 8_000_000) if tier == 1 else random.randint(500_000, 3_500_000)
    trait_pool = list(COACH_TRAITS.keys())
    if role == "OC":
        trait_pool = ["Air Raid", "Smashmouth", "Pro Style", "Recruiter", "Tactician"]
    base = 8 if tier == 1 else (5 if tier == 2 else 2)
    return {
        "name": generate_coach_name(),
        "role": role,
        "off": min(10, base + random.randint(0, 3)),
        "def": min(10, base + random.randint(0, 3)),
        "recruit": min(10, base + random.randint(0, 3)),
        "trait": random.choice(trait_pool),
        "salary": cost,
        "history": "External Hire",
        "scouted": False
    }

def engine_generate_roster(tier, base_ovr=None):
    base = base_ovr if base_ovr is not None else (90 if tier == 1 else (82 if tier == 2 else 74))
    roster = {}
    for p in POSITIONS:
        roster[p] = min(99, max(40, int(base + random.randint(-4, 4))))
    return roster

def engine_generate_schedule(my_team, my_conf, rival):
    conf_map = get_conferences_map()
    # Dynamic conf foes
    conf_foes = [t for t in conf_map.get(my_conf, conf_map.get('G5', [])) if t != my_team]
    
    schedule = random.sample(conf_foes, min(8, len(conf_foes)))
    needed = 12 - len(schedule)
    non_conf = [t for t in ALL_TEAMS if t not in conf_map.get(my_conf, []) and t != my_team]
    schedule += random.sample(non_conf, min(len(non_conf), needed))
    if rival in ALL_TEAMS:
        if rival in schedule:
            schedule.remove(rival)
        schedule.append(rival)
    random.shuffle(schedule)
    return schedule[:12]

def get_tier_bonus(rating):
    if rating >= 8:
        return 3
    if rating <= 4:
        return -3
    return 0

def home_field_points(stadium_level: int, is_home: bool) -> float:
    lvl = int(stadium_level)
    if is_home:
        if lvl <= 6: return 0.0
        if lvl <= 8: return 1.0
        if lvl <= 10: return 3.0
        return 4.0
    else:
        if lvl >= 11 and random.random() < 0.25: return -2.0
        if lvl >= 9 and random.random() < 0.25: return -1.5
        return 0.0

# V15 PATCH: Safe Getters + Fixed Syntax
def compute_team_unit_ratings(roster: dict, staff: dict, facilities: dict):
    # SAFE GETTERS (prevents KeyError if a position is missing)
    r = {p: int((roster or {}).get(p, 75) or 75) for p in POSITIONS}

    oc = int(staff.get("OC", {"off": 3}).get("off", 3) or 3)
    dc = int(staff.get("DC", {"def": 3}).get("def", 3) or 3)
    training = int((facilities or {}).get("Training", 1) or 1)

    off = (r["QB"] * 0.34) + (r["OL"] * 0.26) + ((r["RB"] + r["WR"]) / 2 * 0.40)
    deff = (r["DL"] * 0.32) + (r["LB"] * 0.28) + (r["DB"] * 0.40)

    # Coaching/Facilities boosts
    off += oc * 1.2
    deff += dc * 1.2
    off += training * 0.8
    deff += training * 0.8

    # V15 Fix: Correct Tuple Return
    return (
       int(max(40, min(99, round(off)))),
       int(max(40, min(99, round(deff)))),
       int(max(40, min(99, round((sum(r.values()) / len(r)) if r else 75))))
    )

def ensure_opp_units(opp_data: dict):
    if "OffOVR" not in opp_data or "DefOVR" not in opp_data:
        base = int(opp_data.get("OVR", 80))
        opp_data["OffOVR"] = max(50, min(99, base + random.randint(-3, 3)))
        opp_data["DefOVR"] = max(50, min(99, base + random.randint(-3, 3)))
    return opp_data

def engine_play_game_v8(
    my_off, my_def,
    opp_off, opp_def,
    staff, schemes, opp_schemes,
    game_plan, opp_coaches,
    is_home, is_rival,
    my_stadium_level, opp_stadium_level
):
    my_edge = (my_off - opp_def) * 0.35
    opp_edge = (opp_off - my_def) * 0.35

    scheme_bonus_my = 0.0
    scheme_bonus_opp = 0.0
    my_off_s = schemes.get("Off", "Pro Style")
    opp_def_s = opp_schemes.get("Def", "Man Coverage")

    if COUNTERS.get(opp_def_s) == my_off_s:
        scheme_bonus_my += 2.5
        scheme_bonus_opp -= 1.0
    if COUNTERS.get(my_off_s) == opp_def_s:
        scheme_bonus_my -= 2.5
        scheme_bonus_opp += 1.0

    my_oc = staff.get("OC", {"off": 3}).get("off", 3)
    my_dc = staff.get("DC", {"def": 3}).get("def", 3)
    opp_oc = opp_coaches.get("OC", 5)
    opp_dc = opp_coaches.get("DC", 5)

    coaching_my = (get_tier_bonus(my_oc) - get_tier_bonus(opp_dc)) * 1.20
    coaching_opp = (get_tier_bonus(opp_oc) - get_tier_bonus(my_dc)) * 1.20

    hc_trait = staff.get("HC", {}).get("trait", "None")
    if hc_trait == "Tactician":
        coaching_my += 0.9
    elif hc_trait == "Recruiter":
        coaching_my += 0.25

    oc_trait = staff.get("OC", {}).get("trait", "None")
    if oc_trait in ["Air Raid", "Smashmouth", "Pro Style"] and oc_trait == my_off_s:
        scheme_bonus_my += 1.0

    hf = home_field_points(my_stadium_level, True) if is_home else home_field_points(opp_stadium_level, False)

    var_mult = 1.0
    if is_rival: var_mult *= 1.35
    if game_plan == "Aggressive": var_mult *= 1.25
    elif game_plan == "Conservative": var_mult *= 0.85

    base_pts = 27.5
    exp_my = base_pts + my_edge + scheme_bonus_my + coaching_my + (hf if is_home else 0.0)
    exp_opp = base_pts + opp_edge + scheme_bonus_opp + coaching_opp + (0.0 if is_home else (-hf if hf < 0 else 0.0))

    exp_my = max(10, min(50, exp_my))
    exp_opp = max(10, min(50, exp_opp))

    my_score = int(round(random.gauss(exp_my, 7.0 * var_mult)))
    opp_score = int(round(random.gauss(exp_opp, 7.0 * var_mult)))

    if my_score == opp_score:
        my_score += random.choice([0, 3, 7])
        opp_score += random.choice([0, 0, 3])

    my_score = max(0, min(70, my_score))
    opp_score = max(0, min(70, opp_score))

    explain = {
        "my_off": my_off, "my_def": my_def,
        "opp_off": opp_off, "opp_def": opp_def,
        "my_edge": float(my_edge), "opp_edge": float(opp_edge),
        "scheme_my": float(scheme_bonus_my), "scheme_opp": float(scheme_bonus_opp),
        "coach_my": float(coaching_my), "coach_opp": float(coaching_opp),
        "home_field": float(hf),
        "plan": game_plan
    }

    # V15 PATCH: Safe QB
    stats = {
        "qb_duel": [int((st.session_state.get("roster", {}) or {}).get("QB", 75)), int(max(60, min(99, opp_off)))],
        "off_vs_def": [int(my_off), int(opp_def)],
        "def_vs_off": [int(my_def), int(opp_off)],
        "staff": [f"{my_oc}/{my_dc}", f"{opp_oc}/{opp_dc}"],
        "raw_roster": int((my_off + my_def) / 2)
    }

    return {
        "result": "W" if my_score > opp_score else "L",
        "score": f"{my_score}-{opp_score}",
        "stats": stats,
        "explain": explain
    }

def engine_evolve_universe(opponents_db):
    for team, data in opponents_db.items():
        # This is for off-season evolution (progression), NOT for W-L record gen
        wins = int((data.get("OVR", 75) / 100) * 12) + random.randint(-2, 2)
        wins = max(0, min(12, wins))

        change = 0
        if wins >= 10: change = 3
        elif wins <= 4: change = -3
        data["Prestige"] = max(20, min(99, data.get("Prestige", 60) + change))

        if data["Prestige"] > 80 and wins < 6:
            data["Coaches"] = {"OC": random.randint(7, 9), "DC": random.randint(7, 9)}
        elif data["Prestige"] < 70 and wins > 9:
            data["Coaches"] = {"OC": random.randint(3, 6), "DC": random.randint(3, 6)}

        base_ovr = int(data["Prestige"] * 0.9)
        data["OVR"] = base_ovr + random.randint(-3, 3)

        if random.random() < 0.35:
            data.pop("OffOVR", None)
            data.pop("DefOVR", None)
    return opponents_db

# V19: Deterministic Simulation using Sorted Keys
def simulate_ai_regular_season_seeded(seed: int):
    rnd = random.Random(seed)
    results = []
    
    # SORT KEYS TO ENSURE DETERMINISM
    for team in sorted(st.session_state.opponents_db.keys()):
        if team == st.session_state.team_name:
            continue
        
        data = st.session_state.opponents_db[team]
        prestige = data.get("Prestige", 60)
        conf = get_conference(team)
        
        # use rnd instead of random
        if prestige > 90: wins = rnd.choices([12, 11, 10, 9], weights=[10, 30, 40, 20])[0]
        elif prestige > 80: wins = rnd.choices([11, 10, 9, 8, 7], weights=[5, 20, 35, 30, 10])[0]
        elif prestige > 60: wins = rnd.choices([9, 8, 7, 6, 5], weights=[10, 25, 30, 25, 10])[0]
        else: wins = rnd.choices([6, 5, 4, 3, 2], weights=[10, 30, 30, 20, 10])[0]
            
        losses = 12 - wins
        
        base_sos = 80 if conf == "SEC" else 78 if conf == "Big Ten" else 72 if conf in ["ACC", "Big 12"] else 60
        sos = base_sos + rnd.randint(-5, 5)
        
        results.append({"Team": team, "Wins": wins, "Losses": losses, "Conf": conf, "Prestige": prestige, "SOS": sos})
        
    return results

def calculate_committee_score(team_name, wins, losses, conf, sos_score):
    # V12: Enhanced Resume Logic
    score = (wins * 100)
    score -= (losses * 90) # Punish losses slightly more in V12
    
    # Conference Strength
    if conf in ["SEC", "Big Ten"]: score += 130
    elif conf in ["ACC", "Big 12"]: score += 70
    
    # SOS Factor
    score += (sos_score * 1.5)
    
    # G5 Gate
    if conf == "G5" and losses > 0:
        score -= 250
    return int(score)

def generate_nil_class_15(team_needs: list):
    def mk(tier: int, pos: str):
        if tier == 1:
            rating = random.randint(90, 99)
            ask = int(random.randint(2_500_000, 9_000_000) * (1.0 + (rating - 90) / 25))
            badge = "Tier 1"
        elif tier == 2:
            rating = random.randint(84, 89)
            ask = int(random.randint(900_000, 3_500_000) * (1.0 + (rating - 84) / 35))
            badge = "Tier 2"
        else:
            rating = random.randint(76, 83)
            ask = int(random.randint(200_000, 1_200_000) * (1.0 + (rating - 76) / 40))
            badge = "Tier 3"
        return {
            "id": random.randint(10_000, 99_999),
            "tier": tier,
            "tier_label": badge,
            "name": generate_name(),
            "pos": pos,
            "rating": rating,
            "ask": ask,
            "trait": random.choice(TRAITS),
            "status": "AVAILABLE"
        }

    needs = team_needs[:] if team_needs else POSITIONS[:]
    pool = []
    for _ in range(5):
        pos = random.choice(needs if random.random() < 0.70 else POSITIONS)
        pool.append(mk(1, pos))
    for _ in range(5):
        pos = random.choice(needs if random.random() < 0.60 else POSITIONS)
        pool.append(mk(2, pos))
    for _ in range(5):
        pos = random.choice(needs if random.random() < 0.50 else POSITIONS)
        pool.append(mk(3, pos))
    pool.sort(key=lambda x: (x["tier"], -x["rating"]))
    return pool

def generate_top8_prospects(team_needs: list):
    recruits = []
    for _ in range(8):
        pos = random.choice(team_needs if team_needs and random.random() < 0.65 else POSITIONS)
        rating = random.randint(90, 99)
        ask = int(random.randint(2_000_000, 8_000_000) * (1.0 + (rating - 90) / 35))
        recruits.append({
            "id": random.randint(10_000, 99_999),
            "name": generate_name(),
            "pos": pos,
            "rating": rating,
            "ask": ask,
            "trait": random.choice(TRAITS),
            "status": "OPEN",
            "note": ""
        })
    recruits.sort(key=lambda x: x["rating"], reverse=True)
    return recruits

def top8_commit_chance(recruit: dict, spend_by_pos: dict, staff: dict, prestige: int) -> float:
    scout = staff.get("Scout", {"recruit": 1}).get("recruit", 1)
    hc_trait = staff.get("HC", {}).get("trait", "None")

    chance = 0.18
    chance += (max(40, min(99, prestige)) - 60) * 0.004
    chance += (scout - 5) * 0.02
    if hc_trait == "Recruiter":
        chance += 0.05

    pos = recruit["pos"]
    spend = float(spend_by_pos.get(pos, 0.0))
    chance += min(0.20, spend / 10_000_000)

    return max(0.05, min(0.80, chance))

# HS outreach
def process_hs_outreach(total_spend: int, shares_pct: dict, staff: dict, prestige: int, inflation: float, hotspots: dict, home_region: str, team_needs: list):
    results = {"roster_updates": {}, "gems": [], "booster_bonus": 0, "spent": int(total_spend)}
    total_spend = max(0, int(total_spend))
    scout = staff.get("Scout", {"recruit": 1}).get("recruit", 1)
    hc_trait = staff.get("HC", {}).get("trait", "None")

    efficiency = 0.85 if scout >= 8 else (1.0 if scout >= 5 else 1.15)
    base_cost = 900_000 * float(inflation) * float(efficiency)
    hot_positions = hotspots.get(home_region, [])

    for pos in POSITIONS:
        pct = float(shares_pct.get(pos, 0.0))
        amt = total_spend * (pct / 100.0)

        if amt <= 0:
            results["roster_updates"][pos] = -random.randint(1, 3)
            continue
        
        # V19: Diminishing Returns Logic
        cap = base_cost * 2.0
        effective_spend = cap * (1 - math.exp(-amt / cap))
        spend_ratio = effective_spend / max(1.0, base_cost)
        dim = spend_ratio ** 0.85

        pipeline_bonus = 1.15 if pos in hot_positions else 1.0
        need_bonus = 1.25 if pos in team_needs else 1.0
        prestige_factor = max(0.85, min(1.20, (prestige / 75) ** 0.35))

        change = dim * pipeline_bonus * need_bonus * prestige_factor
        change = max(-4, min(12, change))

        if hc_trait == "Recruiter":
            change *= 1.08

        gem_chance = 0.08
        if pos in team_needs: gem_chance += 0.07
        if pos in hot_positions: gem_chance += 0.05
        if scout >= 8: gem_chance += 0.03
        if hc_trait == "Recruiter": gem_chance += 0.02

        if amt > base_cost * 1.25 and random.random() < gem_chance:
            star = generate_star_player(pos, tier=1)
            star["name"] += " (GEM)"
            results["gems"].append(star)
            change += 5
            results["booster_bonus"] += 250_000 + random.randint(0, 250_000)

        results["roster_updates"][pos] = change

    return results

# Conference / Postseason Helpers
def init_playoff_bracket(user_rank, user_team_name):
   """
   Build a CFP bracket with correct Top-12 seeding and Top-4 BYEs.
   Key behavior:
   - Top-12 seeds come directly from selection_sunday_results[:12] (committee order).
   - Seeds 1-4 receive BYEs to the Quarterfinals.
   - Opening Round matches: 5v12, 6v11, 7v10, 8v9.
   """
   results = st.session_state.get("selection_sunday_results", []) or []

   # Pull the committee Top-12 in order; fall back to filler if needed.
   top12 = [t.get("Team") for t in results[:12] if t.get("Team")]

   # Ensure list length 12 (pad if needed)
   while len(top12) < 12:
       top12.append("FCS East")

   # Ensure user appears in the Top-12 at the correct rank (if rank 1-12)
   if 1 <= int(user_rank) <= 12:
       top12[int(user_rank) - 1] = user_team_name

   # Avoid accidental duplicates of the user
   for i, name in enumerate(top12):
       if 1 <= int(user_rank) <= 12:
           if i != (int(user_rank) - 1) and name == user_team_name:
               top12[i] = "FCS East"

   r1_matches = [
       {"seed_high": 5, "seed_low": 12, "t1": top12[4], "t2": top12[11], "winner": None},
       {"seed_high": 6, "seed_low": 11, "t1": top12[5], "t2": top12[10], "winner": None},
       {"seed_high": 7, "seed_low": 10, "t1": top12[6], "t2": top12[9],  "winner": None},
       {"seed_high": 8, "seed_low": 9,  "t1": top12[7], "t2": top12[8],  "winner": None},
   ]

   # Seeds 1-4 get BYEs into Quarterfinals
   qf_seeds = top12[:4]

   return {
       "Type": "CFP",
       "Round": 1,
       "Seeds": top12,
       "QF_Seeds": qf_seeds,
       "Matches": r1_matches,
       "UserAlive": True,
       "Rank": int(user_rank),
   }

def apply_conference_move(to_conf: str, boost_mult: float):
    conf_map = get_conferences_map()
    team = st.session_state.team_name
    cur_conf = st.session_state.team_conf

    # Remove from old
    if cur_conf in conf_map and team in conf_map[cur_conf]:
        conf_map[cur_conf].remove(team)

    # Add to new
    if to_conf not in conf_map:
        conf_map[to_conf] = []
    if team not in conf_map[to_conf]:
        conf_map[to_conf].append(team)

    st.session_state.team_conf = to_conf
    st.session_state.conf_revenue_boost_mult = float(boost_mult)
    add_news(f"{team} joins the {to_conf}.")

def maybe_generate_conference_invite():
    if st.session_state.get("pending_invite"):
        return st.session_state.pending_invite

    conf_map = get_conferences_map()
    team = st.session_state.team_name
    cur_conf = st.session_state.team_conf
    prestige = int(st.session_state.get("prestige", 60) or 60)
    booster = int(st.session_state.get("booster_rating", 50) or 50)
    wins = int((st.session_state.get("record") or {}).get("w", 0) or 0)

    chance = 0.05
    if wins >= 9: chance += 0.08
    if wins >= 11: chance += 0.10
    if booster >= 80: chance += 0.06
    if prestige >= 80: chance += 0.06

    targets = []
    if cur_conf == "G5":
        if prestige >= 74 or wins >= 10: targets += ["Big 12", "ACC"]
        if prestige >= 84 or wins >= 11: targets += ["Big Ten", "SEC"]
    elif cur_conf in ["ACC", "Big 12"]:
        if prestige >= 86 or wins >= 11: targets += ["Big Ten", "SEC"]
    
    # Filter
    targets = [t for t in targets if t in conf_map and t != cur_conf]
    if not targets: return None
    
    if random.random() > min(0.35, chance): return None
    
    to_conf = random.choice(targets)
    base_mult = 1.10
    if to_conf == "SEC": base_mult = 1.18
    elif to_conf == "Big Ten": base_mult = 1.16
    
    note = "Blue-blood TV deal + tougher road games." if to_conf in ["SEC", "Big Ten"] else "New media deal."
    
    st.session_state.pending_invite = {"to_conf": to_conf, "boost_mult": base_mult, "note": note}
    add_news(f"{team} receives a conference invite to the {to_conf}.")
    return st.session_state.pending_invite

def ai_conference_swap_lightweight():
    conf_map = get_conferences_map()
    user_team = st.session_state.team_name
    if random.random() > 0.10: return None
    
    pools = [("ACC", "Big 12"), ("Big Ten", "SEC"), ("G5", "Big 12")]
    from_conf, to_conf = random.choice(pools)
    
    from_list = [t for t in conf_map.get(from_conf, []) if t != user_team]
    if not from_list: return None
    
    team = random.choice(from_list)
    conf_map[from_conf].remove(team)
    conf_map.setdefault(to_conf, []).append(team)
    
    add_news(f"Realignment: {team} moves from {from_conf} to {to_conf}.")

# ==============================================================================
# V15: ACHIEVEMENTS CATALOG & HELPERS
# ==============================================================================
ACHIEVEMENTS_CATALOG = [
   {"id": "WIN_10",  "title": "First 10 Wins",        "icon": "✅", "desc": "Reach 10 career wins."},
   {"id": "WIN_50",  "title": "50 Career Wins",       "icon": "🔥", "desc": "Reach 50 career wins."},
   {"id": "WIN_100", "title": "100 Career Wins",      "icon": "👑", "desc": "Reach 100 career wins."},
   {"id": "BOWL_1",  "title": "First Bowl Win",       "icon": "🎳", "desc": "Win your first bowl game."},
   {"id": "BOWL_10", "title": "10 Bowl Wins",         "icon": "🏅", "desc": "Win 10 bowl games."},
   {"id": "TITLE_1", "title": "National Champion",    "icon": "🏆", "desc": "Win the National Title."},
   {"id": "TITLE_3", "title": "Dynasty Mode",         "icon": "💎", "desc": "Win 3 National Titles."},
   {"id": "PRESTIGE_80", "title": "Blue Blood Status", "icon": "💰", "desc": "Reach 80 prestige."},
   {"id": "BOOST_90",    "title": "Booster Darling",   "icon": "🤑", "desc": "Reach 90 booster confidence."},
]

def _has_achievement(aid: str) -> bool:
   unlocked = st.session_state.get("achievements", []) or []
   return any(x.get("id") == aid for x in unlocked)

def _unlock_achievement(aid: str, title: str, icon: str, desc: str):
   if "achievements" not in st.session_state:
       st.session_state.achievements = []
   st.session_state.achievements.append({
       "id": aid, "title": title, "icon": icon, "desc": desc,
       "year": int(st.session_state.get("year", 0) or 0)
   })
   # Timeline entry
   if "milestone_log" not in st.session_state:
       st.session_state.milestone_log = []
   st.session_state.milestone_log.insert(0, f"{st.session_state.year}: {icon} Achievement Unlocked — {title}")
   st.session_state.milestone_log = st.session_state.milestone_log[:25]
   st.toast(f"{icon} Achievement Unlocked: {title}")
   add_news(f"Achievement unlocked: {title}.")

def check_and_award_achievements():
   cs = st.session_state.get("career_stats", {}) or {}
   wins = int(cs.get("w", 0) or 0)
   bowl_w = int(cs.get("bowl_w", 0) or 0)
   titles = int(cs.get("titles", 0) or 0)
   prestige = int(st.session_state.get("prestige", 0) or 0)
   booster = int(st.session_state.get("booster_rating", 0) or 0)

   if wins >= 10 and not _has_achievement("WIN_10"):
       _unlock_achievement("WIN_10", "First 10 Wins", "✅", "Reach 10 career wins.")
   if wins >= 50 and not _has_achievement("WIN_50"):
       _unlock_achievement("WIN_50", "50 Career Wins", "🔥", "Reach 50 career wins.")
   if wins >= 100 and not _has_achievement("WIN_100"):
       _unlock_achievement("WIN_100", "100 Career Wins", "👑", "Reach 100 career wins.")

   if bowl_w >= 1 and not _has_achievement("BOWL_1"):
       _unlock_achievement("BOWL_1", "First Bowl Win", "🎳", "Win your first bowl game.")
   if bowl_w >= 10 and not _has_achievement("BOWL_10"):
       _unlock_achievement("BOWL_10", "10 Bowl Wins", "🏅", "Win 10 bowl games.")

   if titles >= 1 and not _has_achievement("TITLE_1"):
       _unlock_achievement("TITLE_1", "National Champion", "🏆", "Win the National Title.")
   if titles >= 3 and not _has_achievement("TITLE_3"):
       _unlock_achievement("TITLE_3", "Dynasty Mode", "💎", "Win 3 National Titles.")

   if prestige >= 80 and not _has_achievement("PRESTIGE_80"):
       _unlock_achievement("PRESTIGE_80", "Blue Blood Status", "💰", "Reach 80 prestige.")
   if booster >= 90 and not _has_achievement("BOOST_90"):
       _unlock_achievement("BOOST_90", "Booster Darling", "🤑", "Reach 90 booster confidence.")

def render_achievements_panel():
   st.subheader("🏅 Dynasty Milestones")
   unlocked = st.session_state.get("achievements", []) or []
   unlocked_ids = {x.get("id") for x in unlocked}

   cols = st.columns(3)
   for i, a in enumerate(ACHIEVEMENTS_CATALOG):
       with cols[i % 3]:
           done = a["id"] in unlocked_ids
           badge = "✅ UNLOCKED" if done else "🔒 LOCKED"
           year_txt = ""
           if done:
               yr = next((x.get("year") for x in unlocked if x.get("id") == a["id"]), None)
               if yr: year_txt = f"<div class='small-muted'>Unlocked: {yr}</div>"
           
           # V18 FIX: Flatten HTML
           html = f"""
           <div class='trophy-tile'>
             <div style='font-size:1.6em'>{a['icon']} <b>{a['title']}</b></div>
             <div class='small-muted'>{a['desc']}</div>
             <div style='margin-top:6px; font-weight:800'>{badge}</div>
             {year_txt}
           </div>
           """
           st.markdown(html, unsafe_allow_html=True)

   if st.session_state.get("milestone_log"):
       st.divider()
       st.markdown("### 🧾 Milestone Log")
       st.markdown("<div class='news-box'>", unsafe_allow_html=True)
       for line in st.session_state.milestone_log[:10]:
           st.markdown(f"<div class='news-item'>• {line}</div>", unsafe_allow_html=True)
       st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# ZONE 4: STATE MANAGEMENT (V19 GOLD)
# ==============================================================================
def sync_team_ratings():
    """Recalculate team off/def/ovr globally so it never disappears."""
    if "roster" in st.session_state and "staff" in st.session_state:
        # V15 Safe Call
        res = compute_team_unit_ratings(st.session_state.roster, st.session_state.staff, st.session_state.facilities)
        # res is (off, def, ovr)
        st.session_state.team_off = res[0]
        st.session_state.team_def = res[1]
        st.session_state.team_rating = res[2]

def migrate_state():
    """Ensure session state has all keys and is valid."""
    if "state_version" not in st.session_state:
        st.session_state.state_version = 0.0
        
    v = float(st.session_state.state_version)
    
    # Fix types after JSON load
    if isinstance(st.session_state.get("top8_resolved"), list):
        st.session_state.top8_resolved = set(st.session_state.top8_resolved)

    # V13 PATCH A6: Defensive Coercion
    defaults = {
        "inflation": 1.0,
        "revenue_report": None,
        "postseason_data": {"Type": None, "Rank": 0, "Round": 0, "Matches": []},
        "team_needs": [],
        "game_plan": "Normal",
        "week_index": 0,
        "news": [],
        "offseason_step": 1,
        "nil_class": [],
        "hs_total_spend": 0,
        "hs_shares": {p: 100.0 / len(POSITIONS) for p in POSITIONS},
        "hs_spend_by_pos": {p: 0 for p in POSITIONS},
        "top8": [],
        "top8_resolved": set(),
        "trophies": [],
        "conf_revenue_boost_mult": 1.0,
        "pending_invite": None,
        "season_end_ready": False,
        "booster_rating": 50,
        "ai_records": [],
        "selection_sunday_results": [],
        "last_postseason_result": "NONE",
        # IDENTITY DEFAULTS
        "ad_name": "Coach Prime",
        "team_name": "Unknown U",
        "team_color": "#333333",
        "team_conf": "G5",
        "team_rival": "Rival",
        "home_region": "South",
        "school_tier": 3,
        # V15: Achievements
        "achievements": [],
        "milestone_log": []
    }

    # Ensure identity keys exist even if a save file didn't include them
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
            
    # Force defaults if None/Empty string for identity
    for k in ["ad_name", "team_name", "team_color", "team_conf", "team_rival", "home_region"]:
        if st.session_state.get(k) in [None, ""]:
            st.session_state[k] = defaults[k]
    
    # Numeric coercion for critical stats
    for k in ["year", "budget", "prestige", "job_security", "expected_wins", "tenure", "week_index", "booster_rating", "school_tier"]:
       try:
           st.session_state[k] = int(st.session_state.get(k, 0) or 0)
       except Exception:
           st.session_state[k] = int(defaults.get(k, 0) or 0)

    st.session_state.roster = st.session_state.get("roster", {}) or {p: 75 for p in POSITIONS}
    
    # V15 PATCH: Ensure roster keys
    for p in POSITIONS:
        if p not in st.session_state.roster:
            st.session_state.roster[p] = 75

    st.session_state.staff = st.session_state.get("staff", {}) or {}
    st.session_state.facilities = st.session_state.get("facilities", {}) or {"Marketing": 1, "Training": 1, "Stadium": 1}
    
    # V15 PATCH: Ensure facilities keys
    for k, default_val in {"Marketing": 1, "Training": 1, "Stadium": 1}.items():
       if k not in st.session_state.facilities or st.session_state.facilities[k] in [None, ""]:
           st.session_state.facilities[k] = default_val

    st.session_state.record = st.session_state.get("record", {}) or {"w": 0, "l": 0}
    
    # V18: Ensure conference map exists
    get_conferences_map()
    tc = st.session_state.team_conf
    if tc not in st.session_state.conferences_map:
        st.session_state.conferences_map[tc] = []
    if st.session_state.team_name not in st.session_state.conferences_map[tc]:
        st.session_state.conferences_map[tc].append(st.session_state.team_name)

    sync_team_ratings()
    st.session_state.state_version = STATE_VERSION

def init_session_state_defaults():
    if "game_state" not in st.session_state:
        st.session_state.game_state = "SETUP"

    st.session_state.setdefault("state_version", 0.0)
    st.session_state.setdefault("year", 2026)
    st.session_state.setdefault("tenure", 1)
    st.session_state.setdefault("budget", 5_000_000)
    st.session_state.setdefault("prestige", 60)
    st.session_state.setdefault("job_security", 80)
    st.session_state.setdefault("expected_wins", 6)

    st.session_state.setdefault("record", {"w": 0, "l": 0})
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("news", [])
    st.session_state.setdefault("career_stats", {"w": 0, "l": 0, "bowl_w": 0, "bowl_l": 0, "titles": 0})

    st.session_state.setdefault("roster", {p: 75 for p in POSITIONS})
    st.session_state.setdefault("staff", {})
    st.session_state.setdefault("facilities", {"Marketing": 1, "Training": 1, "Stadium": 1})

    st.session_state.setdefault("my_schemes", {"Off": "Pro Style", "Def": "Man Coverage"})
    st.session_state.setdefault("active_transfers", {p: False for p in POSITIONS})
    st.session_state.setdefault("stars", [])
    st.session_state.setdefault("candidates", {})

    st.session_state.setdefault("schedule", [])
    st.session_state.setdefault("season_logs", [])
    st.session_state.setdefault("season_simulated", False)
    st.session_state.setdefault("season_end_ready", False)
    st.session_state.setdefault("week_index", 0)

    st.session_state.setdefault("offseason_step", 1)
    st.session_state.setdefault("nil_class", [])
    st.session_state.setdefault("hs_total_spend", 0)
    st.session_state.setdefault("hs_shares", {p: 100.0 / len(POSITIONS) for p in POSITIONS})
    st.session_state.setdefault("hs_spend_by_pos", {p: 0 for p in POSITIONS})
    st.session_state.setdefault("top8", [])
    st.session_state.setdefault("top8_resolved", set())

    st.session_state.setdefault("opponents_db", {})
    st.session_state.setdefault("hotspots", {})
    st.session_state.setdefault("postseason_data", {"Type": None, "Rank": 0, "Round": 0, "Matches": []})
    st.session_state.setdefault("selection_sunday_results", [])
    st.session_state.setdefault("ai_records", [])
    st.session_state.setdefault("pending_invite", None)

    st.session_state.setdefault("inflation", 1.0)
    st.session_state.setdefault("revenue_report", None)
    st.session_state.setdefault("booster_rating", 50)
    st.session_state.setdefault("trophies", [])
    st.session_state.setdefault("conf_revenue_boost_mult", 1.0)
    st.session_state.setdefault("last_postseason_result", "NONE")
    
    # V15: Achievements
    st.session_state.setdefault("achievements", [])
    st.session_state.setdefault("milestone_log", [])
    
    # V18: Dynamic Conf Map
    st.session_state.setdefault("conferences_map", {k: list(v) for k,v in CONFERENCES.items()})

    migrate_state()

# ==============================================================================
# ZONE 5: SYSTEM & SAVE/LOAD (V12)
# ==============================================================================
def safe_json_default(obj):
    # Safer JSON fallback serializer
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj)

def render_system_sidebar():
    with st.sidebar:
        st.header("💾 Dynasty System")
        st.caption(f"Version {STATE_VERSION} (Restored)")
        
        # EXPORT
        if st.button("Export Save File"):
            state_copy = dict(st.session_state)
            if "top8_resolved" in state_copy:
                state_copy["top8_resolved"] = list(state_copy["top8_resolved"])
            
            export_data = {k: v for k, v in state_copy.items() if k in ALLOWED_SAVE_KEYS}
            
            json_str = json.dumps(export_data, default=safe_json_default)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name=f"CFB_Mogul_Save_{timestamp}.json",
                mime="application/json"
            )
            
        # IMPORT
        uploaded_file = st.file_uploader("Import Save File", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                # White-list filter & Restore
                for k, v in data.items():
                    if k not in ALLOWED_SAVE_KEYS:
                        continue
                    if k == "top8_resolved":
                        st.session_state[k] = set(v) if isinstance(v, list) else set()
                    else:
                        st.session_state[k] = v
                
                migrate_state() 
                st.session_state.candidates = {}   # transient UI cache
                sync_team_ratings()                # derived OFF/DEF/OVR always present
                
                st.success("Save Loaded Successfully! Reloading...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error loading save: {e}")

# ==============================================================================
# ZONE 6: UI / ROUTES
# ==============================================================================
def end_regular_season_and_stay_on_results():
    if st.session_state.season_end_ready:
        return

    st.session_state.season_simulated = True
    st.session_state.season_end_ready = True
    rev = engine_calculate_revenue(st.session_state.school_tier, st.session_state.facilities["Marketing"], st.session_state.inflation)
    st.session_state.budget += rev
    st.session_state.revenue_report = f"End of Regular Season Payout: +{helper_format_cash(rev)}"
    add_news(f"Regular season ends at {st.session_state.record['w']}-{st.session_state.record['l']}.")
    
    # Generate AI records DETERMINISTICALLY based on Year
    st.session_state.ai_records = simulate_ai_regular_season_seeded(st.session_state.year)
    st.session_state.game_state = "SEASON_END"

def render_news_box():
    st.markdown("### 🗞️ News Feed")
    st.markdown("<div class='news-box'>", unsafe_allow_html=True)
    if st.session_state.news:
        for n in st.session_state.news[:10]:
            st.markdown(f"<div class='news-item'>• {n}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='news-item'>• No headlines yet.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------- VIEWS -------------------------------------------

def run_setup():
    st.title("🏆 College Football Mogul V19.1")
    st.markdown("### Dynasty Mode (Restored Edition)")

    c1, c2 = st.columns(2)
    name = c1.text_input("AD Name", "Coach Prime")
    diff = c2.selectbox("Difficulty", ["Normal", "Hard", "Easy"])

    sorted_teams = sorted(REAL_WORLD_INIT.keys()) + sorted([t for t in ALL_TEAMS if t not in REAL_WORLD_INIT])
    team = st.selectbox("Select Team", sorted_teams)

    if team in REAL_WORLD_INIT:
        d = REAL_WORLD_INIT[team]
        tier = d["Tier"]
        budget = 25_000_000 if tier == 1 else (15_000_000 if tier == 2 else 5_000_000)
        conf = get_conference(team)
        rival = d.get("Rival", "Rival")
    else:
        tier, budget, conf, rival = 3, 5_000_000, get_conference(team), "Rival"

    expect = 10 if tier == 1 else (8 if tier == 2 else (6 if tier == 3 else 4))
    st.info(f"**{team}** | Conf: {conf} | Tier: {tier} | Budget: {helper_format_cash(budget)} | Rival: {rival}")
    st.caption(f"Expectation: {expect}+ Wins")

    if st.button("Start Dynasty", type="primary"):
        st.session_state.ad_name = name
        st.session_state.team_name = team
        st.session_state.team_color = TEAMS_DB.get(team, {}).get("color", "#333333")
        st.session_state.team_conf = conf
        st.session_state.team_rival = rival
        st.session_state.home_region = "South"
        st.session_state.school_tier = tier

        st.session_state.expected_wins = expect
        st.session_state.school_tier = tier
        st.session_state.budget = int(budget * (0.75 if diff == "Hard" else 1.25 if diff == "Easy" else 1.0))

        st.session_state.roster = engine_generate_roster(tier, REAL_WORLD_INIT.get(team, {}).get("Talent"))
        st.session_state.prestige = REAL_WORLD_INIT.get(team, {}).get("Prestige", 60)
        st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)

        st.session_state.staff = {}
        for r in ["HC", "OC", "DC", "Scout"]:
            st.session_state.staff[r] = engine_generate_coach(r, tier)

        val = 10 if tier == 1 else 5
        st.session_state.facilities = {"Marketing": val, "Training": val, "Stadium": val}

        st.session_state.opponents_db = {}
        for opp in ALL_TEAMS:
            if opp in REAL_WORLD_INIT:
                data = REAL_WORLD_INIT[opp]
                st.session_state.opponents_db[opp] = {
                    "Prestige": data["Prestige"],
                    "OVR": data["Talent"],
                    "Off": random.choice(SCHEMES["Offense"]),
                    "Def": random.choice(SCHEMES["Defense"]),
                    "Coaches": {"OC": random.randint(5, 9), "DC": random.randint(5, 9)},
                    "Stadium": random.randint(5, 11)
                }
            else:
                pres = 85 if opp in CONFERENCES["SEC"] else 65
                ovr = 82 if opp in CONFERENCES["SEC"] else 70
                st.session_state.opponents_db[opp] = {
                    "Prestige": pres, "OVR": ovr,
                    "Off": "Pro Style", "Def": "Man Coverage",
                    "Coaches": {"OC": 5, "DC": 5},
                    "Stadium": random.randint(4, 10)
                }
        
        # V18: Dynamic Conf Map
        if "conferences_map" not in st.session_state:
             st.session_state.conferences_map = {k: list(v) for k,v in CONFERENCES.items()}
        # Ensure user is in conf map
        if conf not in st.session_state.conferences_map:
             st.session_state.conferences_map[conf] = []
        if team not in st.session_state.conferences_map[conf]:
             st.session_state.conferences_map[conf].append(team)

        st.session_state.hotspots = generate_hotspots()
        st.session_state.schedule = engine_generate_schedule(team, conf, rival)

        st.session_state.week_index = 0
        st.session_state.record = {"w": 0, "l": 0}
        st.session_state.season_logs = []
        st.session_state.season_simulated = False
        st.session_state.season_end_ready = False

        st.session_state.offseason_step = 1
        st.session_state.nil_class = []
        st.session_state.hs_total_spend = 0
        st.session_state.hs_shares = {p: 100.0 / len(POSITIONS) for p in POSITIONS}
        st.session_state.hs_spend_by_pos = {p: 0 for p in POSITIONS}
        st.session_state.top8 = []
        st.session_state.top8_resolved = set()

        st.session_state.trophies = []
        st.session_state.conf_revenue_boost_mult = 1.0
        st.session_state.pending_invite = None
        st.session_state.booster_rating = 50
        st.session_state.ai_records = []
        st.session_state.selection_sunday_results = []
        st.session_state.last_postseason_result = "NONE"

        # V15 Achievements
        st.session_state.achievements = []
        st.session_state.milestone_log = []

        add_news(f"{team} hires {st.session_state.staff['HC']['name']} as HC.")
        st.session_state.game_state = "DASHBOARD"
        st.rerun()

def show_dashboard():
    sync_team_ratings()
    thresh = 0 if st.session_state.tenure <= 2 else 30
    if st.session_state.job_security < thresh:
        st.session_state.game_state = "FIRED"
        st.rerun()

    if st.session_state.season_end_ready:
        st.markdown("""
        <div style="background:#ffcccb; padding:10px; border-radius:5px; text-align:center; border:2px solid #e00; color: #333;">
            <h3>🚨 SEASON COMPLETE</h3>
            <p>The regular season is over. Go to results/postseason.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Resume Postseason / Season End", type="primary"):
            st.session_state.game_state = "SEASON_END"
            st.rerun()

    if st.session_state.revenue_report:
        st.markdown(f"<div class='finance-alert'>💰 FINANCIAL REPORT<br>{st.session_state.revenue_report}</div>", unsafe_allow_html=True)

    sec = st.session_state.job_security
    sec_cls = "security-safe" if sec > 75 else ("security-warm" if sec > 40 else "security-hot")
    st.markdown(f"<div class='security-box'>Year {st.session_state.tenure} | Security: <span class='{sec_cls}'>{sec}%</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background-color: {st.session_state.team_color}; padding: 10px; border-radius: 5px; color: white;'><h2>{st.session_state.team_name}</h2></div>", unsafe_allow_html=True)

    # V15 Fix: Safe getter for team rating
    if isinstance(st.session_state.team_rating, dict):
        raw_roster_val = int(st.session_state.team_rating.get("raw", 75) or 75)
    else:
        raw_roster_val = int(st.session_state.team_rating or 75)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Budget", helper_format_cash(st.session_state.budget))
    # V15: Handle dict or int for ratings
    ovr_val = st.session_state.team_rating if isinstance(st.session_state.team_rating, int) else st.session_state.team_rating["raw"]
    off_val = st.session_state.team_off if isinstance(st.session_state.team_off, int) else st.session_state.team_off["off"]
    def_val = st.session_state.team_def if isinstance(st.session_state.team_def, int) else st.session_state.team_def["def"]

    c2.metric("OVR", ovr_val)
    c3.metric("OFF", off_val, f"Raw: {raw_roster_val}")
    c4.metric("DEF", def_val)
    saban = calculate_saban_score(st.session_state.career_stats, st.session_state.prestige)
    c5.metric("Legacy", saban, f"Titles: {st.session_state.career_stats['titles']}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Strategy", "Staff", "Facilities", "Season (Weekly)", "Legacy"])

    with tab1:
        c1, c2 = st.columns(2)
        st.session_state.my_schemes["Off"] = c1.selectbox("Offense", SCHEMES["Offense"], index=SCHEMES["Offense"].index(st.session_state.my_schemes.get("Off", "Pro Style")))
        st.session_state.my_schemes["Def"] = c2.selectbox("Defense", SCHEMES["Defense"], index=SCHEMES["Defense"].index(st.session_state.my_schemes.get("Def", "Man Coverage")))

        st.write("Unit Strength")
        for p, v in st.session_state.roster.items():
            lab = f"{p}: {int(v)}" + (" (RENTAL)" if st.session_state.active_transfers.get(p) else "")
            st.progress(min(1.0, v / 100.0), text=lab) # V18.1 FIX: Added text=
        st.caption("V8 engine uses OFF vs DEF matchups + coaching + scheme + home-field tiers.")

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
                        <div><span class='badge {badge_cls}'>RATING: {rtg}</span>
                             <span class='badge badge-trait'>Trait: {c.get('trait','None')}</span></div>
                        <div class='small-muted'>{helper_format_cash(c.get('salary',0))}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Fire", key=f"fire_{role}"):
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
                for j, cand in enumerate(st.session_state.candidates[role]):
                    with cols[j]:
                        rr = role_rating(cand, role)
                        vis_rate = f"{rr}" if cand.get("scouted") else f"{get_letter_grade(rr)}"
                        vis_trait = cand.get("trait") if cand.get("scouted") else "???"
                        st.markdown(f"""
                        <div class='staff-card'>
                            <div class='staff-name'>{cand['name']}</div>
                            <div class='small-muted'>{cand.get('history','')}</div>
                            <div style='margin:5px 0'>
                                <span class='badge badge-trait'>{role} OVR: {vis_rate}</span>
                                <span class='badge badge-trait'>Trait: {vis_trait}</span>
                            </div>
                            <div style='font-weight:bold'>{helper_format_cash(cand['salary'])}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        b1, b2 = st.columns(2)
                        if b1.button("Hire", key=f"h_{role}_{j}"):
                            if st.session_state.budget >= cand["salary"]:
                                st.session_state.budget -= cand["salary"]
                                st.session_state.staff[role] = cand
                                add_news(f"{st.session_state.team_name} hires {cand['name']} as {role}.")
                                if role in st.session_state.candidates:
                                    del st.session_state.candidates[role]
                                st.rerun()
                            else:
                                st.error("Not enough budget.")
                        if not cand.get("scouted") and b2.button("Scout ($25k)", key=f"sc_{role}_{j}"):
                            if st.session_state.budget >= 25_000:
                                st.session_state.budget -= 25_000
                                cand["scouted"] = True
                                st.rerun()
                            else:
                                st.error("Not enough budget.")
                if st.button(f"Promote GA (Free)", key=f"ga_{role}"):
                    ga = generate_ga_coach(role)
                    st.session_state.staff[role] = ga
                    add_news(f"{st.session_state.team_name} promotes {ga['name']} to {role}.")
                    if role in st.session_state.candidates:
                        del st.session_state.candidates[role]
                    st.rerun()
        else:
            st.info("No vacancies. Fire someone to shop the market.")

    with tab3:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Marketing", st.session_state.facilities["Marketing"], delta="Rev: +$2M/yr")
            if st.button("Upgrade ($1M)", key="um"):
                if st.session_state.budget >= 1_000_000:
                    st.session_state.budget -= 1_000_000
                    st.session_state.facilities["Marketing"] += 1
                    add_news("Marketing upgraded. Boosters are pleased.")
                    st.rerun()
        with c2:
            st.metric("Training", st.session_state.facilities["Training"], delta="OFF/DEF Boost")
            if st.button("Upgrade ($3M)", key="ut"):
                if st.session_state.budget >= 3_000_000:
                    st.session_state.budget -= 3_000_000
                    st.session_state.facilities["Training"] += 1
                    add_news("Training upgraded. Player development improves.")
                    st.rerun()
        with c3:
            st.metric("Stadium", st.session_state.facilities["Stadium"], delta="Home Field (Tiered)")
            st.caption("Tier: <7 none, 7–8 small, 9+ big.")
            if st.button("Upgrade ($10M)", key="us"):
                if st.session_state.budget >= 10_000_000:
                    st.session_state.budget -= 10_000_000
                    st.session_state.facilities["Stadium"] += 1
                    st.session_state.prestige = min(99, st.session_state.prestige + 1)
                    add_news("Stadium upgraded. Home field advantage grows.")
                    st.rerun()

    with tab4:
        if len(st.session_state.staff) < 4:
            st.error("Fill Staff First!")
            return

        if not st.session_state.schedule:
            st.session_state.schedule = engine_generate_schedule(st.session_state.team_name, st.session_state.team_conf, st.session_state.team_rival)

        st.session_state.game_plan = st.selectbox(
            "Weekly Gameplan",
            ["Conservative", "Normal", "Aggressive"],
            index=["Conservative", "Normal", "Aggressive"].index(st.session_state.game_plan)
        )

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
        render_news_box()
        st.divider()

        if not st.session_state.season_simulated:
            wk = st.session_state.week_index
            if wk < 12:
                opp = st.session_state.schedule[wk]
                opp_data = ensure_opp_units(st.session_state.opponents_db.get(opp, {"OVR": 80, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}, "Stadium": 7}))
                is_riv = (opp == st.session_state.team_rival)
                opp_off = int(opp_data["OffOVR"])
                opp_def = int(opp_data["DefOVR"])

                st.subheader(f"Next Game: Week {wk+1} vs {opp}")
                # V15 Safe Getter
                my_off_val = off_val
                my_def_val = def_val
                
                st.caption(f"Matchup: Your OFF {my_off_val} vs Opp DEF {opp_def} | Your DEF {my_def_val} vs Opp OFF {opp_off}")
                st.caption(f"Stadiums: Yours {st.session_state.facilities['Stadium']} | Opp {opp_data.get('Stadium',7)}")

                if is_riv:
                    st.warning("RIVALRY WEEK: More chaos, bigger stakes!")

                colA, colB = st.columns(2)

                def play_one_week():
                    # V12.1 LOC FIX
                    is_home = (wk % 2 == 0)
                    loc_str = "HOME" if is_home else "@AWAY"
                    
                    res = engine_play_game_v8(
                        my_off_val, my_def_val,
                        opp_off, opp_def,
                        st.session_state.staff, st.session_state.my_schemes,
                        {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                        st.session_state.game_plan,
                        opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                        is_home=is_home, is_rival=is_riv,
                        my_stadium_level=st.session_state.facilities["Stadium"],
                        opp_stadium_level=opp_data.get("Stadium", 7)
                    )
                    st.session_state.season_logs.append({
                        "Week": wk + 1, "Opponent": opp, "Score": f"{res['result']} {res['score']}",
                        "Stats": res["stats"], "Explain": res["explain"], "OppOVR": int(opp_data.get("OVR", 80)),
                        "Loc": loc_str
                    })
                    if res["result"] == "W":
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

                    st.session_state.week_index += 1
                    if st.session_state.week_index >= 12:
                        end_regular_season_and_stay_on_results()

                if colA.button("🏈 PLAY WEEK", type="primary"):
                    play_one_week()
                    st.rerun()

                if colB.button("⏩ SIM REST OF SEASON"):
                    while not st.session_state.season_simulated:
                        wk2 = st.session_state.week_index
                        if wk2 >= 12: break
                        opp2 = st.session_state.schedule[wk2]
                        opp_data2 = ensure_opp_units(st.session_state.opponents_db.get(opp2, {"OVR": 80, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}, "Stadium": 7}))
                        
                        is_riv2 = (opp2 == st.session_state.team_rival)
                        is_home2 = (wk2 % 2 == 0)
                        loc_str2 = "HOME" if is_home2 else "@AWAY"

                        res2 = engine_play_game_v8(
                            my_off_val, my_def_val,
                            int(opp_data2["OffOVR"]), int(opp_data2["DefOVR"]),
                            st.session_state.staff, st.session_state.my_schemes,
                            {"Off": opp_data2.get("Off", "Pro Style"), "Def": opp_data2.get("Def", "Man Coverage")},
                            st.session_state.game_plan,
                            opp_data2.get("Coaches", {"OC": 5, "DC": 5}),
                            is_home=is_home2, is_rival=is_riv2,
                            my_stadium_level=st.session_state.facilities["Stadium"],
                            opp_stadium_level=opp_data2.get("Stadium", 7)
                        )
                        st.session_state.season_logs.append({
                            "Week": wk2 + 1, "Opponent": opp2, "Score": f"{res2['result']} {res2['score']}",
                            "Stats": res2["stats"], "Explain": res2["explain"], "OppOVR": int(opp_data2.get("OVR", 80)),
                            "Loc": loc_str2
                        })
                        if res2["result"] == "W":
                            st.session_state.record["w"] += 1
                            st.session_state.career_stats["w"] += 1
                            st.session_state.job_security = min(100, st.session_state.job_security + (5 if is_riv else 2))
                        else:
                            st.session_state.record["l"] += 1
                            st.session_state.career_stats["l"] += 1
                            pen = 2 if st.session_state.tenure <= 2 else 5
                            st.session_state.job_security = max(0, st.session_state.job_security - pen)

                        st.session_state.week_index += 1
                        if st.session_state.week_index >= 12: break

                    end_regular_season_and_stay_on_results()
                    st.rerun()

    with tab5:
        st.subheader("🏛️ Trophy Case (Quick View)")
        cs = st.session_state.career_stats
        st.write(f"**Titles:** {cs['titles']}  |  **Bowl W-L:** {cs['bowl_w']}-{cs['bowl_l']}  |  **Career W-L:** {cs['w']}-{cs['l']}")
        st.write(f"**Current Prestige:** {st.session_state.prestige}")
        st.write(f"**Legacy (Saban) Score:** {calculate_saban_score(cs, st.session_state.prestige)}")
        st.divider()
        render_trophy_gallery("🏆 Trophy Case Gallery")
        st.divider()
        # V15: Achievements + Timeline
        render_achievements_panel()
        st.divider()
        render_dynasty_timeline()

def show_season_end():
    sync_team_ratings()
    st.title("📊 Season End — Results Hub")
    st.markdown(f"<div class='nil-alert'>Regular season complete. Record: <b>{st.session_state.record['w']}-{st.session_state.record['l']}</b> | Budget: <b>{helper_format_cash(st.session_state.budget)}</b></div>", unsafe_allow_html=True)

    render_news_box()
    
    # V12: Resume Tile
    avg_sos, best_win, worst_loss = get_season_metrics()
    st.divider()
    st.subheader("🏆 Your Tournament Resume")
    st.markdown(f"""
    <div class='resume-box'>
        <div class='resume-grid'>
            <div><div class='resume-label'>Record</div><div class='resume-val'>{st.session_state.record['w']}-{st.session_state.record['l']}</div></div>
            <div><div class='resume-label'>SOS Score</div><div class='resume-val'>{avg_sos}</div></div>
            <div><div class='resume-label'>Best Win</div><div class='resume-val'>{best_win}</div></div>
            <div><div class='resume-label'>Worst Loss</div><div class='resume-val'>{worst_loss}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Game-by-game recap")
    for log in st.session_state.season_logs:
        res = "W" if log["Score"].startswith("W") else "L"
        css = "game-card-win" if res == "W" else "game-card-loss"
        s = log["Stats"]
        st.markdown(f"""
        <div class='game-card {css}'>
            <div class='card-header'><span>{log['Score']}</span><span>vs {log['Opponent']} (OVR {log.get('OppOVR','?')})</span></div>
            <div class='stat-grid'>
                <div class='stat-row'><span>🔥 QB Duel</span><span>{s['qb_duel'][0]} vs {s['qb_duel'][1]}</span></div>
                <div class='stat-row'><span>⚔️ OFF vs DEF</span><span>{s['off_vs_def'][0]} vs {s['off_vs_def'][1]}</span></div>
                <div class='stat-row'><span>🛡️ DEF vs OFF</span><span>{s['def_vs_off'][0]} vs {s['def_vs_off'][1]}</span></div>
                <div class='stat-row'><span>🧠 Staff</span><span>{s['staff'][0]} vs {s['staff'][1]}</span></div>
                <div class='stat-row'><span>💪 Raw</span><span>{s['raw_roster']}</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    c1, c2 = st.columns(2)

    if c1.button("Enter Selection Sunday (Reveal Rankings) 🏆", type="primary"):
        # V13 PATCH A5: Reset flag on ENTERING selection sunday, not inside it
        st.session_state.last_postseason_result = "NONE"

        # V12.1 Defensive check: If AI records missing, rebuild them
        if not st.session_state.ai_records:
            st.session_state.ai_records = simulate_ai_regular_season_seeded(st.session_state.year)

        all_teams = st.session_state.ai_records[:]
        
        # V12: Real SOS Calc
        user_sos = avg_sos 
        
        user_score = calculate_committee_score(
            st.session_state.team_name,
            st.session_state.record['w'],
            st.session_state.record['l'],
            st.session_state.team_conf,
            user_sos
        )
        
        user_entry = {
            "Team": st.session_state.team_name,
            "Wins": st.session_state.record['w'],
            "Losses": st.session_state.record['l'],
            "Conf": st.session_state.team_conf,
            "Score": user_score,
            "IsUser": True
        }
        all_teams.append(user_entry)
        
        for t in all_teams:
            if "Score" not in t:
                # V12: Use pre-calculated SOS from AI Sim
                t["Score"] = calculate_committee_score(t["Team"], t["Wins"], t["Losses"], t["Conf"], t.get("SOS", 60))
                t["IsUser"] = False
                
        all_teams.sort(key=lambda x: x["Score"], reverse=True)
        st.session_state.selection_sunday_results = all_teams
        st.session_state.game_state = "SELECTION_SUNDAY"
        st.rerun()

    if c2.button("Back to Dashboard"):
        st.session_state.game_state = "DASHBOARD"
        st.rerun()

def show_selection_sunday():
    sync_team_ratings()
    st.title("🏆 SELECTION SUNDAY")
    st.markdown("The Committee has met. Here are the final rankings.")
    
    results = st.session_state.selection_sunday_results
    
    user_rank = -1
    for i, t in enumerate(results):
        if t.get("IsUser"):
            user_rank = i + 1
            break
            
    # V18 FIX: Show Bye Status
    if user_rank <= 4:
        st.success(f"✅ Top-4 Seed (#{user_rank}): You receive a First Round BYE.")

    st.write("### 📊 Final Committee Rankings")
    
    for i, t in enumerate(results[:25]):
        rank = i + 1
        is_user = t.get("IsUser", False)
        bg_class = "rank-row-user" if is_user else "rank-row"
        
        status = ""
        if rank <= 12: status = "🏆 CFP"
        elif t["Wins"] >= 6: status = "🎳 BOWL"
        else: status = "❌ OUT"
        
        st.markdown(f"""
        <div class='{bg_class}'>
            <div class='rank-num'>#{rank}</div>
            <div class='rank-team'>{t['Team']} <span style='font-size:0.8em; color:#666'>({t['Conf']})</span></div>
            <div class='rank-rec'><b>{t['Wins']}-{t['Losses']}</b></div>
            <div style='width:80px; text-align:right; font-weight:bold;'>{status}</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    user_wins = st.session_state.record['w']
    
    if user_wins < 6:
        st.error("❌ You did not qualify for a bowl game (less than 6 wins).")
        # V13 PATCH A4b: Set Flag and Record History
        st.session_state.last_postseason_result = "NO_BOWL"
        
        if st.button("End Season -> Offseason", type="primary"):
            hist = {
                "Year": st.session_state.year, 
                "Record": f"{user_wins}-{st.session_state.record['l']}", 
                "Rank": "NR", 
                "Bowl": "None",
                "PostseasonResult": "NO_BOWL"
            }
            st.session_state.history.append(hist)
            st.session_state.game_state = "SEASON_RECAP"
            st.rerun()
            
    elif user_rank <= 12:
        st.success(f"🎉 You made the COLLEGE FOOTBALL PLAYOFF! (Rank #{user_rank})")
        if st.button("Advance to CFP 🏆", type="primary"):
            st.session_state.postseason_data = init_playoff_bracket(user_rank, st.session_state.team_name)
            st.session_state.game_state = "POSTSEASON"
            st.rerun()
            
    else:
        st.info(f"🎳 You are invited to a Bowl Game! (Rank #{user_rank})")
        if st.button("Accept Bowl Invite", type="primary"):
            bowl = get_bowl_name(user_rank)
            candidates = [t["Team"] for t in results if not t.get("IsUser")]
            if not candidates:
                opp = "FCS West"
            else:
                opp = random.choice(candidates) 
            
            st.session_state.postseason_data = {
                "Type": "BOWL", "Bowl": bowl, "Rank": user_rank, "Opponent": opp,
                "OppData": ensure_opp_units(st.session_state.opponents_db.get(opp, {"OVR": 85, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}, "Stadium": 8}))
            }
            st.session_state.game_state = "POSTSEASON"
            st.rerun()

def show_postseason():
    sync_team_ratings()
    st.title("Postseason Hub")
    data = st.session_state.postseason_data or {}

    if not data.get("Type"):
        st.warning("Postseason data missing. Returning to Season End.")
        st.session_state.game_state = "SEASON_END"
        st.rerun()

    if data.get("Type") == "BOWL":
        bowl_name = data.get("Bowl", "Bowl Game")
        opponent = data.get("Opponent", "Opponent")

        st.markdown(
            f"<div class='bracket-box'><h3>{bowl_name}</h3><h1>VS {opponent}</h1></div>",
            unsafe_allow_html=True
        )

        if st.button("PLAY BOWL GAME 🏈", type="primary"):
            fallback = {
                "OVR": 85,
                "Off": "Pro Style",
                "Def": "Man Coverage",
                "Coaches": {"OC": 5, "DC": 5},
                "Stadium": 8
            }
            opp_data = ensure_opp_units(data.get("OppData") or st.session_state.opponents_db.get(opponent, fallback) or fallback)

            opp_off = int(opp_data.get("OffOVR", opp_data.get("OVR", 80)))
            opp_def = int(opp_data.get("DefOVR", opp_data.get("OVR", 80)))

            res = engine_play_game_v8(
                st.session_state.team_off,
                st.session_state.team_def,
                opp_off, opp_def,
                st.session_state.staff,
                st.session_state.my_schemes,
                {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                st.session_state.game_plan,
                opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                is_home=False,
                is_rival=False,
                my_stadium_level=st.session_state.facilities.get("Stadium", 7),
                opp_stadium_level=opp_data.get("Stadium", 8)
            )

            wins = st.session_state.record["w"] + (1 if res["result"] == "W" else 0)
            losses = st.session_state.record["l"] + (1 if res["result"] == "L" else 0)

            # V13 PATCH A4: Set Flag & Record
            if res["result"] == "W":
                st.session_state.last_postseason_result = "BOWL_WIN"
                st.session_state.budget += 2_000_000
                st.session_state.career_stats["bowl_w"] += 1
                add_news(f"{st.session_state.team_name} wins {bowl_name}! ({res['score']})")
                st.toast("🎳 BOWL WIN BONUS: $2M")
                award_trophy(bowl_name if bowl_name in TROPHY_ICONS else "Bowl Win")
            else:
                st.session_state.last_postseason_result = "BOWL_LOSS"
                st.session_state.career_stats["bowl_l"] += 1
                add_news(f"{st.session_state.team_name} falls in {bowl_name} ({res['score']})")

            delta = wins - st.session_state.expected_wins
            if delta > 0:
                st.session_state.budget += delta * 1_000_000
            elif delta < 0:
                st.session_state.budget -= abs(delta) * 500_000

            # V15 Patch: Clamp Budget
            st.session_state.budget = max(0, int(st.session_state.budget))

            hist = {
                "Year": st.session_state.year, 
                "Record": f"{wins}-{losses}", 
                "Rank": f"#{data.get('Rank','?')}", 
                "Bowl": bowl_name,
                "PostseasonResult": st.session_state.last_postseason_result
            }
            st.session_state.history.append(hist)
            
            # V15 Achievements
            check_and_award_achievements()

            st.session_state.game_state = "SEASON_RECAP"
            st.session_state.offseason_step = 1
            st.rerun()

    elif data.get("Type") == "CFP":
        round_num = int(data.get("Round", 1))
        round_names = ["Opening Rd", "Quarterfinals", "Semifinals", "Championship"]
        label = round_names[round_num - 1] if 1 <= round_num <= 4 else f"Round {round_num}"
        st.header(f"CFP Round: {label}")

        st.write("--- Bracket Status ---")
        for m in data.get("Matches", []):
            if m.get("winner"):
                st.markdown(f"<div class='bracket-row'>✅ {m['winner']} advances</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='bracket-row'>{m.get('t1','?')} vs {m.get('t2','?')}</div>", unsafe_allow_html=True)

        user_match = None
        for m in data.get("Matches", []):
            if m.get("t1") == st.session_state.team_name or m.get("t2") == st.session_state.team_name:
                user_match = m
                break

        # V18 FIX: If Top-4 Seed in Round 1, Show BYE UI
        if not user_match and data.get("UserAlive") and round_num == 1:
            st.success("✅ FIRST ROUND BYE")
            st.info("You are a Top-4 Seed. You automatically advance to the Quarterfinals.")
            
            if st.button("Simulate Opening Round & Advance", type="primary"):
                # Sim round 1 winners
                next_round_teams = []
                for m in data.get("Matches", []):
                    t1, t2 = m.get("t1"), m.get("t2")
                    o1 = st.session_state.opponents_db.get(t1, {"OVR": 82}).get("OVR", 82)
                    o2 = st.session_state.opponents_db.get(t2, {"OVR": 82}).get("OVR", 82)
                    p = o1 / max(1.0, (o1 + o2))
                    winner = t1 if random.random() < p else t2
                    m["winner"] = winner
                    next_round_teams.append(winner)
                
                # Build Round 2 (Seeds 1-4 vs Winners)
                seeds = data.get("QF_Seeds", [])
                new_matches = []
                if len(seeds) == 4 and len(next_round_teams) >= 4:
                    # 1 plays lowest remaining seed logic simplified here to bracket slot
                    for i in range(4):
                        new_matches.append({"t1": seeds[i], "t2": next_round_teams[3-i], "winner": None})
                
                st.session_state.postseason_data["Round"] = 2
                st.session_state.postseason_data["Matches"] = new_matches
                add_news(f"{st.session_state.team_name} advances to Quarterfinals after Bye.")
                st.rerun()

        elif data.get("UserAlive") and user_match:
            opp = user_match["t2"] if user_match["t1"] == st.session_state.team_name else user_match["t1"]
            fallback = {"OVR": 88, "Off": "Pro Style", "Def": "Man Coverage", "Coaches": {"OC": 5, "DC": 5}, "Stadium": 9}
            opp_data = ensure_opp_units(st.session_state.opponents_db.get(opp, fallback) or fallback)

            opp_off = int(opp_data.get("OffOVR", opp_data.get("OVR", 80)))
            opp_def = int(opp_data.get("DefOVR", opp_data.get("OVR", 80)))

            st.info(f"Your Matchup: vs {opp} (OVR: {opp_data.get('OVR',88)} | OFF {opp_off} / DEF {opp_def})")

            if st.button("PLAY PLAYOFF GAME 🏈", type="primary"):
                res = engine_play_game_v8(
                    st.session_state.team_off, st.session_state.team_def,
                    opp_off, opp_def,
                    st.session_state.staff,
                    st.session_state.my_schemes,
                    {"Off": opp_data.get("Off", "Pro Style"), "Def": opp_data.get("Def", "Man Coverage")},
                    st.session_state.game_plan,
                    opp_data.get("Coaches", {"OC": 5, "DC": 5}),
                    is_home=False,
                    is_rival=False,
                    my_stadium_level=st.session_state.facilities.get("Stadium", 7),
                    opp_stadium_level=opp_data.get("Stadium", 9)
                )

                next_round_teams = []
                for m in data.get("Matches", []):
                    if m is user_match:
                        if res["result"] == "W":
                            m["winner"] = st.session_state.team_name
                            next_round_teams.append(st.session_state.team_name)
                            add_news(f"{st.session_state.team_name} advances in the CFP!")
                            st.toast("VICTORY! Advancing...")
                        else:
                            m["winner"] = opp
                            next_round_teams.append(opp)
                            st.session_state.postseason_data["UserAlive"] = False
                            # V13 PATCH A4: Set Flag
                            st.session_state.last_postseason_result = "CFP_LOSS"
                            add_news(f"{st.session_state.team_name} is eliminated by {opp}.")
                            st.error(f"Eliminated by {opp}")
                    else:
                        t1, t2 = m.get("t1"), m.get("t2")
                        if not t1 or not t2:
                            continue
                        o1 = st.session_state.opponents_db.get(t1, {"OVR": 82}).get("OVR", 82)
                        o2 = st.session_state.opponents_db.get(t2, {"OVR": 82}).get("OVR", 82)
                        p = o1 / max(1.0, (o1 + o2))
                        winner = t1 if random.random() < p else t2
                        m["winner"] = winner
                        next_round_teams.append(winner)

                time.sleep(0.6)

                if st.session_state.postseason_data.get("UserAlive"):
                    if round_num == 4:
                        # V13 PATCH A4: Title Win
                        st.session_state.last_postseason_result = "TITLE"
                        st.session_state.budget += 50_000_000
                        st.session_state.career_stats["titles"] += 1
                        st.balloons()
                        st.success("NATIONAL CHAMPIONS!")
                        add_news(f"{st.session_state.team_name} wins the NATIONAL TITLE!")
                        award_trophy("National Title")
                        
                        # V15 Patch: Clamp Budget
                        st.session_state.budget = max(0, int(st.session_state.budget))
                        
                        # V15 Achievements
                        check_and_award_achievements()

                        hist = {
                            "Year": st.session_state.year, 
                            "Record": "CHAMPS", 
                            "Rank": "#1", 
                            "Bowl": "National Title",
                            "PostseasonResult": "TITLE"
                        }
                        st.session_state.history.append(hist)

                        # V13 PATCH A1: Forced Recap Flow
                        st.session_state.game_state = "SEASON_RECAP"
                        st.session_state.offseason_step = 1
                        st.rerun()
                    else:
                        new_matches = []
                        if round_num == 1:
                            seeds = data.get("QF_Seeds", [])
                            if len(seeds) == 4 and len(next_round_teams) >= 4:
                                for i in range(4):
                                    new_matches.append({"t1": seeds[i], "t2": next_round_teams[3 - i], "winner": None})
                        elif round_num == 2:
                            if len(next_round_teams) >= 4:
                                new_matches.append({"t1": next_round_teams[0], "t2": next_round_teams[3], "winner": None})
                                new_matches.append({"t1": next_round_teams[1], "t2": next_round_teams[2], "winner": None})
                        elif round_num == 3:
                            if len(next_round_teams) >= 2:
                                new_matches.append({"t1": next_round_teams[0], "t2": next_round_teams[1], "winner": None})

                        st.session_state.postseason_data["Round"] = round_num + 1
                        st.session_state.postseason_data["Matches"] = new_matches
                        st.rerun()
                else:
                    # V13 PATCH A4: Elimination History
                    hist = {
                        "Year": st.session_state.year, 
                        "Record": "Playoff Loss", 
                        "Rank": f"#{data.get('Rank','?')}", 
                        "Bowl": "CFP",
                        "PostseasonResult": "CFP_LOSS"
                    }
                    st.session_state.history.append(hist)
                    
                    # V13 PATCH A1: Forced Recap Flow
                    st.session_state.game_state = "SEASON_RECAP"
                    st.session_state.offseason_step = 1
                    st.rerun()
        else:
            st.info("You are no longer alive in the bracket.")
            # V13 PATCH A1: Forced Recap Flow
            if st.button("Close Season → Recap", type="primary"):
                st.session_state.game_state = "SEASON_RECAP"
                st.session_state.offseason_step = 1
                st.rerun()

def show_season_recap():
    sync_team_ratings()
    st.title(f"SEASON RECAP: {st.session_state.year}")
    
    summary = build_season_summary_dict()

    # V14 POLISH: Use Flag for Headline
    result_flag = st.session_state.get("last_postseason_result", "NONE")
    
    if result_flag == "TITLE":
        headline = "DYNASTY! NATIONAL CHAMPIONS!"
        subhead = f"{st.session_state.team_name} shocks the world and takes the crown!"
    elif summary["Delta"] >= 3:
        headline = "Exceeding All Expectations!"
        subhead = f"Fans are ecstatic as {st.session_state.team_name} dominates the competition."
    elif summary["Delta"] <= -3:
        headline = "Disaster in the Making?"
        subhead = f"Boosters grow restless as {st.session_state.team_name} underperforms."
    else:
        headline = "Season Concludes"
        subhead = f"The {st.session_state.team_name} finish with a record of {summary['Record']}."

    st.markdown(f"<div class='newspaper-head'>{headline}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='newspaper-sub'>{subhead}</div>", unsafe_allow_html=True)
    
    st.subheader("📌 Season Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Record", summary["Record"])
    c2.metric("Final Rank", summary["FinalRank"])
    c3.metric("SOS", summary["SOS"])
    c4.metric("Postseason", summary["Postseason"])

    st.markdown(
       f"""
       <div class='resume-box'>
           <div class='resume-grid'>
               <div><div class='resume-label'>Best Win</div><div class='resume-val'>{summary["BestWin"]}</div></div>
               <div><div class='resume-label'>Worst Loss</div><div class='resume-val'>{summary["WorstLoss"]}</div></div>
               <div><div class='resume-label'>Expectation</div><div class='resume-val'>{summary["ExpectedWins"]} wins</div></div>
               <div><div class='resume-label'>Result vs Expectation</div><div class='resume-val'>{("+" if summary["Delta"]>=0 else "") + str(summary["Delta"])}</div></div>
           </div>
       </div>
       """, unsafe_allow_html=True
    )

    st.divider()
    
    # Booster logic using V13.1 Explicit Flag
    current_boost = st.session_state.booster_rating
    
    booster_change = summary["Delta"] * 5
    
    if result_flag == "TITLE": booster_change += 25
    elif result_flag == "BOWL_WIN": booster_change += 8
    elif result_flag == "CFP_LOSS": booster_change += 12
    elif result_flag == "BOWL_LOSS": booster_change += 3
    elif result_flag == "NO_BOWL": booster_change -= 8
    
    new_boost = max(0, min(100, current_boost + booster_change))
    
    # V15 Patch 4: Safe HTML color
    meter_color = "#28a745" if new_boost > 60 else ("#dc3545" if new_boost < 40 else "#ffc107")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("💰 Booster Confidence")
        st.markdown(f"""
        <div class="booster-meter-container">
            <div class="booster-meter-fill" style="width: {new_boost}%; background-color: {meter_color};"></div>
        </div>
        <div style="text-align:center; font-weight:bold; margin-top:5px;">{new_boost}/100</div>
        """, unsafe_allow_html=True)
        if new_boost > 80: st.success("Boosters are happy! Budget bonus incoming.")
        elif new_boost < 30: st.error("Boosters are angry. Job security at risk.")
    
    with c2:
        st.subheader("🏆 Legacy Growth")
        # V13 PATCH A2: Safe Record Parse
        try:
            wins_added = int(st.session_state.record.get("w", 0))
        except Exception:
            wins_added = 0
            
        added_titles = 1 if result_flag == "TITLE" else 0
        st.write(f"Wins Added: +{wins_added}")
        st.write(f"Titles Added: +{added_titles}")
    
    st.divider()
    
    if st.button("Close the Book on " + str(st.session_state.year) + " -> Go to Offseason", type="primary"):
        st.session_state.booster_rating = new_boost
        if new_boost >= 80:
            bonus = 3_000_000
            st.session_state.budget += bonus
            st.toast(f"Booster Donation: +{helper_format_cash(bonus)}")
        elif new_boost <= 20:
            st.session_state.job_security -= 10
            st.toast("Booster Pressure: Security -10")
        
        check_and_award_achievements()

        st.session_state.game_state = "OFFSEASON"
        st.session_state.offseason_step = 1
        st.rerun()

# V19: The "War Room" Allocation System
def show_offseason_hs_outreach():
    st.subheader("2) HS Outreach: The War Room")
    st.write("Set your total recruiting budget, then distribute it to position groups.")

    # Context Data
    hot = st.session_state.hotspots.get(st.session_state.home_region, [])
    needs = st.session_state.get("team_needs", [])
    
    # 1. THE WALLET (Total Budget Input)
    max_budget = int(st.session_state.budget)
    current_cap = int(st.session_state.get("hs_total_spend", 0))
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f"<div class='recruiting-intel'>Needs: <b>{', '.join(needs)}</b> | Pipeline: <b>{', '.join(hot)}</b></div>", unsafe_allow_html=True)
    with c2:
        # Step 1: User defines the CAP
        new_cap = st.number_input(
            "Total Recruiting Budget ($)",
            min_value=0,
            max_value=max_budget,
            value=current_cap,
            step=250_000,
            help="How much total cash do you want to commit to High School recruiting?"
        )

    st.session_state.hs_total_spend = new_cap

    # 2. STATE MANAGEMENT
    if "hs_alloc_by_pos" not in st.session_state or not isinstance(st.session_state.hs_alloc_by_pos, dict):
        st.session_state.hs_alloc_by_pos = {p: 0 for p in POSITIONS}
    
    alloc = st.session_state.hs_alloc_by_pos
    
    # V19: Quick Buttons
    colA, colB, colC = st.columns(3)
    if colA.button("⚖️ Balanced"):
        share = int(new_cap / 7)
        for p in POSITIONS: alloc[p] = share
        st.rerun()
    if colB.button("🎯 Needs Heavy"):
        if not needs:
            share = int(new_cap / 7)
            for p in POSITIONS: alloc[p] = share
        else:
            need_share = int((new_cap * 0.7) / len(needs))
            other_share = int((new_cap * 0.3) / (7 - len(needs))) if (7 - len(needs)) > 0 else 0
            for p in POSITIONS:
                alloc[p] = need_share if p in needs else other_share
        st.rerun()
    if colC.button("🔥 Pipeline Focus"):
        if not hot:
            share = int(new_cap / 7)
            for p in POSITIONS: alloc[p] = share
        else:
            hot_share = int((new_cap * 0.6) / len(hot))
            other_share = int((new_cap * 0.4) / (7 - len(hot))) if (7 - len(hot)) > 0 else 0
            for p in POSITIONS:
                alloc[p] = hot_share if p in hot else other_share
        st.rerun()

    # Auto-Clamp: If user lowered the cap, shrink allocations proportionally to fit
    total_allocated = sum(alloc.values())
    if total_allocated > new_cap:
        # Simple clamp
        while total_allocated > new_cap:
            for p in POSITIONS:
                if alloc[p] > 0:
                    deduct = min(alloc[p], 250_000)
                    alloc[p] -= deduct
                    total_allocated -= deduct
                    if total_allocated <= new_cap: break
    
    remaining = new_cap - total_allocated
    
    # 3. THE DASHBOARD (Visual Feedback)
    if remaining == 0 and new_cap > 0:
        st.success(f"✅ Fully Allocated: {helper_format_cash(new_cap)}")
    elif remaining > 0:
        st.warning(f"⚠️ Unassigned Funds: {helper_format_cash(remaining)}")
    elif remaining < 0:
        st.error(f"🚫 Over Budget: {helper_format_cash(remaining)}")
    else:
        st.info("Set a budget above to begin.")

    st.divider()

    # 4. THE ALLOCATOR (Grid UI)
    # V19 Change: Number Inputs instead of buttons
    cols = st.columns(2)
    
    for idx, pos in enumerate(POSITIONS):
        with cols[idx % 2]:
            current_amt = alloc.get(pos, 0)
            
            # Badge logic
            badges = ""
            if pos in needs: badges += " 🔴"
            if pos in hot: badges += " 🔥"
            
            val = st.number_input(
                f"{pos} {badges}",
                min_value=0,
                max_value=max_budget,
                value=current_amt,
                step=100_000,
                key=f"input_{pos}"
            )
            alloc[pos] = val

    # 5. EXECUTION
    st.divider()
    
    # Sync data for engine
    st.session_state.hs_alloc_by_pos = alloc
    spend_by_pos = {p: int(alloc.get(p, 0)) for p in POSITIONS}
    st.session_state.hs_spend_by_pos = spend_by_pos

    # Re-calc remaining for button state
    final_allocated = sum(alloc.values())
    final_remaining = new_cap - final_allocated

    if st.button("Confirm & Run Recruiting 🚀", type="primary", disabled=(new_cap == 0)):
        if final_remaining != 0:
            st.error(f"You must allocate exactly {helper_format_cash(new_cap)}. Current variance: {helper_format_cash(final_remaining)}")
            return

        # Engine Call
        res = process_hs_outreach(
            new_cap,
            normalize_shares({p: (spend_by_pos[p] / max(1, new_cap)) * 100 for p in POSITIONS}),
            st.session_state.staff,
            st.session_state.prestige,
            st.session_state.inflation,
            st.session_state.hotspots,
            st.session_state.home_region,
            needs
        )

        # Apply Results
        st.session_state.budget -= res["spent"]
        if res["booster_bonus"] > 0:
            st.session_state.budget += res["booster_bonus"]
            st.toast(f"💎 Booster Bonus: {helper_format_cash(res['booster_bonus'])}")
            add_news("Boosters go wild over a surprise recruit!")

        for p, g in res["roster_updates"].items():
            loss = random.randint(1, 4)
            st.session_state.roster[p] = max(40, min(99, int(st.session_state.roster[p] - loss + g)))

        if res["gems"]:
            st.session_state.stars.extend(res["gems"])
            add_news(f"Scouts found {len(res['gems'])} hidden gems!")

        st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)
        add_news("Signing Day complete. New rankings released.")
        
        sync_team_ratings()
        st.success("Class Signed! Roster Updated.")
        st.rerun()

def show_offseason_nil_v8():
    st.subheader("1) NIL Prospects (Class of 15)")
    needs = st.session_state.get("team_needs", [])

    if not st.session_state.nil_class:
        st.session_state.nil_class = generate_nil_class_15(needs)
        add_news("NIL board posted: 15 prospects (Tier 1/2/3).")

    st.markdown(f"<div class='recruiting-intel'>Team Needs: <b>{', '.join(needs) if needs else 'Balanced'}</b></div>", unsafe_allow_html=True)
    st.write("You can sign any of these 15. When they’re gone, they’re gone (no infinite respawn).")

    signed = sum(1 for p in st.session_state.nil_class if p["status"] == "SIGNED")
    available = 15 - signed
    st.caption(f"Signed: {signed} | Remaining available: {available}")

    for p in st.session_state.nil_class:
        tier_badge = "badge-tier-s" if p["tier"] == 1 else ("badge-tier-a" if p["tier"] == 2 else "badge-tier-f")
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.markdown(f"⭐ <b>{p['tier_label']}</b> — {p['pos']} {p['name']} ({p['rating']}) — {p['trait']}", unsafe_allow_html=True)
        c2.markdown(f"<span class='badge {tier_badge}'>{p['tier_label']}</span>", unsafe_allow_html=True)
        c3.write(f"Ask: {helper_format_cash(p['ask'])}")
        if p["status"] == "SIGNED":
            c4.write("✅ SIGNED")
        else:
            if c4.button("Sign", key=f"nil_sign_{p['id']}"):
                if st.session_state.budget >= p["ask"]:
                    st.session_state.budget -= p["ask"]
                    st.session_state.roster[p["pos"]] = max(st.session_state.roster[p["pos"]], p["rating"])
                    p["status"] = "SIGNED"
                    add_news(f"{st.session_state.team_name} signs NIL {p['tier_label']} {p['pos']} {p['name']} ({p['rating']}).")
                    
                    # V13 PATCH A3: Immediate Sync
                    sync_team_ratings()
                    st.toast("Signed ✔️")
                    st.rerun()
                else:
                    st.error("Not enough budget.")

# V16 FIX: Show Top-8 V8
def show_offseason_top8_v8():
   st.subheader("3) Top-8 Battles — Close on Elites")

   needs = st.session_state.get("team_needs", []) or []
   prestige = int(st.session_state.get("prestige", 60) or 60)
   staff = st.session_state.get("staff", {}) or {}

   if not st.session_state.get("top8"):
       st.session_state.top8 = generate_top8_prospects(needs)
       add_news("Top-8 board posted: 8 elite prospects (high ceiling, expensive battles).")

   if "top8_resolved" not in st.session_state or not isinstance(st.session_state.top8_resolved, set):
       tr = st.session_state.get("top8_resolved", [])
       st.session_state.top8_resolved = set(tr) if isinstance(tr, list) else set()

   budget = int(st.session_state.get("budget", 0) or 0)

   st.markdown(f"<div class='nil-alert'>Available Budget: <b>{helper_format_cash(budget)}</b></div>", unsafe_allow_html=True)
   st.markdown(f"<div class='recruiting-intel'>Team Needs: <b>{', '.join(needs) if needs else 'Balanced'}</b></div>", unsafe_allow_html=True)

   step = 250_000
   st.caption(f"Tip: Use offers in {helper_format_cash(step)} steps. Each recruit allows ONE pitch per offseason.")

   commits = [r for r in st.session_state.top8 if r.get("status") == "COMMITTED"]
   st.write(f"**Commits:** {len(commits)} / 8")

   st.divider()

   for r in st.session_state.top8:
       rid = int(r.get("id", 0) or 0)
       pos = r.get("pos", "??")
       rating = int(r.get("rating", 0) or 0)
       ask = int(r.get("ask", 0) or 0)
       status = r.get("status", "OPEN")
       already = rid in st.session_state.top8_resolved

       c1, c2, c3 = st.columns([4, 2, 2])

       with c1:
           need_tag = " (NEED)" if pos in needs else ""
           st.markdown(f"⭐ **{pos}{need_tag} — {r.get('name','Prospect')} ({rating})** \nTrait: {r.get('trait','')}")

       with c2:
           st.write(f"Ask: {helper_format_cash(ask)}")
           max_offer = max(0, min(budget, max(ask * 2, step)))
           offer = st.slider(
               "Offer",
               0, max_offer,
               min(int(r.get("offer", 0) or 0), max_offer),
               step=step,
               key=f"offer_{rid}"
           )
           r["offer"] = int(offer)

       with c3:
           if status == "COMMITTED":
               st.success("✅ COMMITTED")
           elif status == "LOST":
               st.error("❌ LOST")
           else:
               spend_by_pos = {p: 0 for p in POSITIONS}
               spend_by_pos[pos] = float(r.get("offer", 0) or 0)

               chance = top8_commit_chance(r, spend_by_pos, staff, prestige)

               if ask > 0 and (r.get("offer", 0) or 0) >= ask:
                   chance = min(0.90, chance + 0.12)

               st.write(f"Pitch Chance: **{int(chance*100)}%**")

               disabled = already or (int(r.get("offer", 0) or 0) <= 0)
               label = "Pitch (Already attempted)" if already else "Pitch Recruit"
               if st.button(label, key=f"pitch_{rid}", disabled=disabled):
                   offer_amt = int(r.get("offer", 0) or 0)
                   if offer_amt > int(st.session_state.budget or 0):
                       st.error("Not enough budget for that offer.")
                       st.stop()

                   st.session_state.budget = max(0, int(st.session_state.budget - offer_amt))

                   roll = random.random()
                   if roll < chance:
                       r["status"] = "COMMITTED"
                       add_news(f"{st.session_state.team_name} lands TOP-8 {pos} {r.get('name','Recruit')} ({rating})!")
                       try:
                           st.session_state.roster[pos] = max(int(st.session_state.roster.get(pos, 75) or 75), rating)
                       except Exception:
                           st.session_state.roster[pos] = rating
                   else:
                       r["status"] = "LOST"
                       add_news(f"{st.session_state.team_name} misses on TOP-8 {pos} {r.get('name','Recruit')}.")

                   st.session_state.top8_resolved.add(rid)
                   sync_team_ratings()
                   st.rerun()

   st.divider()

   if st.button("Sim Remaining Pitches (auto-offer small amounts)"):
       for r in st.session_state.top8:
           rid = int(r.get("id", 0) or 0)
           if rid in st.session_state.top8_resolved:
               continue
           if r.get("status") != "OPEN":
               st.session_state.top8_resolved.add(rid)
               continue

           budget_now = int(st.session_state.get("budget", 0) or 0)
           if budget_now < step:
               break

           ask = int(r.get("ask", 0) or 0)
           pos = r.get("pos", "QB")
           offer_amt = int(max(step, min(budget_now, max(step, ask // 4))))
           offer_amt = offer_amt - (offer_amt % step)

           spend_by_pos = {p: 0 for p in POSITIONS}
           spend_by_pos[pos] = float(offer_amt)

           chance = top8_commit_chance(r, spend_by_pos, staff, prestige)
           if ask > 0 and offer_amt >= ask:
               chance = min(0.90, chance + 0.12)

           st.session_state.budget = max(0, int(st.session_state.budget - offer_amt))

           if random.random() < chance:
               r["status"] = "COMMITTED"
               rating = int(r.get("rating", 0) or 0)
               add_news(f"{st.session_state.team_name} lands TOP-8 {pos} {r.get('name','Recruit')} ({rating})!")
               st.session_state.roster[pos] = max(int(st.session_state.roster.get(pos, 75) or 75), rating)
           else:
               r["status"] = "LOST"
               add_news(f"{st.session_state.team_name} misses on TOP-8 {pos} {r.get('name','Recruit')}.")

           st.session_state.top8_resolved.add(rid)

       sync_team_ratings()
       st.rerun()

# ==============================================================================
# REQUIRED FUNCTION GUARD (PLACE BELOW FUNCTION DEFINITIONS)
# ==============================================================================
REQUIRED_FUNCS = [
   # setup / pipelines
   "generate_hotspots",
   "compute_team_needs",
   "engine_generate_roster",
   "engine_generate_schedule",

   # season end / postseason
   "init_playoff_bracket",

   # offseason modules
   "show_offseason_nil_v8",
   "show_offseason_hs_outreach",
   "show_offseason_top8_v8",

   # recruiting / HS
   "generate_nil_class_15",
   "process_hs_outreach",
   "generate_top8_prospects",
   "top8_commit_chance",

   # conf / routing
   "apply_conference_move",
   "maybe_generate_conference_invite",
   "ai_conference_swap_lightweight",
   "show_fired",
   "show_retirement",
   "init_session_state_defaults"
]
_missing = [f for f in REQUIRED_FUNCS if f not in globals()]
if _missing:
   st.error("Missing required functions: " + ", ".join(_missing))
   st.stop()

# ==============================================================================
# ZONE 7: INITIALIZATION & ROUTER
# ==============================================================================
# 1) Initialize State (First thing that runs)
init_session_state_defaults()

# 2) Render Sidebar
render_system_sidebar()

# 3) Route
if st.session_state.game_state == "SETUP":
    run_setup()
elif st.session_state.game_state == "FIRED":
    show_fired()
elif st.session_state.game_state == "DASHBOARD":
    show_dashboard()
elif st.session_state.game_state == "SEASON_END":
    show_season_end()
elif st.session_state.game_state == "SELECTION_SUNDAY":
    show_selection_sunday()
elif st.session_state.game_state == "POSTSEASON":
    show_postseason()
elif st.session_state.game_state == "SEASON_RECAP":
    show_season_recap()
elif st.session_state.game_state == "OFFSEASON":
    show_offseason()
elif st.session_state.game_state == "RETIREMENT":
    show_retirement()
else:
    st.session_state.game_state = "DASHBOARD"
    st.rerun()
