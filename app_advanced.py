import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import re
from datetime import datetime

st.set_page_config(page_title="Netflix Analytics Pro", layout="wide", page_icon="🎬")

np.random.seed(42)

st.title("🎬 Netflix Content Performance & Viewer Retention Dashboard")
st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

@st.cache_data
def generate_data(n_rows=5000):
    genres = ['Sci-Fi', 'Documentary', 'Comedy', 'Horror', 'Drama']
    tiers = ['Basic', 'Standard', 'Premium']
    
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
        'User_Tier': np.random.choice(tiers, n_rows, p=[0.30, 0.45, 0.25])
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

st.sidebar.header("🎛️ Dashboard Controls")
st.sidebar.markdown("---")

st.sidebar.subheader("📊 Data Settings")
if st.sidebar.button("🔄 Regenerate Data", use_container_width=True):
    np.random.seed(np.random.randint(1, 10000))
    st.session_state.data = generate_data(5000)
    st.rerun()

sample_size = st.sidebar.slider("Sample Size", 1000, 10000, 5000, 500)
if st.sidebar.button("📏 Resize Dataset", use_container_width=True):
    st.session_state.data = generate_data(sample_size)
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filters")

selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=df_full['Genre'].unique().tolist(),
    default=df_full['Genre'].unique().tolist()
)

selected_tiers = st.sidebar.multiselect(
    "Select User Tiers",
    options=['Basic', 'Standard', 'Premium'],
    default=['Basic', 'Standard', 'Premium']
)

content_type = st.sidebar.radio(
    "Content Type",
    options=["All", "Netflix Originals Only", "Licensed Only"]
)

completion_range = st.sidebar.slider(
    "Completion % Range",
    0, 100, (0, 100)
)

df_filtered = df_full[
    (df_full['Genre'].isin(selected_genres)) &
    (df_full['User_Tier'].isin(selected_tiers)) &
    (df_full['Completion_Percentage'] >= completion_range[0]) &
    (df_full['Completion_Percentage'] <= completion_range[1])
]

if content_type == "Netflix Originals Only":
    df_filtered = df_filtered[df_filtered['Is_Original'] == True]
elif content_type == "Licensed Only":
    df_filtered = df_filtered[df_filtered['Is_Original'] == False]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Records", f"{len(df_filtered):,}")
st.sidebar.metric("Total Records", f"{len(df_full):,}")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Analytics", "🎨 Visualizations", "📋 Data Explorer"])

