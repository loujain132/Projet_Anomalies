
import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path
from datetime import datetime

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="NEXORA AI | Intelligence Platform",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "results" / "dossiers_avec_anomalies.csv"

# =====================================================
# CHARGEMENT DES DONNEES
# =====================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

try:
    df = load_data()
except Exception as e:
    st.error(f"Impossible de charger le dataset : {e}")
    st.info("Vérifie que le fichier existe dans results/")
    st.stop()

required_columns = [
    "id_dossier", "age_demandeur", "montant_demande",
    "revenu_mensuel", "nb_documents",
    "delai_traitement_jours", "nb_erreurs",
    "type_dossier", "region", "anomalie_reelle",
    "anomalie_IF", "anomalie_LOF"
]

missing = [c for c in required_columns if c not in df.columns]

if missing:
    st.error(f"Colonnes manquantes : {missing}")
    st.stop()

total = len(df)
real_anomalies = int(df["anomalie_reelle"].sum())
if_anomalies = int(df["anomalie_IF"].sum())
lof_anomalies = int(df["anomalie_LOF"].sum())
normal = total - real_anomalies

# =====================================================
# DESIGN CSS
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@500;600;700;800&display=swap');

:root {
    --purple: #a855f7;
    --pink: #ec4899;
    --violet: #7c3aed;
    --gold: #fbbf24;
    --background: #080610;
}

