#!/usr/bin/env python3
"""
Visualization Generator for SME Innovation Analysis
Creates comprehensive charts and graphs for the secondary dataset
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")

class SMEVisualizationGenerator:
    """Generate visualizations for SME innovation analysis"""
    
    def __init__(self, data_path='../'):
        self.data_path = data_path
        self.load_data()
        
    def load_data(self):
        """Load necessary datasets"""
        self.gdp = pd.read_csv(f'{self.data_path}/macroeconomic/gdp_growth_rate.csv')
        self.inflation = pd.read_csv(f'{self.data_path}/macroeconomic/inflation_rates.csv')
        self.interest = pd.read_csv(f'{self.data_path}/macroeconomic/interest_rates.csv')
        self.broadband = pd.read_csv(f'{self.data_path}/macroeconomic/broadband_penetration.csv')
        self.sme_landscape = pd.read_csv(f'{self.data_path}/industry_specific/sme_landscape_data.csv')
        self.sectoral = pd.read_csv(f'{self.data_path}/industry_specific/sectoral_growth_rates.csv')
        self.fintech = pd.read_csv(f'{self.data_path}/technology_adoption/mobile_money_fintech_adoption.csv')
        self.ict = pd.read_csv(f'{self.data_path}/technology_adoption/ict_development_index.csv')
        
    def create_innovation_timeline(self):
        """Create innovation adoption timeline"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('SME Innovation Adoption Timeline (2015-2024)', fontsize=16, fontweight='bold')
        
        # Tech adoption
        ax1 = axes[0, 0]
        sme_data = self.sme_landscape[self.sme_landscape['year'].notna()]
        ax1.plot(sme_data['year'], sme_data['tech_enabled_smes_percent'], marker='o', linewidth=2)
        ax1.set_title('Technology-Enabled SMEs')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Percentage (%)')
        ax1.grid(True, alpha=0.3)
        
        # Fintech adoption
        ax2 = axes[0, 1]
        ax2.plot(sme_data['year'], sme_data['fintech_adoption_rate'], marker='s', linewidth=2, color='green')
        ax2.plot(sme_data['year'], sme_data['e_commerce_participation'], marker='^', linewidth=2, color='orange')
        ax2.set_title('Fintech & E-commerce Adoption')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Percentage (%)')
        ax2.legend(['Fintech', 'E-commerce'])
        ax2.grid(True, alpha=0.3)
        
        # Digital payments
        ax3 = axes[1, 0]
        ax3.plot(sme_data['year'], sme_data['digital_payment_usage'], marker='d', linewidth=2, color='purple')
        ax3.set_title('Digital Payment Usage')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Percentage (%)')
        ax3.grid(True, alpha=0.3)
        
        # Cloud computing
        ax4 = axes[1, 1]
        ax4.plot(sme_data['year'], sme_data['cloud_computing_adoption'], marker='*', linewidth=2, color='red')
        ax4.set_title('Cloud Computing Adoption')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Percentage (%)')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('innovation_timeline.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_constraint_heatmap(self):
        """Create heatmap of innovation constraints"""
        # Prepare constraint data
        constraints_data = {
            'Finance Access': [68.5, 67.2, 65.8, 64.3, 62.7, 65.8, 61.5, 58.9, 56.2, 53.8],
            'Infrastructure': [72.3, 70.8, 69.2, 67.5, 65.8, 68.5, 64.2, 61.7, 59.1, 56.5],
            'Digital Skills': [78.6, 76.9, 75.1, 73.2, 71.3, 73.8, 69.5, 66.8, 64.0, 61.2],
            'Regulation': [65.4, 64.1, 62.7, 61.3, 59.8, 61.2, 58.5, 56.2, 53.8, 51.4],
            'Market Access': [58.7, 57.5, 56.2, 54.9, 53.6, 55.8, 52.3, 50.2, 48.0, 45.8]
        }
        
        years = list(range(2015, 2025))
        df = pd.DataFrame(constraints_data, index=years).T
        
        plt.figure(figsize=(12, 6))
        sns.heatmap(df, annot=True, fmt='.1f', cmap='YlOrRd', cbar_kws={'label': 'Severity (%)'})
        plt.title('Innovation Constraints Heatmap (2015-2024)', fontsize=14, fontweight='bold')
        plt.xlabel('Year')
        plt.ylabel('Constraint Type')
        plt.tight_layout()
        plt.savefig('constraints_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_sectoral_comparison(self):
        """Create sectoral innovation comparison"""
        sectors = ['Manufacturing', 'Services', 'Agriculture', 'Trade', 'Construction']
        innovation_index = [4.5, 5.5, 3.2, 5.1, 3.5]
        digitalization_rate = [35.7, 45.6, 11.2, 38.5, 22.3]
        sme_contribution = [42.6, 58.9, 65.3, 72.8, 61.5]
        
        x = np.arange(len(sectors))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        bars1 = ax.bar(x - width, innovation_index, width, label='Innovation Index (0-10)')
        bars2 = ax.bar(x, [d/10 for d in digitalization_rate], width, label='Digitalization Rate (/10)')
        bars3 = ax.bar(x + width, [s/10 for s in sme_contribution], width, label='SME Contribution (/10)')
        
        ax.set_xlabel('Sector', fontweight='bold')
        ax.set_ylabel('Score', fontweight='bold')
        ax.set_title('Sectoral Innovation Performance Comparison (2024)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(sectors)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        plt.savefig('sectoral_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_regional_digital_map(self):
        """Create regional digital divide visualization"""
        regions = ['South West', 'South East', 'South South', 'North Central', 'North West', 'North East']
        broadband_2024 = [65.8, 48.9, 51.2, 35.6, 28.4, 22.5]
        urban = [82.3, 78.6, 74.2, 71.8, 68.5, 64.7]
        rural = [48.5, 38.2, 35.8, 28.6, 18.5, 12.3]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Regional broadband comparison
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(regions)))
        bars = ax1.barh(regions, broadband_2024, color=colors)
        ax1.set_xlabel('Broadband Penetration (%)', fontweight='bold')
        ax1.set_title('Regional Broadband Penetration (2024)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for bar, value in zip(bars, broadband_2024):
            ax1.text(value + 1, bar.get_y() + bar.get_height()/2, f'{value:.1f}%', 
                    va='center', fontsize=9)
        
        # Urban-Rural gap
        x = np.arange(len(regions))
        width = 0.35
        
        bars1 = ax2.bar(x - width/2, urban, width, label='Urban', color='steelblue')
        bars2 = ax2.bar(x + width/2, rural, width, label='Rural', color='coral')
        
        ax2.set_ylabel('Penetration Rate (%)', fontweight='bold')
        ax2.set_title('Urban vs Rural Digital Divide (2024)', fontsize=12, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(regions, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig('regional_digital_divide.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_financial_inclusion_dashboard(self):
        """Create financial inclusion dashboard"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Financial inclusion rate over time
        ax1 = fig.add_subplot(gs[0, :2])
        fintech_yearly = self.fintech.groupby(pd.to_datetime(self.fintech['year'].astype(str) + '-' + self.fintech['month'], format='%Y-%b').dt.year).agg({
            'financial_inclusion_rate': 'mean'
        })
        ax1.plot(fintech_yearly.index, fintech_yearly['financial_inclusion_rate'], 
                marker='o', linewidth=2, markersize=8, color='darkgreen')
        ax1.set_title('Financial Inclusion Rate Progress', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Inclusion Rate (%)')
        ax1.grid(True, alpha=0.3)
        ax1.fill_between(fintech_yearly.index, fintech_yearly['financial_inclusion_rate'], 
                        alpha=0.3, color='lightgreen')
        
        # Mobile money growth
        ax2 = fig.add_subplot(gs[0, 2])
        latest_fintech = self.fintech.iloc[-1]
        categories = ['Accounts', 'Agents', 'Wallets']
        values = [
            latest_fintech['mobile_money_accounts_millions'],
            latest_fintech['mobile_money_agents_thousands']/10,
            latest_fintech['digital_wallet_users_millions']
        ]
        ax2.bar(categories, values, color=['blue', 'orange', 'green'])
        ax2.set_title('Mobile Money Ecosystem (2024)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Scale (Millions/10K)')
        
        # Payment channels distribution
        ax3 = fig.add_subplot(gs[1, 0])
        channels = ['USSD', 'Mobile App', 'Web', 'POS', 'ATM']
        percentages = [38.5, 28.7, 15.2, 12.8, 4.8]
        colors_pie = plt.cm.Set3(np.linspace(0, 1, len(channels)))
        ax3.pie(percentages, labels=channels, autopct='%1.1f%%', colors=colors_pie)
        ax3.set_title('Digital Payment Channels (2024)', fontsize=12, fontweight='bold')
        
        # SME financing sources
        ax4 = fig.add_subplot(gs[1, 1:])
        sources = ['Personal\nSavings', 'Family &\nFriends', 'Bank\nLoans', 'Microfinance', 
                  'Govt\nGrants', 'VC/Angel', 'Crowdfunding']
        percentages = [61.8, 41.0, 25.2, 38.3, 7.3, 6.5, 2.6]
        bars = ax4.bar(sources, percentages, color='teal')
        ax4.set_title('SME Financing Sources (2024)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('% of SMEs Using')
        ax4.set_ylim(0, 70)
        
        # Add value labels
        for bar, value in zip(bars, percentages):
            ax4.text(bar.get_x() + bar.get_width()/2, value + 1, f'{value:.1f}%',
                    ha='center', va='bottom', fontsize=8)
        
        # Fintech companies growth
        ax5 = fig.add_subplot(gs[2, :])
        fintech_companies = self.fintech[['year', 'month', 'fintech_companies']].copy()
        fintech_companies['date'] = pd.to_datetime(fintech_companies['year'].astype(str) + '-' + fintech_companies['month'], format='%Y-%b')
        ax5.plot(fintech_companies['date'], fintech_companies['fintech_companies'], 
                linewidth=2, color='purple')
        ax5.set_title('Growth of Fintech Companies in Nigeria', fontsize=12, fontweight='bold')
        ax5.set_xlabel('Year')
        ax5.set_ylabel('Number of Companies')
        ax5.grid(True, alpha=0.3)
        ax5.fill_between(fintech_companies['date'], fintech_companies['fintech_companies'],
                        alpha=0.3, color='lavender')
        
        plt.suptitle('Financial Inclusion & Fintech Dashboard', fontsize=16, fontweight='bold', y=0.98)
        plt.tight_layout()
        plt.savefig('financial_inclusion_dashboard.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_innovation_correlation_matrix(self):
        """Create correlation matrix for innovation variables"""
        # Select key variables
        sme_data = self.sme_landscape[self.sme_landscape['year'].notna()]
        
        variables = [
            'tech_enabled_smes_percent',
            'fintech_adoption_rate',
            'e_commerce_participation',
            'digital_payment_usage',
            'cloud_computing_adoption',
            'social_media_marketing',
            'sme_gdp_contribution_percent',
            'formal_sector_percent'
        ]
        
        corr_data = sme_data[variables].corr()
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        mask = np.triu(np.ones_like(corr_data, dtype=bool))
        sns.heatmap(corr_data, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1,
                   cbar_kws={"shrink": 0.8, "label": "Correlation"})
        
        plt.title('Innovation Variables Correlation Matrix', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('innovation_correlation_matrix.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_macroeconomic_trends(self):
        """Create macroeconomic trends visualization"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Macroeconomic Environment for SME Innovation', fontsize=16, fontweight='bold')
        
        # GDP Growth
        ax1 = axes[0, 0]
        gdp_data = self.gdp[['year', 'quarter', 'gdp_growth_rate', 'sme_contribution_percent']].copy()
        gdp_data['period'] = gdp_data['year'].astype(str) + '-' + gdp_data['quarter']
        ax1.plot(range(len(gdp_data)), gdp_data['gdp_growth_rate'], label='GDP Growth', linewidth=2)
        ax1_twin = ax1.twinx()
        ax1_twin.plot(range(len(gdp_data)), gdp_data['sme_contribution_percent'], 
                     color='orange', label='SME Contribution', linewidth=2, linestyle='--')
        ax1.set_title('GDP Growth & SME Contribution')
        ax1.set_xlabel('Quarter')
        ax1.set_ylabel('GDP Growth Rate (%)')
        ax1_twin.set_ylabel('SME Contribution (%)', color='orange')
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        ax1_twin.legend(loc='upper right')
        
        # Inflation Trend
        ax2 = axes[0, 1]
        inflation_monthly = self.inflation[['year', 'month', 'headline_inflation']].copy()
        inflation_monthly['date'] = pd.to_datetime(inflation_monthly['year'].astype(str) + '-' + inflation_monthly['month'], format='%Y-%b')
        ax2.plot(inflation_monthly['date'], inflation_monthly['headline_inflation'], 
                color='red', linewidth=2)
        ax2.set_title('Inflation Rate Trend')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Inflation Rate (%)')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=15, color='gray', linestyle='--', alpha=0.5, label='15% threshold')
        ax2.legend()
        
        # Interest Rates
        ax3 = axes[1, 0]
        interest_data = self.interest[['year', 'month', 'monetary_policy_rate', 'sme_lending_rate_average']].copy()
        interest_data['date'] = pd.to_datetime(interest_data['year'].astype(str) + '-' + interest_data['month'], format='%Y-%b')
        ax3.plot(interest_data['date'], interest_data['monetary_policy_rate'], 
                label='MPR', linewidth=2, color='darkblue')
        ax3.plot(interest_data['date'], interest_data['sme_lending_rate_average'], 
                label='SME Lending Rate', linewidth=2, color='darkred')
        ax3.set_title('Interest Rates')
        ax3.set_xlabel('Year')
        ax3.set_ylabel('Rate (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # ICT Development
        ax4 = axes[1, 1]
        ict_data = self.ict[['year', 'ict_development_index', 'internet_users_percent']].copy()
        ax4.bar(ict_data['year'], ict_data['internet_users_percent'], alpha=0.6, label='Internet Users %')
        ax4_twin = ax4.twinx()
        ax4_twin.plot(ict_data['year'], ict_data['ict_development_index'], 
                     color='green', marker='o', linewidth=2, label='ICT Index')
        ax4.set_title('ICT Development Progress')
        ax4.set_xlabel('Year')
        ax4.set_ylabel('Internet Users (%)')
        ax4_twin.set_ylabel('ICT Development Index', color='green')
        ax4.legend(loc='upper left')
        ax4_twin.legend(loc='upper right')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('macroeconomic_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def create_innovation_forecast(self):
        """Create innovation adoption forecast"""
        # Historical data
        sme_data = self.sme_landscape[self.sme_landscape['year'].notna()].copy()
        
        # Simple projection for 2025-2027
        last_year = 2024
        last_value = sme_data.iloc[-1]['tech_enabled_smes_percent']
        growth_rate = 0.08  # 8% annual growth
        
        forecast_years = [2025, 2026, 2027]
        forecast_values = [last_value * (1 + growth_rate) ** (i+1) for i in range(3)]
        
        plt.figure(figsize=(12, 6))
        
        # Historical
        plt.plot(sme_data['year'], sme_data['tech_enabled_smes_percent'], 
                marker='o', linewidth=2, label='Historical', color='blue')
        
        # Forecast
        plt.plot(forecast_years, forecast_values, 
                marker='s', linewidth=2, linestyle='--', label='Forecast', color='red')
        
        # Confidence interval
        upper_bound = [v * 1.1 for v in forecast_values]
        lower_bound = [v * 0.9 for v in forecast_values]
        plt.fill_between(forecast_years, lower_bound, upper_bound, alpha=0.3, color='red')
        
        plt.title('SME Technology Adoption: Historical Trend and Forecast', fontsize=14, fontweight='bold')
        plt.xlabel('Year')
        plt.ylabel('Technology-Enabled SMEs (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlim(2014, 2028)
        plt.ylim(0, 100)
        
        # Add annotations
        plt.annotate(f'2024: {last_value:.1f}%', xy=(2024, last_value), 
                    xytext=(2024, last_value-10), fontsize=9,
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
        plt.annotate(f'2027 (projected): {forecast_values[-1]:.1f}%', 
                    xy=(2027, forecast_values[-1]), 
                    xytext=(2026, forecast_values[-1]+5), fontsize=9,
                    arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig('innovation_forecast.png', dpi=300, bbox_inches='tight')
        plt.show()
        
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("Generating SME Innovation Visualizations...")
        
        print("1. Creating Innovation Timeline...")
        self.create_innovation_timeline()
        
        print("2. Creating Constraints Heatmap...")
        self.create_constraint_heatmap()
        
        print("3. Creating Sectoral Comparison...")
        self.create_sectoral_comparison()
        
        print("4. Creating Regional Digital Map...")
        self.create_regional_digital_map()
        
        print("5. Creating Financial Inclusion Dashboard...")
        self.create_financial_inclusion_dashboard()
        
        print("6. Creating Innovation Correlation Matrix...")
        self.create_innovation_correlation_matrix()
        
        print("7. Creating Macroeconomic Trends...")
        self.create_macroeconomic_trends()
        
        print("8. Creating Innovation Forecast...")
        self.create_innovation_forecast()
        
        print("\nAll visualizations generated successfully!")
        print("Files saved in current directory.")

def main():
    """Main execution"""
    generator = SMEVisualizationGenerator()
    generator.generate_all_visualizations()

if __name__ == "__main__":
    main()