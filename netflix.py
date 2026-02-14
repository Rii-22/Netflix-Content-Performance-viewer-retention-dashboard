import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import re
from datetime import datetime

np.random.seed(42)

print("=" * 80)
print("NETFLIX CONTENT PERFORMANCE & VIEWER RETENTION ANALYSIS")
print("=" * 80)
print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

def generate_netflix_data(n_rows=5000):
    print(f"🎬 Generating synthetic dataset with {n_rows:,} viewing records...")
    
    genres = ['Sci-Fi', 'Documentary', 'Comedy', 'Horror', 'Drama']
    user_tiers = ['Basic', 'Standard', 'Premium']
    
    original_titles = [
        'Netflix Original Stranger Things',
        'Netflix Original The Crown',
        'Netflix Original Squid Game',
        'Netflix Original Bridgerton',
        'Netflix Original Wednesday',
        'Netflix Original Dark',
        'Netflix Original Ozark',
        'Netflix Original The Witcher',
        'Netflix Original Money Heist',
        'Netflix Original Black Mirror'
    ]
    
    licensed_titles = [
        'Breaking Bad',
        'Friends',
        'The Office',
        'Suits',
        'Peaky Blinders',
        'Sherlock',
        'The Walking Dead',
        'Grey\'s Anatomy',
        'Supernatural',
        'Criminal Minds'
    ]
    
    all_titles = original_titles + licensed_titles
    
    data = {
        'Title_Name': np.random.choice(all_titles, size=n_rows),
        'Genre': np.random.choice(genres, size=n_rows, 
                                  p=[0.25, 0.15, 0.30, 0.10, 0.20]),
        'User_Tier': np.random.choice(user_tiers, size=n_rows,
                                      p=[0.30, 0.45, 0.25])
    }
    
    watch_times = []
    total_durations = []
    
    for tier in data['User_Tier']:
        if tier == 'Premium':
            base_watch = np.random.gamma(shape=3, scale=25)
            total_dur = np.random.gamma(shape=3, scale=35)
        elif tier == 'Standard':
            base_watch = np.random.gamma(shape=2.5, scale=20)
            total_dur = np.random.gamma(shape=2.5, scale=30)
        else:
            base_watch = np.random.gamma(shape=2, scale=15)
            total_dur = np.random.gamma(shape=2, scale=25)
        
        watch_times.append(min(base_watch, total_dur))
        total_durations.append(total_dur)
    
    data['Watch_Time_Mins'] = np.round(watch_times, 2)
    data['Total_Duration_Mins'] = np.round(total_durations, 2)
    data['Last_Login_Days_Ago'] = np.random.randint(0, 61, size=n_rows)
    
    df = pd.DataFrame(data)
    
    print(f"✅ Dataset generated successfully!")
    print(f"   - Shape: {df.shape}")
    print(f"   - Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB\n")
    
    return df

netflix_df = generate_netflix_data(5000)

print("📊 Sample Data Preview:")
print(netflix_df.head(10))
print("\n" + "=" * 80 + "\n")

print("🔧 FEATURE ENGINEERING & REGEX ANALYSIS")
print("-" * 80)

def identify_originals(df):
    pattern = r'^Netflix Original'
    df['Is_Original'] = df['Title_Name'].apply(
        lambda x: bool(re.search(pattern, x, re.IGNORECASE))
    )
    return df

netflix_df = identify_originals(netflix_df)

netflix_df['Completion_Percentage'] = np.round(
    (netflix_df['Watch_Time_Mins'] / netflix_df['Total_Duration_Mins']) * 100,
    2
)

netflix_df['Completion_Percentage'] = netflix_df['Completion_Percentage'].replace(
    [np.inf, -np.inf], np.nan
).fillna(0)

netflix_df['Completion_Percentage'] = np.minimum(
    netflix_df['Completion_Percentage'], 100
)

print(f"✅ Regex Analysis Complete:")
print(f"   - Netflix Originals: {netflix_df['Is_Original'].sum():,} "
      f"({netflix_df['Is_Original'].sum()/len(netflix_df)*100:.1f}%)")
