import streamlit as st
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import re
from datetime import datetime

st.set_page_config(page_title="Netflix Analytics", layout="wide", page_icon="🎬")

np.random.seed(42)

st.title("🎬 Netflix Content Performance & Viewer Retention Dashboard")
st.markdown(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.divider()

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
    
    for tier in data['User_Tier']:
        if tier == 'Premium':
            watch = np.random.gamma(3, 25)
            total = np.random.gamma(3, 35)
        elif tier == 'Standard':
            watch = np.random.gamma(2.5, 20)
            total = np.random.gamma(2.5, 30)
        else:
            watch = np.random.gamma(2, 15)
            total = np.random.gamma(2, 25)
        
        watch_times.append(min(watch, total))
        total_durations.append(total)
    
    data['Watch_Time_Mins'] = np.round(watch_times, 2)
    data['Total_Duration_Mins'] = np.round(total_durations, 2)
    data['Last_Login_Days_Ago'] = np.random.randint(0, 61, n_rows)
    
    df = pd.DataFrame(data)
    
    pattern = r'^Netflix Original'
    df['Is_Original'] = df['Title_Name'].str.contains(pattern, case=False, regex=True)
    
    df['Completion_Percentage'] = np.minimum(
        np.round((df['Watch_Time_Mins'] / df['Total_Duration_Mins']) * 100, 2),
        100
    )
    df['Completion_Percentage'] = df['Completion_Percentage'].fillna(0)
    
    return df

with st.spinner('Loading data...'):
    df = generate_data(5000)

st.success(f"✅ Dataset loaded: {df.shape[0]:,} records")

with st.expander("📊 View Sample Data"):
    st.dataframe(df.head(10), use_container_width=True)

st.divider()
st.header("🔧 Content Analysis")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Netflix Originals", f"{df['Is_Original'].sum():,}")
with col2:
    st.metric("Licensed Content", f"{(~df['Is_Original']).sum():,}")
with col3:
    st.metric("Avg Completion", f"{df['Completion_Percentage'].mean():.1f}%")
with col4:
    st.metric("Total Views", f"{len(df):,}")

st.divider()
st.header("📊 Statistical Analysis")

corr, pval = stats.pearsonr(df['Completion_Percentage'], df['Last_Login_Days_Ago'])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Correlation", f"{corr:.4f}")
with col2:
    st.metric("P-value", f"{pval:.6f}")
with col3:
    sig = "✓ Significant" if pval < 0.05 else "✗ Not Significant"
    st.metric("Result", sig)

if corr < 0:
    st.info("💡 Users with higher completion rates log in more frequently!")
else:
    st.info("💡 Users with higher completion rates logged in less recently.")

st.divider()
st.header("🎭 Genre Performance")

genre_stats = df.groupby('Genre').agg({
    'Completion_Percentage': 'mean',
    'Watch_Time_Mins': 'mean',
    'Title_Name': 'count'
}).round(2)

genre_stats.columns = ['Avg_Completion_%', 'Avg_Watch_Time', 'View_Count']
genre_stats = genre_stats.sort_values('Avg_Completion_%', ascending=False)

top_genre = genre_stats.index[0]
top_completion = genre_stats.iloc[0]['Avg_Completion_%']

st.success(f"🏆 Most Engaging: **{top_genre}** ({top_completion:.1f}% avg completion)")
st.dataframe(genre_stats, use_container_width=True)

st.divider()
st.header("💳 User Tier Performance")

tier_stats = df.groupby('User_Tier').agg({
    'Watch_Time_Mins': 'mean',
    'Completion_Percentage': 'mean',
    'Last_Login_Days_Ago': 'mean'
}).round(2)

tier_stats = tier_stats.reindex(['Basic', 'Standard', 'Premium'])
st.dataframe(tier_stats, use_container_width=True)

st.divider()
st.header("📈 Visualizations")

fig = plt.figure(figsize=(16, 10))
fig.patch.set_facecolor('white')

netflix_red = '#E50914'
colors_tier = ['#564d4d', '#831010', netflix_red]

ax1 = plt.subplot(2, 2, 1)
bars = ax1.bar(tier_stats.index, tier_stats['Watch_Time_Mins'], 
               color=colors_tier, edgecolor='black', linewidth=1.5, alpha=0.85)
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
ax1.set_title('Average Watch Time by User Tier', fontsize=14, fontweight='bold', pad=10)
ax1.set_ylabel('Minutes', fontsize=11, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')

ax2 = plt.subplot(2, 2, 2)
sample_idx = np.random.choice(len(df), 500, replace=False)
sample = df.iloc[sample_idx]
scatter = ax2.scatter(sample['Completion_Percentage'], sample['Last_Login_Days_Ago'],
                     c=sample['Last_Login_Days_Ago'], cmap='RdYlGn_r',
                     alpha=0.6, s=40, edgecolors='black', linewidth=0.5)
z = np.polyfit(df['Completion_Percentage'], df['Last_Login_Days_Ago'], 1)
p = np.poly1d(z)
x_line = np.linspace(0, 100, 100)
ax2.plot(x_line, p(x_line), color=netflix_red, linewidth=2.5, 
         linestyle='--', label=f'y={z[0]:.3f}x+{z[1]:.1f}')
ax2.set_title('Completion vs Retention', fontsize=14, fontweight='bold', pad=10)
ax2.set_xlabel('Completion %', fontsize=11, fontweight='bold')
ax2.set_ylabel('Days Since Login', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.legend(loc='upper right', fontsize=9)
cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('Days', fontsize=9)

ax3 = plt.subplot(2, 2, 3)
content_counts = df['Is_Original'].value_counts()
labels = ['Netflix Originals', 'Licensed']
sizes = [content_counts[True], content_counts[False]]
colors = [netflix_red, '#564d4d']
explode = (0.05, 0)
wedges, texts, autotexts = ax3.pie(sizes, explode=explode, labels=labels,
                                     colors=colors, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 11})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
for text in texts:
    text.set_fontweight('bold')
ax3.set_title('Content Mix', fontsize=14, fontweight='bold', pad=10)

ax4 = plt.subplot(2, 2, 4)
genre_data = [df[df['Genre'] == g]['Completion_Percentage'].values for g in genre_stats.index]
bp = ax4.boxplot(genre_data, labels=genre_stats.index, patch_artist=True,
                 showmeans=True, meanprops=dict(marker='D', markerfacecolor='red', markersize=6))
for patch in bp['boxes']:
    patch.set_facecolor('lightblue')
    patch.set_alpha(0.7)
ax4.set_title('Completion by Genre', fontsize=14, fontweight='bold', pad=10)
ax4.set_ylabel('Completion %', fontsize=11, fontweight='bold')
ax4.grid(axis='y', alpha=0.3, linestyle='--')
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=15)

plt.tight_layout()
st.pyplot(fig)
plt.close()

st.divider()
st.header("📋 Executive Summary")

st.subheader("Question")
st.write("Does content completion significantly impact user retention?")

st.subheader("Statistical Findings")
st.write(f"• Correlation: **{corr:.4f}**")
st.write(f"• P-value: **{pval:.6f}**")
st.write(f"• Result: **{'SIGNIFICANT ✓' if pval < 0.05 else 'NOT SIGNIFICANT ✗'}** (α = 0.05)")

st.subheader("Business Interpretation")

if pval < 0.05 and corr < 0:
    st.success("✅ YES - Content completion SIGNIFICANTLY impacts retention.")
    st.markdown("**Key Insights:**")
    st.write(f"• Strong negative correlation (r = {corr:.4f})")
    st.write("• Higher completion → More frequent logins → Lower churn")
    st.markdown("**Recommendations:**")
    st.write(f"1. 🎯 Invest in engaging content, especially **{top_genre}** ({top_completion:.1f}% completion)")
    st.write("2. 📊 Use completion % as churn prediction metric")
    st.write("3. 🔔 Target users with <50% completion for re-engagement")
    st.write(f"4. 💎 Premium users watch {tier_stats.loc['Premium', 'Watch_Time_Mins']:.1f} mins avg - promote upgrades")
elif pval < 0.05:
    st.warning("⚠️ Positive correlation detected - 'binge-and-pause' behavior")
    st.write("• Investigate weekly vs full-season release strategies")
else:
    st.error("❌ NO significant impact found")
    st.write("• Explore other retention drivers: content variety, device usage, tenure")

st.divider()
st.subheader("Key Metrics")
st.write(f"• Records Analyzed: **{len(df):,}**")
st.write(f"• Top Genre: **{top_genre}** ({top_completion:.2f}%)")
st.write(f"• Platform Avg Completion: **{df['Completion_Percentage'].mean():.2f}%**")

st.success("✅ Analysis Complete")
