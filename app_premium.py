import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import re
from datetime import datetime

st.set_page_config(
    page_title="Netflix Analytics Pro",
    layout="wide",
    page_icon="🎬",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        background-color: #141414;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #2a2a2a;
        border-radius: 4px;
        color: #ffffff;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E50914;
    }
    div[data-testid="metric-container"] {
        background-color: #2a2a2a;
        border: 1px solid #404040;
        padding: 15px;
        border-radius: 8px;
        color: #ffffff;
    }
    div[data-testid="stMetricLabel"] {
        color: #b3b3b3;
        font-size: 14px;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff;
        font-size: 28px;
        font-weight: 700;
    }
    .stDataFrame {
        background-color: #2a2a2a;
    }
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Netflix Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    p, li {
        color: #e5e5e5;
    }
    .stMarkdown {
        color: #e5e5e5;
    }
    div.stButton > button {
        background-color: #E50914;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 4px;
        padding: 10px 24px;
    }
    div.stButton > button:hover {
        background-color: #b20710;
    }
    .stSelectbox, .stMultiSelect {
        color: #ffffff;
    }
    .success-box {
        background-color: #1e4620;
        border-left: 4px solid #46d369;
        padding: 16px;
        border-radius: 4px;
        color: #ffffff;
    }
    .warning-box {
        background-color: #4a3c1e;
        border-left: 4px solid #f5c518;
        padding: 16px;
        border-radius: 4px;
        color: #ffffff;
    }
    .info-box {
        background-color: #1e3a4a;
        border-left: 4px solid #4a9eff;
        padding: 16px;
        border-radius: 4px;
        color: #ffffff;
    }
    .error-box {
        background-color: #4a1e1e;
        border-left: 4px solid #e50914;
        padding: 16px;
        border-radius: 4px;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

np.random.seed(42)

@st.cache_data
def generate_data(n_rows=5000):
    genres = ['Sci-Fi', 'Documentary', 'Comedy', 'Horror', 'Drama']
    tiers = ['Basic', 'Standard', 'Premium']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
    
    originals = [
        'Netflix Original Stranger Things', 'Netflix Original The Crown',
        'Netflix Original Squid Game', 'Netflix Original Bridgerton',
        'Netflix Original Wednesday', 'Netflix Original Dark',
        'Netflix Original Ozark', 'Netflix Original The Witcher',
        'Netflix Original Money Heist', 'Netflix Original Black Mirror'
    ]
    
    licensed = [
        'Breaking Bad', 'Friends', 'The Office', 'Suits', 'Peaky Blinders',
        'Sherlock', 'The Walking Dead', 'Greys Anatomy', 'Supernatural', 'Criminal Minds'
    ]
    
    all_titles = originals + licensed
    
    data = {
        'Title_Name': np.random.choice(all_titles, n_rows),
        'Genre': np.random.choice(genres, n_rows, p=[0.25, 0.15, 0.30, 0.10, 0.20]),
        'User_Tier': np.random.choice(tiers, n_rows, p=[0.30, 0.45, 0.25]),
        'Region': np.random.choice(regions, n_rows, p=[0.30, 0.25, 0.20, 0.15, 0.10])
    }
    
    watch_times = []
    total_durations = []
    last_logins = []
    
    for i, tier in enumerate(data['User_Tier']):
        if tier == 'Premium':
            watch = np.random.gamma(3, 25)
            total = np.random.gamma(3, 35)
            login_bias = np.random.randint(0, 30)
        elif tier == 'Standard':
            watch = np.random.gamma(2.5, 20)
            total = np.random.gamma(2.5, 30)
            login_bias = np.random.randint(0, 45)
        else:
            watch = np.random.gamma(2, 15)
            total = np.random.gamma(2, 25)
            login_bias = np.random.randint(0, 60)
        
        watch_times.append(min(watch, total))
        total_durations.append(total)
        
        completion_estimate = min(watch, total) / total if total > 0 else 0
        login_days = int(login_bias * (1 - completion_estimate * 0.6) + np.random.normal(0, 5))
        last_logins.append(max(0, min(60, login_days)))
    
    data['Watch_Time_Mins'] = np.round(watch_times, 2)
    data['Total_Duration_Mins'] = np.round(total_durations, 2)
    data['Last_Login_Days_Ago'] = last_logins
    
    df = pd.DataFrame(data)
    
    pattern = r'^Netflix Original'
    df['Is_Original'] = df['Title_Name'].str.contains(pattern, case=False, regex=True)
    
    df['Completion_Percentage'] = np.minimum(
        np.round((df['Watch_Time_Mins'] / df['Total_Duration_Mins']) * 100, 2),
        100
    )
    df['Completion_Percentage'] = df['Completion_Percentage'].fillna(0)
    
    return df

if 'data' not in st.session_state:
    st.session_state.data = generate_data(5000)

df_full = st.session_state.data

st.markdown("<h1 style='text-align: center; color: #E50914; font-size: 48px;'>🎬 NETFLIX</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #ffffff; font-size: 28px;'>Content Performance & Viewer Retention Dashboard</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #b3b3b3;'>Analysis Date: {datetime.now().strftime('%B %d, %Y')}</p>", unsafe_allow_html=True)
st.markdown("---")

with st.sidebar:
    st.markdown("<h2 style='color: #E50914;'>⚙️ Dashboard Controls</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h3 style='color: #ffffff;'>📊 Data Management</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Regenerate", use_container_width=True):
            np.random.seed(np.random.randint(1, 10000))
            st.session_state.data = generate_data(5000)
            st.rerun()
    
    with col2:
        sample_size = st.selectbox("Size", [1000, 2500, 5000, 7500, 10000], index=2)
    
    if st.button("📏 Apply Size", use_container_width=True):
        st.session_state.data = generate_data(sample_size)
        st.rerun()
    
    st.markdown("---")
    st.markdown("<h3 style='color: #ffffff;'>🔍 Filters</h3>", unsafe_allow_html=True)
    
    selected_genres = st.multiselect(
        "Genres",
        options=df_full['Genre'].unique().tolist(),
        default=df_full['Genre'].unique().tolist()
    )
    
    selected_tiers = st.multiselect(
        "User Tiers",
        options=['Basic', 'Standard', 'Premium'],
        default=['Basic', 'Standard', 'Premium']
    )
    
    selected_regions = st.multiselect(
        "Regions",
        options=df_full['Region'].unique().tolist(),
        default=df_full['Region'].unique().tolist()
    )
    
    content_type = st.radio(
        "Content Type",
        options=["All", "Originals", "Licensed"]
    )
    
    completion_range = st.slider(
        "Completion Range (%)",
        0, 100, (0, 100)
    )
    
    st.markdown("---")
    st.metric("Filtered Records", f"{len(df_full):,}")

df_filtered = df_full[
    (df_full['Genre'].isin(selected_genres)) &
    (df_full['User_Tier'].isin(selected_tiers)) &
    (df_full['Region'].isin(selected_regions)) &
    (df_full['Completion_Percentage'] >= completion_range[0]) &
    (df_full['Completion_Percentage'] <= completion_range[1])
]

if content_type == "Originals":
    df_filtered = df_filtered[df_filtered['Is_Original'] == True]
elif content_type == "Licensed":
    df_filtered = df_filtered[df_filtered['Is_Original'] == False]

tab1, tab2, tab3, tab4 = st.tabs(["📊 OVERVIEW", "📈 ANALYTICS", "🎨 VISUALIZATIONS", "📋 DATA"])

with tab1:
    st.markdown("<h2 style='color: #ffffff;'>Key Performance Indicators</h2>", unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "TOTAL VIEWS",
            f"{len(df_filtered):,}",
            delta=f"{len(df_filtered) - len(df_full)}" if len(df_filtered) != len(df_full) else None
        )
    
    with col2:
        avg_completion = df_filtered['Completion_Percentage'].mean()
        st.metric(
            "AVG COMPLETION",
            f"{avg_completion:.1f}%",
            delta=f"{avg_completion - df_full['Completion_Percentage'].mean():.1f}%" if len(df_filtered) != len(df_full) else None
        )
    
    with col3:
        avg_watch = df_filtered['Watch_Time_Mins'].mean()
        st.metric(
            "AVG WATCH TIME",
            f"{avg_watch:.0f} min",
            delta=f"{avg_watch - df_full['Watch_Time_Mins'].mean():.0f}" if len(df_filtered) != len(df_full) else None
        )
    
    with col4:
        originals_pct = (df_filtered['Is_Original'].sum() / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            "ORIGINALS",
            f"{originals_pct:.1f}%"
        )
    
    with col5:
        avg_login = df_filtered['Last_Login_Days_Ago'].mean()
        st.metric(
            "DAYS SINCE LOGIN",
            f"{avg_login:.0f}",
            delta=f"{avg_login - df_full['Last_Login_Days_Ago'].mean():.0f}" if len(df_filtered) != len(df_full) else None,
            delta_color="inverse"
        )
    
    st.markdown("")
    st.markdown("---")
    
    st.markdown("<h2 style='color: #ffffff;'>Distribution Overview</h2>", unsafe_allow_html=True)
    st.markdown("")
    
    if len(df_filtered) > 0:
        netflix_red = '#E50914'
        netflix_dark = '#141414'
        netflix_gray = '#2a2a2a'
        
        fig = plt.figure(figsize=(18, 8))
        fig.patch.set_facecolor(netflix_dark)
        
        ax1 = plt.subplot(1, 3, 1)
        ax1.set_facecolor(netflix_dark)
        genre_counts = df_filtered['Genre'].value_counts()
        colors_genre = [netflix_red if i == 0 else '#b20710' if i == 1 else '#831010' if i == 2 else '#564d4d' if i == 3 else '#404040' 
                        for i in range(len(genre_counts))]
        bars = ax1.barh(genre_counts.index, genre_counts.values, color=colors_genre, edgecolor='white', linewidth=1.5)
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax1.text(width + 50, bar.get_y() + bar.get_height()/2.,
                     f'{int(width):,}', ha='left', va='center', fontsize=12, 
                     fontweight='bold', color='white')
        ax1.set_title('Volume by Genre', fontsize=18, fontweight='bold', color='white', pad=20)
        ax1.set_xlabel('Count', fontsize=13, fontweight='bold', color='white')
        ax1.tick_params(colors='white', labelsize=11)
        ax1.spines['bottom'].set_color('#404040')
        ax1.spines['left'].set_color('#404040')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='x', alpha=0.2, linestyle='--', linewidth=1, color='#404040')
        ax1.set_axisbelow(True)
        
        ax2 = plt.subplot(1, 3, 2)
        ax2.set_facecolor(netflix_dark)
        region_counts = df_filtered['Region'].value_counts()
        colors_region = ['#70b5f9', '#70b5f9', '#70b5f9', '#70b5f9', '#70b5f9'][:len(region_counts)]
        bars = ax2.bar(range(len(region_counts)), region_counts.values, color=colors_region, 
                       edgecolor='white', linewidth=1.5, width=0.7)
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 30,
                     f'{int(height):,}', ha='center', va='bottom', fontsize=11, 
                     fontweight='bold', color='white')
        ax2.set_xticks(range(len(region_counts)))
        ax2.set_xticklabels(region_counts.index, rotation=20, ha='right', fontsize=11)
        ax2.set_title('Volume by Region', fontsize=18, fontweight='bold', color='white', pad=20)
        ax2.set_ylabel('Count', fontsize=13, fontweight='bold', color='white')
        ax2.tick_params(colors='white', labelsize=11)
        ax2.spines['bottom'].set_color('#404040')
        ax2.spines['left'].set_color('#404040')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(axis='y', alpha=0.2, linestyle='--', linewidth=1, color='#404040')
        ax2.set_axisbelow(True)
        
        ax3 = plt.subplot(1, 3, 3)
        ax3.set_facecolor(netflix_dark)
        tier_counts = df_filtered['User_Tier'].value_counts().reindex(['Basic', 'Standard', 'Premium'])
        colors_tier = ['#564d4d', '#831010', netflix_red]
        bars = ax3.bar(tier_counts.index, tier_counts.values, color=colors_tier, 
                       edgecolor='white', linewidth=1.5, width=0.6)
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 30,
                     f'{int(height):,}', ha='center', va='bottom', fontsize=12, 
                     fontweight='bold', color='white')
        ax3.set_title('Volume by User Tier', fontsize=18, fontweight='bold', color='white', pad=20)
        ax3.set_ylabel('Count', fontsize=13, fontweight='bold', color='white')
        ax3.tick_params(colors='white', labelsize=11)
        ax3.spines['bottom'].set_color('#404040')
        ax3.spines['left'].set_color('#404040')
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.grid(axis='y', alpha=0.2, linestyle='--', linewidth=1, color='#404040')
        ax3.set_axisbelow(True)
        
        plt.tight_layout(pad=3.0)
        st.pyplot(fig)
        plt.close()

