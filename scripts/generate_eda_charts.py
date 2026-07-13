import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Define dataset paths
datasets = {
    "car_claims": r"c:\Yoge Studies\Guvi Projects\acko_ai_native_insurance_platform\DataSet\claim_Quotation_datas\Claims\acko_car_claims.csv",
    "bike_claims": r"c:\Yoge Studies\Guvi Projects\acko_ai_native_insurance_platform\DataSet\claim_Quotation_datas\Claims\acko_bike_claims.csv",
    "car_quotation": r"c:\Yoge Studies\Guvi Projects\acko_ai_native_insurance_platform\DataSet\claim_Quotation_datas\Quotation\acko_car_quotation.csv",
    "bike_quotation": r"c:\Yoge Studies\Guvi Projects\acko_ai_native_insurance_platform\DataSet\claim_Quotation_datas\Quotation\acko_bike_quotation.csv"
}

# Base directory for figures
fig_base_dir = r"c:\Yoge Studies\Guvi Projects\acko_ai_native_insurance_platform\reports\figures"

# Professional Color Palette
PRIMARY_COLOR = '#1f4e79'   # Deep Blue
SECONDARY_COLOR = '#2e75b6' # Medium Blue
ACCENT_COLOR = '#c55a11'    # Coral/Rust
SUCCESS_COLOR = '#375623'   # Forest Green
NEUTRAL_LIGHT = '#f2f2f2'   # Soft Grey
GRID_COLOR = '#d9d9d9'

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'axes.grid': True,
    'grid.color': GRID_COLOR,
    'grid.linestyle': '--',
    'grid.alpha': 0.7
})

def create_dirs():
    for ds_name in datasets.keys():
        d = os.path.join(fig_base_dir, ds_name)
        os.makedirs(d, exist_ok=True)
    os.makedirs(os.path.join(fig_base_dir, "master"), exist_ok=True)
    print("Output directories initialized.")

