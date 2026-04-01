
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# Set style
plt.style.use('default')
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Configuration
DB_PATH = r"c:\Users\agb83\Documents\Thesisly\17 Rahul\ict-impact-dashboard\backend\database\ict_survey.db"
OUTPUT_DIR = r"c:\Users\agb83\Documents\Thesisly\17 Rahul\ict-impact-dashboard\figures"

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")

def get_data():
    """Fetch data from SQLite database"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    
    # query to fetch all chart survey responses
    query = """
    SELECT 
        college,
        hardware_quality,
        software_availability,
        internet_speed,
        digital_collection,
        infrastructure_score,
        overall_satisfaction,
        service_efficiency,
        financial_barrier,
        technical_barrier,
        training_barrier,
        policy_barrier,
        barrier_score
    FROM survey_responses
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Convert numeric columns explicitly
    numeric_cols = [
        'hardware_quality', 'software_availability', 'internet_speed', 'digital_collection',
        'infrastructure_score', 'overall_satisfaction', 'service_efficiency',
        'financial_barrier', 'technical_barrier', 'training_barrier', 'policy_barrier',
        'barrier_score'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df

def plot_infrastructure_assessment(df):
    """1. Infrastructure Assessment by College (Grouped Bar Chart)"""
    print("Generating: Infrastructure Assessment by College...")
    
    # Calculate averages by college
    metrics = ['hardware_quality', 'software_availability', 'internet_speed', 'digital_collection']
    college_avg = df.groupby('college')[metrics].mean()
    
    # Rename columns for better labels
    college_avg.columns = ['Hardware', 'Software', 'Internet', 'Digital']
    
    ax = college_avg.plot(kind='bar', figsize=(14, 8), width=0.8)
    plt.title('Infrastructure Assessment by College', fontsize=16, pad=20)
    plt.xlabel('College', fontsize=12)
    plt.ylabel('Average Score (1-5)', fontsize=12)
    plt.ylim(0, 5.5)
    plt.legend(title='Infrastructure Type', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/1_infrastructure_by_college.png", dpi=300, bbox_inches='tight')
    plt.close()

def plot_satisfaction_distribution(df):
    """2. Satisfaction Distribution (Histogram)"""
    print("Generating: Satisfaction Distribution...")
    
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='overall_satisfaction', bins=np.arange(1, 12) - 0.5, kde=True, color='#3b82f6')
    plt.title('Distribution of Overall Satisfaction Scores', fontsize=16, pad=20)
    plt.xlabel('Satisfaction Score (1-10)', fontsize=12)
    plt.ylabel('Count of Responses', fontsize=12)
    plt.xticks(range(1, 11))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/2_satisfaction_distribution.png", dpi=300)
    plt.close()

def plot_satisfaction_categories(df):
    """3. Satisfaction Categories (Pie Chart)"""
    print("Generating: Satisfaction Categories...")
    
    def categorize(score):
        if score <= 4: return 'Low (1-4)'
        elif score <= 7: return 'Medium (5-7)'
        else: return 'High (8-10)'
    
    categories = df['overall_satisfaction'].apply(categorize).value_counts()
    
    plt.figure(figsize=(10, 8))
    colors = {'Low (1-4)': '#ef4444', 'Medium (5-7)': '#f59e0b', 'High (8-10)': '#10b981'}
    
    # Ensure all categories exist in colors dict logic
    pie_colors = [colors.get(x, '#cccccc') for x in categories.index]
    
    plt.pie(categories, labels=categories.index, autopct='%1.1f%%', startangle=90, 
            colors=pie_colors, textprops={'fontsize': 12})
    plt.title('User Satisfaction Level Distribution', fontsize=16)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/3_satisfaction_categories_pie.png", dpi=300)
    plt.close()

def plot_barrier_assessment(df):
    """4. Barrier Assessment (Horizontal Bar Chart)"""
    print("Generating: Barrier Assessment...")
    
    barriers = ['financial_barrier', 'technical_barrier', 'training_barrier', 'policy_barrier']
    avg_scores = df[barriers].mean().sort_values(ascending=True)
    
    # Clean labels
    labels = [x.replace('_barrier', '').replace('_', ' ').title() for x in avg_scores.index]
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(labels, avg_scores.values, color='#ef4444')
    
    plt.title('Average Barrier Scores (Higher = More Significant)', fontsize=16, pad=20)
    plt.xlabel('Average Score (1-5)', fontsize=12)
    plt.xlim(0, 5.5)
    
    # Add value labels
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{width:.2f}', 
                 va='center', fontweight='bold')
        
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/4_barrier_assessment.png", dpi=300)
    plt.close()