print(f"   - Licensed Content: {(~netflix_df['Is_Original']).sum():,} "
      f"({(~netflix_df['Is_Original']).sum()/len(netflix_df)*100:.1f}%)")
print(f"\n📈 Completion Percentage Statistics:")
print(netflix_df['Completion_Percentage'].describe())
print("\n" + "=" * 80 + "\n")

print("📊 BUSINESS ANALYTICS & STATISTICAL INSIGHTS")
print("-" * 80)

print("\n🔍 RETENTION CORRELATION ANALYSIS")
print("-" * 40)

correlation_coef, p_value = stats.pearsonr(
    netflix_df['Completion_Percentage'],
    netflix_df['Last_Login_Days_Ago']
)

print(f"Pearson Correlation Coefficient: {correlation_coef:.4f}")
print(f"P-value: {p_value:.6f}")
print(f"Statistical Significance: {'YES ✓' if p_value < 0.05 else 'NO ✗'} (α = 0.05)")

if correlation_coef < 0:
    print(f"\n💡 Insight: Negative correlation detected!")
    print(f"   Users with higher completion rates log in more frequently (lower days ago).")
else:
    print(f"\n💡 Insight: Positive correlation detected!")
    print(f"   Users with higher completion rates tend to have logged in less recently.")

print("\n\n🎭 GENRE PERFORMANCE ANALYSIS")
print("-" * 40)

genre_performance = netflix_df.groupby('Genre').agg({
    'Completion_Percentage': ['mean', 'median', 'std', 'count'],
    'Watch_Time_Mins': 'mean',
    'Is_Original': 'sum'
}).round(2)

genre_performance.columns = ['_'.join(col).strip() for col in genre_performance.columns.values]
genre_performance = genre_performance.rename(columns={
    'Completion_Percentage_mean': 'Avg_Completion_%',
    'Completion_Percentage_median': 'Median_Completion_%',
    'Completion_Percentage_std': 'Std_Completion_%',
    'Completion_Percentage_count': 'Title_Count',
    'Watch_Time_Mins_mean': 'Avg_Watch_Time',
    'Is_Original_sum': 'Original_Count'
})

genre_performance = genre_performance.sort_values('Avg_Completion_%', ascending=False)

print("\nGenre Performance Metrics:")
print(genre_performance)

most_addictive_genre = genre_performance.index[0]
most_addictive_completion = genre_performance.iloc[0]['Avg_Completion_%']

print(f"\n🏆 MOST ADDICTIVE GENRE: {most_addictive_genre}")
print(f"   Average Completion Rate: {most_addictive_completion:.2f}%")

print("\n\n💳 USER TIER PERFORMANCE")
print("-" * 40)

tier_performance = netflix_df.groupby('User_Tier').agg({
    'Watch_Time_Mins': 'mean',
    'Completion_Percentage': 'mean',
    'Last_Login_Days_Ago': 'mean'
}).round(2)

tier_performance = tier_performance.reindex(['Basic', 'Standard', 'Premium'])

print(tier_performance)
print("\n" + "=" * 80 + "\n")

print("📈 GENERATING EXECUTIVE DASHBOARD...")
print("-" * 80 + "\n")

fig = plt.figure(figsize=(16, 12))
fig.suptitle('Netflix Content Performance & Viewer Retention Dashboard',
             fontsize=20, fontweight='bold', y=0.995)

netflix_red = '#E50914'
netflix_dark = '#221f1f'
colors_tier = ['#564d4d', '#831010', netflix_red]
colors_content = [netflix_red, '#564d4d']

ax1 = plt.subplot(2, 2, 1)

tier_watch_time = tier_performance['Watch_Time_Mins']
bars = ax1.bar(tier_watch_time.index, tier_watch_time.values, 
               color=colors_tier, edgecolor='black', linewidth=1.5, alpha=0.85)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f} min',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_title('Average Watch Time by User Tier', 
              fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('User Tier', fontsize=12, fontweight='bold')
