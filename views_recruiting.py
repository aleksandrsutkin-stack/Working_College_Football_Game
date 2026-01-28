"""
Recruiting and offseason view functions for CFB Mogul V27.6
"""

import streamlit as st
import random
import math
from typing import List, Optional, Tuple
from config import POSITIONS, TRAITS
from models import (
    BudgetManager, safe_int, safe_float, helper_format_cash, format_position_delta,
    sync_team_ratings, add_news, safe_toast, generate_name, generate_star_player,
    compute_team_needs, normalize_shares, OpponentManager, get_conferences_map,
    apply_conference_move
)
from engine import distribute_exact, sync_alloc_to_inputs, engine_generate_schedule

# ============================================================================
# HS OUTREACH UI HELPERS
# ============================================================================

def render_hs_results_summary() -> bool:
    """Display HS outreach results if available."""
    last = st.session_state.get("hs_last_results", None)
    if not last:
        return False
    
    st.success("✅ HS Outreach Complete — Results Summary")
    cA, cB, cC = st.columns(3)
    cA.metric("Spent", helper_format_cash(last.get("spent", 0)))
    cB.metric("Booster Bonus", helper_format_cash(last.get("booster_bonus", 0)))
    cC.metric("Hidden Gems", int(last.get("gem_count", 0)))
    
    st.markdown("### 📈 Position Improvements")
    pos_changes = last.get("pos_changes", {}) or {}
    for p in POSITIONS:
        delta = pos_changes.get(p, 0)
        st.write(f"{p}: **{format_position_delta(delta)}**")
    
    if st.button("Dismiss Results"):
        st.session_state.hs_last_results = None
        st.rerun()
    
    st.divider()
    return True

def render_hs_budget_controls(max_budget: int, needs: List[str], hot: List[str]) -> int:
    """Render budget controls for HS recruiting."""
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(
            f"<div class='recruiting-intel'>Needs: <b>{', '.join(needs)}</b> | Pipeline: <b>{', '.join(hot)}</b></div>",
            unsafe_allow_html=True
        )
    with c2:
        current_cap = int(st.session_state.get("hs_total_spend", 0))
        safe_current_cap = min(current_cap, max_budget)
        new_cap = st.number_input(
            "Total Recruiting Budget ($)",
            min_value=0,
            max_value=max_budget,
            value=safe_current_cap,
            step=250_000,
            format="$%d"
        )
    
    new_cap = min(int(new_cap), max_budget)
    st.session_state.hs_total_spend = new_cap
    return new_cap

def render_hs_quick_allocations(budget: int, needs: List[str], hot: List[str]) -> Optional[dict]:
    """Render quick allocation buttons."""
    colA, colB, colC = st.columns(3)
    clicked = None
    
    if colA.button("⚖️ Balanced"):
        weights = {p: 1.0 for p in POSITIONS}
        clicked = distribute_exact(budget, weights, step=100_000)
    
    if colB.button("🎯 Needs Heavy"):
        weights = {p: (3.0 if p in needs else 1.0) for p in POSITIONS}
        clicked = distribute_exact(budget, weights, step=100_000)
    
    if colC.button("🔥 Pipeline Focus"):
        weights = {p: (3.0 if p in hot else 1.0) for p in POSITIONS}
        clicked = distribute_exact(budget, weights, step=100_000)
    
    return clicked

def render_hs_position_allocators(budget: int, needs: List[str], hot: List[str]) -> dict:
    """Render individual position allocators."""
    if "hs_alloc_by_pos" not in st.session_state:
        st.session_state.hs_alloc_by_pos = {p: 0 for p in POSITIONS}
    
    alloc = st.session_state.hs_alloc_by_pos
    for p in POSITIONS:
        key = f"input_{p}"
        if key not in st.session_state:
            st.session_state[key] = int(alloc.get(p, 0) or 0)
    
    st.divider()
    cols = st.columns(2)
    # V27.6 FIX: Format inputs with $ to prevent crash on user typing symbols
    new_alloc = alloc.copy()
    for idx, pos in enumerate(POSITIONS):
        with cols[idx % 2]:
            badges = ""
            if pos in needs:
                badges += " 🔴"
            if pos in hot:
                badges += " 🔥"
            
            val = st.number_input(
                f"{pos}{badges}",
                min_value=0,
                max_value=budget,
                value=int(alloc.get(pos, 0)),
                step=100_000,
                format="$%d",
                key=f"hs_pos_input_{pos}_v27"
            )
            new_alloc[pos] = int(val)
    
    return new_alloc

