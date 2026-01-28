"""
Data models, utility functions, and manager classes for CFB Mogul V27.6
"""

import streamlit as st
import random
import datetime
from config import POSITIONS, TROPHY_ICONS, CONFERENCES, ALL_TEAMS

# ============================================================================
# CORE UTILITIES
# ============================================================================

def safe_int(value, default: int = 0) -> int:
    """Safely convert any value to integer with fallback."""
    try:
        if value is None or value == "": return default
        return int(float(value))
    except (ValueError, TypeError): return default

def safe_float(value, default: float = 0.0) -> float:
    """Safely convert any value to float with fallback."""
    try:
        if value is None or value == "": return default
        return float(value)
    except (ValueError, TypeError): return default

def safe_dict(x):
    """Safely return a dict or empty dict if None."""
    return x if isinstance(x, dict) else {}

def clamp_budget() -> None:
    """Ensure budget never goes negative due to rounding errors."""
    try:
        st.session_state.budget = max(0, int(st.session_state.get("budget", 0) or 0))
    except Exception:
        st.session_state.budget = 0

def safe_toast(msg: str) -> None:
    """Show toast notification with fallback to st.info."""
    try: 
        st.toast(msg)
    except Exception:
        try: 
            st.info(msg)
        except Exception: 
            pass

# ============================================================================
# FORMATTING & VALIDATION
# ============================================================================

def helper_format_cash(amount: int) -> str:
    """Format currency amounts for display."""
    try: 
        amount = int(amount)
    except Exception: 
        amount = 0
    return f"${amount/1_000_000:.1f}M" if amount >= 1_000_000 else f"${int(amount/1_000)}K"

def format_position_delta(delta: float) -> str:
    """Format position rating changes with +/- sign."""
    try: 
        delta = float(delta)
    except Exception: 
        delta = 0.0
    sign = "+" if delta >= 0 else ""
    return f"{sign}{int(round(delta))}"

def get_letter_grade(rating: int) -> str:
    """Convert numeric rating (0-10) to letter grade."""
    if rating >= 9: return "A+"
    elif rating >= 8: return "A"
    elif rating >= 7: return "B"
    elif rating >= 5: return "C"
    elif rating >= 3: return "D"
    else: return "F"

def validate_budget_input(amount: int, max_budget: int, action: str = "transaction") -> bool:
    """Validate budget transaction before execution."""
    amount = safe_int(amount, 0)
    max_budget = safe_int(max_budget, 0)
    if amount < 0:
        st.error(f"❌ Invalid {action}: Amount cannot be negative (${amount:,})")
        return False
    if amount > max_budget:
        st.error(f"❌ Insufficient funds for {action}\n\nNeed: {helper_format_cash(amount)}\nHave: {helper_format_cash(max_budget)}\nShort: {helper_format_cash(amount - max_budget)}")
        return False
    return True

# ============================================================================
# GENERATORS
# ============================================================================

def generate_name() -> str:
    """Generate random player name from pool."""
    first = ["Marcus", "Trey", "Deion", "Caleb", "Jalen", "Bo", "Ty", "Zay", "Kool-Aid", "Tank", "Arch", "Shedeur", "Quinn", "Travis", "Ashton", "Jaxson", "Miller"]
    last = ["King", "Sanders", "Ewers", "Milroe", "Hunter", "Bond", "Nix", "Penix", "Bowers", "Manning", "Gabriel", "Beck", "Jeanty", "Judkins", "Dart", "Moss"]
    return f"{random.choice(first)} {random.choice(last)}"

def generate_coach_name() -> str:
    """Generate random coach name from pool."""
    first = ["Kirby", "Nick", "Ryan", "Lane", "Dabo", "Lincoln", "Steve", "Chip", "Deion", "Marcus", "Dan", "Kalen", "Matt", "Luke"]
    last = ["Smart", "Saban", "Day", "Kiffin", "Swinney", "Riley", "Sarkisian", "Kelly", "Sanders", "Freeman", "Lanning", "DeBoer", "Rhule", "Fickell"]
    return f"{random.choice(first)} {random.choice(last)}"

def generate_star_player(pos: str, tier: int = 1) -> dict:
    """Generate a star recruit/player."""
    base = 86 if tier == 1 else 78
    return {
        "name": generate_name(),
        "pos": pos,
        "rating": random.randint(base, min(99, base + 10))
    }