def generate_car_quotation_charts():
    name = "car_quotation"
    print(f"Generating charts for {name}...")
    df = pd.read_csv(datasets[name])
    out_dir = os.path.join(fig_base_dir, name)
    
    # 1. Target Variable Distribution (annual_premium)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.hist(df['annual_premium'], bins=50, color=PRIMARY_COLOR, edgecolor='white')
    ax1.set_title("Annual Premium Distribution")
    ax1.set_xlabel("Annual Premium (INR)")
    ax1.set_ylabel("Count")
    ax1.ticklabel_format(style='plain', axis='x')
    
    ax2.hist(np.log1p(df['annual_premium']), bins=50, color=SECONDARY_COLOR, edgecolor='white')
    ax2.set_title("Log-Transformed Annual Premium Distribution")
    ax2.set_xlabel("Log(Annual Premium)")
    ax2.set_ylabel("Count")
    fig.suptitle("Car Underwriting Target Variable Distribution (Skewness Analysis)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "01_target_distribution.png"), dpi=150)
    plt.close()
    
    # 2. Numerical Univariate - IDV & Age
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.boxplot(df['idv'], vert=False, patch_artist=True, boxprops=dict(facecolor=SECONDARY_COLOR, color=PRIMARY_COLOR))
    ax1.set_title("Insured Declared Value (IDV)")
    ax1.set_xlabel("IDV (INR)")
    ax1.ticklabel_format(style='plain', axis='x')
    
    ax2.boxplot(df['customer_age'], vert=False, patch_artist=True, boxprops=dict(facecolor=ACCENT_COLOR, color='black'))
    ax2.set_title("Customer Age Range")
    ax2.set_xlabel("Age (Years)")
    fig.suptitle("Univariate Analysis: Core Continuous Risk Drivers")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "02_numerical_univariate.png"), dpi=150)
    plt.close()
    
    # 3. Categorical Univariate - Segment Count Plot
    plt.figure(figsize=(10, 5))
    counts = df['segment'].value_counts()
    plt.bar(counts.index, counts.values, color=PRIMARY_COLOR, edgecolor='black')
    plt.title("Vehicle Segment Distribution")
    plt.xlabel("Segment")
    plt.ylabel("Number of Quotations")
    for i, v in enumerate(counts.values):
        plt.text(i, v + 2000, f"{v/len(df)*100:.1f}%", ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "03_categorical_univariate_segment.png"), dpi=150)
    plt.close()

    # 4. Bivariate - Premium vs IDV Scatter
    plt.figure(figsize=(10, 6))
    sample = df.sample(5000, random_state=42)
    plt.scatter(sample['idv'], sample['annual_premium'], alpha=0.5, color=PRIMARY_COLOR, label='Quotes')
    # Fit line
    m, c = np.polyfit(sample['idv'], sample['annual_premium'], 1)
    plt.plot(sample['idv'], m*sample['idv'] + c, color=ACCENT_COLOR, linewidth=2, label=f'Linear Fit (m={m:.4f})')
    plt.title("Annual Premium vs. Insured Declared Value (IDV)")
    plt.xlabel("IDV (INR)")
    plt.ylabel("Annual Premium (INR)")
    plt.legend()
    plt.ticklabel_format(style='plain', axis='x')
    plt.ticklabel_format(style='plain', axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "04_bivariate_premium_vs_idv.png"), dpi=150)
    plt.close()
    
    # 5. Bivariate - Premium vs Segment (Box)
    plt.figure(figsize=(10, 6))
    segments = df['segment'].unique()
    data_to_plot = [df[df['segment'] == s]['annual_premium'] for s in segments]
    plt.boxplot(data_to_plot, labels=segments, patch_artist=True, boxprops=dict(facecolor=SECONDARY_COLOR))
    plt.title("Premium Range Spread across Vehicle Segments")
    plt.xlabel("Vehicle Segment")
    plt.ylabel("Annual Premium (INR)")
    plt.yscale('log') # Log scale because of extreme premiums
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "05_bivariate_premium_vs_segment.png"), dpi=150)
    plt.close()

    # 6. Bivariate - Premium vs NCB Percent (Box)
    plt.figure(figsize=(10, 6))
    ncb_vals = sorted(df['ncb_percent'].unique())
    data_to_plot = [df[df['ncb_percent'] == n]['annual_premium'] for n in ncb_vals]
    plt.boxplot(data_to_plot, labels=[f"{n}%" for n in ncb_vals], patch_artist=True, boxprops=dict(facecolor=SUCCESS_COLOR))
    plt.title("Premium Impact of No Claim Bonus (NCB) Discount Tiers")
    plt.xlabel("NCB Percent Tier")
    plt.ylabel("Annual Premium (INR)")
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "06_bivariate_premium_vs_ncb.png"), dpi=150)
    plt.close()

    # 7. Correlation Matrix Heatmap
    plt.figure(figsize=(10, 8))
    corr = df.select_dtypes(include=[np.number]).corr()
    # Mask out leakage variables for clean presentation if needed, or show all to highlight leakage
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Matrix of Quotation Numerical Features")
    # Annotate important correlations
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            text_color = 'white' if abs(corr.iloc[i, j]) > 0.6 else 'black'
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color=text_color, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "07_correlation_matrix.png"), dpi=150)
    plt.close()