def validate_and_fix_allocation(alloc: dict, budget: int) -> Tuple[dict, bool]:
    """Validate and auto-fix allocations that exceed budget."""
    allocated = sum(int(alloc.get(p, 0) or 0) for p in POSITIONS)
    remaining = budget - allocated
    
    if remaining < 0 and allocated > 0:
        st.warning(f"⚠️ Manual adjustments exceeded budget by {helper_format_cash(abs(remaining))}. Auto-fixing...")
        scale = budget / allocated if allocated > 0 else 0.0
        fixed_alloc = {p: int(alloc[p] * scale) for p in POSITIONS}
        sync_alloc_to_inputs(fixed_alloc)
        import time
        time.sleep(0.8)
        return fixed_alloc, True
    
    return alloc, False

def execute_hs_outreach(budget: int, alloc: dict, needs: List[str]) -> None:
    """Execute HS outreach with given budget and allocation."""
    if not BudgetManager.spend(budget, "HS recruiting", show_toast=False):
        return
    
    shares = normalize_shares({p: (alloc[p] / max(1, budget)) * 100 for p in POSITIONS})
    res = process_hs_outreach(
        budget, shares, st.session_state.staff, st.session_state.prestige,
        st.session_state.inflation, st.session_state.hotspots,
        st.session_state.home_region, needs, is_dollars=True
    )
    
    if res["booster_bonus"] > 0:
        BudgetManager.add(res["booster_bonus"], "Boosters go wild over surprise recruits!", show_toast=True)
    
    for p, gain in res["roster_updates"].items():
        loss = random.randint(1, 4)
        current = safe_int(st.session_state.roster.get(p, 75), 75)
        st.session_state.roster[p] = max(40, min(99, current - loss + int(gain)))
    
    if res["gems"]:
        st.session_state.stars.extend(res["gems"])
        add_news(f"Scouts found {len(res['gems'])} hidden gems!")
    
    st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)
    sync_team_ratings()
    st.session_state.hs_last_results = {
        "spent": int(res.get("spent", 0) or 0),
        "booster_bonus": int(res.get("booster_bonus", 0) or 0),
        "pos_changes": dict(res.get("roster_updates", {}) or {}),
        "gem_count": len(res.get("gems", []) or [])
    }
    safe_toast("HS Outreach complete! See results above.")
    st.rerun()

# ============================================================================
# HS OUTREACH SCREEN
# ============================================================================

def show_offseason_hs_outreach():
    """HS Outreach screen - Step 2 of offseason."""
    if render_hs_results_summary():
        return
    
    st.subheader("2) HS Outreach: The War Room")
    st.write("Set your total recruiting budget, then distribute it to position groups.")
    
    hot = st.session_state.hotspots.get(st.session_state.home_region, [])
    needs = st.session_state.get("team_needs", [])
    max_budget = BudgetManager.get_current()
    
    new_cap = render_hs_budget_controls(max_budget, needs, hot)
    
    quick_alloc = render_hs_quick_allocations(new_cap, needs, hot)
    if quick_alloc:
        st.session_state.hs_alloc_by_pos = quick_alloc
        sync_alloc_to_inputs(quick_alloc)
        st.rerun()
    
    alloc = render_hs_position_allocators(new_cap, needs, hot)
    alloc, needs_rerun = validate_and_fix_allocation(alloc, new_cap)
    if needs_rerun:
        st.session_state.hs_alloc_by_pos = alloc
        st.rerun()
    
    allocated = sum(int(alloc.get(p, 0) or 0) for p in POSITIONS)
    remaining = new_cap - allocated
    
    st.divider()
    if new_cap == 0:
        st.info("Set a budget above to begin.")
    elif remaining == 0:
        st.success(f"✅ Fully Allocated: {helper_format_cash(new_cap)}")
    elif remaining > 0:
        st.warning(f"⚠️ Unassigned Funds: {helper_format_cash(remaining)}")
    else:
        st.error(f"🚫 Over Budget: {helper_format_cash(abs(remaining))}")
    
    st.session_state.hs_alloc_by_pos = alloc
    st.session_state.hs_spend_by_pos = {p: int(alloc.get(p, 0) or 0) for p in POSITIONS}
    
    disabled_confirm = (new_cap == 0) or (remaining != 0)
    if st.button("Confirm & Run Recruiting 🚀", type="primary", disabled=disabled_confirm):
        execute_hs_outreach(new_cap, alloc, needs)

