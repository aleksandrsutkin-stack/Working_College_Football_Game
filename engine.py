"""
Game simulation engine and AI logic for CFB Mogul V27.6
"""

import random
import math
import streamlit as st
from models import safe_int, safe_float, safe_dict, generate_name, generate_coach_name
from config import POSITIONS, ALL_TEAMS, SCHEMES, COACH_TRAITS, OFF_COUNTERED_BY, DEF_COUNTERS

# ============================================================================
# BUDGET DISTRIBUTION
# ============================================================================

def distribute_exact(total: int, weights: dict, step: int = 100_000) -> dict:
    """Distribute a total budget across positions based on weights."""
    total = max(0, int(total))
    if total == 0: 
        return {p: 0 for p in POSITIONS}
    
    w = {}
    for p in POSITIONS:
        try: 
            w[p] = max(0.0, float(weights.get(p, 0.0)))
        except Exception: 
            w[p] = 0.0
    
    s = sum(w.values())
    if s <= 0: 
        w = {p: 1.0 for p in POSITIONS}
        s = float(len(POSITIONS))
    
    alloc = {}
    for p in POSITIONS:
        raw = total * (w[p] / s)
        alloc[p] = int(raw // step) * step
    
    remainder = total - sum(alloc.values())
    if remainder > 0:
        order = sorted(POSITIONS, key=lambda p: w[p], reverse=True)
        i = 0
        while remainder > 0:
            p = order[i % len(order)]
            add = min(step, remainder)
            alloc[p] += add
            remainder -= add
            i += 1
    
    remainder = total - sum(alloc.values())
    if remainder < 0:
        order = sorted(POSITIONS, key=lambda p: w[p])
        i = 0
        while remainder < 0:
            p = order[i % len(order)]
            take = min(alloc[p], step, abs(remainder))
            alloc[p] -= take
            remainder += take
            i += 1
    
    return alloc

def sync_alloc_to_inputs(alloc: dict):
    """Sync allocation dict to session state input widgets."""
    for p in POSITIONS:
        st.session_state[f"input_{p}"] = int(alloc.get(p, 0) or 0)

# ============================================================================
# GENERATION FUNCTIONS
# ============================================================================

def engine_generate_coach(role, tier):
    """Generate a coach with random attributes based on tier."""
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
    """Generate a full roster based on school tier."""
    base = base_ovr if base_ovr is not None else (90 if tier == 1 else (82 if tier == 2 else 74))
    roster = {}
    for p in POSITIONS:
        roster[p] = min(99, max(40, int(base + random.randint(-4, 4))))
    return roster

def engine_generate_schedule(my_team, my_conf, rival):
    """Generate a 12-game schedule with deterministic RNG."""
    from models import get_conferences_map
    
    conf_map = get_conferences_map()
    
    # Deterministic per-year seed
    year_seed = int(st.session_state.get("year", 0) or 0)
    seed_str = f"{my_team}|{my_conf}|{rival}|{year_seed}"
    rng = random.Random(seed_str)

    conf_foes = [t for t in conf_map.get(my_conf, conf_map.get("G5", [])) if t != my_team]
    schedule = rng.sample(conf_foes, min(8, len(conf_foes)))

    pool = [t for t in ALL_TEAMS if t != my_team and t not in schedule]
    rng.shuffle(pool)

    for opp in pool:
        if len(schedule) >= 12: 
            break
        schedule.append(opp)

    if rival in ALL_TEAMS and rival != my_team and rival not in schedule:
        if len(schedule) >= 12: 
            schedule[-1] = rival
        else: 
            schedule.append(rival)
    elif rival in schedule:
        # Move rival to end for drama
        schedule.remove(rival)
        schedule.append(rival)

    if len(schedule) < 12:
        pad_pool = [t for t in ALL_TEAMS if t != my_team and t not in schedule]
        rng.shuffle(pad_pool)
        schedule.extend(pad_pool[: max(0, 12 - len(schedule))])

    rng.shuffle(schedule)
    return schedule[:12]

# ============================================================================
# GAME MECHANICS
# ============================================================================

def get_tier_bonus(rating):
    """Get game bonus/penalty based on coach tier."""
    if rating >= 8: return 3
    if rating <= 4: return -3
    return 0

def home_field_points(stadium_level: int) -> float:
    """Calculate home field advantage based on stadium tier."""
    lvl = int(stadium_level)
    if lvl <= 6: return 0.0
    if lvl <= 8: return 1.0
    if lvl <= 10: return 3.0
    return 4.0

def compute_team_unit_ratings(roster: dict, staff: dict, facilities: dict):
    """Calculate team OFF/DEF/OVR based on roster, staff, and facilities."""
    roster = roster or {}
    staff = staff or {}
    facilities = facilities or {}
    
    r = {p: safe_int(roster.get(p, 75), 75) for p in POSITIONS}
    oc = safe_int((staff.get("OC") or {}).get("off", 3), 3)
    dc = safe_int((staff.get("DC") or {}).get("def", 3), 3)
    training = safe_int(facilities.get("Training", 1), 1)
    
    off = (r["QB"] * 0.34) + (r["OL"] * 0.26) + ((r["RB"] + r["WR"]) / 2 * 0.40)
    deff = (r["DL"] * 0.32) + (r["LB"] * 0.28) + (r["DB"] * 0.40)
    
    off += oc * 1.2
    deff += dc * 1.2
    off += training * 0.8
    deff += training * 0.8
    
    return (
        int(max(40, min(99, round(off)))),
        int(max(40, min(99, round(deff)))),
        int(max(40, min(99, round((sum(r.values()) / len(r)) if r else 75))))
    )

# ============================================================================
# MAIN GAME ENGINE
# ============================================================================

def engine_play_game_v8(my_off, my_def, opp_off, opp_def, staff, schemes, opp_schemes, 
                        game_plan, opp_coaches, is_home, is_rival, my_stadium_level, 
                        opp_stadium_level, rng=None):
    """
    V8 Game Engine: Simulates a single game with detailed mechanics.
    Returns dict with result, score, stats, and explanation.
    """
    rng = rng or random.Random()
    
    my_edge = (my_off - opp_def) * 0.35
    opp_edge = (opp_off - my_def) * 0.35
    
    scheme_bonus_my = scheme_bonus_opp = 0.0
    my_off_s = schemes.get("Off", "Pro Style")
    opp_def_s = opp_schemes.get("Def", "Man Coverage")

    if OFF_COUNTERED_BY.get(my_off_s) == opp_def_s:
        scheme_bonus_my -= 2.5
        scheme_bonus_opp += 1.0
    if DEF_COUNTERS.get(opp_def_s) == my_off_s:
        scheme_bonus_my += 2.5
        scheme_bonus_opp -= 1.0

    oc_obj = safe_dict(staff.get("OC"))
    dc_obj = safe_dict(staff.get("DC"))
    my_oc = safe_int(oc_obj.get("off", 3), 3)
    my_dc = safe_int(dc_obj.get("def", 3), 3)
    opp_coaches = safe_dict(opp_coaches)
    opp_oc = safe_int(opp_coaches.get("OC", 5), 5)
    opp_dc = safe_int(opp_coaches.get("DC", 5), 5)

    coaching_my = (get_tier_bonus(my_oc) - get_tier_bonus(opp_dc)) * 1.20
    coaching_opp = (get_tier_bonus(opp_oc) - get_tier_bonus(my_dc)) * 1.20

    hc_trait = safe_dict(staff.get("HC")).get("trait", "None")
    if hc_trait == "Tactician": 
        coaching_my += 0.9
    elif hc_trait == "Recruiter": 
        coaching_my += 0.25

    oc_trait = safe_dict(staff.get("OC")).get("trait", "None")
    if oc_trait in ["Air Raid", "Smashmouth", "Pro Style"] and oc_trait == my_off_s:
        scheme_bonus_my += 1.0

    hf = home_field_points(my_stadium_level) if is_home else 0.0
    opp_hf = home_field_points(opp_stadium_level) if not is_home else 0.0

    var_mult = 1.0
    if is_rival: 
        var_mult *= 1.35
    if game_plan == "Aggressive": 
        var_mult *= 1.25
    elif game_plan == "Conservative": 
        var_mult *= 0.85

    base_pts = 27.5
    exp_my = base_pts + my_edge + scheme_bonus_my + coaching_my + hf
    exp_opp = base_pts + opp_edge + scheme_bonus_opp + coaching_opp + opp_hf
    exp_my = max(10, min(50, exp_my))
    exp_opp = max(10, min(50, exp_opp))

    my_score = int(round(rng.gauss(exp_my, 7.0 * var_mult)))
    opp_score = int(round(rng.gauss(exp_opp, 7.0 * var_mult)))

    if my_score == opp_score:
        my_score += rng.choice([0, 3, 7])
        opp_score += rng.choice([0, 0, 3])

    my_score = max(0, min(70, my_score))
    opp_score = max(0, min(70, opp_score))
    
    explain = {
        "my_off": my_off,
        "my_def": my_def,
        "opp_off": opp_off,
        "opp_def": opp_def,
        "my_edge": float(my_edge),
        "opp_edge": float(opp_edge),
        "scheme_my": float(scheme_bonus_my),
        "scheme_opp": float(scheme_bonus_opp),
        "coach_my": float(coaching_my),
        "coach_opp": float(coaching_opp),
        "home_field": float(hf),
        "plan": game_plan
    }
    
    stats = {
        "qb_duel": [
            int((st.session_state.get("roster", {}) or {}).get("QB", 75)),
            int(max(60, min(99, opp_off)))
        ],
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

# ============================================================================
# AI SIMULATION
# ============================================================================

def simulate_ai_regular_season_seeded(seed: int):
    """Simulate AI teams' regular season results with deterministic RNG."""
    from models import get_conference
    
    rnd = random.Random(seed)
    results = []
    
    # Ensure opponents_db exists
    if len(st.session_state.opponents_db) < len(ALL_TEAMS):
        for t in ALL_TEAMS:
            if t not in st.session_state.opponents_db:
                st.session_state.opponents_db[t] = {"Prestige": 60, "OVR": 75}

    for team in sorted(st.session_state.opponents_db.keys()):
        if team == st.session_state.team_name: 
            continue
        
        data = st.session_state.opponents_db[team]
        prestige = data.get("Prestige", 60)
        conf = get_conference(team)
        
        if prestige > 90:
            wins = rnd.choices([12, 11, 10, 9], weights=[10, 30, 40, 20])[0]
        elif prestige > 80:
            wins = rnd.choices([11, 10, 9, 8, 7], weights=[5, 20, 35, 30, 10])[0]
        elif prestige > 60:
            wins = rnd.choices([9, 8, 7, 6, 5], weights=[10, 25, 30, 25, 10])[0]
        else:
            wins = rnd.choices([6, 5, 4, 3, 2], weights=[10, 30, 30, 20, 10])[0]
        
        losses = 12 - wins
        
        base_sos = 80 if conf == "SEC" else 78 if conf == "Big Ten" else 72 if conf in ["ACC", "Big 12"] else 60
        sos = base_sos + rnd.randint(-5, 5)
        
        results.append({
            "Team": team,
            "Wins": wins,
            "Losses": losses,
            "Conf": conf,
            "Prestige": prestige,
            "SOS": sos
        })
    
    return results