with tab2:
    st.markdown("<h2 style='color: #ffffff;'>Statistical Analysis & Business Insights</h2>", unsafe_allow_html=True)
    st.markdown("")
    
    if len(df_filtered) > 10:
        corr, pval = stats.pearsonr(df_filtered['Completion_Percentage'], df_filtered['Last_Login_Days_Ago'])
        
        st.markdown("<h3 style='color: #E50914;'>🔍 Retention Correlation Analysis</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("CORRELATION", f"{corr:.4f}")
        with col2:
            st.metric("P-VALUE", f"{pval:.6f}")
        with col3:
            sig = "✓ SIGNIFICANT" if pval < 0.05 else "✗ NOT SIGNIFICANT"
            st.metric("RESULT", sig)
        with col4:
            st.metric("SAMPLE SIZE", f"{len(df_filtered):,}")
        
        st.markdown("")
        
        if corr < 0:
            st.markdown("""
            <div class='success-box'>
                <strong>💡 NEGATIVE CORRELATION DETECTED</strong><br>
                Users with higher completion rates log in more frequently (lower days since last login).
                This indicates strong engagement correlation with content consumption.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='info-box'>
                <strong>💡 POSITIVE CORRELATION DETECTED</strong><br>
                Users with higher completion rates have logged in less recently.
                This suggests potential "binge-and-pause" viewing behavior.
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("---")
        st.markdown("")
        
        st.markdown("<h3 style='color: #E50914;'>📊 Does content completion significantly impact user retention?</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("<h4 style='color: #ffffff;'>Statistical Findings</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <p style='color: #e5e5e5; font-size: 16px;'>
            • <strong>Correlation Coefficient:</strong> {corr:.4f}<br>
            • <strong>P-value:</strong> {pval:.6f}<br>
            • <strong>Significance Level (α):</strong> 0.05<br>
            • <strong>Result:</strong> <span style='color: {"#46d369" if pval < 0.05 else "#e50914"}; font-weight: bold;'>
            {'STATISTICALLY SIGNIFICANT ✓' if pval < 0.05 else 'NOT STATISTICALLY SIGNIFICANT ✗'}</span>
            </p>
            """, unsafe_allow_html=True)
        
        with col2:
            if pval < 0.05:
                st.markdown("""
                <div style='background-color: #1e4620; padding: 30px; border-radius: 8px; text-align: center;'>
                    <h2 style='color: #46d369; margin: 0;'>✅ YES</h2>
                    <p style='color: #ffffff; margin: 10px 0 0 0;'>SIGNIFICANT<br>IMPACT</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background-color: #4a1e1e; padding: 30px; border-radius: 8px; text-align: center;'>
                    <h2 style='color: #e50914; margin: 0;'>❌ NO</h2>
                    <p style='color: #ffffff; margin: 10px 0 0 0;'>SIGNIFICANT<br>IMPACT</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("---")
        st.markdown("")
        
        st.markdown("<h4 style='color: #ffffff;'>Business Interpretation</h4>", unsafe_allow_html=True)
        st.markdown("")
        
        if pval < 0.05 and corr < 0:
            st.markdown("""
            <div class='success-box'>
                <strong style='font-size: 18px;'>✅ YES - Content completion SIGNIFICANTLY impacts user retention.</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            st.markdown("<h4 style='color: #E50914;'>🎯 Key Insights:</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <ul style='color: #e5e5e5; font-size: 15px; line-height: 1.8;'>
                <li>Strong negative correlation detected (r = {corr:.4f})</li>
                <li>Users who complete more content log in MORE frequently</li>
                <li>Higher completion rates → Lower churn risk</li>
                <li>This relationship is statistically significant (p < 0.05)</li>
            </ul>
            """, unsafe_allow_html=True)
            
            genre_perf = df_filtered.groupby('Genre')['Completion_Percentage'].mean().sort_values(ascending=False)
            top_genre = genre_perf.index[0]
            top_completion = genre_perf.iloc[0]
            
            tier_perf = df_filtered.groupby('User_Tier')['Watch_Time_Mins'].mean()
            premium_watch = tier_perf.get('Premium', 0)
            
            st.markdown("")
            st.markdown("<h4 style='color: #E50914;'>💼 Strategic Recommendations:</h4>", unsafe_allow_html=True)
            st.markdown(f"""
            <ol style='color: #e5e5e5; font-size: 15px; line-height: 1.9;'>
                <li><strong>🎯 CONTENT STRATEGY:</strong> Invest heavily in engaging content that drives completion,
                especially in <strong>{top_genre}</strong> ({top_completion:.1f}% avg completion)</li>
                <li><strong>📊 RETENTION METRICS:</strong> Implement completion % as leading indicator in churn prediction models</li>
                <li><strong>🔔 ENGAGEMENT CAMPAIGNS:</strong> Target users with &lt;50% completion for personalized re-engagement</li>
                <li><strong>💎 PREMIUM VALUE:</strong> Premium users watch {premium_watch:.1f} mins average - leverage in upsell messaging</li>
                <li><strong>🎬 ORIGINAL CONTENT:</strong> Netflix Originals drive {(df_filtered['Is_Original'].sum()/len(df_filtered)*100):.1f}% of viewing - 
                continue exclusive content investment</li>
            </ol>
            """, unsafe_allow_html=True)
            
        elif pval < 0.05:
            st.markdown("""
            <div class='warning-box'>
                <strong style='font-size: 18px;'>⚠️ UNEXPECTED FINDING - Positive correlation detected</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <p style='color: #e5e5e5; font-size: 15px;'>
            • Users with higher completion log in LESS frequently (r = {corr:.4f})<br>
            • Suggests "binge-and-pause" viewing behavior<br><br>
            <strong>💼 Recommendations:</strong><br>
            • Investigate weekly episode releases vs full-season drops<br>
            • Design engagement tactics for periods between content consumption<br>
            • Personalized notifications for new releases based on viewing history
            </p>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='error-box'>
                <strong style='font-size: 18px;'>❌ NO - Content completion does NOT significantly impact retention (current data)</strong>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <p style='color: #e5e5e5; font-size: 15px;'>
            <strong>📊 Implications:</strong><br>
            • Correlation not statistically significant (p ≥ 0.05)<br>
            • Other factors may be stronger retention drivers<br>
            • Current filters may limit sample size<br><br>
            <strong>💼 Recommendations:</strong><br>
            • Expand filter criteria for more data points<br>
            • Investigate alternative drivers: content variety, tenure, device usage<br>
            • Conduct segmented cohort analysis
            </p>
            """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("---")
        st.markdown("")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h4 style='color: #ffffff;'>🎭 Top Performing Genres</h4>", unsafe_allow_html=True)
            genre_stats = df_filtered.groupby('Genre')['Completion_Percentage'].mean().sort_values(ascending=False).head(5)
            for idx, (genre, completion) in enumerate(genre_stats.items()):
                st.markdown(f"""
                <div style='background-color: #2a2a2a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid {"#E50914" if idx == 0 else "#831010" if idx == 1 else "#564d4d"};'>
                    <span style='color: #ffffff; font-size: 16px; font-weight: bold;'>{idx+1}. {genre}</span>
                    <span style='float: right; color: #46d369; font-size: 16px; font-weight: bold;'>{completion:.1f}%</span>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("<h4 style='color: #ffffff;'>💳 Tier Performance Comparison</h4>", unsafe_allow_html=True)
            tier_stats = df_filtered.groupby('User_Tier')['Watch_Time_Mins'].mean().reindex(['Premium', 'Standard', 'Basic'])
            for idx, (tier, mins) in enumerate(tier_stats.items()):
                st.markdown(f"""
                <div style='background-color: #2a2a2a; padding: 12px; margin: 8px 0; border-radius: 6px; border-left: 4px solid {"#E50914" if tier == "Premium" else "#831010" if tier == "Standard" else "#564d4d"};'>
                    <span style='color: #ffffff; font-size: 16px; font-weight: bold;'>{tier}</span>
                    <span style='float: right; color: #70b5f9; font-size: 16px; font-weight: bold;'>{mins:.0f} mins</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='warning-box'>
            <strong>⚠️ Insufficient data for statistical analysis.</strong><br>
            Please adjust filters to include more records (minimum 10 required).
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.markdown("<h2 style='color: #ffffff;'>Advanced Data Visualizations</h2>", unsafe_allow_html=True)
    st.markdown("")
    
    if len(df_filtered) > 10:
        netflix_red = '#E50914'
        netflix_dark = '#141414'
        
        fig = plt.figure(figsize=(20, 14))
        fig.patch.set_facecolor(netflix_dark)
        
        tier_stats = df_filtered.groupby('User_Tier')['Watch_Time_Mins'].mean().reindex(['Basic', 'Standard', 'Premium'])
        colors_tier = ['#564d4d', '#831010', netflix_red]
        
        ax1 = plt.subplot(3, 3, 1)
        ax1.set_facecolor(netflix_dark)
        bars = ax1.bar(tier_stats.index, tier_stats.values, color=colors_tier, 
                       edgecolor='white', linewidth=2, alpha=0.9, width=0.6)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.0f}', ha='center', va='bottom', fontsize=13, fontweight='bold', color='white')
        ax1.set_title('Avg Watch Time by Tier', fontsize=16, fontweight='bold', color='white', pad=15)
        ax1.set_ylabel('Minutes', fontsize=12, fontweight='bold', color='white')
        ax1.tick_params(colors='white', labelsize=11)
        ax1.spines['bottom'].set_color('#404040')
        ax1.spines['left'].set_color('#404040')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.grid(axis='y', alpha=0.2, linestyle='--', color='#404040')
        ax1.set_axisbelow(True)
        
        ax2 = plt.subplot(3, 3, 2)
        ax2.set_facecolor(netflix_dark)
        if len(df_filtered) > 500:
            sample = df_filtered.sample(500)
        else:
            sample = df_filtered
        scatter = ax2.scatter(sample['Completion_Percentage'], sample['Last_Login_Days_Ago'],
                             c=sample['Last_Login_Days_Ago'], cmap='RdYlGn_r',
                             alpha=0.7, s=60, edgecolors='white', linewidth=0.5)
        z = np.polyfit(df_filtered['Completion_Percentage'], df_filtered['Last_Login_Days_Ago'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(0, 100, 100)
        ax2.plot(x_line, p(x_line), color=netflix_red, linewidth=3.5, 
                 linestyle='--', label=f'Trend: y={z[0]:.3f}x+{z[1]:.1f}')
        ax2.set_title('Completion vs Retention', fontsize=16, fontweight='bold', color='white', pad=15)
        ax2.set_xlabel('Completion %', fontsize=12, fontweight='bold', color='white')
        ax2.set_ylabel('Days Since Login', fontsize=12, fontweight='bold', color='white')
        ax2.tick_params(colors='white', labelsize=11)
        ax2.spines['bottom'].set_color('#404040')
        ax2.spines['left'].set_color('#404040')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(True, alpha=0.2, linestyle='--', color='#404040')
        ax2.legend(loc='best', fontsize=10, framealpha=0.3, facecolor=netflix_dark, edgecolor='white', labelcolor='white')
        
        ax3 = plt.subplot(3, 3, 3)
        ax3.set_facecolor(netflix_dark)
        content_counts = df_filtered['Is_Original'].value_counts()
        labels = ['Netflix\nOriginals', 'Licensed\nContent']
        sizes = [content_counts.get(True, 0), content_counts.get(False, 0)]
        colors = [netflix_red, '#564d4d']
        explode = (0.08, 0)
        wedges, texts, autotexts = ax3.pie(sizes, explode=explode, labels=labels,
                                             colors=colors, autopct='%1.1f%%',
                                             startangle=90, textprops={'fontsize': 13, 'color': 'white', 'fontweight': 'bold'})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(15)
        ax3.set_title('Content Mix Distribution', fontsize=16, fontweight='bold', color='white', pad=15)
        
        ax4 = plt.subplot(3, 3, 4)
        ax4.set_facecolor(netflix_dark)
        genre_stats = df_filtered.groupby('Genre')['Completion_Percentage'].mean().sort_values(ascending=False)
        colors_genre = [netflix_red if i == 0 else '#b20710' if i == 1 else '#831010' if i == 2 else '#564d4d' if i == 3 else '#404040' 
                        for i in range(len(genre_stats))]
        bars = ax4.barh(genre_stats.index, genre_stats.values, color=colors_genre, 
                        edgecolor='white', linewidth=1.5, alpha=0.9)
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax4.text(width + 1, bar.get_y() + bar.get_height()/2.,
                     f'{width:.1f}%', ha='left', va='center', fontsize=12, fontweight='bold', color='white')
        ax4.set_title('Completion % by Genre', fontsize=16, fontweight='bold', color='white', pad=15)
        ax4.set_xlabel('Completion %', fontsize=12, fontweight='bold', color='white')
        ax4.tick_params(colors='white', labelsize=11)
        ax4.spines['bottom'].set_color('#404040')
        ax4.spines['left'].set_color('#404040')
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.grid(axis='x', alpha=0.2, linestyle='--', color='#404040')
        ax4.set_axisbelow(True)
        
        ax5 = plt.subplot(3, 3, 5)
        ax5.set_facecolor(netflix_dark)
        region_watch = df_filtered.groupby('Region')['Watch_Time_Mins'].mean().sort_values(ascending=False)
        bars = ax5.bar(range(len(region_watch)), region_watch.values, color='#70b5f9', 
                       edgecolor='white', linewidth=1.5, alpha=0.9, width=0.7)
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold', color='white')
        ax5.set_xticks(range(len(region_watch)))
        ax5.set_xticklabels([r.replace(' ', '\n') for r in region_watch.index], fontsize=10)
        ax5.set_title('Avg Watch Time by Region', fontsize=16, fontweight='bold', color='white', pad=15)
        ax5.set_ylabel('Minutes', fontsize=12, fontweight='bold', color='white')
        ax5.tick_params(colors='white', labelsize=11)
        ax5.spines['bottom'].set_color('#404040')
        ax5.spines['left'].set_color('#404040')
        ax5.spines['top'].set_visible(False)
        ax5.spines['right'].set_visible(False)
        ax5.grid(axis='y', alpha=0.2, linestyle='--', color='#404040')
        ax5.set_axisbelow(True)
        
        ax6 = plt.subplot(3, 3, 6)
        ax6.set_facecolor(netflix_dark)
        tier_completion = df_filtered.groupby('User_Tier')['Completion_Percentage'].mean().reindex(['Basic', 'Standard', 'Premium'])
        bars = ax6.bar(tier_completion.index, tier_completion.values, color=colors_tier,
                       edgecolor='white', linewidth=2, alpha=0.9, width=0.6)
        for bar in bars:
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=13, fontweight='bold', color='white')
        ax6.set_title('Completion % by Tier', fontsize=16, fontweight='bold', color='white', pad=15)
        ax6.set_ylabel('Completion %', fontsize=12, fontweight='bold', color='white')
        ax6.tick_params(colors='white', labelsize=11)
        ax6.spines['bottom'].set_color('#404040')
        ax6.spines['left'].set_color('#404040')
        ax6.spines['top'].set_visible(False)
        ax6.spines['right'].set_visible(False)
        ax6.grid(axis='y', alpha=0.2, linestyle='--', color='#404040')
        ax6.set_axisbelow(True)
        
        ax7 = plt.subplot(3, 3, 7)
        ax7.set_facecolor(netflix_dark)
        genre_data = [df_filtered[df_filtered['Genre'] == g]['Completion_Percentage'].values 
                      for g in genre_stats.index]
        bp = ax7.boxplot(genre_data, labels=[g[:8] for g in genre_stats.index], patch_artist=True,
                         showmeans=True, notch=True,
                         meanprops=dict(marker='D', markerfacecolor=netflix_red, markersize=7),
                         medianprops=dict(color='white', linewidth=2.5),
                         whiskerprops=dict(color='white', linewidth=1.5),
                         capprops=dict(color='white', linewidth=1.5),
                         flierprops=dict(marker='o', markerfacecolor='white', markersize=4))
        colors_box = ['#70b5f9', '#5aa3e8', '#4a93d8', '#3a83c8', '#2a73b8'][:len(genre_stats)]
        for patch, color in zip(bp['boxes'], colors_box):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            patch.set_edgecolor('white')
            patch.set_linewidth(1.5)
        ax7.set_title('Completion Distribution', fontsize=16, fontweight='bold', color='white', pad=15)
        ax7.set_ylabel('Completion %', fontsize=12, fontweight='bold', color='white')
        ax7.tick_params(colors='white', labelsize=10)
        ax7.spines['bottom'].set_color('#404040')
        ax7.spines['left'].set_color('#404040')
        ax7.spines['top'].set_visible(False)
        ax7.spines['right'].set_visible(False)
        ax7.grid(axis='y', alpha=0.2, linestyle='--', color='#404040')
        ax7.set_axisbelow(True)
        
        ax8 = plt.subplot(3, 3, 8)
        ax8.set_facecolor(netflix_dark)
        original_completion = df_filtered.groupby('Is_Original')['Completion_Percentage'].mean()
        labels = ['Licensed', 'Originals']
        values = [original_completion.get(False, 0), original_completion.get(True, 0)]
        colors = ['#564d4d', netflix_red]
        bars = ax8.bar(labels, values, color=colors, edgecolor='white', linewidth=2, alpha=0.9, width=0.5)
        for bar in bars:
            height = bar.get_height()
            ax8.text(bar.get_x() + bar.get_width()/2., height + 1,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=14, fontweight='bold', color='white')
        ax8.set_title('Completion: Originals vs Licensed', fontsize=16, fontweight='bold', color='white', pad=15)
        ax8.set_ylabel('Completion %', fontsize=12, fontweight='bold', color='white')
        ax8.tick_params(colors='white', labelsize=12)
        ax8.spines['bottom'].set_color('#404040')
        ax8.spines['left'].set_color('#404040')
        ax8.spines['top'].set_visible(False)
        ax8.spines['right'].set_visible(False)
        ax8.grid(axis='y', alpha=0.2, linestyle='--', color='#404040')
        ax8.set_axisbelow(True)
        
        ax9 = plt.subplot(3, 3, 9)
        ax9.set_facecolor(netflix_dark)
        bins = [0, 25, 50, 75, 100]
        df_filtered['Completion_Bin'] = pd.cut(df_filtered['Completion_Percentage'], bins=bins, 
                                                labels=['0-25%', '25-50%', '50-75%', '75-100%'])
        bin_counts = df_filtered['Completion_Bin'].value_counts().sort_index()
        colors_hist = ['#e50914', '#b20710', '#831010', '#46d369']
        bars = ax9.bar(bin_counts.index, bin_counts.values, color=colors_hist, 
                       edgecolor='white', linewidth=1.5, alpha=0.9)
        for bar in bars:
            height = bar.get_height()
            ax9.text(bar.get_x() + bar.get_width()/2., height + 20,
                     f'{int(height):,}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='white')
        ax9.set_title('User Completion Distribution', fontsize=16, fontweight='bold', color='white', pad=15)
        ax9.set_ylabel('User Count', fontsize=12, fontweight='bold', color='white')
        ax9.set_xlabel('Completion Range', fontsize=12, fontweight='bold', color='white')
        ax9.tick_params(colors='white', labelsize=11)
        ax9.spines['bottom'].set_color('#404040')
        ax9.spines['left'].set_color('#404040')
        ax9.spines['top'].set_visible(False)
        ax9.spines['right'].set_visible(False)
        ax9.grid(axis='y', alpha=0.2, linestyle='--', color='#404040')
        ax9.set_axisbelow(True)
        plt.setp(ax9.xaxis.get_majorticklabels(), rotation=20, ha='right')
        
        plt.tight_layout(pad=3.5)
        st.pyplot(fig)
        plt.close()
    else:
        st.markdown("""
        <div class='warning-box'>
            <strong>⚠️ Insufficient data for visualizations.</strong><br>
            Please adjust filters to include more records.
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown("<h2 style='color: #ffffff;'>Data Explorer & Export</h2>", unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox("📊 Sort by", df_filtered.columns.tolist())
    with col2:
        sort_order = st.radio("⬆️ Order", ["Ascending", "Descending"], horizontal=True)
    with col3:
        show_rows = st.number_input("📏 Rows", 10, 1000, 100, 10)
    
    st.markdown("")
    
    df_display = df_filtered.sort_values(sort_by, ascending=(sort_order=="Ascending")).head(show_rows)
    st.dataframe(df_display, use_container_width=True, height=500)
    
    st.markdown("")
    st.markdown("---")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #ffffff;'>📊 Summary Statistics</h3>", unsafe_allow_html=True)
        st.dataframe(df_filtered.describe().round(2), use_container_width=True)
    
    with col2:
        st.markdown("<h3 style='color: #ffffff;'>📥 Export Options</h3>", unsafe_allow_html=True)
        st.markdown("")
        
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv,
            file_name=f'netflix_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
            use_container_width=True
        )
        
        st.markdown("")
        
        summary_csv = df_filtered.describe().to_csv().encode('utf-8')
        st.download_button(
            label="📊 Download Summary Stats (CSV)",
            data=summary_csv,
            file_name=f'netflix_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
            use_container_width=True
        )

st.markdown("")
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <p style='color: #666; font-size: 14px;'>
        🎬 <strong style='color: #E50914;'>NETFLIX</strong> Content Performance Dashboard<br>
        Built with Streamlit • Data Analytics Platform • © 2025
    </p>
</div>
""", unsafe_allow_html=True)