# ============================================================================
# NIL SCREEN
# ============================================================================

def generate_nil_class_15(team_needs: list):
    """Generate 15 NIL prospects (5 per tier)."""
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

def show_offseason_nil_v8():
    """NIL Prospects screen - Step 1 of offseason."""
    st.subheader("1) NIL Prospects (Class of 15)")
    needs = st.session_state.get("team_needs", [])
    
    if not st.session_state.nil_class:
        st.session_state.nil_class = generate_nil_class_15(needs)
        add_news("NIL board posted: 15 prospects (Tier 1/2/3).")

    st.markdown(
        f"<div class='recruiting-intel'>Team Needs: <b>{', '.join(needs) if needs else 'Balanced'}</b></div>",
        unsafe_allow_html=True
    )
    st.write("You can sign any of these 15. When they're gone, they're gone (no infinite respawn).")
    
    signed = sum(1 for p in st.session_state.nil_class if p["status"] == "SIGNED")
    available = 15 - signed
    st.caption(f"Signed: {signed} | Remaining available: {available}")

    for p in st.session_state.nil_class:
        tier_badge = "badge-tier-s" if p["tier"] == 1 else ("badge-tier-a" if p["tier"] == 2 else "badge-tier-f")
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        c1.markdown(
            f"⭐ <b>{p['tier_label']}</b> — {p['pos']} {p['name']} ({p['rating']}) — {p['trait']}",
            unsafe_allow_html=True
        )
        c2.markdown(f"<span class='badge {tier_badge}'>{p['tier_label']}</span>", unsafe_allow_html=True)
        c3.write(f"Ask: {helper_format_cash(p['ask'])}")
        
        if p["status"] == "SIGNED":
            c4.write("✅ SIGNED")
        else:
            if c4.button("Sign", key=f"nil_sign_{p['id']}"):
                if BudgetManager.spend(p["ask"], f"sign {p['pos']} {p['name']}"):
                    st.session_state.roster[p["pos"]] = max(st.session_state.roster[p["pos"]], p["rating"])
                    p["status"] = "SIGNED"
                    add_news(f"{st.session_state.team_name} signs NIL {p['tier_label']} {p['pos']} {p['name']} ({p['rating']}).")
                    sync_team_ratings()
                    safe_toast("Signed ✔️")
                    st.rerun()

# ============================================================================
# HS OUTREACH LOGIC
# ============================================================================

def process_hs_outreach(total_spend: int, shares_or_alloc: dict, staff: dict, prestige: int,
                        inflation: float, hotspots: dict, home_region: str, team_needs: list,
                        is_dollars: bool = False):
    """Process HS outreach recruiting with budget distribution."""
    total_spend = max(0, int(total_spend))
    staff = staff or {}
    
    scout = safe_int((staff.get("Scout") or {}).get("recruit", 1), 1)
    hc_trait = (staff.get("HC") or {}).get("trait", "None")

    efficiency = 0.85 if scout >= 8 else (1.0 if scout >= 5 else 1.15)
    base_cost = 900_000 * float(inflation) * float(efficiency)
    hot_positions = hotspots.get(home_region, [])
    
    if is_dollars:
        allocated = 0
        for p in POSITIONS:
            try:
                allocated += int(float(shares_or_alloc.get(p, 0) or 0))
            except:
                pass
        spent = max(0, min(total_spend, allocated))
    else:
        spent = total_spend
    
    results = {"roster_updates": {}, "gems": [], "booster_bonus": 0, "spent": int(spent)}

    for pos in POSITIONS:
        raw = float(shares_or_alloc.get(pos, 0.0) or 0.0)
        if is_dollars:
            amt = max(0.0, raw)
        else:
            pct = raw
            amt = total_spend * (pct / 100.0)
        
        if amt <= 0:
            results["roster_updates"][pos] = -random.randint(1, 3)
            continue
        
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
        if pos in team_needs:
            gem_chance += 0.07
        if pos in hot_positions:
            gem_chance += 0.05
        if scout >= 8:
            gem_chance += 0.03
        if hc_trait == "Recruiter":
            gem_chance += 0.02
        
        if amt > base_cost * 1.25 and random.random() < gem_chance:
            star = generate_star_player(pos, tier=1)
            star["name"] += " (GEM)"
            results["gems"].append(star)
            change += 5
            results["booster_bonus"] += 250_000 + random.randint(0, 250_000)
        
        results["roster_updates"][pos] = change
    
    return results

