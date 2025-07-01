import streamlit as st
landing_page = st.Page("landing_page.py", title="Landing Page", icon=":material/home:")
adjust_target_pace = st.Page("adjust_target_pace.py", title="Target Pace Adjustment", icon=":material/keyboard_double_arrow_right:")
adjust_performance_pace = st.Page("adjust_performance_pace.py", title="Performance Adjustment", icon=":material/keyboard_double_arrow_left:")


pg = st.navigation([landing_page, adjust_target_pace, adjust_performance_pace])
#st.set_page_config(page_title="Landing Page", page_icon=":material/home:")

pg.run()