def generate_bike_quotation_charts():
    name = "bike_quotation"
    print(f"Generating charts for {name}...")
    df = pd.read_csv(datasets[name])
    out_dir = os.path.join(fig_base_dir, name)
    
    # 1. Target Variable Distribution
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    ax1.hist(df['annual_premium'], bins=50, color=PRIMARY_COLOR, edgecolor='white')
    ax1.set_title("Annual Premium Distribution")
    ax1.set_xlabel("Annual Premium (INR)")
    ax1.set_ylabel("Count")
    ax1.ticklabel_format(style='plain', axis='x')
    
    ax2.hist(np.log1p(df['annual_premium']), bins=50, color=SECONDARY_COLOR, edgecolor='white')
    ax2.set_title("Log-Transformed Annual Premium Distribution")
    ax2.set_xlabel("Log(Annual Premium)")
    ax2.set_ylabel("Count")
    fig.suptitle("Bike Underwriting Target Variable Distribution (Skewness Analysis)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "01_target_distribution.png"), dpi=150)
    plt.close()
    
    # 2. Categorical Univariate - Fuel & Usage
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fc = df['fuel_type'].value_counts()
    ax1.bar(fc.index, fc.values, color=[PRIMARY_COLOR, SUCCESS_COLOR], edgecolor='black')
    ax1.set_title("Fuel Type split (ICE vs. EV)")
    ax1.set_xlabel("Fuel Type")
    ax1.set_ylabel("Quotations")
    for i, v in enumerate(fc.values):
        ax1.text(i, v + 2000, f"{v/len(df)*100:.1f}%", ha='center', fontweight='bold')
        
    uc = df['usage_type'].value_counts()
    ax2.bar(uc.index, uc.values, color=SECONDARY_COLOR, edgecolor='black')
    ax2.set_title("Rider Usage Classification")
    ax2.set_xlabel("Usage Type")
    ax2.set_ylabel("Quotations")
    for i, v in enumerate(uc.values):
        ax2.text(i, v + 2000, f"{v/len(df)*100:.1f}%", ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "02_categorical_univariate.png"), dpi=150)
    plt.close()

    # 3. Bivariate - Premium vs usage type (Box)
    plt.figure(figsize=(10, 6))
    usages = df['usage_type'].unique()
    data_to_plot = [df[df['usage_type'] == u]['annual_premium'] for u in usages]
    plt.boxplot(data_to_plot, labels=usages, patch_artist=True, boxprops=dict(facecolor=ACCENT_COLOR))
    plt.title("Bike Premium Spread by Rider Usage Type")
    plt.xlabel("Usage Type")
    plt.ylabel("Annual Premium (INR)")
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "03_bivariate_premium_vs_usage.png"), dpi=150)
    plt.close()

    # 4. Bivariate - Premium vs IDV Scatter
    plt.figure(figsize=(10, 6))
    sample = df.sample(5000, random_state=42)
    plt.scatter(sample['idv'], sample['annual_premium'], alpha=0.5, color=PRIMARY_COLOR, label='Quotes')
    m, c = np.polyfit(sample['idv'], sample['annual_premium'], 1)
    plt.plot(sample['idv'], m*sample['idv'] + c, color=ACCENT_COLOR, linewidth=2, label=f'Linear Fit (m={m:.4f})')
    plt.title("Bike Annual Premium vs. Insured Declared Value (IDV)")
    plt.xlabel("IDV (INR)")
    plt.ylabel("Annual Premium (INR)")
    plt.legend()
    plt.ticklabel_format(style='plain', axis='x')
    plt.ticklabel_format(style='plain', axis='y')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "04_bivariate_premium_vs_idv.png"), dpi=150)
    plt.close()

    # 5. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    corr = df.select_dtypes(include=[np.number]).corr()
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Matrix of Bike Quotation Numerical Features")
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            text_color = 'white' if abs(corr.iloc[i, j]) > 0.6 else 'black'
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color=text_color, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "05_correlation_matrix.png"), dpi=150)
    plt.close()

def generate_car_claims_charts():
    name = "car_claims"
    print(f"Generating charts for {name}...")
    df = pd.read_csv(datasets[name])
    out_dir = os.path.join(fig_base_dir, name)
    
    # 1. Target Variable Distribution - Class Balance
    plt.figure(figsize=(8, 5))
    vc = df['claim_approved'].value_counts()
    labels = ['Approved (1)', 'Rejected (0)']
    plt.bar(labels, vc.values, color=[SUCCESS_COLOR, ACCENT_COLOR], edgecolor='black', width=0.5)
    plt.title("Car Claim Approval Class Balance")
    plt.xlabel("Claim Status")
    plt.ylabel("Count")
    for i, v in enumerate(vc.values):
        plt.text(i, v + 2000, f"{v} ({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "01_target_balance.png"), dpi=150)
    plt.close()
    
    # 2. Bivariate - Approval vs Damage Severity Score
    plt.figure(figsize=(10, 5))
    # Group by severity and calculate mean approval
    grouped = df.groupby('damage_severity_score')['claim_approved'].mean() * 100
    plt.plot(grouped.index, grouped.values, marker='o', linewidth=2.5, color=PRIMARY_COLOR)
    plt.title("Car Claim Approval Rate by Damage Severity Score")
    plt.xlabel("Damage Severity Score (1 - 10)")
    plt.ylabel("Approval Rate (%)")
    plt.ylim(0, 105)
    for x, y in zip(grouped.index, grouped.values):
        plt.text(x, y + 2, f"{y:.1f}%", ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "02_approval_vs_severity.png"), dpi=150)
    plt.close()

    # 3. Bivariate - Claim Approved vs Claim Amount
    plt.figure(figsize=(10, 6))
    data_to_plot = [df[df['claim_approved'] == 0]['claim_amount'], df[df['claim_approved'] == 1]['claim_amount']]
    plt.boxplot(data_to_plot, labels=['Rejected (0)', 'Approved (1)'], patch_artist=True, boxprops=dict(facecolor=SECONDARY_COLOR))
    plt.title("Claim Amount Distribution by Approval Status")
    plt.xlabel("Claim Status")
    plt.ylabel("Claim Amount (INR) - Log Scale")
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "03_claim_amount_vs_approval.png"), dpi=150)
    plt.close()

    # 4. Bivariate - Incident Type and Approval Status (Grouped Bar)
    plt.figure(figsize=(12, 6))
    crosstab = pd.crosstab(df['incident_type'], df['claim_approved'], normalize='index') * 100
    crosstab.plot(kind='bar', stacked=True, color=[ACCENT_COLOR, SUCCESS_COLOR], edgecolor='black', ax=plt.gca())
    plt.title("Car Claim Status Split by Incident Type")
    plt.xlabel("Incident Type")
    plt.ylabel("Percentage (%)")
    plt.legend(['Rejected (0)', 'Approved (1)'], bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "04_incident_type_vs_approval.png"), dpi=150)
    plt.close()

    # 5. Correlation Heatmap (numerical claim features)
    plt.figure(figsize=(12, 10))
    corr = df.select_dtypes(include=[np.number]).corr()
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Matrix of Car Claim Numerical Features")
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            text_color = 'white' if abs(corr.iloc[i, j]) > 0.6 else 'black'
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color=text_color, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "05_correlation_matrix.png"), dpi=150)
    plt.close()

