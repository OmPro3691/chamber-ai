import streamlit as st
import google.generativeai as genai

# UI Optimization for Mobile Phone
st.set_page_config(page_title="Chamber AI Elite", layout="centered", initial_sidebar_state="collapsed")
st.title("🏛️ Parliament AI: Evolving Engine")

# 1. App Memory Initialization
if "used_arguments" not in st.session_state:
    st.session_state.used_arguments = []
if "last_processed_hash" not in st.session_state:
    st.session_state.last_processed_hash = ""
if "latest_rebuttal" not in st.session_state:
    st.session_state.latest_rebuttal = "System initialized. Waiting for input..."
if "bill_draft_text" not in st.session_state:
    st.session_state.bill_draft_text = ""
if "sudden_changes" not in st.session_state:
    st.session_state.sudden_changes = [] 

# 2. Sidebar - Settings Menu
with st.sidebar:
    st.header("⚙️ Core Controls")
    api_key = st.text_input("Gemini API Key:", type="password")
    role = st.radio("Identity Stance:", ("Kiren Rijiju (Cabinet Minister - Ruling)", "Normal Member of Parliament (Ruling Stance)"))
    language = st.selectbox("Language Framework:", ("English", "Parliamentary Hindi", "Hinglish"))
    aggressiveness = st.selectbox("Debate Attack Style:", ("Assertive & Firm", "Aggressive & Dominating", "Diplomatic & Calm"))
    
    st.markdown("---")
    st.header("🚨 Sudden Scenario Shifts")
    new_change = st.text_input("Add New Rule/Format Shift:", key="new_change_input")
    if st.button("➕ Add Shift"):
        if new_change:
            st.session_state.sudden_changes.append(new_change)
            st.success("Shift added!")
            
    if st.session_state.sudden_changes:
        st.markdown("**Active Rule Changes:**")
        for i, change in enumerate(st.session_state.sudden_changes):
            st.markdown(f"{i+1}. {change}")
    
    if st.button("🧹 Factory Reset (Wipe All)"):
        st.session_state.used_arguments = []
        st.session_state.last_processed_hash = ""
        st.session_state.sudden_changes = [] 
        st.success("Complete memory wipe successful!")

if not api_key:
    st.warning("👈 Slide open the sidebar menu (top left) and enter your Gemini API Key to unlock the engine.")
    st.stop()

genai.configure(api_key=api_key)

# 3. Master AI Instructions
master_system_instruction = f"""
You are the elite live speech strategist for {role} in a Youth Parliament debate regarding a CAA and NRC framework. 

YOUR COMMANDS:
1. ANTI-REPETITION PROTOCOL: Review both [IMPORTED LONG-TERM MEMORY] and [CURRENT SESSION MEMORY]. You are strictly FORBIDDEN from repeating any argument, constitutional article, or statistic found in these memory banks. 
2. ARGUMENT EVOLUTION: You must evolve the debate. Find fresh angles, deeper administrative logic, or unmentioned historical precedents.
3. GOOGLE SEARCH GROUNDING: Double-check every legal clause and statistic using Google Search.
4. PROOF REQUIREMENT: Append a '[VERIFIABLE SOURCE/PROOF]' tag citing the specific Act section or Supreme Court judgment.
5. LIVE ADAPTATION: Fully integrate [ACTIVE SCENARIO SHIFTS] and [OFFICIAL BILL/ORDINANCE DRAFT].

OUTPUT PROTOCOL (in {language}, {aggressiveness} tone):
- [SPEAKER & STANCE]: Who is talking & Core Point.
- [FACT-CHECK]: [ACCURATE / MISLEADING / FALSE] + Verifiable Source/Proof from Search.
- [EVOLVED COUNTER]: 2 bullet points of advanced defense.
- [READ OUT LOUD]: A 2-sentence script for the MP to speak.
"""

# 4. The 4-Tab Mobile Layout
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Dashboard", "📜 Draft Upload", "💾 Memory Vault", "🔍 Fact Engine"])

