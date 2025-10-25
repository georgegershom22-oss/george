#!/usr/bin/env python3
"""
Data Analysis and Visualization Module
Comprehensive analysis tools for the generated dataset
"""

import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class DataAnalyzer:
    """Comprehensive data analysis and visualization tools."""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path
        self.data = None
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load dataset from multiple formats."""
        print("Loading dataset...")
        
        # Load HDF5 data
        with h5py.File(f"{self.dataset_path}/training_data.h5", 'r') as f:
            self.data = {
                'states': f['states'][:],
                'actions': f['actions'][:],
                'rewards': f['rewards'][:],
                'timestamps': f['timestamps'][:],
                'episodes': f['episodes'][:],
                'timesteps': f['timesteps'][:]
            }
        
        # Load detailed CSV data
        self.df = pd.read_csv(f"{self.dataset_path}/detailed_data.csv")
        
        print(f"Loaded {len(self.df)} timesteps from {len(np.unique(self.data['episodes']))} episodes")
    
    def analyze_reward_distribution(self, save_plots=True):
        """Analyze reward distribution and components."""
        print("Analyzing reward distribution...")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Overall reward distribution
        axes[0, 0].hist(self.df['reward'], bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Reward Distribution')
        axes[0, 0].set_xlabel('Reward')
        axes[0, 0].set_ylabel('Frequency')
        
        # Reward over time
        axes[0, 1].plot(self.df['timestamp'], self.df['reward'], alpha=0.7)
        axes[0, 1].set_title('Reward Over Time')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Reward')
        
        # Reward components
        reward_components = [col for col in self.df.columns if 'reward' in col.lower() and col != 'reward']
        if reward_components:
            for component in reward_components:
                axes[1, 0].plot(self.df['timestamp'], self.df[component], 
                               label=component, alpha=0.7)
            axes[1, 0].set_title('Reward Components Over Time')
            axes[1, 0].set_xlabel('Time (s)')
            axes[1, 0].set_ylabel('Reward Component Value')
            axes[1, 0].legend()
        
        # Reward by episode
        episode_rewards = self.df.groupby('episode')['reward'].mean()
        axes[1, 1].bar(range(len(episode_rewards)), episode_rewards)
        axes[1, 1].set_title('Average Reward by Episode')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Average Reward')
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_path}/reward_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Statistical analysis
        reward_stats = {
            'mean': np.mean(self.df['reward']),
            'std': np.std(self.df['reward']),
            'min': np.min(self.df['reward']),
            'max': np.max(self.df['reward']),
            'median': np.median(self.df['reward']),
            'skewness': stats.skew(self.df['reward']),
            'kurtosis': stats.kurtosis(self.df['reward'])
        }
        
        print("Reward Statistics:")
        for key, value in reward_stats.items():
            print(f"  {key}: {value:.4f}")
        
        return reward_stats
    
    def analyze_state_space(self, save_plots=True):
        """Analyze state space distribution and clustering."""
        print("Analyzing state space...")
        
        states = self.data['states']
        
        # PCA analysis
        pca = PCA(n_components=min(10, states.shape[1]))
        states_pca = pca.fit_transform(states)
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # PCA explained variance
        axes[0, 0].bar(range(len(pca.explained_variance_ratio_)), 
                      pca.explained_variance_ratio_)
        axes[0, 0].set_title('PCA Explained Variance Ratio')
        axes[0, 0].set_xlabel('Principal Component')
        axes[0, 0].set_ylabel('Explained Variance Ratio')
        
        # First two principal components
        scatter = axes[0, 1].scatter(states_pca[:, 0], states_pca[:, 1], 
                                   c=self.data['rewards'], cmap='viridis', alpha=0.6)
        axes[0, 1].set_title('State Space (First 2 PCs)')
        axes[0, 1].set_xlabel('PC1')
        axes[0, 1].set_ylabel('PC2')
        plt.colorbar(scatter, ax=axes[0, 1], label='Reward')
        
        # State distribution
        axes[0, 2].hist(states.flatten(), bins=50, alpha=0.7, edgecolor='black')
        axes[0, 2].set_title('State Value Distribution')
        axes[0, 2].set_xlabel('State Value')
        axes[0, 2].set_ylabel('Frequency')
        
        # State correlation matrix
        state_corr = np.corrcoef(states.T)
        im = axes[1, 0].imshow(state_corr, cmap='coolwarm', vmin=-1, vmax=1)
        axes[1, 0].set_title('State Correlation Matrix')
        plt.colorbar(im, ax=axes[1, 0])
        
        # State variance by dimension
        state_var = np.var(states, axis=0)
        axes[1, 1].bar(range(len(state_var)), state_var)
        axes[1, 1].set_title('State Variance by Dimension')
        axes[1, 1].set_xlabel('State Dimension')
        axes[1, 1].set_ylabel('Variance')
        
        # Clustering analysis
        kmeans = KMeans(n_clusters=5, random_state=42)
        clusters = kmeans.fit_predict(states)
        
        scatter = axes[1, 2].scatter(states_pca[:, 0], states_pca[:, 1], 
                                   c=clusters, cmap='tab10', alpha=0.6)
        axes[1, 2].set_title('State Clustering (K-means)')
        axes[1, 2].set_xlabel('PC1')
        axes[1, 2].set_ylabel('PC2')
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_path}/state_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # State space statistics
        state_stats = {
            'dimension': states.shape[1],
            'mean_variance': np.mean(state_var),
            'max_variance': np.max(state_var),
            'min_variance': np.min(state_var),
            'pca_explained_variance': pca.explained_variance_ratio_[:5].tolist(),
            'clustering_silhouette': self._calculate_silhouette_score(states, clusters)
        }
        
        print("State Space Statistics:")
        for key, value in state_stats.items():
            print(f"  {key}: {value}")
        
        return state_stats
    
    def analyze_action_space(self, save_plots=True):
        """Analyze action space distribution and patterns."""
        print("Analyzing action space...")
        
        actions = self.data['actions']
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Action distribution
        axes[0, 0].hist(actions.flatten(), bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Action Distribution')
        axes[0, 0].set_xlabel('Action Value')
        axes[0, 0].set_ylabel('Frequency')
        
        # Action over time
        for i in range(actions.shape[1]):
            axes[0, 1].plot(self.data['timestamps'], actions[:, i], 
                           label=f'Action {i+1}', alpha=0.7)
        axes[0, 1].set_title('Actions Over Time')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Action Value')
        axes[0, 1].legend()
        
        # Action correlation
        action_corr = np.corrcoef(actions.T)
        im = axes[1, 0].imshow(action_corr, cmap='coolwarm', vmin=-1, vmax=1)
        axes[1, 0].set_title('Action Correlation Matrix')
        plt.colorbar(im, ax=axes[1, 0])
        
        # Action variance by dimension
        action_var = np.var(actions, axis=0)
        axes[1, 1].bar(range(len(action_var)), action_var)
        axes[1, 1].set_title('Action Variance by Dimension')
        axes[1, 1].set_xlabel('Action Dimension')
        axes[1, 1].set_ylabel('Variance')
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_path}/action_analysis.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Action space statistics
        action_stats = {
            'dimension': actions.shape[1],
            'mean': np.mean(actions),
            'std': np.std(actions),
            'min': np.min(actions),
            'max': np.max(actions),
            'mean_variance': np.mean(action_var),
            'action_correlation': action_corr.tolist()
        }
        
        print("Action Space Statistics:")
        for key, value in action_stats.items():
            print(f"  {key}: {value}")
        
        return action_stats
    
    def analyze_episode_progression(self, save_plots=True):
        """Analyze how episodes progress and improve over time."""
        print("Analyzing episode progression...")
        
        # Group by episode
        episode_data = self.df.groupby('episode').agg({
            'reward': ['mean', 'std', 'min', 'max'],
            'max_temperature': ['mean', 'max'],
            'max_von_mises_strain': ['mean', 'max'],
            'estimated_density': ['mean', 'max']
        }).reset_index()
        
        # Flatten column names
        episode_data.columns = ['episode'] + [f"{col[0]}_{col[1]}" for col in episode_data.columns[1:]]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Reward progression
        axes[0, 0].plot(episode_data['episode'], episode_data['reward_mean'], 'b-', label='Mean')
        axes[0, 0].fill_between(episode_data['episode'], 
                               episode_data['reward_mean'] - episode_data['reward_std'],
                               episode_data['reward_mean'] + episode_data['reward_std'],
                               alpha=0.3, label='±1σ')
        axes[0, 0].set_title('Reward Progression by Episode')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Reward')
        axes[0, 0].legend()
        
        # Temperature progression
        axes[0, 1].plot(episode_data['episode'], episode_data['max_temperature_mean'], 'r-')
        axes[0, 1].set_title('Temperature Progression by Episode')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Max Temperature (°C)')
        
        # Strain progression
        axes[0, 2].plot(episode_data['episode'], episode_data['max_von_mises_strain_mean'], 'g-')
        axes[0, 2].set_title('Strain Progression by Episode')
        axes[0, 2].set_xlabel('Episode')
        axes[0, 2].set_ylabel('Max Von Mises Strain')
        
        # Density progression
        axes[1, 0].plot(episode_data['episode'], episode_data['estimated_density_mean'], 'm-')
        axes[1, 0].set_title('Density Progression by Episode')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Estimated Density')
        
        # Learning curve (moving average)
        window_size = max(5, len(episode_data) // 10)
        reward_ma = episode_data['reward_mean'].rolling(window=window_size).mean()
        axes[1, 1].plot(episode_data['episode'], reward_ma, 'b-', linewidth=2)
        axes[1, 1].set_title(f'Learning Curve (Moving Average, window={window_size})')
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Moving Average Reward')
        
        # Episode length distribution
        episode_lengths = self.df.groupby('episode').size()
        axes[1, 2].hist(episode_lengths, bins=20, alpha=0.7, edgecolor='black')
        axes[1, 2].set_title('Episode Length Distribution')
        axes[1, 2].set_xlabel('Episode Length (timesteps)')
        axes[1, 2].set_ylabel('Frequency')
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_path}/episode_progression.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Episode statistics
        episode_stats = {
            'num_episodes': len(episode_data),
            'mean_episode_length': np.mean(episode_lengths),
            'std_episode_length': np.std(episode_lengths),
            'reward_improvement': episode_data['reward_mean'].iloc[-1] - episode_data['reward_mean'].iloc[0],
            'final_reward': episode_data['reward_mean'].iloc[-1],
            'best_reward': np.max(episode_data['reward_mean'])
        }
        
        print("Episode Progression Statistics:")
        for key, value in episode_stats.items():
            print(f"  {key}: {value}")
        
        return episode_stats
    
    def analyze_physical_relationships(self, save_plots=True):
        """Analyze relationships between physical variables."""
        print("Analyzing physical relationships...")
        
        # Select relevant columns
        physical_cols = ['max_temperature', 'max_von_mises_strain', 'estimated_density', 
                        'strain_heterogeneity', 'max_displacement', 'reward']
        
        # Filter to existing columns
        available_cols = [col for col in physical_cols if col in self.df.columns]
        physical_data = self.df[available_cols]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        
        # Temperature vs Strain
        if 'max_temperature' in available_cols and 'max_von_mises_strain' in available_cols:
            scatter = axes[0, 0].scatter(physical_data['max_temperature'], 
                                       physical_data['max_von_mises_strain'],
                                       c=physical_data['reward'], cmap='viridis', alpha=0.6)
            axes[0, 0].set_title('Temperature vs Strain')
            axes[0, 0].set_xlabel('Max Temperature (°C)')
            axes[0, 0].set_ylabel('Max Von Mises Strain')
            plt.colorbar(scatter, ax=axes[0, 0], label='Reward')
        
        # Temperature vs Density
        if 'max_temperature' in available_cols and 'estimated_density' in available_cols:
            scatter = axes[0, 1].scatter(physical_data['max_temperature'], 
                                       physical_data['estimated_density'],
                                       c=physical_data['reward'], cmap='viridis', alpha=0.6)
            axes[0, 1].set_title('Temperature vs Density')
            axes[0, 1].set_xlabel('Max Temperature (°C)')
            axes[0, 1].set_ylabel('Estimated Density')
            plt.colorbar(scatter, ax=axes[0, 1], label='Reward')
        
        # Strain vs Density
        if 'max_von_mises_strain' in available_cols and 'estimated_density' in available_cols:
            scatter = axes[0, 2].scatter(physical_data['max_von_mises_strain'], 
                                       physical_data['estimated_density'],
                                       c=physical_data['reward'], cmap='viridis', alpha=0.6)
            axes[0, 2].set_title('Strain vs Density')
            axes[0, 2].set_xlabel('Max Von Mises Strain')
            axes[0, 2].set_ylabel('Estimated Density')
            plt.colorbar(scatter, ax=axes[0, 2], label='Reward')
        
        # Correlation heatmap
        corr_matrix = physical_data.corr()
        im = axes[1, 0].imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        axes[1, 0].set_title('Physical Variables Correlation')
        axes[1, 0].set_xticks(range(len(corr_matrix.columns)))
        axes[1, 0].set_yticks(range(len(corr_matrix.columns)))
        axes[1, 0].set_xticklabels(corr_matrix.columns, rotation=45)
        axes[1, 0].set_yticklabels(corr_matrix.columns)
        plt.colorbar(im, ax=axes[1, 0])
        
        # Reward vs Physical variables
        if 'reward' in available_cols:
            reward_corr = corr_matrix['reward'].drop('reward')
            axes[1, 1].bar(range(len(reward_corr)), reward_corr.values)
            axes[1, 1].set_title('Reward Correlation with Physical Variables')
            axes[1, 1].set_xlabel('Physical Variable')
            axes[1, 1].set_ylabel('Correlation with Reward')
            axes[1, 1].set_xticks(range(len(reward_corr)))
            axes[1, 1].set_xticklabels(reward_corr.index, rotation=45)
        
        # Time series of key variables
        if 'max_temperature' in available_cols:
            axes[1, 2].plot(self.df['timestamp'], self.df['max_temperature'], 'r-', alpha=0.7, label='Temperature')
            if 'max_von_mises_strain' in available_cols:
                ax2 = axes[1, 2].twinx()
                ax2.plot(self.df['timestamp'], self.df['max_von_mises_strain'], 'b-', alpha=0.7, label='Strain')
                ax2.set_ylabel('Max Von Mises Strain')
            axes[1, 2].set_title('Key Variables Over Time')
            axes[1, 2].set_xlabel('Time (s)')
            axes[1, 2].set_ylabel('Max Temperature (°C)')
            axes[1, 2].legend()
        
        plt.tight_layout()
        if save_plots:
            plt.savefig(f"{self.dataset_path}/physical_relationships.png", dpi=300, bbox_inches='tight')
        plt.show()
        
        # Physical relationship statistics
        physical_stats = {
            'correlation_matrix': corr_matrix.to_dict(),
            'reward_correlations': reward_corr.to_dict() if 'reward' in available_cols else {},
            'temperature_strain_correlation': corr_matrix.loc['max_temperature', 'max_von_mises_strain'] if 'max_temperature' in available_cols and 'max_von_mises_strain' in available_cols else None
        }
        
        print("Physical Relationship Statistics:")
        for key, value in physical_stats.items():
            if key != 'correlation_matrix':
                print(f"  {key}: {value}")
        
        return physical_stats
    
    def _calculate_silhouette_score(self, data, clusters):
        """Calculate silhouette score for clustering."""
        try:
            from sklearn.metrics import silhouette_score
            return silhouette_score(data, clusters)
        except:
            return 0.0
    
    def generate_comprehensive_report(self, output_path: str = "comprehensive_analysis_report.html"):
        """Generate comprehensive analysis report."""
        print("Generating comprehensive analysis report...")
        
        # Run all analyses
        reward_stats = self.analyze_reward_distribution(save_plots=True)
        state_stats = self.analyze_state_space(save_plots=True)
        action_stats = self.analyze_action_space(save_plots=True)
        episode_stats = self.analyze_episode_progression(save_plots=True)
        physical_stats = self.analyze_physical_relationships(save_plots=True)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Comprehensive Dataset Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .statistics {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .plot {{ text-align: center; margin: 20px 0; }}
                .plot img {{ max-width: 100%; height: auto; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Comprehensive Dataset Analysis Report</h1>
                <p>Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Dataset: {self.dataset_path}</p>
            </div>
            
            <div class="section">
                <h2>Reward Analysis</h2>
                <div class="plot">
                    <img src="reward_analysis.png" alt="Reward Analysis">
                </div>
                <h3>Statistics:</h3>
        """
        
        for key, value in reward_stats.items():
            html_content += f'<div class="statistics"><strong>{key}:</strong> {value:.4f}</div>'
        
        html_content += """
            </div>
            
            <div class="section">
                <h2>State Space Analysis</h2>
                <div class="plot">
                    <img src="state_analysis.png" alt="State Space Analysis">
                </div>
                <h3>Statistics:</h3>
        """
        
        for key, value in state_stats.items():
            if isinstance(value, list):
                html_content += f'<div class="statistics"><strong>{key}:</strong> {value}</div>'
            else:
                html_content += f'<div class="statistics"><strong>{key}:</strong> {value:.4f}</div>'
        
        html_content += """
            </div>
            
            <div class="section">
                <h2>Action Space Analysis</h2>
                <div class="plot">
                    <img src="action_analysis.png" alt="Action Space Analysis">
                </div>
                <h3>Statistics:</h3>
        """
        
        for key, value in action_stats.items():
            if isinstance(value, list):
                html_content += f'<div class="statistics"><strong>{key}:</strong> {value}</div>'
            else:
                html_content += f'<div class="statistics"><strong>{key}:</strong> {value:.4f}</div>'
        
        html_content += """
            </div>
            
            <div class="section">
                <h2>Episode Progression Analysis</h2>
                <div class="plot">
                    <img src="episode_progression.png" alt="Episode Progression Analysis">
                </div>
                <h3>Statistics:</h3>
        """
        
        for key, value in episode_stats.items():
            html_content += f'<div class="statistics"><strong>{key}:</strong> {value:.4f}</div>'
        
        html_content += """
            </div>
            
            <div class="section">
                <h2>Physical Relationships Analysis</h2>
                <div class="plot">
                    <img src="physical_relationships.png" alt="Physical Relationships Analysis">
                </div>
                <h3>Statistics:</h3>
        """
        
        for key, value in physical_stats.items():
            if key != 'correlation_matrix':
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        html_content += f'<div class="statistics"><strong>{key}_{subkey}:</strong> {subvalue:.4f}</div>'
                else:
                    html_content += f'<div class="statistics"><strong>{key}:</strong> {value:.4f}</div>'
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Comprehensive analysis report saved to: {output_path}")

def main():
    """Test the data analyzer."""
    dataset_path = "real_time_training_dataset"
    
    if os.path.exists(dataset_path):
        analyzer = DataAnalyzer(dataset_path)
        analyzer.generate_comprehensive_report()
    else:
        print("No dataset found for analysis. Please generate dataset first.")

if __name__ == "__main__":
    main()