def generate_bike_claims_charts():
    name = "bike_claims"
    print(f"Generating charts for {name}...")
    df = pd.read_csv(datasets[name])
    out_dir = os.path.join(fig_base_dir, name)
    
    # 1. Target Variable Distribution - Class Balance
    plt.figure(figsize=(8, 5))
    vc = df['claim_approved'].value_counts()
    labels = ['Approved (1)', 'Rejected (0)']
    plt.bar(labels, vc.values, color=[SUCCESS_COLOR, ACCENT_COLOR], edgecolor='black', width=0.5)
    plt.title("Bike Claim Approval Class Balance")
    plt.xlabel("Claim Status")
    plt.ylabel("Count")
    for i, v in enumerate(vc.values):
        plt.text(i, v + 2000, f"{v} ({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "01_target_balance.png"), dpi=150)
    plt.close()
    
    # 2. Bivariate - Approval vs Helmet Worn (Grouped Bar)
    plt.figure(figsize=(8, 5))
    crosstab = pd.crosstab(df['helmet_worn'], df['claim_approved'], normalize='index') * 100
    crosstab.plot(kind='bar', stacked=True, color=[ACCENT_COLOR, SUCCESS_COLOR], edgecolor='black', ax=plt.gca())
    plt.title("Claim Approval split by Helmet Compliance")
    plt.xlabel("Helmet Worn (0: No, 1: Yes)")
    plt.ylabel("Percentage (%)")
    plt.xticks(rotation=0)
    plt.legend(['Rejected (0)', 'Approved (1)'])
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "02_approval_vs_helmet.png"), dpi=150)
    plt.close()

    # 3. Bivariate - Approval vs Rider Experience Years
    plt.figure(figsize=(12, 5))
    grouped = df.groupby('rider_experience_years')['claim_approved'].mean() * 100
    plt.plot(grouped.index, grouped.values, marker='s', color=PRIMARY_COLOR, linewidth=2)
    plt.title("Bike Claim Approval Rate by Rider License Experience")
    plt.xlabel("Rider License Experience (Years)")
    plt.ylabel("Approval Rate (%)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "03_approval_vs_experience.png"), dpi=150)
    plt.close()

    # 4. Bivariate - Approval vs Damage Severity Score
    plt.figure(figsize=(10, 5))
    grouped = df.groupby('damage_severity_score')['claim_approved'].mean() * 100
    plt.plot(grouped.index, grouped.values, marker='o', linewidth=2.5, color=PRIMARY_COLOR)
    plt.title("Bike Claim Approval Rate by Damage Severity Score")
    plt.xlabel("Damage Severity Score (1 - 10)")
    plt.ylabel("Approval Rate (%)")
    plt.ylim(0, 105)
    for x, y in zip(grouped.index, grouped.values):
        plt.text(x, y + 2, f"{y:.1f}%", ha='center', fontsize=9, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "04_approval_vs_severity.png"), dpi=150)
    plt.close()

    # 5. Correlation Heatmap
    plt.figure(figsize=(12, 10))
    corr = df.select_dtypes(include=[np.number]).corr()
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Matrix of Bike Claim Numerical Features")
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            text_color = 'white' if abs(corr.iloc[i, j]) > 0.6 else 'black'
            plt.text(j, i, f"{corr.iloc[i, j]:.2f}", ha='center', va='center', color=text_color, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "05_correlation_matrix.png"), dpi=150)
    plt.close()