ax1.set_ylabel('Average Watch Time (Minutes)', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_axisbelow(True)

max_tier = tier_watch_time.idxmax()
ax1.annotate(f'{max_tier} users watch\n{tier_watch_time.max():.1f} min on average',
             xy=(tier_watch_time.index.tolist().index(max_tier), tier_watch_time.max()),
             xytext=(20, 20), textcoords='offset points',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
             arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', lw=2),
             fontsize=10, fontweight='bold')

ax2 = plt.subplot(2, 2, 2)

sample_size = 500
sample_indices = np.random.choice(len(netflix_df), sample_size, replace=False)
sample_df = netflix_df.iloc[sample_indices]

scatter = ax2.scatter(sample_df['Completion_Percentage'], 
                     sample_df['Last_Login_Days_Ago'],
                     c=sample_df['Last_Login_Days_Ago'], 
                     cmap='RdYlGn_r',
                     alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

z = np.polyfit(netflix_df['Completion_Percentage'], 
               netflix_df['Last_Login_Days_Ago'], 1)
p = np.poly1d(z)
x_trend = np.linspace(netflix_df['Completion_Percentage'].min(), 
                      netflix_df['Completion_Percentage'].max(), 100)
ax2.plot(x_trend, p(x_trend), color=netflix_red, linewidth=3, 
         linestyle='--', label=f'Trendline: y={z[0]:.3f}x+{z[1]:.2f}')

ax2.set_title('Content Completion vs. User Retention', 
              fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Completion Percentage (%)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Days Since Last Login', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_axisbelow(True)
ax2.legend(loc='upper right', fontsize=10)

cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('Days Since Login', fontsize=10, fontweight='bold')

ax2.text(0.05, 0.95, f'Correlation: {correlation_coef:.3f}\np-value: {p_value:.4f}',
         transform=ax2.transAxes, fontsize=11, verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
         fontweight='bold')

ax3 = plt.subplot(2, 2, 3)

content_mix = netflix_df['Is_Original'].value_counts()
labels = ['Netflix Originals', 'Licensed Content']
sizes = [content_mix[True], content_mix[False]]
explode = (0.05, 0)

wedges, texts, autotexts = ax3.pie(sizes, explode=explode, labels=labels,
                                     colors=colors_content, autopct='%1.1f%%',
                                     startangle=90, textprops={'fontsize': 12},
                                     wedgeprops={'edgecolor': 'black', 
                                                'linewidth': 2, 'alpha': 0.85})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(13)

for text in texts:
    text.set_fontweight('bold')
    text.set_fontsize(12)

ax3.set_title('Content Mix: Originals vs. Licensed', 
              fontsize=14, fontweight='bold', pad=15)

ax4 = plt.subplot(2, 2, 4)

genre_data = [netflix_df[netflix_df['Genre'] == genre]['Completion_Percentage'].values 
              for genre in genre_performance.index]

bp = ax4.boxplot(genre_data, labels=genre_performance.index, patch_artist=True,
                 notch=True, showmeans=True,
                 meanprops=dict(marker='D', markerfacecolor='red', markersize=8),
                 boxprops=dict(facecolor='lightblue', alpha=0.7),
                 medianprops=dict(color='red', linewidth=2),
                 whiskerprops=dict(linewidth=1.5),
                 capprops=dict(linewidth=1.5))

colors_box = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(genre_performance)))
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)

ax4.set_title('Completion Distribution by Genre', 
              fontsize=14, fontweight='bold', pad=15)
ax4.set_xlabel('Genre', fontsize=12, fontweight='bold')
ax4.set_ylabel('Completion Percentage (%)', fontsize=12, fontweight='bold')
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.set_axisbelow(True)
ax4.tick_params(axis='x', rotation=15)

