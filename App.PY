"""
College Football Mogul V27.6
Main entry point for Streamlit deployment
"""

import streamlit as st
from config import setup_page_config, inject_custom_css
from state import init_session_state_defaults, render_system_sidebar
from views_core import run_setup, show_dashboard, show_fired, show_retirement
from views_season import show_season_end, show_selection_sunday, show_postseason, show_season_recap
from views_recruiting import show_offseason, show_recruiting_wrap
from config import ALL_TEAMS, TEAMS_DB

# Required function verification
REQUIRED_FUNCS = [
    "run_setup", "show_dashboard", "show_season_end", "show_selection_sunday",
    "show_postseason", "show_season_recap", "show_offseason", "show_recruiting_wrap",
    "show_fired", "show_retirement"
]

def verify_required_functions():
    """Verify all required functions are available."""
    import sys
    current_module = sys.modules[__name__]
    missing = []
    for fn in REQUIRED_FUNCS:
        if not hasattr(current_module, fn):
            missing.append(fn)
    
    if missing:
        st.error(f"❌ Missing required functions: {', '.join(missing)}")
        st.error("Please check that all view modules are properly imported.")
        st.stop()

# ============================================================================
# INITIALIZATION
# ============================================================================
setup_page_config()
inject_custom_css()
init_session_state_defaults()
verify_required_functions()
render_system_sidebar()

# ============================================================================
# ROUTER
# ============================================================================

if st.session_state.game_state == "SETUP":
    run_setup()

elif st.session_state.game_state == "FIRED":
    show_fired()

elif st.session_state.game_state == "DASHBOARD":
    show_dashboard()

elif st.session_state.game_state == "SEASON_END":
    # Team identity recovery (crash protection)
    if st.session_state.team_name == "Unknown U":
        st.warning("⚠️ Team Identity Lost! The previous crash may have reset your team name.")
        
        suggested = st.session_state.get("last_known_team_name")
        if suggested and suggested in ALL_TEAMS:
            st.info(f"Suggested restore: **{suggested}**")
            if st.button("Restore Suggested Team", type="primary"):
                st.session_state.team_name = suggested
                st.session_state.team_color = st.session_state.get("last_known_team_color") or TEAMS_DB.get(suggested, {}).get("color", "#333333")
                st.rerun()

        c_fix1, c_fix2 = st.columns([3, 1])
        new_name_fix = c_fix1.selectbox("Restore Your Team:", sorted(ALL_TEAMS))
        if c_fix2.button("Restore Name"):
            st.session_state.team_name = new_name_fix
            st.session_state.team_color = TEAMS_DB.get(new_name_fix, {}).get("color", "#333333")
            st.rerun()
    
    show_season_end()

elif st.session_state.game_state == "SELECTION_SUNDAY":
    show_selection_sunday()

elif st.session_state.game_state == "POSTSEASON":
    show_postseason()

elif st.session_state.game_state == "SEASON_RECAP":
    show_season_recap()

elif st.session_state.game_state == "OFFSEASON":
    show_offseason()

elif st.session_state.game_state == "RECRUITING_WRAP":
    show_recruiting_wrap()

elif st.session_state.game_state == "RETIREMENT":
    show_retirement()

else:
    # Fallback to dashboard
    st.session_state.game_state = "DASHBOARD"
    st.rerun()