def generate_master_comparative_charts():
    print("Generating master comparative charts...")
    out_dir = os.path.join(fig_base_dir, "master")
    
    # 1. Car vs Bike Quotation Target Comparison (Log scale Boxplots side-by-side)
    car_df = pd.read_csv(datasets["car_quotation"])
    bike_df = pd.read_csv(datasets["bike_quotation"])
    
    plt.figure(figsize=(10, 6))
    data_to_plot = [car_df['annual_premium'], bike_df['annual_premium']]
    plt.boxplot(data_to_plot, labels=['Car Underwriting Premium', 'Bike Underwriting Premium'], patch_artist=True, boxprops=dict(facecolor=SECONDARY_COLOR))
    plt.title("Underwriting Premium Scales Comparison (Car vs. Bike)")
    plt.ylabel("Annual Premium (INR) - Log Scale")
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "01_premium_comparison.png"), dpi=150)
    plt.close()

    # 2. Car vs Bike Claims Target Comparison (Approval distributions)
    car_claims_df = pd.read_csv(datasets["car_claims"])
    bike_claims_df = pd.read_csv(datasets["bike_claims"])
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    cc_app = car_claims_df['claim_approved'].value_counts(normalize=True)*100
    ax1.bar(['Approved (1)', 'Rejected (0)'], cc_app.values, color=[SUCCESS_COLOR, ACCENT_COLOR], edgecolor='black', width=0.5)
    ax1.set_title("Car Claims Approval Rate")
    ax1.set_ylabel("Percentage (%)")
    ax1.set_ylim(0, 105)
    for i, v in enumerate(cc_app.values):
        ax1.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')
        
    bc_app = bike_claims_df['claim_approved'].value_counts(normalize=True)*100
    ax2.bar(['Approved (1)', 'Rejected (0)'], bc_app.values, color=[SUCCESS_COLOR, ACCENT_COLOR], edgecolor='black', width=0.5)
    ax2.set_title("Bike Claims Approval Rate")
    ax2.set_ylabel("Percentage (%)")
    ax2.set_ylim(0, 105)
    for i, v in enumerate(bc_app.values):
        ax2.text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')
        
    fig.suptitle("Claim Approval Rates Comparison (Car vs. Bike Assets)")
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "02_claims_approval_comparison.png"), dpi=150)
    plt.close()
    
    # 3. EV Penetration Comparison in Platform
    plt.figure(figsize=(10, 6))
    car_ev_pct = (car_df['fuel_type'] == 'Electric').mean() * 100
    bike_ev_pct = (bike_df['fuel_type'] == 'Electric').mean() * 100
    plt.bar(['Car Quotation (EV)', 'Bike Quotation (EV)'], [car_ev_pct, bike_ev_pct], color=[PRIMARY_COLOR, SUCCESS_COLOR], edgecolor='black', width=0.4)
    plt.title("EV Penetration Rates across Platform Underwriting Portfolios")
    plt.ylabel("EV Percentage (%)")
    plt.ylim(0, 50)
    for i, v in enumerate([car_ev_pct, bike_ev_pct]):
        plt.text(i, v + 1, f"{v:.2f}%", ha='center', fontweight='bold', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "03_ev_penetration_comparison.png"), dpi=150)
    plt.close()

if __name__ == "__main__":
    create_dirs()
    generate_car_quotation_charts()
    generate_bike_quotation_charts()
    generate_car_claims_charts()
    generate_bike_claims_charts()
    generate_master_comparative_charts()
    print("EDA Visualizations Successfully Generated and Exported.")