with tab1:
    st.header("Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Views",
            f"{len(df_filtered):,}",
            delta=f"{len(df_filtered) - len(df_full)}" if len(df_filtered) != len(df_full) else None
        )
    
    with col2:
        avg_completion = df_filtered['Completion_Percentage'].mean()
        st.metric(
            "Avg Completion",
            f"{avg_completion:.1f}%",
            delta=f"{avg_completion - df_full['Completion_Percentage'].mean():.1f}%" if len(df_filtered) != len(df_full) else None
        )
    
    with col3:
        avg_watch = df_filtered['Watch_Time_Mins'].mean()
        st.metric(
            "Avg Watch Time",
            f"{avg_watch:.0f} min",
            delta=f"{avg_watch - df_full['Watch_Time_Mins'].mean():.0f}" if len(df_filtered) != len(df_full) else None
        )
    
    with col4:
        originals_pct = (df_filtered['Is_Original'].sum() / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            "Originals %",
            f"{originals_pct:.1f}%"
        )
    
    with col5:
        avg_login = df_filtered['Last_Login_Days_Ago'].mean()
        st.metric(
            "Avg Days Since Login",
            f"{avg_login:.0f}",
            delta=f"{avg_login - df_full['Last_Login_Days_Ago'].mean():.0f}" if len(df_filtered) != len(df_full) else None,
            delta_color="inverse"
        )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Content Mix")
        content_counts = df_filtered['Is_Original'].value_counts()
        mix_df = pd.DataFrame({
            'Type': ['Netflix Originals', 'Licensed Content'],
            'Count': [content_counts.get(True, 0), content_counts.get(False, 0)],
            'Percentage': [
                f"{(content_counts.get(True, 0) / len(df_filtered) * 100):.1f}%" if len(df_filtered) > 0 else "0%",
                f"{(content_counts.get(False, 0) / len(df_filtered) * 100):.1f}%" if len(df_filtered) > 0 else "0%"
            ]
        })
        st.dataframe(mix_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("💳 User Distribution")
        tier_counts = df_filtered['User_Tier'].value_counts()
        tier_df = pd.DataFrame({
            'Tier': ['Basic', 'Standard', 'Premium'],
            'Count': [
                tier_counts.get('Basic', 0),
                tier_counts.get('Standard', 0),
                tier_counts.get('Premium', 0)
            ],
            'Percentage': [
                f"{(tier_counts.get('Basic', 0) / len(df_filtered) * 100):.1f}%" if len(df_filtered) > 0 else "0%",
                f"{(tier_counts.get('Standard', 0) / len(df_filtered) * 100):.1f}%" if len(df_filtered) > 0 else "0%",
                f"{(tier_counts.get('Premium', 0) / len(df_filtered) * 100):.1f}%" if len(df_filtered) > 0 else "0%"
            ]
        })
        st.dataframe(tier_df, hide_index=True, use_container_width=True)

with tab2:
    st.header("📊 Statistical Analysis & Insights")
    
    if len(df_filtered) > 10:
        corr, pval = stats.pearsonr(df_filtered['Completion_Percentage'], df_filtered['Last_Login_Days_Ago'])
        
        st.subheader("🔍 Retention Correlation Analysis")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Correlation Coefficient", f"{corr:.4f}")
        with col2:
            st.metric("P-value", f"{pval:.6f}")
        with col3:
            sig = "✓ Significant" if pval < 0.05 else "✗ Not Significant"
            st.metric("Statistical Significance", sig)
        with col4:
            st.metric("Sample Size", f"{len(df_filtered):,}")
        
        if corr < 0:
            st.success("💡 **Negative Correlation Detected:** Users with higher completion rates log in more frequently (lower days since last login).")
        else:
            st.info("💡 **Positive Correlation Detected:** Users with higher completion rates have logged in less recently.")
        
        st.divider()
        
        st.subheader("Does content completion significantly impact user retention?")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Statistical Findings")
            st.write(f"• **Correlation Coefficient:** {corr:.4f}")
            st.write(f"• **P-value:** {pval:.6f}")
            st.write(f"• **Significance Level (α):** 0.05")
            st.write(f"• **Result:** **{'STATISTICALLY SIGNIFICANT ✓' if pval < 0.05 else 'NOT STATISTICALLY SIGNIFICANT ✗'}**")
        
        with col2:
            if pval < 0.05:
                st.success("### ✅ SIGNIFICANT IMPACT")
            else:
                st.error("### ❌ NO SIGNIFICANT IMPACT")
        
        st.divider()
        
        st.markdown("### Business Interpretation")
        
        if pval < 0.05 and corr < 0:
            st.success("✅ **YES** - Content completion **SIGNIFICANTLY** impacts user retention.")
            
            st.markdown("#### 🎯 Key Insights:")
            st.write(f"• Strong negative correlation detected (r = {corr:.4f})")
            st.write("• Users who complete more content log in MORE frequently")
            st.write("• Higher completion rates → Lower churn risk")
            st.write("• This relationship is statistically significant (p < 0.05)")
            
            genre_perf = df_filtered.groupby('Genre')['Completion_Percentage'].mean().sort_values(ascending=False)
            top_genre = genre_perf.index[0]
            top_completion = genre_perf.iloc[0]
            
            tier_perf = df_filtered.groupby('User_Tier')['Watch_Time_Mins'].mean()
            premium_watch = tier_perf.get('Premium', 0)
            
            st.markdown("#### 💼 Strategic Recommendations:")
            st.write(f"1. 🎯 **CONTENT STRATEGY:** Invest heavily in engaging content that drives completion rates, particularly in **{top_genre}** (Avg. {top_completion:.1f}% completion)")
            st.write("2. 📊 **RETENTION METRICS:** Implement completion percentage as a leading indicator in churn prediction models")
            st.write("3. 🔔 **ENGAGEMENT CAMPAIGNS:** Create targeted campaigns for users with <50% completion rates")
            st.write(f"4. 💎 **PREMIUM VALUE PROP:** Premium users watch {premium_watch:.1f} mins on average - use this in upsell messaging")
            st.write(f"5. 🎬 **ORIGINAL CONTENT:** Netflix Originals represent {(df_filtered['Is_Original'].sum()/len(df_filtered)*100):.1f}% of viewing - continue exclusive content investment")
            
        elif pval < 0.05:
            st.warning("⚠️ **UNEXPECTED FINDING** - Positive correlation detected (binge-and-pause behavior)")
            st.write(f"• Users with higher completion log in LESS frequently (r = {corr:.4f})")
            st.write("• This suggests users binge content then take breaks")
            st.markdown("#### 💼 Recommendations:")
            st.write("• Investigate optimal content release strategies (weekly episodes vs. full season drops)")
            st.write("• Design engagement tactics for the gap between content consumption periods")
            st.write("• Consider personalized notifications for new releases based on viewing history")
        else:
            st.error("❌ **NO** - Content completion does NOT significantly impact user retention (based on current filtered data)")
            st.markdown("#### 📊 Implications:")
            st.write("• The correlation is not statistically significant (p ≥ 0.05)")
            st.write("• Other factors may be stronger drivers of retention")
            st.write("• Current filter settings may be limiting the sample size")
            st.markdown("#### 💼 Recommendations:")
            st.write("• Expand filter criteria to include more data points")
            st.write("• Investigate alternative retention drivers: content variety, subscription tenure, device usage")
            st.write("• Conduct segmented analysis by user cohorts or demographics")
        
        st.divider()
        
        st.subheader("🎭 Genre Performance Analysis")
        
        genre_stats = df_filtered.groupby('Genre').agg({
            'Completion_Percentage': ['mean', 'median', 'std', 'count'],
            'Watch_Time_Mins': 'mean',
            'Last_Login_Days_Ago': 'mean'
        }).round(2)
        
        genre_stats.columns = ['Avg_Completion_%', 'Median_Completion_%', 'Std_Completion', 
                               'View_Count', 'Avg_Watch_Mins', 'Avg_Days_Since_Login']
        genre_stats = genre_stats.sort_values('Avg_Completion_%', ascending=False)
        
        if len(genre_stats) > 0:
            top_genre = genre_stats.index[0]
            top_completion = genre_stats.iloc[0]['Avg_Completion_%']
            st.success(f"🏆 **Most Engaging Genre:** **{top_genre}** with {top_completion:.1f}% average completion rate")
        
        st.dataframe(genre_stats, use_container_width=True)
        
        st.divider()
        
        st.subheader("💳 User Tier Performance")
        
        tier_stats = df_filtered.groupby('User_Tier').agg({
            'Watch_Time_Mins': ['mean', 'median', 'max'],
            'Completion_Percentage': ['mean', 'median'],
            'Last_Login_Days_Ago': ['mean', 'median']
        }).round(2)
        
        tier_stats.columns = ['Avg_Watch_Mins', 'Median_Watch_Mins', 'Max_Watch_Mins',
                              'Avg_Completion_%', 'Median_Completion_%',
                              'Avg_Days_Since_Login', 'Median_Days_Since_Login']
        
        tier_stats = tier_stats.reindex(['Basic', 'Standard', 'Premium'])
        
        st.dataframe(tier_stats, use_container_width=True)
        
    else:
        st.warning("⚠️ Insufficient data for statistical analysis. Please adjust filters to include more records.")

with tab3:
    st.header("📈 Data Visualizations")
    
    if len(df_filtered) > 10:
        netflix_red = '#E50914'
        colors_tier = ['#564d4d', '#831010', netflix_red]
        
        fig = plt.figure(figsize=(18, 12))
        fig.patch.set_facecolor('white')
        
        tier_stats = df_filtered.groupby('User_Tier')['Watch_Time_Mins'].mean().reindex(['Basic', 'Standard', 'Premium'])
        
        ax1 = plt.subplot(2, 3, 1)
        bars = ax1.bar(tier_stats.index, tier_stats.values, 
                       color=colors_tier, edgecolor='black', linewidth=2, alpha=0.85)
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
        ax1.set_title('Average Watch Time by User Tier', fontsize=15, fontweight='bold', pad=15)
        ax1.set_ylabel('Minutes', fontsize=12, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1.5)
        ax1.set_axisbelow(True)
        
        ax2 = plt.subplot(2, 3, 2)
        if len(df_filtered) > 500:
            sample_idx = np.random.choice(len(df_filtered), 500, replace=False)
            sample = df_filtered.iloc[sample_idx]
        else:
            sample = df_filtered
        scatter = ax2.scatter(sample['Completion_Percentage'], sample['Last_Login_Days_Ago'],
                             c=sample['Last_Login_Days_Ago'], cmap='RdYlGn_r',
                             alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        z = np.polyfit(df_filtered['Completion_Percentage'], df_filtered['Last_Login_Days_Ago'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(0, 100, 100)
        ax2.plot(x_line, p(x_line), color=netflix_red, linewidth=3, 
                 linestyle='--', label=f'Trend: y={z[0]:.3f}x+{z[1]:.1f}')
        ax2.set_title('Completion vs Retention', fontsize=15, fontweight='bold', pad=15)
        ax2.set_xlabel('Completion %', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Days Since Login', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--', linewidth=1.5)
        ax2.legend(loc='best', fontsize=10, framealpha=0.9)
        cbar = plt.colorbar(scatter, ax=ax2)
        cbar.set_label('Days', fontsize=10, fontweight='bold')
        
        ax3 = plt.subplot(2, 3, 3)
        content_counts = df_filtered['Is_Original'].value_counts()
        labels = ['Netflix Originals', 'Licensed']
        sizes = [content_counts.get(True, 0), content_counts.get(False, 0)]
        colors = [netflix_red, '#564d4d']
        explode = (0.05, 0)
        wedges, texts, autotexts = ax3.pie(sizes, explode=explode, labels=labels,
                                             colors=colors, autopct='%1.1f%%',
                                             startangle=90, textprops={'fontsize': 12})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(14)
        for text in texts:
            text.set_fontweight('bold')
            text.set_fontsize(12)
        ax3.set_title('Content Mix', fontsize=15, fontweight='bold', pad=15)
        
        ax4 = plt.subplot(2, 3, 4)
        genre_stats = df_filtered.groupby('Genre')['Completion_Percentage'].mean().sort_values(ascending=False)
        bars = ax4.barh(genre_stats.index, genre_stats.values, color=netflix_red, 
                        edgecolor='black', linewidth=1.5, alpha=0.85)
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax4.text(width, bar.get_y() + bar.get_height()/2.,
                     f'{width:.1f}%', ha='left', va='center', fontsize=11, fontweight='bold', 
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        ax4.set_title('Avg Completion % by Genre', fontsize=15, fontweight='bold', pad=15)
        ax4.set_xlabel('Completion %', fontsize=12, fontweight='bold')
        ax4.grid(axis='x', alpha=0.3, linestyle='--', linewidth=1.5)
        ax4.set_axisbelow(True)
        
        ax5 = plt.subplot(2, 3, 5)
        genre_data = [df_filtered[df_filtered['Genre'] == g]['Completion_Percentage'].values 
                      for g in genre_stats.index]
        bp = ax5.boxplot(genre_data, labels=genre_stats.index, patch_artist=True,
                         showmeans=True, notch=True,
                         meanprops=dict(marker='D', markerfacecolor='red', markersize=7),
                         medianprops=dict(color='darkred', linewidth=2))
        colors_box = plt.cm.RdYlGn(np.linspace(0.4, 0.9, len(genre_stats)))
        for patch, color in zip(bp['boxes'], colors_box):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
            patch.set_edgecolor('black')
            patch.set_linewidth(1.5)
        ax5.set_title('Completion Distribution by Genre', fontsize=15, fontweight='bold', pad=15)
        ax5.set_ylabel('Completion %', fontsize=12, fontweight='bold')
        ax5.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1.5)
        ax5.set_axisbelow(True)
        plt.setp(ax5.xaxis.get_majorticklabels(), rotation=20, ha='right')
        
        ax6 = plt.subplot(2, 3, 6)
        tier_completion = df_filtered.groupby('User_Tier')['Completion_Percentage'].mean().reindex(['Basic', 'Standard', 'Premium'])
        bars = ax6.bar(tier_completion.index, tier_completion.values,
                       color=colors_tier, edgecolor='black', linewidth=2, alpha=0.85)
        for bar in bars:
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
        ax6.set_title('Avg Completion % by Tier', fontsize=15, fontweight='bold', pad=15)
        ax6.set_ylabel('Completion %', fontsize=12, fontweight='bold')
        ax6.grid(axis='y', alpha=0.3, linestyle='--', linewidth=1.5)
        ax6.set_axisbelow(True)
        
        plt.tight_layout(pad=3.0)
        st.pyplot(fig)
        plt.close()
        
    else:
        st.warning("⚠️ Insufficient data for visualizations. Please adjust filters.")

with tab4:
    st.header("🔍 Data Explorer")
    
    st.subheader("Raw Data Preview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        sort_by = st.selectbox("Sort by", df_filtered.columns.tolist())
    with col2:
        sort_order = st.radio("Order", ["Ascending", "Descending"], horizontal=True)
    with col3:
        show_rows = st.number_input("Rows to display", 10, 1000, 50, 10)
    
    df_display = df_filtered.sort_values(sort_by, ascending=(sort_order=="Ascending")).head(show_rows)
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Summary Statistics")
        st.dataframe(df_filtered.describe(), use_container_width=True)
    
    with col2:
        st.subheader("📁 Download Data")
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name=f'netflix_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv',
            use_container_width=True
        )

st.divider()
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🎬 Netflix Content Performance Dashboard | Built with Streamlit | © 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)