.stApp {
    background:
        radial-gradient(ellipse at 15% 10%, #35104d55, transparent 38%),
        radial-gradient(ellipse at 90% 20%, #65104435, transparent 35%),
        radial-gradient(ellipse at 50% 90%, #39105a25, transparent 40%),
        #080610;
    color: #f8f5ff;
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit branding */

#MainMenu, footer, header {
    visibility: hidden;
}

/* Main content */

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #10091d, #0a0712);
    border-right: 1px solid #a855f733;
}

section[data-testid="stSidebar"] * {
    color: #eee5ff;
}

section[data-testid="stSidebar"] .stRadio label {
    background: #ffffff08;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 5px;
    transition: 0.3s;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: #a855f733;
}

/* Headings */

h1, h2, h3 {
    font-family: 'Inter', sans-serif !important;
    color: #ffffff !important;
}

/* Hero */

.hero {
    position: relative;
    overflow: hidden;
    padding: 35px;
    border-radius: 25px;
    border: 1px solid #c084fc55;
    background:
        radial-gradient(circle at 80% 40%, #a855f733, transparent 35%),
        linear-gradient(120deg, #1a102b, #100b1b 60%, #24102d);
    box-shadow: 0 0 35px #a855f71c;
    margin-bottom: 28px;
}

.hero::after {
    content: "";
    position: absolute;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    right: -70px;
    top: -100px;
    background: #d946ef;
    filter: blur(100px);
    opacity: 0.25;
    animation: pulse 5s infinite alternate;
}

@keyframes pulse {
    from { transform: scale(0.8); opacity: 0.15; }
    to { transform: scale(1.4); opacity: 0.4; }
}

.hero-label {
    color: #e879f9;
    font-size: 12px;
    letter-spacing: 4px;
    font-weight: 800;
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(32px, 5vw, 56px);
    font-weight: 800;
    margin: 15px 0;
    background: linear-gradient(90deg, #fff, #d8b4fe, #f0abfc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-description {
    color: #c4b5d5;
    font-size: 15px;
    line-height: 1.8;
    max-width: 650px;
}

/* Logo */

.logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 25px;
    font-weight: 800;
    letter-spacing: 3px;
    background: linear-gradient(90deg, #c084fc, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.logo-sub {
    font-size: 10px;
    letter-spacing: 4px;
    color: #a78bba;
}

/* Cards */

.metric-card {
    background: linear-gradient(145deg, #21142fdd, #120d1ddd);
    border: 1px solid #c084fc35;
    border-radius: 19px;
    padding: 22px;
    min-height: 145px;
    transition: all .3s ease;
    box-shadow: 0 8px 25px #00000030;
    position: relative;
    overflow: hidden;
}

.metric-card:hover {
    transform: translateY(-7px);
    border-color: #d946ef;
    box-shadow: 0 10px 35px #a855f735;
}

.metric-label {
    color: #b9a9cc;
    font-size: 12px;
    letter-spacing: 1.5px;
    font-weight: 700;
}

.metric-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 34px;
    font-weight: 800;
    color: white;
    margin-top: 15px;
}

.metric-icon {
    font-size: 25px;
    float: right;
}

.metric-foot {
    color: #c084fc;
    font-size: 11px;
    margin-top: 7px;
}

/* Panels */

.panel {
    background: #160f21cc;
    border: 1px solid #a855f733;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 30px #00000025;
}

.panel-title {
    font-size: 16px;
    font-weight: 800;
    color: #f5eaff;
    margin-bottom: 15px;
}

.section-title {
    font-size: 21px;
    font-weight: 800;
    margin: 30px 0 18px;
}

/* AI orb */

.orb-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 18px;
}

.orb {
    width: 135px;
    height: 135px;
    border-radius: 50%;
    background:
        radial-gradient(circle at 35% 30%, #f5d0fe, #c026d3 25%, #6b21a8 55%, #170b29 78%);
    box-shadow:
        0 0 25px #c026d3,
        0 0 60px #9333ea,
        inset 0 0 25px #f0abfc;
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-12px) scale(1.04); }
}

/* Buttons */

.stButton button {
    background: linear-gradient(100deg, #7c3aed, #c026d3, #ec4899);
    color: white !important;
    border: none;
    border-radius: 12px;
    font-weight: 700;
    transition: .3s;
}

.stButton button:hover {
    box-shadow: 0 0 25px #c026d388;
    transform: translateY(-2px);
}

/* Inputs */

.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background: #1b1228;
    border-color: #a855f755;
    color: white;
    border-radius: 10px;
}

/* Dataframe */

[data-testid="stDataFrame"] {
    border: 1px solid #a855f755;
    border-radius: 12px;
}

/* Status */

.status {
    display: inline-block;
    padding: 7px 13px;
    border-radius: 30px;
    color: #86efac;
    background: #14532d44;
    border: 1px solid #22c55e66;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

.small-text {
    color: #a99ab8;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("""
    <div style="text-align:center;padding:15px 0 25px;">
        <div class="logo">✦ NEXORA</div>
        <div class="logo-sub">ARTIFICIAL INTELLIGENCE</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="status">● SYSTEM ACTIVE</div>',
                unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### NAVIGATION")

    page = st.radio(
        "Navigation",
        [
            "⌂  Overview",
            "▤  Dossiers",
            "◈  Anomaly Analysis",
            "✧  AI Assistant",
            "⚙  About Project"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### PROJECT STATUS")
    st.markdown(
        f"<p class='small-text'>Dataset : {total} dossiers</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='small-text'>Models : Isolation Forest + LOF</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#887694;font-size:11px;'>"
        "NEXORA AI · VERSION 1.0<br>POWERED BY PYTHON"
        "</div>",
        unsafe_allow_html=True
    )

# =====================================================
# HERO
# =====================================================

def show_hero(title, subtitle):

    st.markdown(f"""
    <div class="hero">
        <div class="hero-label">✦ INTELLIGENCE PLATFORM</div>
        <div class="hero-title">{title}</div>
        <div class="hero-description">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# METRIC CARD
# =====================================================

def metric_card(icon, label, value, foot, color="#c084fc"):

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color};">{value}</div>
        <div class="metric-foot">{foot}</div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# PAGE 1 : OVERVIEW
# =====================================================

if page == "⌂  Overview":

    show_hero(
        "BEYOND DATA.",
        "Welcome to NEXORA AI — an intelligent platform dedicated "
        "to administrative anomaly detection and data exploration."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("▤", "TOTAL DOSSIERS", total,
                    "Dataset loaded", "#d8b4fe")

    with c2:
        metric_card("⚠", "REAL ANOMALIES", real_anomalies,
                    f"{real_anomalies / total * 100:.1f}% of dataset",
                    "#fb7185")

    with c3:
        metric_card("◈", "ISOLATION FOREST", if_anomalies,
                    "Predicted anomalies", "#c084fc")

    with c4:
        metric_card("✧", "LOCAL OUTLIER FACTOR", lof_anomalies,
                    "Predicted anomalies", "#f0abfc")

    st.markdown('<div class="section-title">✦ INTELLIGENCE CENTER</div>',
                unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">ANOMALY DISTRIBUTION</div>',
                    unsafe_allow_html=True)

        chart_data = pd.DataFrame({
            "Category": ["Normal dossiers", "Real anomalies"],
            "Count": [normal, real_anomalies]
        })

        chart = alt.Chart(chart_data).mark_arc(
            innerRadius=85,
            outerRadius=130,
            cornerRadius=8
        ).encode(
            theta=alt.Theta("Count:Q"),
            color=alt.Color(
                "Category:N",
                scale=alt.Scale(
                    domain=["Normal dossiers", "Real anomalies"],
                    range=["#9333ea", "#ec4899"]
                ),
                legend=alt.Legend(labelColor="#eee5ff")
            ),
            tooltip=["Category", "Count"]
        ).properties(height=300).configure_view(
            strokeOpacity=0
        )

        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">AI CORE</div>',
                    unsafe_allow_html=True)

        st.markdown("""
        <div class="orb-container">
            <div class="orb"></div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:Orbitron;color:#e9d5ff;
                        font-size:20px;font-weight:800;">
                NEXORA CORE
            </div>
            <p class="small-text">
                Intelligence & anomaly monitoring
            </p>
            <span class="status">● DATASET CONNECTED</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">◈ MODEL COMPARISON</div>',
                unsafe_allow_html=True)

    comparison = pd.DataFrame({
        "Model": ["Isolation Forest", "LOF"],
        "Anomalies detected": [if_anomalies, lof_anomalies]
    })

    bar = alt.Chart(comparison).mark_bar(
        cornerRadiusEnd=8,
        color="#c084fc"
    ).encode(
        x=alt.X("Anomalies detected:Q", title="Number of anomalies"),
        y=alt.Y("Model:N", sort="-x", title=None),
        tooltip=["Model", "Anomalies detected"]
    ).properties(height=150).configure_view(strokeOpacity=0)

    st.altair_chart(bar, use_container_width=True)

    st.caption("NEXORA AI — Data shown from your project dataset.")


# =====================================================
# PAGE 2 : DOSSIERS
# =====================================================

elif page == "▤  Dossiers":

    show_hero(
        "DOSSIER EXPLORER",
        "Explore, search and filter administrative dossiers."
    )

    search = st.text_input("⌕ Search by dossier ID")

    col1, col2 = st.columns(2)

    with col1:
        regions = ["All"] + sorted(df["region"].dropna().astype(str).unique())
        selected_region = st.selectbox("Region", regions)

    with col2:
        types = ["All"] + sorted(
            df["type_dossier"].dropna().astype(str).unique()
        )
        selected_type = st.selectbox("Dossier type", types)

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["id_dossier"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    if selected_region != "All":
        filtered = filtered[filtered["region"] == selected_region]

    if selected_type != "All":
        filtered = filtered[filtered["type_dossier"] == selected_type]

    st.markdown(
        f"<div class='panel-title'>{len(filtered)} DOSSIERS FOUND</div>",
        unsafe_allow_html=True
    )

    st.dataframe(filtered, use_container_width=True, height=430)

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Export filtered dossiers",
        data=csv,
        file_name="nexora_dossiers.csv",
        mime="text/csv"
    )


# =====================================================
# PAGE 3 : ANOMALY ANALYSIS
# =====================================================

elif page == "◈  Anomaly Analysis":

    show_hero(
        "ANOMALY INTELLIGENCE",
        "Analyze the predictions produced by the machine learning models."
    )

    model = st.selectbox(
        "Choose detection model",
        ["Isolation Forest", "Local Outlier Factor"]
    )

    column = "anomalie_IF" if model == "Isolation Forest" else "anomalie_LOF"

    detected = int(df[column].sum())

    a, b = st.columns(2)

    with a:
        metric_card("⚠", "DETECTED ANOMALIES", detected,
                    model, "#fb7185")

    with b:
        metric_card("✓", "NORMAL PREDICTIONS", total - detected,
                    model, "#c084fc")

    anomaly_df = df[df[column] == 1]

    st.markdown('<div class="section-title">DETECTED DOSSIERS</div>',
                unsafe_allow_html=True)

    st.dataframe(anomaly_df, use_container_width=True, height=400)

    st.download_button(
        "⬇ Download anomalies",
        anomaly_df.to_csv(index=False).encode("utf-8"),
        file_name=f"anomalies_{column}.csv",
        mime="text/csv"
    )

    st.markdown('<div class="section-title">ANOMALIES BY REGION</div>',
                unsafe_allow_html=True)

    region_data = (
        anomaly_df.groupby("region")
        .size()
        .reset_index(name="Anomalies")
    )

    region_chart = alt.Chart(region_data).mark_bar(
        color="#d946ef",
        cornerRadiusEnd=6
    ).encode(
        x=alt.X("region:N", title="Region"),
        y=alt.Y("Anomalies:Q", title="Number of anomalies"),
        tooltip=["region", "Anomalies"]
    ).properties(height=300).configure_view(strokeOpacity=0)

    st.altair_chart(region_chart, use_container_width=True)


# =====================================================
# PAGE 4 : AI ASSISTANT
# =====================================================

elif page == "✧  AI Assistant":

    show_hero(
        "NEXORA AI ASSISTANT",
        "Your intelligent companion for understanding administrative anomaly detection."
    )

    st.markdown("""
    <div class="panel">
        <div class="orb-container">
            <div class="orb"></div>
        </div>
        <div style="text-align:center;">
            <div class="logo">NEXORA INTELLIGENCE</div>
            <p class="small-text">
                Ask questions about your dataset and detection models.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask NEXORA about your project...")

    if question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        # Assistant local : sans API, avec informations du dataset
        answer = (
            f"Voici quelques informations sur ton dataset :\n\n"
            f"- Nombre total de dossiers : {total}\n"
            f"- Anomalies réelles : {real_anomalies}\n"
            f"- Anomalies détectées par Isolation Forest : {if_anomalies}\n"
            f"- Anomalies détectées par LOF : {lof_anomalies}\n\n"
            "Je suis actuellement en mode démonstration locale. "
            "Pour obtenir des réponses générées par un modèle IA, "
            "il faudra configurer l'API avec l'aide d'un adulte."
        )

        with st.chat_message("assistant"):
            st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })


# =====================================================
# PAGE 5 : ABOUT
# =====================================================

elif page == "⚙  About Project":

    show_hero(
        "ABOUT NEXORA",
        "An intelligent project for detecting anomalies in administrative dossiers."
    )

    st.markdown("""
    <div class="panel">
        <div class="panel-title">PROJECT OVERVIEW</div>
        <p class="small-text">
            NEXORA AI is an anomaly detection platform based on
            machine learning techniques.
        </p>
        <br>
        <div class="panel-title">TECHNOLOGIES</div>
        <p>Python · Pandas · Scikit-learn · Streamlit · Altair</p>
        <br>
        <div class="panel-title">MACHINE LEARNING MODELS</div>
        <p>Isolation Forest</p>
        <p>Local Outlier Factor (LOF)</p>
        <br>
        <div class="panel-title">DATASET</div>
        <p class="small-text">
            Synthetic administrative dataset used for educational
            and demonstration purposes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("NEXORA AI © 2026 — Intelligent Data Exploration")
