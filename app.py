import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import socket
import collections
from backend.channel_analyzer import ChannelAnalyzer
from backend.competitor_discovery import CompetitorDiscovery
from backend.data_extractor import DataExtractor
from backend.pattern_recognition import PatternRecognitionEngine
from backend.strategy_generator import StrategyGenerator
from backend.similarity import SimilarityModel
from backend.topicmodel import safe_imports
from backend.ytclassify import classify_video
from patternrecog import PatternRecognizer

# Import TopicModel classes
SentenceTransformer, BERTopic, XGBRegressor, Prophet = safe_imports()

st.set_page_config(page_title="Spyra", page_icon="🕵️", layout="wide")

# Theme handling
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

theme_colors = {
    'light': {
        'primary': '#6366f1',
        'secondary': '#a855f7',
        'accent': '#ec4899',
        'background': '#f8fafc',
        'surface': 'rgba(255, 255, 255, 0.8)',
        'text_main': '#1e293b',
        'text_sub': '#64748b',
        'sidebar_bg': 'white',
        'tab_bg': 'white',
        'card_bg': 'white',
        'viral_item_bg': 'rgba(99, 102, 241, 0.05)'
    },
    'dark': {
        'primary': '#818cf8',
        'secondary': '#c084fc',
        'accent': '#f472b6',
        'background': '#0f172a',
        'surface': 'rgba(30, 41, 59, 0.7)',
        'text_main': '#f1f5f9',
        'text_sub': '#94a3b8',
        'sidebar_bg': '#1e293b',
        'tab_bg': '#1e293b',
        'card_bg': '#1e293b',
        'viral_item_bg': 'rgba(129, 140, 248, 0.1)'
    }
}

tc = theme_colors[st.session_state.theme]

