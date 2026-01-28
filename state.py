"""
State management, migration, and save/load functionality for CFB Mogul V27.6
"""

import streamlit as st
import json
import datetime
import time
from config import ALLOWED_SAVE_KEYS, STATE_VERSION, POSITIONS, CONFERENCES
from models import (
    safe_int, safe_float, generate_hotspots, compute_team_needs,
    get_conferences_map
)

# ============================================================================
# STATE SYNCHRONIZATION
# ============================================================================

def sync_team_ratings():
    """Recalculate team OFF/DEF/OVR from roster, staff, and facilities."""
    from engine import compute_team_unit_ratings
    
    if "roster" in st.session_state and "staff" in st.session_state and "facilities" in st.session_state:
        try:
            res = compute_team_unit_ratings(
                st.session_state.roster,
                st.session_state.staff,
                st.session_state.facilities
            )
            st.session_state.team_off = res[0]
            st.session_state.team_def = res[1]
            st.session_state.team_rating = res[2]
        except Exception:
            st.session_state.team_off = int(st.session_state.get("team_off", 75) or 75)
            st.session_state.team_def = int(st.session_state.get("team_def", 75) or 75)
            st.session_state.team_rating = int(st.session_state.get("team_rating", 75) or 75)

# ============================================================================
# STATE MIGRATION
# ============================================================================