def generate_ga_coach(role: str) -> dict:
    """Generate a Graduate Assistant coach (low ratings, free)."""
    base = random.randint(2, 5)
    return {
        "name": generate_coach_name() + " (GA)",
        "role": role,
        "off": min(10, base + random.randint(0, 2)),
        "def": min(10, base + random.randint(0, 2)),
        "recruit": min(10, base + random.randint(0, 2)),
        "trait": "None",
        "salary": 0,
        "history": "Internal Promotion",
        "scouted": True
    }

# ============================================================================
# MANAGER CLASSES
# ============================================================================

class BudgetManager:
    """Centralized budget operations with validation and news integration."""
    
    @staticmethod
    def get_current() -> int:
        return safe_int(st.session_state.get("budget", 0), 0)
    
    @staticmethod
    def spend(amount: int, description: str, show_toast: bool = True) -> bool:
        amount = safe_int(amount, 0)
        if not validate_budget_input(amount, BudgetManager.get_current(), description):
            return False
        st.session_state.budget = BudgetManager.get_current() - amount
        clamp_budget()
        if show_toast: 
            safe_toast(f"Spent {helper_format_cash(amount)} on {description}")
        return True
    
    @staticmethod
    def add(amount: int, description: str, show_toast: bool = True) -> None:
        amount = safe_int(amount, 0)
        st.session_state.budget = BudgetManager.get_current() + amount
        clamp_budget()
        if show_toast and amount > 0: 
            safe_toast(f"Received {helper_format_cash(amount)}: {description}")
        if description: 
            add_news(description)
    
    @staticmethod
    def calculate_revenue(tier: int, marketing_level: int, inflation: float) -> int:
        base_revenue = {1: 40_000_000, 2: 25_000_000, 3: 10_000_000, 4: 5_000_000}.get(tier, 5_000_000)
        marketing_bonus = safe_int(marketing_level, 0) * 2_000_000
        total = (base_revenue + marketing_bonus) * float(inflation)
        conf_boost = float(st.session_state.get("conf_revenue_boost_mult", 1.0))
        total *= conf_boost
        return int(total)


class OpponentManager:
    """Centralized management of opponent team data."""
    
    @staticmethod
    def get(team_name: str) -> dict:
        if "opponents_db" not in st.session_state: 
            st.session_state.opponents_db = {}
        if team_name not in st.session_state.opponents_db:
            st.session_state.opponents_db[team_name] = {"Prestige": 60, "OVR": 75}
        
        opp = st.session_state.opponents_db[team_name]
        opp.setdefault("Prestige", 60)
        opp.setdefault("OVR", 75)
        
        if "OffOVR" not in opp or "DefOVR" not in opp:
            base = safe_int(opp.get("OVR", 75), 75)
            opp["OffOVR"] = max(50, min(99, base + random.randint(-3, 3)))
            opp["DefOVR"] = max(50, min(99, base + random.randint(-3, 3)))
        
        if "Coaches" not in opp or not isinstance(opp.get("Coaches"), dict):
            opp["Coaches"] = {"OC": 5, "DC": 5}
        else:
            opp["Coaches"].setdefault("OC", 5)
            opp["Coaches"].setdefault("DC", 5)
            
        opp.setdefault("Stadium", 7)
        opp.setdefault("Off", "Pro Style")
        opp.setdefault("Def", "Man Coverage")
        return opp
    
    @staticmethod
    def evolve_universe() -> None:
        if "opponents_db" not in st.session_state: 
            return
        for team, data in st.session_state.opponents_db.items():
            base_ovr = safe_int(data.get("OVR", 75), 75)
            wins = int((base_ovr / 100) * 12) + random.randint(-2, 2)
            wins = max(0, min(12, wins))
            prev_prestige = safe_int(data.get("Prestige", 60), 60)
            change = 3 if wins >= 10 else (-3 if wins <= 4 else 0)
            data["Prestige"] = max(20, min(99, prev_prestige + change))
            
            if data["Prestige"] > 80 and wins < 6:
                data["Coaches"] = {"OC": random.randint(7, 9), "DC": random.randint(7, 9)}
            elif data["Prestige"] < 70 and wins > 9:
                data["Coaches"] = {"OC": random.randint(3, 6), "DC": random.randint(3, 6)}
            
            base_from_prestige = int(data["Prestige"] * 0.9)
            data["OVR"] = base_from_prestige + random.randint(-3, 3)
            
            if random.random() < 0.35:
                data.pop("OffOVR", None)
                data.pop("DefOVR", None)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def make_deterministic_rng(*parts) -> random.Random:
    """Creates a stable RNG based on current save state + inputs."""
    base = (
        str(st.session_state.get("state_version", "")),
        str(st.session_state.get("year", "")),
        str(st.session_state.get("team_name", ""))
    )
    seed_str = "|".join([*base, *[str(p) for p in parts]])
    return random.Random(seed_str)