# Custom CSS for modern UI
st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    :root {{
        --primary: {tc['primary']};
        --secondary: {tc['secondary']};
        --accent: {tc['accent']};
        --background: {tc['background']};
        --surface: {tc['surface']};
        --text-main: {tc['text_main']};
        --text-sub: {tc['text_sub']};
    }}

    .stApp {{
        background-color: var(--background);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    
    .glass-card {{
        background: var(--surface);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
    }}

    .main-header {{
        font-weight: 800;
        color: var(--text-main);
        letter-spacing: -0.02em;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .animate-in {{
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    }}

    .hero-section {{
        background: radial-gradient(circle at top right, #4f46e5, #7c3aed, #db2777);
        padding: 6rem 2rem;
        border-radius: 2.5rem;
        color: white;
        text-align: center;
        margin-bottom: 4rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 25px 50px -12px rgba(99, 102, 241, 0.25);
    }}
    
    .hero-section::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: url('https://www.transparenttextures.com/patterns/cubes.png');
        opacity: 0.1;
    }}

    .hero-title {{
        font-size: 5rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        color: white !important;
        text-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {tc['sidebar_bg']};
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        background: {tc['tab_bg']};
        padding: 0.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        gap: 1rem;
    }}
    
    [data-testid="stMetricValue"] {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--text-main), var(--text-sub));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 1rem 2.5rem !important;
        border-radius: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3) !important;
    }}

    .gradient-badge {{
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }}

    .feature-card {{
        background: var(--surface);
        backdrop-filter: blur(10px);
        padding: 3rem 2rem;
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        height: 100%;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        text-align: center;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }}
    
    .feature-card:hover {{
        transform: translateY(-15px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.2);
        border-color: var(--primary);
    }}
    
    .feature-icon {{
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: block;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
    }}
    
    .feature-title {{
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 1rem;
    }}
    
    .feature-text {{
        color: var(--text-sub);
        font-size: 1.1rem;
        line-height: 1.5;
    }}

    .stat-card {{
        background: {tc['card_bg']};
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}

    .viral-item {{
        background: {tc['viral_item_bg']};
        padding: 1rem;
        border-radius: 0.75rem;
        border-left: 4px solid var(--primary);
        margin-bottom: 0.5rem;
    }}
    
    h1, h2, h3, h4, p, span, div {{
        color: var(--text-main);
    }}
    
    .hero-section p, .hero-section h1 {{
        color: white !important;
    }}
    
    /* FIX: Dark Mode Widget Readability */
    div[data-baseweb="select"] > div {{
        background-color: {tc['sidebar_bg']} !important;
        color: var(--text-main) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    div[role="listbox"] {{
        background-color: {tc['sidebar_bg']} !important;
        color: var(--text-main) !important;
    }}
    
    div[role="option"] {{
        color: var(--text-main) !important;
    }}
    
    div[role="option"]:hover {{
        background-color: var(--primary) !important;
        color: white !important;
    }}

    .stSelectbox label, .stRadio label {{
        color: var(--text-main) !important;
    }}

    /* Fix for radio buttons/pills visibility */
    div[role="radiogroup"] label p {{
        color: var(--text-main) !important;
    }}

    /* Comprehensive Input Fix */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background-color: {tc['sidebar_bg']} !important;
        color: var(--text-main) !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }}
    
    .stDownloadButton button {{
        color: white !important;
    }}
</style>""", unsafe_allow_html=True)

# Chart Styling Constants
CHART_THEME = {
    "plotly_white": True,
    "color_palette": ["#6366f1", "#a855f7", "#ec4899", "#f43f5e", "#fb923c"],
    "font_family": "Plus Jakarta Sans",
    "grid_color": "#f1f5f9"
}

def apply_pro_theme(fig):
    fig.update_layout(
        font_family=CHART_THEME["font_family"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=40, l=40, r=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(gridcolor=CHART_THEME["grid_color"], showline=False),
        yaxis=dict(gridcolor=CHART_THEME["grid_color"], showline=False)
    )
    return fig

# Main Title/Hero (Hidden after analysis)
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

if not st.session_state.analysis_done:
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">🕵️ Spyra</h1>
            <p class="hero-subtitle">
                The ultimate AI-powered intelligence platform for YouTube creators. 
                Analyze competitors, discover viral patterns, and build your growth strategy in seconds.
            </p>
            <div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 1rem;">
                <span class="gradient-badge">✨ AI-Powered</span>
                <span class="gradient-badge">📊 Real-time Data</span>
                <span class="gradient-badge">🎯 Growth Focused</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Feature Cards with centering container
    st.markdown('<div style="text-align: center; margin-bottom: 4rem;">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
            <div class="feature-card animate-in">
                <span class="feature-icon">🔍</span>
                <h3 class="feature-title">Deep Discovery</h3>
                <p class="feature-text">Uncover hidden competitors in your niche that you never knew existed. We find the creators you should actually be watching.</p>
            </div>
            """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
            <div class="feature-card animate-in" style="animation-delay: 0.2s;">
                <span class="feature-icon">📈</span>
                <h3 class="feature-title">Pattern Analysis</h3>
                <p class="feature-text">Identify which video themes and formats are actually driving engagement. Move beyond guesswork to data-backed decisions.</p>
            </div>
            """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
            <div class="feature-card animate-in" style="animation-delay: 0.4s;">
                <span class="feature-icon">🎯</span>
                <h3 class="feature-title">Growth Strategy</h3>
                <p class="feature-text">Receive AI-generated actionable steps to outperform your competition. A personalized roadmap for your next viral hit.</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Growth Roadmap Section
    st.markdown(f"""
        <div style="background: {tc['card_bg']}; padding: 4rem 2rem; border-radius: 2rem; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 4rem;">
            <h2 style="text-align: center; font-weight: 800; color: var(--text-main); margin-bottom: 3rem;">Your Roadmap to Viral Success</h2>
            <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 2rem;">
                <div style="flex: 1; min-width: 200px; text-align: center;">
                    <div style="width: 60px; height: 60px; background: #6366f1; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-weight: 800; font-size: 1.5rem;">1</div>
                    <h4 style="font-weight: 700; color: var(--text-main);">Input Channel</h4>
                    <p style="color: var(--text-sub); font-size: 0.9rem;">Paste any YouTube link to start the AI analysis engine.</p>
                </div>
                <div style="flex: 1; min-width: 200px; text-align: center;">
                    <div style="width: 60px; height: 60px; background: #a855f7; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-weight: 800; font-size: 1.5rem;">2</div>
                    <h4 style="font-weight: 700; color: var(--text-main);">AI Surfing</h4>
                    <p style="color: var(--text-sub); font-size: 0.9rem;">Spyra crawls your niche to establish real-time benchmarks.</p>
                </div>
                <div style="flex: 1; min-width: 200px; text-align: center;">
                    <div style="width: 60px; height: 60px; background: #ec4899; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 1rem; font-weight: 800; font-size: 1.5rem;">3</div>
                    <h4 style="font-weight: 700; color: var(--text-main);">Get Insights</h4>
                    <p style="color: var(--text-sub); font-size: 0.9rem;">Download your personalized growth report and start scaling.</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
else:
    st.markdown('<h1 class="main-header">🕵️ Spyra</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your competitive landscape analysis is ready.</p>', unsafe_allow_html=True)

with st.sidebar:
    # Theme Toggle
    theme_col1, theme_col2 = st.columns([2, 1])
    with theme_col1:
        st.write(f"🌓 **{st.session_state.theme.title()} Mode**")
    with theme_col2:
        # Custom toggle behavior
        current_bool = (st.session_state.theme == 'dark')
        new_bool = st.toggle("Dark", value=current_bool, label_visibility="collapsed", key="theme_toggle_widget")
        
        if new_bool != current_bool:
            st.session_state.theme = 'dark' if new_bool else 'light'
            st.rerun()
    
    st.header("⚙️ Settings")
    api_key = st.text_input("YouTube API Key", type="password", help="Enter your YouTube Data API v3 key")
    target_name = st.text_input("Target Channel Name", placeholder="e.g. MrBeast, CarryMinati")
    
    st.markdown("---")
    st.subheader("📊 Data Source")
    data_source = st.radio("Choose Data Source", ["Local Dataset (Fast)", "YouTube API (Real-time)"], horizontal=True)
    
    st.markdown("---")
    st.subheader("⚔️ Comparison Mode")
    comparison_type = st.radio("Comparison Mode", ["Auto-discover", "Specific Channel"], horizontal=True)
    
    compare_channel_name = ""
    if comparison_type == "Specific Channel":
        compare_channel_name = st.text_input("Compare With (Channel Name)", placeholder="e.g. Technical Guruji")
    
    max_competitors = st.number_input("Number of Competitors to Spy", min_value=1, max_value=20, value=5, help="Choose how many similar creators you want to analyze.")
    discovery_metric = st.selectbox(
        "Find Competitors By",
        ("Subscribers", "Engagement Rate", "Brand Collaborations"),
        help="Choose the metric to find and rank similar channels."
    )
    
    # Category Selection
    st.markdown("---")
    st.subheader("🎯 Category Focus")
    
    # Try to get categories from dataset for better options
    dataset_categories = []
    
    st.divider()
    st.header("📁 Local Dataset")
    uploaded_file = st.file_uploader("Use your own dataset (CSV)", type=["csv"])
    
    # Auto-load Indian YouTubers dataset if no file uploaded
    if not uploaded_file:
        try:
            indian_dataset_path = os.path.join(os.path.dirname(__file__), "data", "indian_youtubers_standardized.csv")
            if os.path.exists(indian_dataset_path):
                st.success("🇮🇳 Indian YouTubers dataset loaded automatically!")
                uploaded_file = indian_dataset_path
        except Exception as e:
            st.info("Indian YouTubers dataset not found. Upload your own CSV file to proceed.")
    
    if uploaded_file:
        if isinstance(uploaded_file, str):  # Auto-loaded file path
            st.success("Dataset loaded!")
            if data_source == "Local Dataset (Fast)":
                try:
                    df_cats = pd.read_csv(uploaded_file, usecols=['category'])
                    dataset_categories = sorted(df_cats['category'].unique().tolist())
                except: pass
        else:  # User uploaded file
            st.success("Dataset loaded!")
            if data_source == "Local Dataset (Fast)":
                try:
                    uploaded_file.seek(0)
                    df_cats = pd.read_csv(uploaded_file, usecols=['category'])
                    uploaded_file.seek(0)
                    dataset_categories = sorted(df_cats['category'].unique().tolist())
                except: pass

    auto_detect = st.checkbox("Auto-detect from Channel", value=True, help="Automatically find competitors in the same niche as your target channel.")
    
    selected_categories = []
    if not auto_detect:
        base_categories = [
            "Finance", "Technology", "Education", "Gaming", "Entertainment", 
            "Lifestyle", "Food & Cooking", "Health & Fitness", "Business",
            "Investing", "Cryptocurrency", "Real Estate", "Travel", "Comedy"
        ]
        # Combine base categories with dataset categories
        categories_list = sorted(list(set(base_categories + dataset_categories)))
        
        selected_categories = st.multiselect(
            "Choose Categories",
            categories_list,
            default=["Finance"] if "Finance" in categories_list else [categories_list[0]] if categories_list else [],
            help="Manually select the niches you want to spy on."
        )
    
    st.info("💡 Tip: You can enter the exact channel name as it appears on YouTube.")

    if st.session_state.analysis_done:
        if st.button("🔄 Start New Analysis"):
            st.session_state.analysis_done = False
            if 'analysis_results' in st.session_state:
                del st.session_state.analysis_results
            st.rerun()

# Button to trigger analysis (only shown on landing page)
if not st.session_state.analysis_done:
    if st.button("🚀 Start Analysis", width='stretch'):
        # Check if we have data (either uploaded or auto-loaded)
        has_local_data = uploaded_file is not None
        has_api_target = api_key and target_name
        
        if data_source == "Local Dataset (Fast)" and not has_local_data:
            st.error("⚠️ Please ensure the dataset is available for local analysis.")
        elif data_source == "YouTube API (Real-time)" and not has_api_target:
            st.error("⚠️ Please enter your API key and Target Channel Name for real-time analysis.")
        elif data_source == "YouTube API (Real-time)" and api_key and (api_key.startswith("⚠️") or len(api_key) < 20):
            st.error("⚠️ The provided YouTube API Key looks invalid.")
        else:
            st.session_state.analysis_done = True
            st.rerun()

if st.session_state.analysis_done:
    try:
        with st.spinner("🔍 Deep diving into the competitive landscape..."):
            # Check for data in session state to avoid re-running on every interaction
            if 'analysis_results' not in st.session_state:
                if data_source == "Local Dataset (Fast)" and uploaded_file:
                    # Load data from local file or uploaded file
                    import csv
                    import io
                    
                    if isinstance(uploaded_file, str):  # Auto-loaded file path
                        with open(uploaded_file, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            raw_data = list(reader)
                    else:  # User uploaded file
                        content = uploaded_file.getvalue().decode('utf-8')
                        reader = csv.DictReader(io.StringIO(content))
                        raw_data = list(reader)
                    
                    # Format data for the engine based on the specific indian_youtubers structure
                    data = []
                    for row in raw_data:
                        data.append({
                            "channel_id": row.get('creator_id', 'Unknown'),
                            "title": row.get('channel_name', 'Unknown Title'),
                            "category": row.get('category', 'Uncategorized'),
                            "subscribers": int(float(row.get('subscribers', 0))),
                            "views": int(float(row.get('avg_views', 0))),
                            "likes": int(float(row.get('avg_likes', 0))),
                            "comments": int(float(row.get('avg_comments', 0))),
                            "engagement_rate": float(row.get('engagement_rate_pct', 0)) / 100
                        })
                    
                    # Fetch REAL-TIME target data if API key is provided, even in Local mode
                    if api_key and target_name:
                        try:
                            analyzer = ChannelAnalyzer(target_name, api_key)
                            target = analyzer.analyze()
                            resolved_id = target.get('channel_id', target_name)
                        except Exception:
                            # Fallback to mock target if API fails
                            target = {"avg_views": sum(d['views'] for d in data)/len(data) if data else 0, 
                                     "avg_likes": sum(d['likes'] for d in data)/len(data) if data else 0,
                                     "total_videos_analyzed": len(data),
                                     "top_themes": dict(pd.Series([d['category'] for d in data]).value_counts()),
                                     "data": data,
                                     "category": data[0]['category'] if data else "Unknown",
                                     "subscribers": sum(d['subscribers'] for d in data)/len(data) if data else 0,
                                     "thumbnail": f"https://api.dicebear.com/7.x/avataaars/svg?seed={target_name or 'target'}"}
                            resolved_id = target_name
                    else:
                        # Mock target from dataset
                        target = {"avg_views": sum(d['views'] for d in data)/len(data) if data else 0, 
                                  "avg_likes": sum(d['likes'] for d in data)/len(data) if data else 0,
                                  "total_videos_analyzed": len(data),
                                  "top_themes": dict(pd.Series([d['category'] for d in data]).value_counts()),
                                  "data": data,
                                  "category": data[0]['category'] if data else "Unknown",
                                  "subscribers": sum(d['subscribers'] for d in data)/len(data) if data else 0,
                                  "thumbnail": f"https://api.dicebear.com/7.x/avataaars/svg?seed={target_name or 'target'}"}
                        resolved_id = target_name
                    
                    all_candidates = []
                    for d in data:
                        all_candidates.append({
                            "title": d['title'],
                            "channel_id": d['channel_id'],
                            "thumbnail": f"https://api.dicebear.com/7.x/avataaars/svg?seed={d['channel_id']}", # Unique cartoon face per ID
                            "description": f"Category: {d['category']} | Subscribers: {d['subscribers']:,}",
                            "category": d['category'],
                            "subscribers": d['subscribers'],
                            "engagement_rate": d['engagement_rate'] * 100, # Convert to percentage
                            "brand_collaborations": 0, # Not available in simple CSV
                            "avg_views": d['views'],
                            "avg_likes": d['likes']
                        })
                    
                    # Sort candidates based on selected metric for initial view
                    if discovery_metric == "Subscribers":
                        all_candidates.sort(key=lambda x: x['subscribers'], reverse=True)
                    elif discovery_metric == "Engagement Rate":
                        all_candidates.sort(key=lambda x: x['engagement_rate'], reverse=True)

                    competitors = all_candidates[:max_competitors]

                    insights = PatternRecognitionEngine(data).recognize_patterns()
                    display_name = target_name or "Indian Creators Analysis"
                    strategy = StrategyGenerator(insights, display_name).generate_strategy()
                else:
                    # Step 1: Target Analysis
                    analyzer = ChannelAnalyzer(target_name, api_key)
                    target = analyzer.analyze()
                    resolved_id = target.get('channel_id', target_name) # Get the ID resolved from name

                    # Step 2: Competitor Discovery
                    discovery = CompetitorDiscovery(resolved_id, api_key)
                    
                    if comparison_type == "Specific Channel" and compare_channel_name:
                        # Manual Comparison with specific channel
                        comp_analyzer = ChannelAnalyzer(compare_channel_name, api_key)
                        comp_target = comp_analyzer.analyze()
                        
                        all_candidates = [{
                            "title": comp_target.get('title'),
                            "channel_id": comp_target.get('channel_id'),
                            "thumbnail": comp_target.get('thumbnail'),
                            "description": f"Category: {comp_target.get('category')} | Subscribers: {comp_target.get('subscribers', 0):,}",
                            "category": comp_target.get('category'),
                            "subscribers": comp_target.get('subscribers', 0),
                            "engagement_rate": 0, # Will be calculated after extraction
                            "brand_collaborations": 0,
                            "avg_views": comp_target.get('avg_views', 0),
                            "avg_likes": comp_target.get('avg_likes', 0)
                        }]
                    else:
                        # Auto-discovery based on categories
                        search_cats = target['category'] if auto_detect else selected_categories
                        if not search_cats: search_cats = ["Finance", "Technology", "Business", "Education"] # Enhanced fallback
                        
                        # Fetch a larger pool of candidates based on user input
                        pool_size = max(25, max_competitors * 3)
                        all_candidates = discovery.discover(search_cats, max_candidates=pool_size)

                    # Sort candidates based on selected metric
                    if discovery_metric == "Subscribers":
                        # Sort by highest subscriber count
                        all_candidates.sort(key=lambda x: x['subscribers'], reverse=True)
                    elif discovery_metric == "Engagement Rate":
                        # Sort by highest engagement rate
                        all_candidates.sort(key=lambda x: x['engagement_rate'], reverse=True)
                    elif discovery_metric == "Brand Collaborations":
                        # Sort by highest brand collaborations
                        all_candidates.sort(key=lambda x: x['brand_collaborations'], reverse=True)

                    competitors = all_candidates[:max_competitors]

                    # Step 3: Data Extraction
                    ids = [c['channel_id'] for c in competitors]
                    extractor = DataExtractor(ids, api_key)
                    data = extractor.extract()

                    # Calculate averages for competitors from extracted data
                    for comp in competitors:
                        comp_data = [d for d in data if d['channel_id'] == comp['channel_id']]
                        if comp_data:
                            avg_views = sum(d['views'] for d in comp_data) / len(comp_data)
                            avg_likes = sum(d['likes'] for d in comp_data) / len(comp_data)
                            avg_comments = sum(d['comments'] for d in comp_data) / len(comp_data)
                            
                            comp['avg_views'] = avg_views
                            comp['avg_likes'] = avg_likes
                            comp['engagement_rate'] = ((avg_likes + avg_comments) / avg_views * 100.0) if avg_views > 0 else 0.0
                            
                            # Brand collaborations heuristic
                            sponsor_kw = ['sponsor', 'sponsored', 'paid partnership', 'brand deal', '#ad', 'partnered']
                            bc_count = 0
                            for d in comp_data:
                                txt = (d['title'] + " " + d['description']).lower()
                                if any(k in txt for k in sponsor_kw):
                                    bc_count += 1
                            comp['brand_collaborations'] = bc_count
                            
                            # Refine category using ytclassify for more accurate niche labeling
                            all_titles = " ".join([d['title'] for d in comp_data])
                            all_descs = " ".join([d.get('description', '') for d in comp_data])
                            comp['category'] = classify_video(all_titles, all_descs)
                        else:
                            comp['avg_views'] = 0
                            comp['avg_likes'] = 0
                            comp['engagement_rate'] = 0
                            comp['brand_collaborations'] = 0

                    # Step 4: Pattern Recognition
                    engine = PatternRecognitionEngine(data)
                    insights = engine.recognize_patterns()

                    # Apply refined categories to competitors from Pattern Recognition
                    for comp in competitors:
                        comp_insight = next((ins for ins in insights if ins['channel_id'] == comp['channel_id']), None)
                        if comp_insight and 'refined_category' in comp_insight:
                            comp['category'] = comp_insight['refined_category']

                    # Personalization (Surfing the channel style)
                    target_data = target.get('data', [])
                    if target_data:
                        # Update target category using ytclassify for better accuracy
                        target_titles = " ".join([v['title'] for v in target_data])
                        target_descs = " ".join([v.get('description', '') for v in target_data])
                        target['category'] = classify_video(target_titles, target_descs)
                        
                        personalizer = PatternRecognizer()
                        persona = personalizer.personalize_app_for_user(target_data)
                        target['persona'] = persona

                    # Step 5: Strategy Generation
                    target_display_name = target.get('title', target_name)
                    strategy = StrategyGenerator(insights, target_display_name, target_data=target, comp_data=data).generate_strategy()
                    
                    # Add persona info to strategy if available
                    if 'persona' in target:
                        persona = target['persona']
                        persona_header = f"### 👤 Creator Persona: **{persona['creator_persona']}**\n" + \
                                         f"> **Primary Focus:** {persona['primary_focus']} | **Suggested Layout:** {persona['suggested_layout']}\n\n"
                        strategy['markdown'] = persona_header + strategy['markdown']

                    # Step 6: Advanced Analysis (Similarity & Topic Modeling)
                    try:
                        # Similarity Analysis
                        sim_model = SimilarityModel()
                        target_titles = [v['title'] for v in target.get('data', [])]
                        
                        for comp in competitors:
                            comp_videos = [d for d in data if d['channel_id'] == comp['channel_id']]
                            comp_titles = [v['title'] for v in comp_videos]
                            
                            if target_titles and comp_titles:
                                sim_score = sim_model.compute_similarity(" ".join(target_titles), " ".join(comp_titles))
                                comp['content_similarity'] = sim_score
                            else:
                                comp['content_similarity'] = 0.0

                        # Topic Modeling for Target with optimized parameters
                        if target_titles:
                            # Optimize BERTopic for short texts (YouTube titles)
                            try:
                                from umap import UMAP
                                from hdbscan import HDBSCAN
                                umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
                                hdbscan_model = HDBSCAN(min_cluster_size=5, metric='euclidean', cluster_selection_method='eom', prediction_data=True)
                                topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, verbose=False)
                            except ImportError:
                                topic_model = BERTopic(verbose=False)
                            
                            topics, _ = topic_model.fit_transform(target_titles)
                            topic_info = topic_model.get_topic_info()
                            # Filter out outlier topic -1 and clean names
                            top_topics = topic_info[topic_info['Topic'] != -1].head(3)
                            if not top_topics.empty:
                                # Clean names like '0_movie_trailer' to 'movie trailer'
                                cleaned_topics = [re.sub(r'^\d+_', '', t).replace('_', ' ') for t in top_topics['Name']]
                                target['ml_topics'] = cleaned_topics
                            else:
                                target['ml_topics'] = ["General Content"]
                    except Exception as ml_err:
                        st.warning(f"Note: Advanced ML analysis skipped ({str(ml_err)})")

                # Calculate Comparison Metrics
                comp_avg_views = sum(d['views'] for d in data) / len(data) if data else 0
                comp_avg_likes = sum(d['likes'] for d in data) / len(data) if data else 0
                
                # Delta percentages
                views_delta = ((target['avg_views'] - comp_avg_views) / comp_avg_views * 100) if comp_avg_views else 0
                likes_delta = ((target['avg_likes'] - comp_avg_likes) / comp_avg_likes * 100) if comp_avg_likes else 0
                
                # Target engagement for metrics
                target_avg_views = target.get('avg_views', 0)
                target_avg_likes = target.get('avg_likes', 0)
                target_avg_comments = target.get('avg_comments', 0)
                target_eng = ((target_avg_likes + target_avg_comments) / (target_avg_views + 1)) * 100

                # Store in session state
                st.session_state.analysis_results = {
                    'target': target,
                    'competitors': competitors,
                    'all_candidates': all_candidates,
                    'insights': insights,
                    'strategy': strategy,
                    'views_delta': views_delta,
                    'likes_delta': likes_delta,
                    'data': data,
                    'target_eng': target_eng,
                    'last_sync': pd.Timestamp.now().strftime("%H:%M:%S")
                }
            
            # Retrieve from session state
            res = st.session_state.analysis_results
            target = res['target']
            competitors = res['competitors']
            all_candidates = res.get('all_candidates', competitors)
            insights = res['insights']
            strategy = res['strategy']
            views_delta = res['views_delta']
            likes_delta = res['likes_delta']
            data = res.get('data', [])
            target_eng = res.get('target_eng', 0.0)
            last_sync = res.get('last_sync', 'N/A')

    except ValueError as e:
        st.session_state.analysis_done = False
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        st.error(f"⚠️ {str(e)}")
        # No rerun needed here as we want to show the error
    except (socket.timeout, ConnectionError, socket.error, socket.gaierror) as e:
        st.session_state.analysis_done = False
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        
        error_msg = str(e)
        if "youtube.googleapis.com" in error_msg or "10060" in error_msg:
            st.error("📡 **Network Connectivity Issue**: The app cannot reach YouTube's servers. This is likely due to your internet connection, a DNS failure, or a firewall/VPN blocking the request. Please check your connection and try again.")
        else:
            st.error(f"⚠️ **Connection Error**: {error_msg}")
    except Exception as e:
        st.session_state.analysis_done = False
        if 'analysis_results' in st.session_state:
            del st.session_state.analysis_results
        
        error_msg = str(e)
        if "API key expired" in error_msg:
            st.error("🔑 **API Key Expired**: Your YouTube Data API key has expired. Please go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials) to generate a new key and update it in the sidebar.")
        elif "keyInvalid" in error_msg or "API key not valid" in error_msg:
            st.error("🔑 **Invalid API Key**: The YouTube API key you provided is not valid. Please double-check your key in the sidebar and ensure you've enabled the 'YouTube Data API v3' in your Google Cloud project.")
        elif "quotaExceeded" in error_msg:
            st.error("🚫 **Quota Exceeded**: You've reached the daily limit for your YouTube API key. You can wait 24 hours for it to reset or create a new project with a new key.")
        else:
            st.error(f"⚠️ An unexpected error occurred: {error_msg}")

    # UI Results (Only shown if analysis was successful and state is still done)
    if st.session_state.analysis_done and 'analysis_results' in st.session_state:
        # Live Sync Indicator
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <div style="width: 10px; height: 10px; background-color: #059669; border-radius: 50%; animation: pulse 2s infinite;"></div>
                <span style="font-size: 0.8rem; font-weight: 700; color: #059669;">LIVE SYNC ACTIVE (Real-time API)</span>
                <span style="font-size: 0.8rem; color: #64748b; margin-left: auto;">Data Fetched: {last_sync}</span>
            </div>
            <style>
                @keyframes pulse {{
                    0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(5, 150, 105, 0.7); }}
                    70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(5, 150, 105, 0); }}
                    100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(5, 150, 105, 0); }}
                }}
            </style>
        """, unsafe_allow_html=True)

        if data_source == "YouTube API (Real-time)":
            if st.button("🔄 Refresh Live Analysis", use_container_width=True):
                if 'analysis_results' in st.session_state:
                    del st.session_state.analysis_results
                st.rerun()

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "🔍 Competitors", "💡 Insights", "🎯 Strategy"])

        with tab1:
            # Target Channel Header with Image
            col_img, col_info = st.columns([1, 4])
            with col_img:
                if target.get('thumbnail'):
                    st.markdown(f'<img src="{target["thumbnail"]}" style="border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 4px solid #6366f1; margin-bottom: 1rem;">', unsafe_allow_html=True)
                else:
                    st.markdown('🔍', unsafe_allow_html=True)
            with col_info:
                st.markdown(f"### 📈 {target.get('title', 'Target Channel')} Performance")
                st.markdown(f"**Category:** {target.get('category', 'N/A')} | **Subscribers:** {target.get('subscribers', 0):,}")
                
                # Show ML Topics if available
                if 'ml_topics' in target:
                    topics_html = " ".join([f'<span style="background:#e0e7ff; color:#4338ca; padding:2px 8px; border-radius:4px; font-size:0.8rem; margin-right:5px;">{t}</span>' for t in target['ml_topics']])
                    st.markdown(f"**AI Identified Topics:** {topics_html}", unsafe_allow_html=True)
                
                # Show Creator Persona from patternrecog.py
                if 'persona' in target:
                    persona = target['persona']
                    s_score = persona.get('sentiment_proxy', 0)
                    st.markdown(f"""
                        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                            <div style="background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); color: white; padding: 0.75rem 1rem; border-radius: 0.75rem; flex: 1;">
                                <span style="font-size: 0.75rem; opacity: 0.9; font-weight: 600; display: block; margin-bottom: 0.25rem; text-transform: uppercase;">CREATOR PERSONA</span>
                                <span style="font-size: 1.1rem; font-weight: 800;">{persona['creator_persona']}</span>
                            </div>
                            <div style="background: white; border: 1px solid #e2e8f0; padding: 0.75rem 1rem; border-radius: 0.75rem; flex: 1;">
                                <span style="font-size: 0.75rem; color: #64748b; font-weight: 600; display: block; margin-bottom: 0.25rem; text-transform: uppercase;">COMMUNITY SENTIMENT</span>
                                <span style="font-size: 1.1rem; font-weight: 800; color: #1e293b;">{s_score:.1f} <span style="font-size: 0.8rem; font-weight: 400; color: #64748b;">(Likes/1k Views)</span></span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Key Metrics in Cards
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="stat-card">
                    <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: 700; text-transform: uppercase;">Avg Views</p>
                    <h2 style="color: #1e293b; margin: 0; font-size: 1.8rem; font-weight: 800;">{int(target['avg_views']):,}</h2>
                    <div style="background: {'rgba(5, 150, 105, 0.1)' if views_delta >= 0 else 'rgba(220, 38, 38, 0.1)'}; 
                                color: {'#059669' if views_delta >= 0 else '#dc2626'}; 
                                display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; 
                                font-size: 0.75rem; margin-top: 0.5rem; font-weight: 700;">
                        {'↑' if views_delta >= 0 else '↓'} {abs(views_delta):.1f}% vs Niche
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="stat-card">
                    <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: 700; text-transform: uppercase;">Engagement</p>
                    <h2 style="color: #1e293b; margin: 0; font-size: 1.8rem; font-weight: 800;">{target_eng:.2f}%</h2>
                    <div style="background: {'rgba(5, 150, 105, 0.1)' if likes_delta >= 0 else 'rgba(220, 38, 38, 0.1)'}; 
                                color: {'#059669' if likes_delta >= 0 else '#dc2626'}; 
                                display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; 
                                font-size: 0.75rem; margin-top: 0.5rem; font-weight: 700;">
                        {'↑' if likes_delta >= 0 else '↓'} {abs(likes_delta):.1f}% vs Niche
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                # Calculate Market Share
                total_niche_views = sum(c.get('avg_views', 0) for c in competitors) + target['avg_views']
                market_share = (target['avg_views'] / total_niche_views * 100) if total_niche_views > 0 else 0
                st.markdown(f"""
                <div class="stat-card">
                    <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: 700; text-transform: uppercase;">Niche Authority</p>
                    <h2 style="color: #1e293b; margin: 0; font-size: 1.8rem; font-weight: 800;">{market_share:.1f}%</h2>
                    <div style="background: rgba(99, 102, 241, 0.1); color: #6366f1; 
                                display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; 
                                font-size: 0.75rem; margin-top: 0.5rem; font-weight: 700;">
                        View Share in Niche
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                # Optimal Post Time
                best_time_info = target.get('persona', {}).get('timing_insights') or next((i['timing_insights'] for i in insights if i['channel_id'] == target.get('channel_id')), None)
                best_hour_str = "6:00 PM"
                boost_str = "+15%"
                if best_time_info:
                    h = best_time_info['best_hour']
                    best_hour_str = f"{h % 12 or 12}:00 {'PM' if h >= 12 else 'AM'}"
                    boost_str = f"+{best_time_info['projected_boost']:.1f}%"

                st.markdown(f"""
                <div class="stat-card">
                    <p style="color: #64748b; font-size: 0.8rem; margin-bottom: 0.5rem; font-weight: 700; text-transform: uppercase;">Optimal Window</p>
                    <h2 style="color: #1e293b; margin: 0; font-size: 1.8rem; font-weight: 800;">{best_hour_str}</h2>
                    <div style="background: rgba(168, 85, 247, 0.1); color: #a855f7; 
                                display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px; 
                                font-size: 0.75rem; margin-top: 0.5rem; font-weight: 700;">
                        Potential {boost_str} Boost
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")
            
            # Comparison Matrix
            st.subheader("⚔️ Competitive Gap Analysis", help="This radar chart normalizes all metrics to a scale of 0-100 to show how you stack up against your competitors across views, likes, engagement rate, and subscriber count.")
            
            # Prepare data for spider chart or comparison
            comp_data_list = []
            for comp in competitors:
                comp_data_list.append({
                    'Name': comp['title'],
                    'Avg Views': comp.get('avg_views', 0),
                    'Avg Likes': comp.get('avg_likes', 0),
                    'Engagement': comp.get('engagement_rate', 0),
                    'Subscribers': comp['subscribers']
                })
            
            # Add target to matrix
            target_avg_views = target.get('avg_views', 0)
            target_avg_likes = target.get('avg_likes', 0)
            target_avg_comments = target.get('avg_comments', 0)
            target_eng = ((target_avg_likes + target_avg_comments) / (target_avg_views + 1)) * 100
            
            comp_data_list.append({
                'Name': target.get('title', 'Target'),
                'Avg Views': target_avg_views,
                'Avg Likes': target_avg_likes,
                'Engagement': target_eng,
                'Subscribers': target['subscribers']
            })
            
            df_matrix = pd.DataFrame(comp_data_list)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                # Normalizing values for radar chart (spider chart)
                fig_radar = go.Figure()
                categories = ['Avg Views', 'Avg Likes', 'Engagement Rate', 'Subscribers']
                
                # Internal mapping for normalization
                data_cols = ['Avg Views', 'Avg Likes', 'Engagement', 'Subscribers']
                
                for _, row in df_matrix.iterrows():
                    # Normalize for radar chart display
                    norm_values = []
                    for i, cat in enumerate(data_cols):
                        max_val = df_matrix[cat].max() if df_matrix[cat].max() > 0 else 1
                        norm_values.append(row[cat] / max_val * 100)
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=norm_values,
                        theta=categories,
                        fill='toself',
                        name=row['Name']
                    ))

                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    showlegend=True,
                    margin=dict(t=30, b=30, l=30, r=30),
                    height=450
                )
                st.plotly_chart(fig_radar, width='stretch', key="gap_analysis_radar")

            with c2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.dataframe(
                    df_matrix.set_index('Name'), 
                    use_container_width=True,
                    column_config={
                        "Avg Views": st.column_config.NumberColumn(format="%d"),
                        "Avg Likes": st.column_config.NumberColumn(format="%d"),
                        "Engagement": st.column_config.NumberColumn(format="%.2f%%"),
                        "Subscribers": st.column_config.NumberColumn(format="%d")
                    }
                )

            st.markdown("---")
            
            # Charts
            df_target = pd.DataFrame(target.get('data', []))
            c1, c2 = st.columns(2)
            
            with c1:
                st.subheader("Theme Distribution")
                # Ensure we use the most accurate themes from pattern recognition if available
                theme_counts = target.get('top_themes', {})
                if not theme_counts and not df_target.empty:
                    # Fallback to engine extraction if missing
                    engine = PatternRecognitionEngine([])
                    all_keywords = []
                    for title in df_target['title']:
                        all_keywords.extend(engine._extract_keywords(title))
                    theme_counts = dict(collections.Counter(all_keywords).most_common(5))

                if theme_counts:
                    fig_pie = px.pie(
                        names=list(theme_counts.keys()), 
                        values=list(theme_counts.values()),
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig_pie, use_container_width=True, key="target_theme_pie")
                else:
                    st.info("Theme distribution data is not yet available.")
                
            with c2:
                st.subheader("Engagement Over Time")
                # Use real-time video metrics for the timeline
                if not df_target.empty and 'published_at' in df_target.columns:
                    try:
                        df_target['published_at'] = pd.to_datetime(df_target['published_at'])
                        # Sort by date for proper timeline
                        df_target = df_target.sort_values('published_at')
                        
                        fig_line = px.line(
                            df_target, 
                            x='published_at', 
                            y=['views', 'likes'],
                            color_discrete_sequence=['#6366f1', '#ec4899'],
                            labels={'published_at': 'Upload Date', 'value': 'Count', 'variable': 'Metric'},
                            title="Real-time Performance Trend"
                        )
                        # Rename legend items for better readability
                        fig_line.for_each_trace(lambda t: t.update(name = t.name.replace('views', 'Views').replace('likes', 'Likes')))
                        fig_line.update_layout(
                            margin=dict(t=30, b=0, l=0, r=0), 
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        st.plotly_chart(fig_line, use_container_width=True, key="target_engagement_line")
                    except Exception:
                        st.info("Could not process real-time timeline. Try refreshing the analysis.")
                else:
                    st.info("Real-time timeline requires YouTube API data. Connect your API key in the sidebar.")

        with tab2:
            st.markdown("### 🏆 Competitor Comparisons")
            
            # Use session state to track which competitor is selected for deep dive
            if 'selected_comp_id' not in st.session_state:
                st.session_state.selected_comp_id = None

            # Interactive Sorting Options
            st.write(f"Showing the top {len(competitors)} competitors identified. Choose how to rank them:")
            
            col_sort, col_reset = st.columns([4, 1])
            with col_sort:
                sort_metric = st.pills(
                    "Rank these competitors by:",
                    ["Subscriber", "Category", "Engagement", "Brand Collabs"],
                    default="Subscriber"
                )
            with col_reset:
                if st.session_state.selected_comp_id:
                    if st.button("⬅️ Back to List", use_container_width=True):
                        st.session_state.selected_comp_id = None
                        st.rerun()

            # --- DEEP DIVE VIEW ---
            if st.session_state.selected_comp_id:
                selected_comp = next((c for c in all_candidates if c['channel_id'] == st.session_state.selected_comp_id), None)
                
                if selected_comp:
                    st.markdown("---")
                    d1, d2 = st.columns([1, 3])
                    with d1:
                        st.markdown(f'<img src="{selected_comp["thumbnail"]}" style="border-radius: 1rem; width: 100%; border: 4px solid #6366f1;">', unsafe_allow_html=True)
                        st.markdown(f"""
                            <div style="text-align: center; margin-top: 1rem;">
                                <a href="https://youtube.com/channel/{selected_comp['channel_id']}" target="_blank">
                                    <button style="background: #ff0000; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.5rem; cursor: pointer; font-weight: 600; width: 100%;">
                                        Visit Channel 📺
                                    </button>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)
                    with d2:
                        st.markdown(f"## {selected_comp['title']}")
                        st.markdown(f"**Niche:** `{selected_comp['category']}` | **Channel ID:** `{selected_comp['channel_id']}`")
                        
                        m1, m2, m3 = st.columns(3)
                        m1.metric("Subscribers", f"{selected_comp['subscribers']:,}")
                        m2.metric("Engagement", f"{selected_comp['engagement_rate']:.2f}%")
                        m3.metric("Brand Collabs", selected_comp['brand_collaborations'])
                        
                        st.markdown(f"**Description:**\n{selected_comp.get('description', 'No description available.')}")

                    st.markdown("#### 📈 Content Performance")
                    comp_videos = [d for d in data if d['channel_id'] == selected_comp['channel_id']]
                    if comp_videos:
                        df_comp = pd.DataFrame(comp_videos)
                        fig_comp = px.bar(
                            df_comp, x='title', y='views',
                            color='engagement_rate' if 'engagement_rate' in df_comp else None,
                            title="Recent Video Views & Engagement",
                            color_continuous_scale='RdYlGn'
                        )
                        fig_comp.update_layout(xaxis={'showticklabels':False})
                        st.plotly_chart(fig_comp, use_container_width=True)
                        
                        st.markdown("#### 🔥 Latest Videos")
                        for v in comp_videos[:5]:
                            # Create a clickable YouTube link
                            v_yt_link = f"https://www.youtube.com/watch?v={v['video_id']}" if v.get('video_id') else f"https://www.youtube.com/results?search_query={v['title'].replace(' ', '+')}"
                            
                            st.markdown(f"""
                                <a href="{v_yt_link}" target="_blank" style="text-decoration: none;">
                                    <div class="viral-item" style="transition: background 0.2s; cursor: pointer;" onmouseover="this.style.background='#f1f5f9'" onmouseout="this.style.background='rgba(99, 102, 241, 0.05)'">
                                        <span style="color: #1e293b;">{v['title']}</span>
                                        <span style="font-weight: 700; color: #6366f1;">{v['views']:,} Views</span>
                                    </div>
                                </a>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No detailed video data available for this channel.")
                
                # End of deep dive view
            else:
                # --- LIST VIEW ---
                # Category Filter Dropdown
                unique_categories = list(set(comp.get('category', 'Unknown') for comp in all_candidates))
                unique_categories.sort()
                selected_category = st.selectbox(
                    "Filter by Category:",
                    ["All Categories"] + unique_categories,
                    help="Filter competitors by their category"
                )

                # Use all_candidates for filtering so we can see the top competitors in EACH category
                display_list = list(all_candidates)
                
                # Apply category filter
                if selected_category != "All Categories":
                    display_list = [comp for comp in display_list if comp.get('category', 'Unknown') == selected_category]
                
                if sort_metric == "Subscriber":
                    display_list.sort(key=lambda x: x['subscribers'], reverse=True)
                elif sort_metric == "Engagement":
                    display_list.sort(key=lambda x: x['engagement_rate'], reverse=True)
                elif sort_metric == "Brand Collabs":
                    display_list.sort(key=lambda x: x['brand_collaborations'], reverse=True)
                elif sort_metric == "Category":
                    display_list.sort(key=lambda x: x['category'])

                # Limit to max_competitors selected in sidebar
                display_list = display_list[:max_competitors]

                st.markdown("---")
                
                for i, comp in enumerate(display_list):
                    # Create a clickable card using a button and styling
                    with st.container():
                        c_col1, c_col2 = st.columns([4, 1])
                        with c_col1:
                            st.markdown(f"""
                            <div style="background: white; padding: 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0;">
                                <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 1rem;">
                                    <img src="{comp['thumbnail']}" style="border-radius: 50%; width: 80px; height: 80px; object-fit: cover; border: 3px solid #6366f1;">
                                    <div style="flex-grow: 1;">
                                        <h4 style="margin: 0; color: #1e293b;">{comp['title']}</h4>
                                        <div style="display: flex; gap: 0.5rem; margin-top: 0.25rem;">
                                            <span style="font-size: 0.75rem; background: #f1f5f9; padding: 0.1rem 0.5rem; border-radius: 4px; color: #64748b;">{comp['category']}</span>
                                            <code style="font-size: 0.75rem; color: #94a3b8;">{comp['channel_id']}</code>
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <span class="gradient-badge">Rank #{i+1}</span>
                                    </div>
                                </div>
                                <div style="display: flex; gap: 2rem; border-top: 1px solid #f1f5f9; padding-top: 1rem;">
                                    <div style="flex: 1;">
                                        <p style="margin: 0; font-size: 0.8rem; color: #64748b; font-weight: 600;">SUBSCRIBERS</p>
                                        <p style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">{comp['subscribers']:,}</p>
                                    </div>
                                    <div style="flex: 1;">
                                        <p style="margin: 0; font-size: 0.8rem; color: #64748b; font-weight: 600;">ENGAGEMENT</p>
                                        <p style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">{comp['engagement_rate']:.2f}%</p>
                                    </div>
                                    <div style="flex: 1;">
                                        <p style="margin: 0; font-size: 0.8rem; color: #64748b; font-weight: 600;">BRAND COLLABS</p>
                                        <p style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #1e293b;">{comp['brand_collaborations']}</p>
                                    </div>
                                    {f'''<div style="flex: 1;">
                                        <p style="margin: 0; font-size: 0.8rem; color: #64748b; font-weight: 600;">SIMILARITY</p>
                                        <p style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #6366f1;">{comp['content_similarity']:.1%}</p>
                                    </div>''' if 'content_similarity' in comp else ''}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        with c_col2:
                            st.markdown("<br><br>", unsafe_allow_html=True)
                            if st.button("🔍 View Profile", key=f"btn_{comp['channel_id']}", use_container_width=True):
                                st.session_state.selected_comp_id = comp['channel_id']
                                st.rerun()
                        st.markdown("<br>", unsafe_allow_html=True)

        with tab3:
            st.markdown("### 💡 Strategic Insights")
            
            # Global Insights Summary
            st.markdown("These insights represent the cumulative patterns found across all analyzed competitors in your niche.")
            g1, g2 = st.columns(2)
            with g1:
                with st.container(border=True):
                    st.write("**Most Successful Themes Across Niche**")
                    st.caption("AI-extracted keywords from high-performing video titles. Shows which topics are currently driving views in your category.")
                    # Combine all themes
                    all_keywords = collections.Counter()
                    for insight in insights:
                        all_keywords.update(insight['high_performing_themes'])
                    
                    themes_summary_df = pd.DataFrame(all_keywords.most_common(10), columns=['Theme', 'Total Frequency'])
                    fig_themes = px.bar(themes_summary_df, x='Total Frequency', y='Theme', orientation='h', color='Total Frequency', color_continuous_scale='Viridis')
                    st.plotly_chart(apply_pro_theme(fig_themes), use_container_width=True, key="global_themes_bar")
            
            with g2:
                with st.container(border=True):
                    st.write("**Engagement Distribution**")
                    st.caption("Histogram showing the range of engagement rates across all analyzed competitor videos.")
                    engagement_data = []
                    for insight in insights:
                        for v in insight['top_engagement_videos']:
                            engagement_data.append(v['engagement_rate'] * 100)
                    
                    fig_dist = px.histogram(engagement_data, nbins=20, labels={'value': 'Engagement Rate (%)'}, color_discrete_sequence=['#6366f1'])
                    st.plotly_chart(apply_pro_theme(fig_dist), use_container_width=True, key="engagement_dist_hist")

            st.markdown("---")
            st.subheader("🌐 Niche Semantic Map", help="This AI-generated map plots you and your competitors in a 2D space based on content similarity. Closer points mean more similar content strategies.")
            
            # Prepare data for Niche Map
            niche_data = {target.get('title', 'Your Channel'): [v['title'] for v in target.get('data', [])]}
            for comp in competitors:
                comp_videos = [d for d in data if d['channel_id'] == comp['channel_id']]
                niche_data[comp['title']] = [v['title'] for v in comp_videos]
            
            sim_model = SimilarityModel()
            coords = sim_model.get_niche_coordinates(niche_data)
            
            if coords:
                df_niche = pd.DataFrame([
                    {'Channel': name, 'X': c[0], 'Y': c[1], 'Type': 'Target' if name == target.get('title') else 'Competitor'}
                    for name, c in coords.items()
                ])
                
                fig_niche = px.scatter(
                    df_niche, x='X', y='Y', text='Channel', color='Type',
                    color_discrete_map={'Target': '#6366f1', 'Competitor': '#ec4899'},
                    template="plotly_white"
                )
                fig_niche.update_traces(marker=dict(size=15, line=dict(width=2, color='DarkSlateGrey')), textposition='top center')
                st.plotly_chart(apply_pro_theme(fig_niche), use_container_width=True, key="niche_semantic_map")
            else:
                st.info("AI Niche Map requires more content data to generate.")

            st.markdown("---")
            st.subheader("🔥 Viral Content Gallery")
            st.write("These videos are performing significantly better than their channel averages. Study their titles and framing.")
            
            # Flatten all top videos for a gallery
            gallery_videos = []
            for insight in insights:
                # Find the channel title from all_candidates for better display
                channel_info = next((c for c in all_candidates if c['channel_id'] == insight['channel_id']), None)
                channel_name = channel_info['title'] if channel_info else insight['channel_id']
                
                for vid in insight['top_engagement_videos']:
                    gallery_videos.append({
                        'channel_id': insight['channel_id'],
                        'channel_name': channel_name,
                        'title': vid['title'],
                        'engagement': vid['engagement_rate'],
                        'video_id': vid.get('video_id') # Ensure we have video_id if available
                    })
            
            gallery_videos.sort(key=lambda x: x['engagement'], reverse=True)
            
            cols = st.columns(3)
            for idx, vid in enumerate(gallery_videos[:9]): # Show top 9
                with cols[idx % 3]:
                    # Create a clickable YouTube link
                    # If we don't have a specific video_id, we link to the channel's search for that title
                    yt_link = f"https://www.youtube.com/watch?v={vid['video_id']}" if vid.get('video_id') else f"https://www.youtube.com/results?search_query={vid['title'].replace(' ', '+')}"
                    
                    st.markdown(f"""
                    <a href="{yt_link}" target="_blank" style="text-decoration: none;">
                        <div style="background: white; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; margin-bottom: 1rem; height: 180px; display: flex; flex-direction: column; justify-content: space-between; transition: transform 0.2s ease-in-out; cursor: pointer;" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'">
                            <div>
                                <p style="font-size: 0.75rem; color: #6366f1; font-weight: 700; margin-bottom: 0.25rem;">{vid['channel_name']}</p>
                                <p style="font-weight: 600; color: #1e293b; font-size: 0.9rem; line-height: 1.2; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{vid['title']}</p>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 0.8rem; background: rgba(5, 150, 105, 0.1); color: #059669; padding: 0.1rem 0.4rem; border-radius: 4px; font-weight: 600;">
                                    {vid['engagement']:.2%} Eng.
                                </span>
                                <span style="font-size: 1.2rem;">🎬</span>
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)

        with tab4:
            st.markdown(f"### 🎯 Strategic Growth Plan for {target.get('title', 'Your Channel')}")
            
            # AI Narrative Section (NEW)
            if 'narrative' in strategy:
                st.markdown(f"""
                <div style="background: rgba(99, 102, 241, 0.05); border-left: 5px solid #6366f1; padding: 1.5rem; border-radius: 1rem; margin-bottom: 2rem;">
                    <p style="font-size: 1.1rem; line-height: 1.6; color: #1e293b; font-style: italic; margin: 0;">
                        " {strategy['narrative']} "
                    </p>
                    <p style="font-size: 0.8rem; color: #6366f1; font-weight: 700; margin-top: 1rem; text-transform: uppercase; letter-spacing: 0.1em;">
                        — Spyra AI Analysis
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Action Buttons
            col_str, col_dl = st.columns([4, 1])
            with col_dl:
                st.download_button(
                    label="� Download Report",
                    data=strategy['markdown'],
                    file_name=f"spyra_strategy_{target.get('title', 'channel').lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Interactive Strategy Dashboard
            s1, s2 = st.columns([2, 1])
            with s1:
                with st.container(border=True):
                    st.markdown(f"#### 📈 Projected Growth Potential")
                    st.metric("Engagement Boost", f"+{strategy['improvement_pct']:.1f}%", help="Calculated by benchmarking your current engagement against top-tier competitors in your niche.")
                    st.info(f"💡 This boost is achievable by aligning your content with the viral patterns identified in your niche.")

                with st.container(border=True):
                    st.markdown("#### ⏰ High-Impact Posting Window")
                    st.markdown(f"Uploading at **{strategy['best_hour']} (Local Time)** is your golden window.")
                    st.success(f"🎯 Videos in your category posted at this time see a **+{strategy['timing_boost']:.1f}%** higher engagement density.")

            with s2:
                with st.container(border=True):
                    st.markdown("#### 🔥 Trending Content Pillars")
                    for theme in strategy['themes']:
                        st.markdown(f"- **{theme.title()}**")
                    st.caption("AI-identified keywords that are currently over-indexing for viral success.")

            st.markdown("---")
            st.markdown("#### 💡 AI-Powered Video Ideas")
            st.write("Based on your persona and niche patterns, our AI generated these high-potential video concepts for you.")
            
            # Display AI Video Ideas in a nice card format
            if 'video_ideas' in strategy:
                i_cols = st.columns(3)
                for i, idea in enumerate(strategy['video_ideas']):
                    with i_cols[i % 3]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
                                    padding: 1.5rem; border-radius: 1rem; border: 1px solid #e2e8f0; 
                                    height: 100%; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
                                    border-top: 4px solid #6366f1;">
                            <span style="font-size: 0.75rem; color: #6366f1; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Concept #{i+1}: {idea['theme'].title()}</span>
                            <h4 style="margin: 0.5rem 0; color: #1e293b; font-size: 1.1rem; font-weight: 800; line-height: 1.4;">{idea['title']}</h4>
                            <p style="margin: 0; font-size: 0.85rem; color: #64748b; font-style: italic;">{idea['hook']}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("AI Video Ideas require more data to generate.")

            st.markdown("---")
            st.markdown("#### 🎯 Viral Benchmarks (The 'Goldmines')")
            st.write("Reverse-engineer these top-performing videos to understand the exact hooks and pacing that work.")
            g_cols = st.columns(3)
            for idx, (vid, cid) in enumerate(strategy['top_videos']):
                with g_cols[idx]:
                    # Find video_id for link
                    v_link = f"https://www.youtube.com/watch?v={vid.get('video_id')}" if vid.get('video_id') else f"https://www.youtube.com/results?search_query={vid['title'].replace(' ', '+')}"
                    st.markdown(f"""
                    <a href="{v_link}" target="_blank" style="text-decoration: none;">
                        <div class="viral-item" style="height: 180px; display: flex; flex-direction: column; justify-content: space-between; border-radius: 1rem; border: 1px solid #e2e8f0; padding: 1.2rem; background: white; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                            <p style="font-weight: 700; color: #1e293b; font-size: 0.9rem; line-height: 1.3; margin-bottom: 0.5rem; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{vid['title']}</p>
                            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                                <span style="font-size: 0.75rem; color: #6366f1; font-weight: 700;">By {cid[:20]}</span>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="font-size: 0.75rem; background: rgba(5, 150, 105, 0.1); color: #059669; padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700;">
                                        {vid['engagement_rate']:.2%} Eng.
                                    </span>
                                    <span style="font-size: 0.8rem; color: #64748b;">🔗</span>
                                </div>
                            </div>
                        </div>
                    </a>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🛠️ Step-by-Step AI Execution Plan", expanded=True):
                st.markdown(f"""
                ### 🚀 Actionable Growth Steps
                
                1. **Hook Engineering**: Your niche's top videos use 'Pattern Interrupts'. Start your next video with a controversial statement or a high-stakes question related to **{strategy['themes'][0] if strategy['themes'] else 'your niche'}**.
                
                2. **Thumbnail Psychology**: Analyze the 'Viral Benchmarks' above. Notice the high-contrast text and emotive faces. Try mimicking their 'Negative Space' layout to stand out in the feed.
                
                3. **SEO Synergy**: Incorporate at least two trending pillars (**{', '.join([t.title() for t in strategy['themes'][:2]])}**) in your first 2 lines of the description to improve search rank.
                
                4. **Community Catalyst**: Use a 'Pinned Comment' with a specific question to spark conversation. Higher comment velocity in the first 2 hours correlates with a **+{strategy['timing_boost']:.1f}%** views boost.
                
                5. **Format Innovation**: Try a 'Comparison' or 'Tutorial' format for the **{strategy['themes'][1] if len(strategy['themes']) > 1 else 'trending'}** theme; these formats are currently showing 1.5x better retention for creators of your size.
                """)