# ============================================================================
# TOP-8 SCREEN
# ============================================================================

def generate_top8_prospects(team_needs: list):
    """Generate 8 elite prospects for Top-8 battles."""
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
    """Calculate commit chance for a Top-8 prospect."""
    staff = staff or {}
    scout = safe_int((staff.get("Scout") or {}).get("recruit", 1), 1)
    hc_trait = (staff.get("HC") or {}).get("trait", "None")

    chance = 0.18
    chance += (max(40, min(99, prestige)) - 60) * 0.004
    chance += (scout - 5) * 0.02
    if hc_trait == "Recruiter":
        chance += 0.05
    
    pos = recruit["pos"]
    spend = float(spend_by_pos.get(pos, 0.0))
    chance += min(0.20, spend / 10_000_000)
    
    return max(0.05, min(0.80, chance))

def show_offseason_top8_v8():
    """Top-8 Battles screen - Step 3 of offseason."""
    st.subheader("3) Top-8 Battles — Close on Elites")
    needs = st.session_state.get("team_needs", [])
    current_budget = int(st.session_state.get("budget", 0) or 0)
    
    if not st.session_state.get("top8"):
        st.session_state.top8 = generate_top8_prospects(needs)
        add_news("Top-8 board posted: 8 elite prospects.")
    
    if "top8_resolved" not in st.session_state:
        st.session_state.top8_resolved = set()

    st.markdown(
        f"<div class='nil-alert'>Available: <b>{helper_format_cash(current_budget)}</b></div>",
        unsafe_allow_html=True
    )
    
    for r in st.session_state.top8:
        rid = int(r["id"])
        pos = r["pos"]
        ask = int(r["ask"])
        already = rid in st.session_state.top8_resolved
        
        c1, c2, c3 = st.columns([4, 2, 2])
        with c1:
            st.markdown(f"⭐ **{pos} {r['name']} ({r['rating']})**")
        with c2:
            row_budget = int(st.session_state.get("budget", 0) or 0)
            max_offer = max(0, min(row_budget, max(ask * 2, 250_000)))
            default_offer = int(r.get("offer", 0) or 0)
            default_offer = max(0, min(default_offer, max_offer))
            offer = st.slider("Offer", 0, max_offer, default_offer, step=250_000, key=f"offer_{rid}")
            r["offer"] = int(offer)
        with c3:
            if r.get("status") == "COMMITTED":
                st.success("✅ COMMITTED")
            elif r.get("status") == "LOST":
                st.error("❌ LOST")
            else:
                chance = top8_commit_chance(r, {p: 0 for p in POSITIONS}, st.session_state.staff, st.session_state.prestige)
                st.write(f"Chance: **{int(chance*100)}%**")
                if st.button("Pitch", key=f"pitch_{rid}", disabled=already or r["offer"]<=0):
                    if BudgetManager.spend(r["offer"], "pitch"):
                        if random.random() < chance:
                            r["status"] = "COMMITTED"
                            st.session_state.roster[pos] = max(st.session_state.roster[pos], r["rating"])
                            safe_toast("Committed!")
                        else:
                            r["status"] = "LOST"
                            safe_toast("Lost recruit.")
                        st.session_state.top8_resolved.add(rid)
                        st.rerun()

    st.divider()
    if st.button("Simulate Remaining Pitches"):
        for r in st.session_state.top8:
            rid = int(r["id"])
            if rid not in st.session_state.top8_resolved and r.get("status") == "OPEN":
                st.session_state.top8_resolved.add(rid)
                r["status"] = "LOST"
        st.rerun()