# --- TAB 2: Draft Upload ---
with tab2:
    st.header("📜 Live Draft Sync")
    st.session_state.bill_draft_text = st.text_area(
        "Paste custom Draft Bill clauses provided by the school here:", 
        height=300
    )

# --- TAB 3: Long-Term Memory Vault ---
with tab3:
    st.header("💾 The Memory Vault")
    st.markdown("Use this to prevent the AI from repeating demo session arguments during the final match.")
    
    imported_memory = st.text_area(
        "📥 Import Past Memory (Paste your demo session notes here):", 
        height=150,
        placeholder="Paste previous arguments here on the day of the final session..."
    )
    
    st.markdown("---")
    st.markdown("📤 **Export Current Session Memory:**")
    st.caption("At the end of the day, copy all text from this box and save it in your phone's Notes app.")
    
    current_session_text = "\n---\n".join(st.session_state.used_arguments) if st.session_state.used_arguments else "No arguments deployed yet."
    st.text_area("Copy this text:", value=current_session_text, height=150, disabled=True)

# --- TAB 1: Live Dashboard ---
with tab1:
    st.markdown("### 🔊 Step 1: Input Stream")
    ambient_feed = st.text_area("Room Feed (Live Audio):", height=80, key="ambient_input")
    whisper_feed = st.text_area("🤫 Your Whispers (Overrides Room Audio):", height=80, key="whisper_input")

    st.markdown("---")
    st.markdown("### ⚡ Step 2: Live Strategy")
    output_container = st.empty()

    @st.fragment(run_every=7)
    def run_analysis_engine():
        ambient = st.session_state.ambient_input
        whisper = st.session_state.whisper_input
        active_shifts_text = "\n- ".join(st.session_state.sudden_changes) if st.session_state.sudden_changes else "Standard parliamentary rules apply."
        
        current_hash = hash(ambient + whisper + active_shifts_text + st.session_state.bill_draft_text + imported_memory)
        
        if (ambient or whisper) and current_hash != st.session_state.last_processed_hash:
            try:
                # FIX APPLIED HERE: tools is now a list containing a dictionary
                model = genai.GenerativeModel(
                    'gemini-1.5-pro', 
                    system_instruction=master_system_instruction,
                    tools=[{"google_search": {}}]
                )
                
                recent_memory = st.session_state.used_arguments[-3:] if st.session_state.used_arguments else "None."
                
                payload = f"""
                [OFFICIAL DRAFT]: {st.session_state.bill_draft_text}
                [ACTIVE SCENARIO SHIFTS]: {active_shifts_text}
                
                [AMBIENT TRANSCRIPT]: {ambient}
                [USER WHISPERS]: {whisper}
                
                [IMPORTED LONG-TERM MEMORY (DO NOT REPEAT)]: 
                {imported_memory if imported_memory else "No past sessions imported."}
                
                [CURRENT SESSION MEMORY (DO NOT REPEAT)]: 
                {recent_memory}
                """
                
                with st.spinner("⚡ Fact-checking and escalating arguments..."):
                    response = model.generate_content(payload)
                    st.session_state.latest_rebuttal = response.text
                    st.session_state.used_arguments.append(response.text)
                    st.session_state.last_processed_hash = current_hash
            except Exception as e:
                st.error(f"Engine Exception: {e}")
                
        output_container.markdown(st.session_state.latest_rebuttal)

    run_analysis_engine()

# --- TAB 4: Fact Engine ---
with tab4:
    st.header("🔍 Manual Fact Engine")
    manual_query = st.text_input("Type specific question:")
    if manual_query:
        try:
            # FIX APPLIED HERE AS WELL
            flash_model = genai.GenerativeModel('gemini-1.5-flash', tools=[{"google_search": {}}])
            with st.spinner("Searching..."):
                res = flash_model.generate_content(f"Fact check: {manual_query}")
                st.info(res.text)
        except Exception as e:
            st.error(f"Search Error: {e}")