def add_news(msg: str):
    """Add a news item to the news feed."""
    if "news" not in st.session_state or st.session_state.news is None: 
        st.session_state.news = []
    stamp = datetime.datetime.now().strftime("%b %d")
    st.session_state.news.insert(0, {"ts": stamp, "text": msg})
    st.session_state.news = st.session_state.news[:40]

def render_news_box():
    """Display news feed."""
    st.subheader("🗞️ News Wire")
    items = st.session_state.get("news", []) or []
    if not items: 
        st.info("No headlines yet.")
        return
    st.markdown("<div class='news-box'>", unsafe_allow_html=True)
    for it in items[:18]:
        txt = it if isinstance(it, str) else f"{it.get('ts','')} - {it.get('text','')}"
        st.markdown(f"<div class='news-item'>{txt}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def get_conferences_map():
    """Get current conference map from session state."""
    if "conferences_map" not in st.session_state or not isinstance(st.session_state.conferences_map, dict):
        st.session_state.conferences_map = {k: list(v) for k, v in CONFERENCES.items()}
    for k, v in CONFERENCES.items(): 
        st.session_state.conferences_map.setdefault(k, list(v))
    return st.session_state.conferences_map

def get_conference(team: str) -> str:
    """Get conference for a given team."""
    conf_map = get_conferences_map()
    for conf, teams in conf_map.items():
        if team in teams: 
            return conf
    return "G5"

def compute_team_needs(roster: dict, k: int = 3) -> list:
    """Identify weakest position groups."""
    roster = roster or {}
    vals = [(pos, safe_int(roster.get(pos, 75), 75)) for pos in POSITIONS]
    vals.sort(key=lambda x: x[1])
    return [p for p, _ in vals[:max(1, int(k))]]

def role_rating(coach: dict, role: str) -> int:
    """Calculate coach rating for specific role."""
    if not coach: return 0
    if role == "HC":
        v = (safe_int(coach.get("off"), 0) + safe_int(coach.get("def"), 0) + safe_int(coach.get("recruit"), 0)) / 3
    elif role == "OC":
        v = safe_int(coach.get("off"), 0)
    elif role == "DC":
        v = safe_int(coach.get("def"), 0)
    elif role == "Scout":
        v = safe_int(coach.get("recruit"), 0)
    else:
        v = safe_int(coach.get("off"), 0)
    return int(max(0, min(10, round(v))))

def get_bowl_name(user_rank: int) -> str:
    """Get bowl game name based on ranking."""
    from config import BOWL_MAPPING
    if user_rank <= 14: tier = "High"
    elif user_rank <= 20: tier = "Mid"
    else: tier = "Low"
    return random.choice(BOWL_MAPPING.get(tier, ["Gator Bowl"]))

def get_season_metrics():
    """Calculate season metrics (SOS, best win, worst loss)."""
    logs = st.session_state.get("season_logs", []) or []
    if not logs: return (0, "N/A", "N/A")
    
    opp_ovrs = [safe_int(x.get("OppOVR", 70), 70) for x in logs]
    avg_sos = int(round(sum(opp_ovrs) / max(1, len(opp_ovrs))))
    
    best_win_ovr = -1
    best_win_label = "N/A"
    worst_loss_ovr = 999
    worst_loss_label = "N/A"
    
    for x in logs:
        opp = x.get("Opponent", "Opponent")
        ovr = safe_int(x.get("OppOVR", 70), 70)
        is_win = str(x.get("Score", "")).startswith("W")
        
        if is_win and ovr > best_win_ovr:
            best_win_ovr = ovr
            best_win_label = f"{opp} (OVR {ovr})"
        if (not is_win) and ovr < worst_loss_ovr:
            worst_loss_ovr = ovr
            worst_loss_label = f"{opp} (OVR {ovr})"
    
    return (avg_sos, best_win_label, worst_loss_label)

def build_season_summary_dict():
    """Build comprehensive season summary."""
    w = safe_int(st.session_state.record.get("w", 0), 0)
    l = safe_int(st.session_state.record.get("l", 0), 0)
    sos, best_win, worst_loss = get_season_metrics()
    expect = safe_int(st.session_state.get("expected_wins", 6), 6)
    delta = w - expect
    
    final_rank = "NR"
    results = st.session_state.get("selection_sunday_results", []) or []
    for i, t in enumerate(results):
        if t.get("IsUser") or t.get("Team") == st.session_state.team_name:
            final_rank = f"#{i+1}"
            break
    
    postseason = st.session_state.get("last_postseason_result", "NONE")
    
    return {
        "Record": f"{w}-{l}",
        "SOS": sos,
        "BestWin": best_win,
        "WorstLoss": worst_loss,
        "ExpectedWins": expect,
        "Delta": delta,
        "FinalRank": final_rank,
        "Postseason": postseason
    }

def generate_hotspots():
    """Generate regional recruiting hotspots."""
    from config import REGION_STRENGTH
    regions = list(REGION_STRENGTH.keys()) or ["South", "Midwest", "West", "North"]
    out = {}
    for r in regions:
        out[r] = random.sample(POSITIONS, k=2)
    return out

def calculate_committee_score(team_name, wins, losses, conf, sos_score):
    """Calculate CFP committee score (V27.6: Enhanced SOS weighting)."""
    score = (wins * 105) - (losses * 115)
    
    # Power conference boost
    if conf in ["SEC", "Big Ten"]: 
        score += 140
    elif conf in ["ACC", "Big 12"]: 
        score += 80
    
    # SOS importance doubled (V27.6)
    score += (sos_score * 3.0)
    
    # G5 "perfection or bust" penalty (V27.6)
    if conf in ["G5", "MAC", "Indep"] and losses > 0:
        score -= 300
        
    return int(score)

def trophy_icon(name: str) -> str:
    """Get emoji icon for trophy name."""
    return TROPHY_ICONS.get(name, TROPHY_ICONS.get("Bowl Win", "🎳"))

def award_trophy(trophy_name: str):
    """Award a trophy to the player's collection."""
    if "trophies" not in st.session_state:
        st.session_state.trophies = []
    st.session_state.trophies.append({
        "Year": st.session_state.year,
        "Name": trophy_name,
        "Icon": trophy_icon(trophy_name)
    })

def render_trophy_gallery(title_text: str = "🏆 Trophy Gallery"):
    """Display the player's trophy collection in a grid."""
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
                f"<div class='trophy-tile'>"
                f"<div style='font-size:2em'>{icon}</div>"
                f"<div style='font-weight:800'>{name}</div>"
                f"<div class='small-muted'>Year {year}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

def calculate_saban_score(career_stats, prestige):
    """Calculate legacy score based on wins, bowls, and titles."""
    return int(
        (career_stats.get("w", 0) * 1) +
        (career_stats.get("bowl_w", 0) * 5) +
        (career_stats.get("titles", 0) * 50) +
        (prestige * 0.5)
    )

def apply_conference_move(to_conf: str, boost_mult: float):
    """Move team to new conference and update revenue multiplier."""
    conf_map = get_conferences_map()
    team = st.session_state.team_name
    cur_conf = st.session_state.team_conf
    
    if cur_conf in conf_map and team in conf_map[cur_conf]:
        conf_map[cur_conf].remove(team)
    if to_conf not in conf_map:
        conf_map[to_conf] = []
    if team not in conf_map[to_conf]:
        conf_map[to_conf].append(team)
    
    st.session_state.team_conf = to_conf
    st.session_state.conf_revenue_boost_mult = float(boost_mult)
    add_news(f"{team} joins the {to_conf}.")

def apply_roster_attrition():
    """V27.6: Simulates graduation and draft declaration to prevent infinite stacking."""
    attrition_log = []
    for p in POSITIONS:
        current = st.session_state.roster[p]
        # Base loss: Seniors graduating
        loss = random.randint(3, 7)
        # Draft penalty: High ratings lose more talent
        if current > 90: 
            loss += random.randint(1, 4)
        
        new_val = max(40, current - loss)
        st.session_state.roster[p] = new_val
        attrition_log.append(f"{p}: -{loss}")
    
    add_news(f"Graduation/Draft departures: {', '.join(attrition_log)}")

def end_regular_season_and_stay_on_results():
    """Finalize regular season and prepare for postseason."""
    if st.session_state.season_end_ready:
        return
    
    st.session_state.season_simulated = True
    st.session_state.season_end_ready = True
    
    rev = BudgetManager.calculate_revenue(
        st.session_state.school_tier,
        st.session_state.facilities["Marketing"],
        st.session_state.inflation
    )
    BudgetManager.add(rev, f"End of Regular Season Payout", show_toast=False)
    st.session_state.revenue_report = f"End of Regular Season Payout: +{helper_format_cash(rev)}"
    add_news(f"Regular season ends at {st.session_state.record['w']}-{st.session_state.record['l']}.")
    
    from engine import simulate_ai_regular_season_seeded
    st.session_state.ai_records = simulate_ai_regular_season_seeded(st.session_state.year)
    st.session_state.game_state = "SEASON_END"

def normalize_shares(shares: dict):
    """Normalize recruiting shares to sum to 100."""
    def _val(pos):
        try:
            return max(0.0, float(shares.get(pos, 0.0)))
        except Exception:
            return 0.0
    
    total = sum(_val(p) for p in POSITIONS)
    if total <= 0:
        return {p: 100.0 / len(POSITIONS) for p in POSITIONS}
    return {p: (_val(p) / total) * 100.0 for p in POSITIONS}

def render_achievements_panel():
    """Display achievements list."""
    st.subheader("🎖️ Achievements")
    ach = st.session_state.get("achievements", []) or []
    if not ach:
        st.info("No achievements yet.")
        return
    for a in ach[-20:][::-1]:
        st.write(f"• {a}")

def render_dynasty_timeline(max_items=25):
    """Display dynasty history timeline."""
    st.subheader("🧾 Dynasty Timeline")
    hist = st.session_state.get("history", []) or []
    if not hist:
        st.info("No seasons logged yet.")
        return
    for h in hist[-12:][::-1]:
        st.write(f"Year {h.get('Year','?')}: {h.get('Record','?')} | Rank {h.get('Rank','NR')} | {h.get('PostseasonResult','')}")

def check_and_award_achievements():
    """Check for and award achievements."""
    if "achievements" not in st.session_state or st.session_state.achievements is None:
        st.session_state.achievements = []
    
    if st.session_state.get("last_postseason_result") == "BOWL_WIN" and "First Bowl Win" not in st.session_state.achievements:
        st.session_state.achievements.append("First Bowl Win")

def init_playoff_bracket(user_rank, user_team_name):
    """Initialize CFP playoff bracket."""
    results = st.session_state.get("selection_sunday_results", []) or []
    top12 = [t.get("Team") for t in results[:12] if t.get("Team")]
    
    while len(top12) < 12: 
        top12.append("FCS East")
    
    seen = set()
    for i in range(len(top12)):
        nm = top12[i]
        if nm in seen: 
            top12[i] = "FCS East"
        else: 
            seen.add(nm)
    
    seed_map = {tm: idx for idx, tm in enumerate(top12, start=1)}
    
    try: 
        ur = int(user_rank)
    except: 
        ur = 999
    
    if 1 <= ur <= 12:
        target_idx = ur - 1
        top12[target_idx] = user_team_name
        seed_map[user_team_name] = ur
        for i in range(len(top12)):
            if i != target_idx and top12[i] == user_team_name: 
                top12[i] = "FCS East"
    
    r1_matches = [
        {"seed_high": 5, "seed_low": 12, "t1": top12[4], "t2": top12[11], "winner": None},
        {"seed_high": 6, "seed_low": 11, "t1": top12[5], "t2": top12[10], "winner": None},
        {"seed_high": 7, "seed_low": 10, "t1": top12[6], "t2": top12[9],  "winner": None},
        {"seed_high": 8, "seed_low": 9,  "t1": top12[7], "t2": top12[8],  "winner": None},
    ]
    qf_seeds = top12[:4]
    
    return {
        "Type": "CFP",
        "Round": 1,
        "Seeds": top12,
        "QF_Seeds": qf_seeds,
        "Matches": r1_matches,
        "UserAlive": True,
        "Rank": int(ur),
        "SeedMap": seed_map
    }