# ============================================================================
# RECRUITING GRADE
# ============================================================================

def compute_recruiting_class_grade():
    """Calculate overall recruiting class grade."""
    nil = st.session_state.get("nil_class", []) or []
    top8 = st.session_state.get("top8", []) or []
    stars = st.session_state.get("stars", []) or []
    
    tier_points = 0
    tier_counts = {1: 0, 2: 0, 3: 0}
    for p in nil:
        if p.get("status") == "SIGNED":
            tier = int(p.get("tier", 3))
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
            tier_points += {1: 12, 2: 7, 3: 3}.get(tier, 3)
    
    top8_commits = [r for r in top8 if r.get("status") == "COMMITTED"]
    top8_points = len(top8_commits) * 10
    
    gem_count = 0
    for s in stars:
        if "(GEM)" in str(s.get("name", "")):
            gem_count += 1
    gem_points = gem_count * 6
    
    score = tier_points + top8_points + gem_points
    
    if score >= 70:
        grade = "A+"
    elif score >= 55:
        grade = "A"
    elif score >= 42:
        grade = "B"
    elif score >= 30:
        grade = "C"
    elif score >= 18:
        grade = "D"
    else:
        grade = "F"
    
    breakdown = {
        "score": score,
        "nil_signed": sum(tier_counts.values()),
        "tier_counts": tier_counts,
        "top8_commits": len(top8_commits),
        "gems_found": gem_count,
        "points": {
            "nil": tier_points,
            "top8": top8_points,
            "gems": gem_points
        }
    }
    
    return grade, score, breakdown

# ============================================================================
# MAIN OFFSEASON ORCHESTRATOR
# ============================================================================

def show_offseason():
    """Main offseason orchestrator."""
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
    
    if step == 1:
        show_offseason_nil_v8()
        st.divider()
        if st.button("Continue to HS Outreach →", type="primary"):
            st.session_state.offseason_step = 2
            st.rerun()
    
    elif step == 2:
        show_offseason_hs_outreach()
        st.divider()
        if st.button("Continue to Top-8 Battles →", type="primary"):
            st.session_state.offseason_step = 3
            st.rerun()
    
    elif step == 3:
        show_offseason_top8_v8()
        st.divider()
        if st.button("Finish Recruiting & Advance Season →", type="primary"):
            grade, score, breakdown = compute_recruiting_class_grade()
            last_hist = st.session_state.history[-1] if st.session_state.history else None
            if last_hist and safe_int(last_hist.get("Year", 0), 0) == year:
                last_hist["RecruitingGrade"] = grade
            
            add_news(f"Recruiting class grade: {grade} ({score} pts)")
            st.session_state.year += 1
            st.session_state.tenure += 1
            st.session_state.inflation = safe_float(st.session_state.get("inflation", 1.0), 1.0) * 1.02
            OpponentManager.evolve_universe()
            
            invite = maybe_generate_conference_invite()
            if not invite:
                ai_conference_swap_lightweight()
            
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
            st.session_state.nil_class = []
            st.session_state.hs_total_spend = 0
            st.session_state.hs_alloc_by_pos = {p: 0 for p in POSITIONS}
            st.session_state.top8 = []
            st.session_state.top8_resolved = set()
            st.session_state.offseason_step = 1
            st.session_state.team_needs = compute_team_needs(st.session_state.roster, k=3)
            from models import generate_hotspots
            st.session_state.hotspots = generate_hotspots()
            sync_team_ratings()
            
            st.session_state.recruiting_summary = {"grade": grade, "score": score, "breakdown": breakdown}
            st.session_state.game_state = "RECRUITING_WRAP"
            st.rerun()

# ============================================================================
# RECRUITING WRAP SCREEN
# ============================================================================