legend_elements = [
    plt.Line2D([0], [0], color='red', linewidth=2, label='Median'),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor='red', 
               markersize=8, label='Mean')
]
ax4.legend(handles=legend_elements, loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig('netflix_performance_dashboard.png', dpi=300, bbox_inches='tight')
print("✅ Dashboard saved as 'netflix_performance_dashboard.png'")
plt.show()

print("\n" + "=" * 80 + "\n")

print("=" * 80)
print("📋 EXECUTIVE BUSINESS SUMMARY")
print("=" * 80)
print()
print("QUESTION:")
print("Based on the p-value from our scipy analysis, does content completion")
print("significantly impact user churn (retention)?")
print()
print("-" * 80)
print()

alpha = 0.05
is_significant = p_value < alpha

print("STATISTICAL FINDINGS:")
print(f"  • Pearson Correlation Coefficient: {correlation_coef:.4f}")
print(f"  • P-value: {p_value:.6f}")
print(f"  • Significance Level (α): {alpha}")
print(f"  • Result: {'STATISTICALLY SIGNIFICANT ✓' if is_significant else 'NOT SIGNIFICANT ✗'}")
print()

print("BUSINESS INTERPRETATION:")
print()

if is_significant:
    if correlation_coef < 0:
        print("✅ YES - Content completion SIGNIFICANTLY impacts user retention.")
        print()
        print("KEY INSIGHTS:")
        print(f"  • Strong negative correlation detected (r = {correlation_coef:.4f})")
        print("  • Users who complete more content log in MORE frequently")
        print("  • Higher completion rates → Lower churn risk")
        print()
        print("STRATEGIC RECOMMENDATIONS:")
        print("  1. 🎯 CONTENT STRATEGY: Invest in highly engaging content that drives")
        print("     completion rates, particularly in the top-performing genre:")
        print(f"     {most_addictive_genre} (Avg. {most_addictive_completion:.1f}% completion)")
        print()
        print("  2. 📊 RETENTION METRICS: Use completion percentage as a leading")
        print("     indicator for churn prediction models")
        print()
        print("  3. 🔔 ENGAGEMENT CAMPAIGNS: Target users with <50% completion rates")
        print("     with personalized recommendations to boost engagement")
        print()
        print("  4. 💎 PREMIUM VALUE: Highlight that Premium users have higher average")
        print(f"     watch times ({tier_performance.loc['Premium', 'Watch_Time_Mins']:.1f} mins)")
        print("     to justify tier upgrades")
        print()
        print("  5. 🎬 ORIGINAL CONTENT: Netflix Originals represent")
        print(f"     {netflix_df['Is_Original'].sum()/len(netflix_df)*100:.1f}% of viewing -")
        print("     continue investing in exclusive content to drive platform loyalty")
        
    else:
        print("⚠️  UNEXPECTED FINDING - Positive correlation detected.")
        print()
        print(f"  • Users with higher completion log in LESS frequently (r = {correlation_coef:.4f})")
        print("  • This suggests 'binge-and-pause' behavior")
        print()
        print("RECOMMENDATION:")
        print("  • Investigate content release strategies (weekly vs. full season drops)")
        print("  • Consider engagement tactics between content consumption periods")
else:
    print("❌ NO - Content completion does NOT significantly impact user retention")
    print("   (based on current data).")
    print()
    print("IMPLICATIONS:")
    print("  • The correlation is not statistically significant (p > 0.05)")
    print("  • Other factors may be stronger drivers of retention")
    print()
    print("RECOMMENDATIONS:")
    print("  • Investigate alternative retention drivers (e.g., content variety,")
    print("    subscription tenure, device usage patterns)")
    print("  • Expand analysis with additional variables")
    print("  • Consider segmentation analysis by user cohorts")

print()
print("-" * 80)
print()
print("ADDITIONAL METRICS:")
print(f"  • Total Viewing Records Analyzed: {len(netflix_df):,}")
print(f"  • Most Addictive Genre: {most_addictive_genre} ({most_addictive_completion:.2f}% avg completion)")
print(f"  • Average Platform Completion Rate: {netflix_df['Completion_Percentage'].mean():.2f}%")
print(f"  • User Engagement Variance: {netflix_df['Completion_Percentage'].std():.2f}% std dev")
print()
print("=" * 80)
print()
print("✅ ANALYSIS COMPLETE - Ready for stakeholder presentation")
print("=" * 80)