"""
Visualization tools for SOFC simulation results.
Creates plots, 3D visualizations, and analysis charts.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pyvista as pv
import h5py
import yaml
import os
from typing import Dict, List, Tuple, Optional, Any, Union
import warnings
warnings.filterwarnings('ignore')


class SOFCVisualizer:
    """
    Visualization tools for SOFC simulation data analysis.
    """
    
    def __init__(self, dataset_dir: str):
        """
        Initialize visualizer with dataset directory.
        
        Args:
            dataset_dir: Path to dataset directory
        """
        self.dataset_dir = dataset_dir
        
        # Load dataset metadata
        metadata_file = os.path.join(dataset_dir, 'dataset_metadata.yaml')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                self.metadata = yaml.safe_load(f)
        else:
            self.metadata = {}
        
        # Load parameter and metric summaries
        self.parameter_df = self._load_parameter_summary()
        self.metric_df = self._load_metric_summary()
        
        # Setup plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def _load_parameter_summary(self) -> Optional[pd.DataFrame]:
        """Load parameter summary CSV."""
        param_file = os.path.join(self.dataset_dir, 'parameter_summary.csv')
        if os.path.exists(param_file):
            return pd.read_csv(param_file)
        return None
        
    def _load_metric_summary(self) -> Optional[pd.DataFrame]:
        """Load metric summary CSV."""
        metric_file = os.path.join(self.dataset_dir, 'metric_summary.csv')
        if os.path.exists(metric_file):
            return pd.read_csv(metric_file)
        return None
        
    def plot_parameter_distributions(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot distributions of all input parameters.
        
        Args:
            save_path: Path to save the plot
            
        Returns:
            Matplotlib figure
        """
        
        if self.parameter_df is None:
            raise ValueError("Parameter data not available")
        
        # Exclude sample_id column
        param_cols = [col for col in self.parameter_df.columns if col != 'sample_id']
        n_params = len(param_cols)
        
        # Calculate subplot grid
        n_cols = 4
        n_rows = (n_params + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4*n_rows))
        axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else []
        
        for i, param in enumerate(param_cols):
            if i < len(axes):
                ax = axes[i]
                
                # Plot histogram with KDE
                self.parameter_df[param].hist(bins=20, alpha=0.7, ax=ax, density=True)
                
                # Add KDE curve
                try:
                    self.parameter_df[param].plot.kde(ax=ax, color='red', linewidth=2)
                except:
                    pass  # Skip KDE if it fails
                
                ax.set_title(f'{param}', fontsize=12)
                ax.set_xlabel('Value')
                ax.set_ylabel('Density')
                ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for i in range(n_params, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    def plot_parameter_correlations(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot correlation matrix of input parameters.
        
        Args:
            save_path: Path to save the plot
            
        Returns:
            Matplotlib figure
        """
        
        if self.parameter_df is None:
            raise ValueError("Parameter data not available")
        
        # Exclude sample_id column
        param_cols = [col for col in self.parameter_df.columns if col != 'sample_id']
        param_data = self.parameter_df[param_cols]
        
        # Calculate correlation matrix
        corr_matrix = param_data.corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, fmt='.2f', cbar_kws={"shrink": .8}, ax=ax)
        
        ax.set_title('Parameter Correlation Matrix', fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    def plot_performance_metrics(self, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot distributions of performance metrics.
        
        Args:
            save_path: Path to save the plot
            
        Returns:
            Matplotlib figure
        """
        
        if self.metric_df is None:
            raise ValueError("Metric data not available")
        
        # Key performance metrics to plot
        key_metrics = [
            'electrochemical_average_current_density',
            'electrochemical_power_density',
            'thermal_average_temperature',
            'mechanical_maximum_von_mises_stress',
            'species_transport_fuel_utilization'
        ]
        
        # Filter available metrics
        available_metrics = [m for m in key_metrics if m in self.metric_df.columns]
        
        if not available_metrics:
            raise ValueError("No key performance metrics found in data")
        
        n_metrics = len(available_metrics)
        n_cols = 3
        n_rows = (n_metrics + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        axes = axes.flatten() if n_rows > 1 else [axes] if n_rows == 1 else []
        
        for i, metric in enumerate(available_metrics):
            if i < len(axes):
                ax = axes[i]
                
                # Plot histogram
                self.metric_df[metric].hist(bins=20, alpha=0.7, ax=ax, color='skyblue')
                
                # Add statistics
                mean_val = self.metric_df[metric].mean()
                std_val = self.metric_df[metric].std()
                
                ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, 
                          label=f'Mean: {mean_val:.3f}')
                ax.axvline(mean_val + std_val, color='orange', linestyle=':', 
                          label=f'+1σ: {mean_val + std_val:.3f}')
                ax.axvline(mean_val - std_val, color='orange', linestyle=':', 
                          label=f'-1σ: {mean_val - std_val:.3f}')
                
                ax.set_title(metric.replace('_', ' ').title(), fontsize=12)
                ax.set_xlabel('Value')
                ax.set_ylabel('Frequency')
                ax.legend()
                ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for i in range(n_metrics, len(axes)):
            axes[i].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    def plot_parameter_sensitivity(self, target_metric: str, 
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot parameter sensitivity analysis for a target metric.
        
        Args:
            target_metric: Name of the target metric
            save_path: Path to save the plot
            
        Returns:
            Matplotlib figure
        """
        
        if self.parameter_df is None or self.metric_df is None:
            raise ValueError("Parameter or metric data not available")
        
        if target_metric not in self.metric_df.columns:
            raise ValueError(f"Target metric '{target_metric}' not found")
        
        # Combine parameter and metric data
        combined_df = pd.concat([self.parameter_df, self.metric_df[target_metric]], axis=1)
        
        # Exclude sample_id column
        param_cols = [col for col in self.parameter_df.columns if col != 'sample_id']
        
        # Calculate correlations
        correlations = []
        for param in param_cols:
            corr = combined_df[param].corr(combined_df[target_metric])
            correlations.append((param, corr))
        
        # Sort by absolute correlation
        correlations.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Plot top correlations
        n_top = min(10, len(correlations))
        top_params = [c[0] for c in correlations[:n_top]]
        top_corrs = [c[1] for c in correlations[:n_top]]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Correlation bar plot
        colors = ['red' if c < 0 else 'blue' for c in top_corrs]
        bars = ax1.barh(range(len(top_params)), top_corrs, color=colors, alpha=0.7)
        ax1.set_yticks(range(len(top_params)))
        ax1.set_yticklabels([p.replace('_', ' ').title() for p in top_params])
        ax1.set_xlabel('Correlation with ' + target_metric.replace('_', ' ').title())
        ax1.set_title('Parameter Sensitivity Analysis')
        ax1.grid(True, alpha=0.3)
        
        # Add correlation values on bars
        for i, (bar, corr) in enumerate(zip(bars, top_corrs)):
            ax1.text(corr + 0.01 if corr > 0 else corr - 0.01, i, f'{corr:.3f}',
                    va='center', ha='left' if corr > 0 else 'right')
        
        # Scatter plot for most correlated parameter
        most_corr_param = top_params[0]
        ax2.scatter(combined_df[most_corr_param], combined_df[target_metric], 
                   alpha=0.6, s=30)
        
        # Add trend line
        z = np.polyfit(combined_df[most_corr_param], combined_df[target_metric], 1)
        p = np.poly1d(z)
        ax2.plot(combined_df[most_corr_param], p(combined_df[most_corr_param]), 
                "r--", alpha=0.8, linewidth=2)
        
        ax2.set_xlabel(most_corr_param.replace('_', ' ').title())
        ax2.set_ylabel(target_metric.replace('_', ' ').title())
        ax2.set_title(f'Strongest Correlation: r = {top_corrs[0]:.3f}')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
        
    def create_interactive_dashboard(self, save_path: Optional[str] = None) -> str:
        """
        Create interactive Plotly dashboard.
        
        Args:
            save_path: Path to save HTML file
            
        Returns:
            HTML string or file path
        """
        
        if self.parameter_df is None or self.metric_df is None:
            raise ValueError("Parameter or metric data not available")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Parameter Distributions', 'Performance Metrics', 
                          'Parameter Correlations', 'Sensitivity Analysis'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Parameter distributions (first few parameters)
        param_cols = [col for col in self.parameter_df.columns if col != 'sample_id'][:5]
        for i, param in enumerate(param_cols):
            fig.add_trace(
                go.Histogram(x=self.parameter_df[param], name=param, 
                           opacity=0.7, nbinsx=20),
                row=1, col=1
            )
        
        # Performance metrics
        metric_cols = [col for col in self.metric_df.columns if col != 'sample_id'][:5]
        for i, metric in enumerate(metric_cols):
            fig.add_trace(
                go.Box(y=self.metric_df[metric], name=metric.split('_')[-1]),
                row=1, col=2
            )
        
        # Parameter correlation heatmap
        param_data = self.parameter_df[param_cols]
        corr_matrix = param_data.corr()
        
        fig.add_trace(
            go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, 
                      y=corr_matrix.columns, colorscale='RdBu', 
                      zmid=0, showscale=False),
            row=2, col=1
        )
        
        # Sensitivity analysis (scatter plot)
        if len(metric_cols) > 0:
            target_metric = metric_cols[0]
            most_corr_param = param_cols[0]  # Simplified selection
            
            fig.add_trace(
                go.Scatter(x=self.parameter_df[most_corr_param], 
                          y=self.metric_df[target_metric],
                          mode='markers', name='Data Points',
                          marker=dict(size=5, opacity=0.6)),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="SOFC Dataset Analysis Dashboard",
            title_x=0.5,
            height=800,
            showlegend=False
        )
        
        if save_path:
            fig.write_html(save_path)
            return save_path
        else:
            return fig.to_html()
            
    def visualize_3d_field(self, sample_id: int, field_name: str, 
                          physics_type: str = 'electrochemical',
                          save_path: Optional[str] = None) -> Any:
        """
        Create 3D visualization of a field using PyVista.
        
        Args:
            sample_id: Sample ID to visualize
            field_name: Name of the field to visualize
            physics_type: Type of physics (electrochemical, thermal, etc.)
            save_path: Path to save image
            
        Returns:
            PyVista plotter object
        """
        
        # Load HDF5 data
        hdf5_file = os.path.join(self.dataset_dir, 'hdf5', f'sample_{sample_id:06d}.h5')
        
        if not os.path.exists(hdf5_file):
            raise FileNotFoundError(f"HDF5 file not found: {hdf5_file}")
        
        with h5py.File(hdf5_file, 'r') as f:
            # Load mesh coordinates
            if 'mesh/coordinates' not in f:
                raise ValueError("Mesh coordinates not found in HDF5 file")
            
            coordinates = f['mesh/coordinates'][:]
            
            # Load field data
            field_path = f'outputs/{physics_type}/fields/{field_name}'
            if field_path not in f:
                raise ValueError(f"Field '{field_name}' not found in {physics_type} results")
            
            field_data = f[field_path][:]
        
        # Create PyVista point cloud
        if coordinates.shape[1] == 2:
            # 2D data - add z=0
            coords_3d = np.column_stack([coordinates, np.zeros(coordinates.shape[0])])
        else:
            coords_3d = coordinates
        
        cloud = pv.PolyData(coords_3d)
        
        # Add field data
        if len(field_data.shape) == 1:
            # Scalar field
            cloud[field_name] = field_data
        else:
            # Vector field - use magnitude
            field_magnitude = np.linalg.norm(field_data, axis=1)
            cloud[f'{field_name}_magnitude'] = field_magnitude
            field_name = f'{field_name}_magnitude'
        
        # Create plotter
        plotter = pv.Plotter(off_screen=save_path is not None)
        
        # Add mesh with field coloring
        plotter.add_mesh(cloud, scalars=field_name, cmap='viridis', 
                        point_size=10, render_points_as_spheres=True)
        
        # Add colorbar
        plotter.add_scalar_bar(field_name.replace('_', ' ').title())
        
        # Set camera and lighting
        plotter.camera_position = 'iso'
        plotter.add_axes()
        
        if save_path:
            plotter.screenshot(save_path)
            plotter.close()
        
        return plotter
        
    def generate_analysis_report(self, output_dir: Optional[str] = None) -> str:
        """
        Generate comprehensive analysis report.
        
        Args:
            output_dir: Directory to save report files
            
        Returns:
            Path to main report file
        """
        
        if output_dir is None:
            output_dir = os.path.join(self.dataset_dir, 'analysis')
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate all plots
        plots = {}
        
        try:
            plots['parameter_distributions'] = self.plot_parameter_distributions(
                os.path.join(output_dir, 'parameter_distributions.png')
            )
            plt.close()
        except Exception as e:
            print(f"Error generating parameter distributions: {e}")
        
        try:
            plots['parameter_correlations'] = self.plot_parameter_correlations(
                os.path.join(output_dir, 'parameter_correlations.png')
            )
            plt.close()
        except Exception as e:
            print(f"Error generating parameter correlations: {e}")
        
        try:
            plots['performance_metrics'] = self.plot_performance_metrics(
                os.path.join(output_dir, 'performance_metrics.png')
            )
            plt.close()
        except Exception as e:
            print(f"Error generating performance metrics: {e}")
        
        # Generate interactive dashboard
        try:
            dashboard_path = os.path.join(output_dir, 'interactive_dashboard.html')
            self.create_interactive_dashboard(dashboard_path)
            plots['dashboard'] = dashboard_path
        except Exception as e:
            print(f"Error generating dashboard: {e}")
        
        # Generate report summary
        report_path = os.path.join(output_dir, 'analysis_report.md')
        self._write_analysis_report(report_path, plots)
        
        return report_path
        
    def _write_analysis_report(self, report_path: str, plots: Dict[str, Any]):
        """Write analysis report in Markdown format."""
        
        with open(report_path, 'w') as f:
            f.write("# SOFC Dataset Analysis Report\n\n")
            f.write(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Dataset summary
            f.write("## Dataset Summary\n\n")
            if self.metadata:
                n_samples = len(self.metadata.get('samples', []))
                f.write(f"- Number of samples: {n_samples}\n")
                f.write(f"- Creation date: {self.metadata.get('creation_date', 'Unknown')}\n")
            
            if self.parameter_df is not None:
                n_params = len([col for col in self.parameter_df.columns if col != 'sample_id'])
                f.write(f"- Number of parameters: {n_params}\n")
            
            if self.metric_df is not None:
                n_metrics = len([col for col in self.metric_df.columns if col != 'sample_id'])
                f.write(f"- Number of metrics: {n_metrics}\n")
            
            f.write("\n")
            
            # Generated plots
            f.write("## Analysis Results\n\n")
            
            for plot_name, plot_info in plots.items():
                if isinstance(plot_info, str) and plot_info.endswith('.png'):
                    f.write(f"### {plot_name.replace('_', ' ').title()}\n\n")
                    f.write(f"![{plot_name}]({os.path.basename(plot_info)})\n\n")
                elif isinstance(plot_info, str) and plot_info.endswith('.html'):
                    f.write(f"### Interactive Dashboard\n\n")
                    f.write(f"[Open Dashboard]({os.path.basename(plot_info)})\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("1. Review parameter distributions for any unexpected patterns\n")
            f.write("2. Check correlation matrix for highly correlated parameters\n")
            f.write("3. Analyze performance metrics for outliers\n")
            f.write("4. Use sensitivity analysis to identify key parameters\n")
            f.write("5. Consider additional sampling in under-represented regions\n\n")


if __name__ == "__main__":
    # Example usage
    dataset_dir = "../../data/sofc_dataset"
    
    if os.path.exists(dataset_dir):
        visualizer = SOFCVisualizer(dataset_dir)
        
        # Generate analysis report
        report_path = visualizer.generate_analysis_report()
        print(f"Analysis report generated: {report_path}")
    else:
        print(f"Dataset directory not found: {dataset_dir}")
        print("Please run the main simulation first to generate data.")