def show_recruiting_wrap():
    """Recruiting wrap-up screen showing final grade."""
    st.title("📦 Recruiting Wrap-Up")

    summary = st.session_state.get("recruiting_summary", {})
    if not summary:
        st.warning("No recruiting summary found.")
        if st.button("Back to Dashboard"):
            st.session_state.game_state = "DASHBOARD"
            st.rerun()
        return

    grade = summary.get("grade", "N/A")
    score = summary.get("score", 0)
    bd = summary.get("breakdown", {}) or {}

    st.success(f"Recruiting Grade: **{grade}**")
    st.write(f"Score: **{score}** points")
    st.caption("Tip: Strong recruiting improves next season's OFF/DEF and keeps boosters happy.")

    c1, c2, c3 = st.columns(3)
    c1.metric("NIL Signed", int(bd.get("nil_signed", 0)))
    c2.metric("Top-8 Commits", int(bd.get("top8_commits", 0)))
    c3.metric("Gems Found", int(bd.get("gems_found", 0)))

    pts = bd.get("points", {}) or {}
    st.markdown("### 📊 Points Breakdown")
    st.write(f"• NIL points: **{int(pts.get('nil', 0))}**")
    st.write(f"• Top-8 points: **{int(pts.get('top8', 0))}**")
    st.write(f"• Gems points: **{int(pts.get('gems', 0))}**")

    st.divider()

    if st.button("Begin New Season →", type="primary"):
        st.session_state.recruiting_summary = None
        st.session_state.game_state = "DASHBOARD"
        st.rerun()

# ============================================================================
# CONFERENCE REALIGNMENT
# ============================================================================

def maybe_generate_conference_invite():
    """Generate a conference invite based on performance."""
    if st.session_state.get("pending_invite"):
        return st.session_state.pending_invite
    
    conf_map = get_conferences_map()
    team = st.session_state.team_name
    cur_conf = st.session_state.team_conf
    prestige = int(st.session_state.get("prestige", 60) or 60)
    booster = int(st.session_state.get("booster_rating", 50) or 50)
    wins = int((st.session_state.get("record") or {}).get("w", 0) or 0)
    
    chance = 0.05
    if wins >= 9:
        chance += 0.08
    if wins >= 11:
        chance += 0.10
    if booster >= 80:
        chance += 0.06
    if prestige >= 80:
        chance += 0.06
    
    targets = []
    if cur_conf == "G5":
        if prestige >= 74 or wins >= 10:
            targets += ["Big 12", "ACC"]
        if prestige >= 84 or wins >= 11:
            targets += ["Big Ten", "SEC"]
    elif cur_conf in ["ACC", "Big 12"]:
        if prestige >= 86 or wins >= 11:
            targets += ["Big Ten", "SEC"]
    
    targets = [t for t in targets if t in conf_map and t != cur_conf]
    if not targets:
        return None
    
    if random.random() > min(0.35, chance):
        return None
    
    to_conf = random.choice(targets)
    base_mult = 1.10
    if to_conf == "SEC":
        base_mult = 1.18
    elif to_conf == "Big Ten":
        base_mult = 1.16
    
    note = "Blue-blood TV deal + tougher road games." if to_conf in ["SEC", "Big Ten"] else "New media deal."
    st.session_state.pending_invite = {"to_conf": to_conf, "boost_mult": base_mult, "note": note}
    add_news(f"{team} receives a conference invite to the {to_conf}.")
    return st.session_state.pending_invite

def ai_conference_swap_lightweight():
    """Simulate AI conference realignment."""
    conf_map = get_conferences_map()
    user_team = st.session_state.team_name
    
    if random.random() > 0.10:
        return None
    
    pools = [("ACC", "Big 12"), ("Big Ten", "SEC"), ("G5", "Big 12")]
    from_conf, to_conf = random.choice(pools)
    from_list = [t for t in conf_map.get(from_conf, []) if t != user_team]
    if not from_list:
        return None
    
    team = random.choice(from_list)
    conf_map[from_conf].remove(team)
    conf_map.setdefault(to_conf, []).append(team)
    add_news(f"Realignment: {team} moves from {from_conf} to {to_conf}.")