def plot_correlation_matrix(df):
    """5. Feature Correlation Matrix"""
    print("Generating: Correlation Matrix...")
    
    cols = [
        'hardware_quality', 'software_availability', 'internet_speed', 'digital_collection',
        'overall_satisfaction', 'service_efficiency',
        'financial_barrier', 'technical_barrier', 'training_barrier', 'policy_barrier'
    ]
    labels = ['Hardware', 'Software', 'Internet', 'Digital', 'Satisfaction', 'Efficiency', 
              'Financial', 'Technical', 'Training', 'Policy']
    
    corr = df[cols].corr()
    
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1,
                xticklabels=labels, yticklabels=labels, square=True, linewidths=.5)
    
    plt.title('Feature Correlation Matrix', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/5_correlation_matrix.png", dpi=300)
    plt.close()

def plot_infrastructure_vs_satisfaction(df):
    """6. Infrastructure vs Satisfaction (Scatter Plot)"""
    print("Generating: Infrastructure vs Satisfaction Scatter...")
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='infrastructure_score', y='overall_satisfaction', 
                    alpha=0.6, s=100, color='#8884d8')
    
    # Add trend line
    sns.regplot(data=df, x='infrastructure_score', y='overall_satisfaction', 
                scatter=False, color='red', line_kws={'linestyle':'--'})
    
    plt.title('Correlation: Infrastructure Quality vs. User Satisfaction', fontsize=16, pad=20)
    plt.xlabel('Infrastructure Score (Composite)', fontsize=12)
    plt.ylabel('Overall Satisfaction Score', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/6_infra_vs_satisfaction.png", dpi=300)
    plt.close()

def plot_responses_by_college(df):
    """7. Responses per College (Simple Bar)"""
    print("Generating: Responses per College...")
    
    counts = df['college'].value_counts()
    
    plt.figure(figsize=(12, 6))
    counts.plot(kind='bar', color='#3b82f6')
    plt.title('Number of Survey Responses by College', fontsize=16, pad=20)
    plt.xlabel('College', fontsize=12)
    plt.ylabel('Number of Responses', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/7_responses_by_college.png", dpi=300)
    plt.close()

def generate_summary_table_image(df):
    """8. Summary Statistics Table as Image"""
    print("Generating: Summary Statistics Table...")
    
    stats_cols = [
        'infrastructure_score', 'overall_satisfaction', 'service_efficiency', 'barrier_score'
    ]
    friendly_names = {
        'infrastructure_score': 'Infrastructure',
        'overall_satisfaction': 'Satisfaction',
        'service_efficiency': 'Efficiency',
        'barrier_score': 'Barrier Impact'
    }
    
    stats = df[stats_cols].describe().round(2).T[['count', 'mean', 'std', 'min', 'max']]
    stats.index = [friendly_names.get(x, x) for x in stats.index]
    
    # Create plot just for the table
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    ax.table(cellText=stats.values, colLabels=stats.columns, rowLabels=stats.index, 
             loc='center', cellLoc='center', colColours=['#f3f4f6']*5)
    
    plt.title('Descriptive Statistics of Key Metrics', fontsize=16, y=0.9)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/8_summary_statistics_table.png", dpi=300, bbox_inches='tight')
    plt.close()

def main():
    ensure_dir(OUTPUT_DIR)
    
    try:
        print("Fetching data from database...")
        df = get_data()
        print(f"Loaded {len(df)} records.")
        
        if len(df) == 0:
            print("Warning: Database is empty! No plots will be generated.")
            return

        plot_infrastructure_assessment(df)
        plot_satisfaction_distribution(df)
        plot_satisfaction_categories(df)
        plot_barrier_assessment(df)
        plot_correlation_matrix(df)
        plot_infrastructure_vs_satisfaction(df)
        plot_responses_by_college(df)
        generate_summary_table_image(df)
        
        print(f"\nSuccess! All figures saved to: {os.path.abspath(OUTPUT_DIR)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