def migrate_state():
    """Migrate and validate session state to current version."""
    if "state_version" not in st.session_state:
        st.session_state.state_version = 0.0
    
    # Convert top8_resolved from list to set if needed
    if isinstance(st.session_state.get("top8_resolved"), list):
        st.session_state.top8_resolved = set(st.session_state.top8_resolved)

    defaults = {
        "year": 2026, "prestige": 60, "job_security": 75, "expected_wins": 6, "tenure": 1,
        "history": [], "schedule": [], "season_simulated": False,
        "active_transfers": {p: False for p in POSITIONS},
        "inflation": 1.0, "revenue_report": None,
        "postseason_data": {"Type": None, "Rank": 0, "Round": 0, "Matches": []},
        "team_needs": [], "game_plan": "Normal", "week_index": 0, "news": [],
        "offseason_step": 1, "nil_class": [], "hs_total_spend": 0,
        "hs_shares": {p: 100.0 / len(POSITIONS) for p in POSITIONS},
        "hs_spend_by_pos": {p: 0 for p in POSITIONS},
        "hs_alloc_by_pos": {p: 0 for p in POSITIONS},
        "top8": [], "top8_resolved": set(), "trophies": [],
        "conf_revenue_boost_mult": 1.0, "pending_invite": None,
        "season_end_ready": False, "booster_rating": 50, "ai_records": [],
        "selection_sunday_results": [], "last_postseason_result": "NONE",
        "ad_name": "Coach Prime", "team_name": "Unknown U", "team_color": "#333333",
        "team_conf": "G5", "team_rival": "Rival", "home_region": "South",
        "school_tier": 3, "achievements": [], "milestone_log": [],
        "conferences_map": {k: list(v) for k, v in CONFERENCES.items()},
        "hs_last_results": None, "recruiting_summary": None,
        "career_stats": {"w": 0, "l": 0, "bowl_w": 0, "bowl_l": 0, "titles": 0},
        "my_schemes": {"Off": "Pro Style", "Def": "Man Coverage"},
        "candidates": {}, "opponents_db": {}, "season_logs": [], "budget": 0,
        "staff": {}, "stars": [],
        "last_known_team_name": None, "last_known_team_color": None
    }

    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Ensure integer fields are actually integers
    for k in ["year", "budget", "prestige", "job_security", "expected_wins", 
              "tenure", "week_index", "booster_rating", "school_tier"]:
        try:
            st.session_state[k] = int(st.session_state.get(k, 0) or 0)
        except Exception:
            st.session_state[k] = int(defaults.get(k, 0) or 0)

    # Ensure roster exists and has all positions
    st.session_state.roster = st.session_state.get("roster", {}) or {p: 75 for p in POSITIONS}
    for p in POSITIONS:
        if p not in st.session_state.roster:
            st.session_state.roster[p] = 75

    # Ensure staff dict exists
    st.session_state.staff = st.session_state.get("staff", {}) or {}
    
    # Ensure facilities exist with defaults
    st.session_state.facilities = st.session_state.get("facilities", {}) or {
        "Marketing": 1, "Training": 1, "Stadium": 1
    }
    for k, default_val in {"Marketing": 1, "Training": 1, "Stadium": 1}.items():
        if k not in st.session_state.facilities or st.session_state.facilities[k] in [None, ""]:
            st.session_state.facilities[k] = default_val

    # Ensure record exists
    st.session_state.record = st.session_state.get("record", {}) or {"w": 0, "l": 0}
    
    # Ensure hotspots exist
    st.session_state.hotspots = st.session_state.get("hotspots", {}) or generate_hotspots()
    
    # Ensure team_needs exist
    st.session_state.team_needs = st.session_state.get("team_needs", []) or compute_team_needs(st.session_state.roster, k=3)

    # Ensure conferences_map exists
    get_conferences_map()
    tc = st.session_state.team_conf
    if tc not in st.session_state.conferences_map:
        st.session_state.conferences_map[tc] = []
    if st.session_state.team_name not in st.session_state.conferences_map[tc]:
        st.session_state.conferences_map[tc].append(st.session_state.team_name)

    # Recruiting migration logic (fix allocations)
    try:
        alloc_map = st.session_state.get("hs_alloc_by_pos", {}) or {}
        need_migrate_alloc = (
            (not isinstance(alloc_map, dict)) or 
            (sum(int(v or 0) for v in alloc_map.values()) == 0 and 
             int(st.session_state.get("hs_total_spend", 0) or 0) > 0)
        )
        
        if need_migrate_alloc:
            hs_total = int(st.session_state.get("hs_total_spend", 0) or 0)
            hs_spend = st.session_state.get("hs_spend_by_pos", {}) or {}
            hs_shares = st.session_state.get("hs_shares", {}) or {}
            alloc = {p: 0 for p in POSITIONS}
            
            if any(int(hs_spend.get(p, 0) or 0) > 0 for p in POSITIONS):
                alloc = {p: int(hs_spend.get(p, 0) or 0) for p in POSITIONS}
            elif hs_total > 0 and any(float(hs_shares.get(p, 0) or 0.0) > 0.0 for p in POSITIONS):
                alloc = {p: int(round((float(hs_shares.get(p, 0) or 0.0) / 100.0) * hs_total)) for p in POSITIONS}
            else:
                alloc = {p: int(st.session_state.get("hs_alloc_by_pos", {}).get(p, 0) or 0) for p in POSITIONS}
            
            # Deterministic adjustment logic
            total_alloc = sum(alloc.values())
            if hs_total > 0 and total_alloc != hs_total:
                remainder = hs_total - total_alloc
                if remainder > 0:
                    order = sorted(POSITIONS, key=lambda p: alloc.get(p, 0), reverse=True)
                    i = 0
                    while remainder > 0:
                        p = order[i % len(order)]
                        add = min(100_000, remainder) if remainder >= 100_000 else remainder
                        alloc[p] += add
                        remainder -= add
                        i += 1
                elif remainder < 0:
                    order = sorted(POSITIONS, key=lambda p: alloc.get(p, 0))
                    i = 0
                    while remainder < 0:
                        p = order[i % len(order)]
                        take = min(100_000, alloc.get(p, 0), abs(remainder))
                        if take <= 0:
                            i += 1
                            continue
                        alloc[p] -= take
                        remainder += take
                        i += 1
            
            st.session_state.hs_alloc_by_pos = alloc
            st.session_state.hs_spend_by_pos = {p: int(alloc.get(p, 0) or 0) for p in POSITIONS}
            total_alloc = sum(st.session_state.hs_spend_by_pos.values()) or 0
            if total_alloc > 0:
                st.session_state.hs_shares = {
                    p: (st.session_state.hs_spend_by_pos[p] / total_alloc) * 100.0 
                    for p in POSITIONS
                }
            else:
                st.session_state.hs_shares = {p: 100.0 / len(POSITIONS) for p in POSITIONS}
    except Exception:
        st.session_state.hs_alloc_by_pos = {p: 0 for p in POSITIONS}
        st.session_state.hs_spend_by_pos = {p: 0 for p in POSITIONS}
        st.session_state.hs_shares = {p: 100.0 / len(POSITIONS) for p in POSITIONS}

    sync_team_ratings()
    st.session_state.state_version = STATE_VERSION
    
    # Persist last known identity
    try:
        tn = st.session_state.get("team_name")
        if tn and tn != "Unknown U":
            st.session_state["last_known_team_name"] = tn
            st.session_state["last_known_team_color"] = st.session_state.get("team_color", "#333333")
    except Exception:
        pass

# ============================================================================
# INITIALIZATION
# ============================================================================

def init_session_state_defaults():
    """Initialize session state with defaults if not present."""
    if "game_state" not in st.session_state:
        st.session_state.game_state = "SETUP"
    migrate_state()

# ============================================================================
# SAVE/LOAD HELPERS
# ============================================================================

def safe_json_default(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    return str(obj)

# ============================================================================
# SAVE/LOAD UI
# ============================================================================

def render_system_sidebar():
    """Render save/load system in sidebar."""
    with st.sidebar:
        st.header("💾 Dynasty System")
        st.caption(f"Version {STATE_VERSION}")
        
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
        
        uploaded_file = st.file_uploader("Import Save File", type=["json"])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                for k, v in data.items():
                    if k in ALLOWED_SAVE_KEYS:
                        if k == "top8_resolved":
                            st.session_state[k] = set(v) if isinstance(v, list) else set()
                        else:
                            st.session_state[k] = v
                migrate_state()
                st.session_state.candidates = {}
                sync_team_ratings()
                st.success("Save Loaded Successfully! Reloading...")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error loading save: {e}")
