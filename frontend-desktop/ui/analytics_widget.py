"""
Analytics widget with Matplotlib charts
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QGridLayout, QScrollArea, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont

from utils.api_client import APIClient


class DataWorker(QThread):
    """Worker thread for fetching analytics data"""
    
    data_loaded = pyqtSignal(bool, dict, str)  # success, data, message
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        """Fetch analytics data"""
        try:
            success, data, message = self.api_client.get_summary()
            self.data_loaded.emit(success, data, message)
        except Exception as e:
            self.data_loaded.emit(False, {}, f"Error loading data: {str(e)}")


class ChartCanvas(FigureCanvas):
    """Custom matplotlib canvas for charts"""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#ffffff')
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set light theme
        plt.style.use('default')
        self.fig.patch.set_facecolor('#ffffff')
    
    def clear_chart(self):
        """Clear the chart"""
        self.fig.clear()
        self.draw()
    
    def create_pie_chart(self, data: dict, title: str):
        """Create a pie chart"""
        self.fig.clear()
        
        if not data:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='#666666')
            ax.set_facecolor('#ffffff')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        
        labels = list(data.keys())
        sizes = list(data.values())
        colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140']
        
        # Shorten labels if too long
        short_labels = [label[:20] + '...' if len(label) > 20 else label for label in labels]
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=short_labels, autopct='%1.1f%%',
            colors=colors[:len(labels)], startangle=90, textprops={'fontsize': 9}
        )
        
        # Style the text
        for text in texts:
            text.set_color('#333333')
            text.set_fontsize(9)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_weight('bold')
        
        ax.set_title(title, color='#333333', fontsize=12, fontweight='bold', pad=15)
        ax.set_facecolor('#ffffff')
        
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self.draw()
    
    def create_bar_chart(self, data: dict, title: str, ylabel: str):
        """Create a bar chart"""
        self.fig.clear()
        
        if not data:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='#666666')
            ax.set_facecolor('#ffffff')
            self.draw()
            return
        
        ax = self.fig.add_subplot(111)
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Shorten labels if needed
        short_labels = [label[:12] + '...' if len(label) > 12 else label for label in labels]
        
        colors = ['#667eea', '#f093fb', '#4facfe']
        bars = ax.bar(short_labels, values, color=colors[:len(labels)], alpha=0.8, width=0.6)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                   f'{height:.1f}',
                   ha='center', va='bottom', color='#333333', fontweight='bold', fontsize=9)
        
        ax.set_title(title, color='#333333', fontsize=12, fontweight='bold', pad=15)
        ax.set_ylabel(ylabel, color='#333333', fontsize=10)
        ax.tick_params(colors='#333333', labelsize=9)
        ax.set_facecolor('#ffffff')
        ax.set_ylim(0, max(values) * 1.15 if values else 1)
        
        # Style spines
        for spine in ax.spines.values():
            spine.set_edgecolor('#dddddd')
        
        # Rotate x-axis labels if needed
        if len(labels) > 3:
            plt.setp(ax.get_xticklabels(), rotation=30, ha='right')
        
        self.fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
        self.draw()
    
    def create_summary_chart(self, summary_data: dict):
        """Create a summary chart with multiple metrics"""
        self.fig.clear()
        
        if not summary_data:
            ax = self.fig.add_subplot(111)
            ax.text(0.5, 0.5, 'No data available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=14, color='#666666')
            ax.set_facecolor('#ffffff')
            self.draw()
            return
        
        # Create subplots with better spacing
        self.fig.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.1, hspace=0.4, wspace=0.4)
        
        ax1 = self.fig.add_subplot(221)  # Top left - Equipment count
        ax2 = self.fig.add_subplot(222)  # Top right - Type distribution
        ax3 = self.fig.add_subplot(223)  # Bottom left - Average flowrate
        ax4 = self.fig.add_subplot(224)  # Bottom right - Averages comparison
        
        # Equipment count (simple text display)
        ax1.text(0.5, 0.5, f"{summary_data.get('total_equipment', 0)}", 
                ha='center', va='center', fontsize=32, fontweight='bold', color='#667eea')
        ax1.text(0.5, 0.25, 'Total Equipment', 
                ha='center', va='center', fontsize=11, color='#666666')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.axis('off')
        ax1.set_facecolor('#ffffff')
        
        # Type distribution pie chart
        type_dist = summary_data.get('type_distribution', {})
        if type_dist:
            labels = list(type_dist.keys())
            sizes = list(type_dist.values())
            colors = ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140']
            
            # Make labels shorter if needed
            short_labels = [label[:15] + '...' if len(label) > 15 else label for label in labels]
            
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=short_labels, autopct='%1.0f%%',
                colors=colors[:len(labels)], startangle=90, textprops={'fontsize': 8}
            )
            
            for text in texts:
                text.set_color('#333333')
                text.set_fontsize(7)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(7)
                autotext.set_weight('bold')
        
        ax2.set_title('Equipment Types', color='#333333', fontsize=10, pad=10)
        ax2.set_facecolor('#ffffff')
        
        # Average flowrate bar
        avg_flowrate = summary_data.get('average_flowrate', 0)
        bars = ax3.bar(['Flowrate'], [avg_flowrate], color='#667eea', alpha=0.8, width=0.5)
        ax3.text(0, avg_flowrate * 1.05, f'{avg_flowrate:.1f}', 
                ha='center', va='bottom', color='#333333', fontweight='bold', fontsize=10)
        ax3.set_title('Avg Flowrate', color='#333333', fontsize=10, pad=10)
        ax3.tick_params(colors='#333333', labelsize=8)
        ax3.set_facecolor('#ffffff')
        ax3.set_ylim(0, avg_flowrate * 1.2)
        for spine in ax3.spines.values():
            spine.set_edgecolor('#dddddd')
        
        # Averages comparison
        metrics = ['Flowrate', 'Pressure', 'Temp']
        values = [
            summary_data.get('average_flowrate', 0),
            summary_data.get('average_pressure', 0),
            summary_data.get('average_temperature', 0)
        ]
        
        colors_bars = ['#667eea', '#f093fb', '#4facfe']
        bars = ax4.bar(metrics, values, color=colors_bars, alpha=0.8, width=0.6)
        
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height * 1.02,
                    f'{value:.1f}',
                    ha='center', va='bottom', color='#333333', fontweight='bold', fontsize=8)
        
        ax4.set_title('Average Values', color='#333333', fontsize=10, pad=10)
        ax4.tick_params(colors='#333333', labelsize=8)
        ax4.set_facecolor('#ffffff')
        ax4.set_ylim(0, max(values) * 1.15 if values else 1)
        for spine in ax4.spines.values():
            spine.set_edgecolor('#dddddd')
        plt.setp(ax4.get_xticklabels(), rotation=0, ha='center')
        
        self.draw()


class AnalyticsWidget(QWidget):
    """Main analytics widget"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.current_data = {}
        self.data_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Title and refresh button
        header_layout = QHBoxLayout()
        
        title = QLabel("Analytics Dashboard")
        title.setAlignment(Qt.AlignLeft)
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        title.setFont(font)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh Data")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton("Export Charts")
        self.export_button.setMinimumHeight(35)
        self.export_button.clicked.connect(self.export_charts)
        self.export_button.setEnabled(False)
        header_layout.addWidget(self.export_button)
        
        main_layout.addLayout(header_layout)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        
        # Summary statistics
        stats_group = QGroupBox("Summary Statistics")
        stats_layout = QGridLayout(stats_group)
        stats_layout.setSpacing(15)
        
        self.total_label = QLabel("Total Equipment: -")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; padding: 10px;")
        stats_layout.addWidget(self.total_label, 0, 0)
        
        self.avg_flowrate_label = QLabel("Avg Flowrate: -")
        self.avg_flowrate_label.setStyleSheet("font-size: 16px; color: #2196F3; padding: 10px;")
        stats_layout.addWidget(self.avg_flowrate_label, 0, 1)
        
        self.avg_pressure_label = QLabel("Avg Pressure: -")
        self.avg_pressure_label.setStyleSheet("font-size: 16px; color: #FF9800; padding: 10px;")
        stats_layout.addWidget(self.avg_pressure_label, 1, 0)
        
        self.avg_temperature_label = QLabel("Avg Temperature: -")
        self.avg_temperature_label.setStyleSheet("font-size: 16px; color: #F44336; padding: 10px;")
        stats_layout.addWidget(self.avg_temperature_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Charts section
        charts_group = QGroupBox("Data Visualizations")
        charts_layout = QVBoxLayout(charts_group)
        charts_layout.setSpacing(15)
        
        # Charts grid
        charts_grid_layout = QGridLayout()
        charts_grid_layout.setSpacing(15)
        
        # Summary chart (top) - larger size
        self.summary_canvas = ChartCanvas(width=12, height=7)
        self.summary_canvas.setMinimumHeight(400)
        charts_grid_layout.addWidget(self.summary_canvas, 0, 0, 1, 2)
        
        # Type distribution chart - better proportions
        self.type_canvas = ChartCanvas(width=6, height=5)
        self.type_canvas.setMinimumHeight(300)
        charts_grid_layout.addWidget(self.type_canvas, 1, 0)
        
        # Averages chart - better proportions
        self.averages_canvas = ChartCanvas(width=6, height=5)
        self.averages_canvas.setMinimumHeight(300)
        charts_grid_layout.addWidget(self.averages_canvas, 1, 1)
        
        # Set row stretch to prevent overlap
        charts_grid_layout.setRowStretch(0, 3)
        charts_grid_layout.setRowStretch(1, 2)
        charts_grid_layout.setColumnStretch(0, 1)
        charts_grid_layout.setColumnStretch(1, 1)
        
        charts_layout.addLayout(charts_grid_layout)
        layout.addWidget(charts_group)
        
        # Data table section
        table_group = QGroupBox("Equipment Data")
        table_layout = QVBoxLayout(table_group)
        
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.horizontalHeader().setStretchLastSection(True)
        self.data_table.setMinimumHeight(200)
        table_layout.addWidget(self.data_table)
        
        layout.addWidget(table_group)
        
        # Set content widget to scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Status label
        self.status_label = QLabel("Click 'Refresh Data' to load analytics")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-style: italic; padding: 10px;")
        main_layout.addWidget(self.status_label)
    
    def refresh_data(self):
        """Refresh analytics data"""
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Authentication Required", "Please login first.")
            return
        
        # Disable refresh button
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Loading...")
        self.status_label.setText("Loading analytics data...")
        
        # Start data worker
        self.data_worker = DataWorker(self.api_client)
        self.data_worker.data_loaded.connect(self.on_data_loaded)
        self.data_worker.start()
    
    @pyqtSlot(bool, dict, str)
    def on_data_loaded(self, success: bool, data: dict, message: str):
        """Handle data loading completion"""
        # Re-enable refresh button
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh Data")
        
        if success:
            self.current_data = data
            self.update_display()
            self.status_label.setText("Data loaded successfully")
            self.export_button.setEnabled(True)
        else:
            self.status_label.setText(f"Failed to load data: {message}")
            self.clear_display()
            self.export_button.setEnabled(False)
        
        # Clean up worker
        if self.data_worker:
            self.data_worker.deleteLater()
            self.data_worker = None
    
    def update_display(self):
        """Update the display with current data"""
        if not self.current_data:
            return
        
        # Update summary statistics
        total = self.current_data.get('total_equipment', 0)
        avg_flowrate = self.current_data.get('average_flowrate', 0)
        avg_pressure = self.current_data.get('average_pressure', 0)
        avg_temperature = self.current_data.get('average_temperature', 0)
        
        self.total_label.setText(f"Total Equipment: {total}")
        self.avg_flowrate_label.setText(f"Avg Flowrate: {avg_flowrate:.2f}")
        self.avg_pressure_label.setText(f"Avg Pressure: {avg_pressure:.2f}")
        self.avg_temperature_label.setText(f"Avg Temperature: {avg_temperature:.2f}")
        
        # Update charts
        self.summary_canvas.create_summary_chart(self.current_data)
        
        type_distribution = self.current_data.get('type_distribution', {})
        self.type_canvas.create_pie_chart(type_distribution, "Equipment Type Distribution")
        
        averages = {
            'Flowrate': avg_flowrate,
            'Pressure': avg_pressure,
            'Temperature': avg_temperature
        }
        self.averages_canvas.create_bar_chart(averages, "Average Values", "Value")
        
        # Update data table (if equipment records are available)
        self.update_data_table()
    
    def update_data_table(self):
        """Update the data table"""
        # For now, show summary data in table format
        # In a full implementation, you might fetch individual records
        
        self.data_table.setRowCount(4)
        self.data_table.setColumnCount(2)
        self.data_table.setHorizontalHeaderLabels(["Metric", "Value"])
        
        metrics = [
            ("Total Equipment", str(self.current_data.get('total_equipment', 0))),
            ("Average Flowrate", f"{self.current_data.get('average_flowrate', 0):.2f}"),
            ("Average Pressure", f"{self.current_data.get('average_pressure', 0):.2f}"),
            ("Average Temperature", f"{self.current_data.get('average_temperature', 0):.2f}")
        ]
        
        for row, (metric, value) in enumerate(metrics):
            self.data_table.setItem(row, 0, QTableWidgetItem(metric))
            self.data_table.setItem(row, 1, QTableWidgetItem(value))
        
        # Add type distribution
        type_dist = self.current_data.get('type_distribution', {})
        if type_dist:
            current_row = self.data_table.rowCount()
            self.data_table.setRowCount(current_row + len(type_dist))
            
            for i, (eq_type, count) in enumerate(type_dist.items()):
                self.data_table.setItem(current_row + i, 0, QTableWidgetItem(f"{eq_type} Count"))
                self.data_table.setItem(current_row + i, 1, QTableWidgetItem(str(count)))
        
        # Resize columns
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    
    def clear_display(self):
        """Clear the display"""
        self.total_label.setText("Total Equipment: -")
        self.avg_flowrate_label.setText("Avg Flowrate: -")
        self.avg_pressure_label.setText("Avg Pressure: -")
        self.avg_temperature_label.setText("Avg Temperature: -")
        
        self.summary_canvas.clear_chart()
        self.type_canvas.clear_chart()
        self.averages_canvas.clear_chart()
        
        self.data_table.setRowCount(0)
    
    def export_charts(self):
        """Export charts to file"""
        if not self.current_data:
            QMessageBox.warning(self, "No Data", "No data available to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Charts",
            "analytics_charts.png",
            "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Create a new figure with all charts
                fig = Figure(figsize=(16, 12), facecolor='white')
                
                # Summary chart
                ax1 = fig.add_subplot(221)
                self._export_summary_to_axis(ax1)
                
                # Type distribution
                ax2 = fig.add_subplot(222)
                self._export_pie_to_axis(ax2, self.current_data.get('type_distribution', {}), 
                                       "Equipment Type Distribution")
                
                # Averages
                ax3 = fig.add_subplot(223)
                averages = {
                    'Flowrate': self.current_data.get('average_flowrate', 0),
                    'Pressure': self.current_data.get('average_pressure', 0),
                    'Temperature': self.current_data.get('average_temperature', 0)
                }
                self._export_bar_to_axis(ax3, averages, "Average Values", "Value")
                
                fig.tight_layout()
                fig.savefig(file_path, dpi=300, bbox_inches='tight')
                
                QMessageBox.information(self, "Export Successful", f"Charts exported to {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export charts: {str(e)}")
    
    def _export_summary_to_axis(self, ax):
        """Export summary data to axis"""
        ax.text(0.5, 0.5, f"{self.current_data.get('total_equipment', 0)}", 
               ha='center', va='center', fontsize=24, fontweight='bold', color='green')
        ax.text(0.5, 0.2, 'Total Equipment', 
               ha='center', va='center', fontsize=12, color='black')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def _export_pie_to_axis(self, ax, data, title):
        """Export pie chart to axis"""
        if data:
            labels = list(data.keys())
            sizes = list(data.values())
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title(title)
    
    def _export_bar_to_axis(self, ax, data, title, ylabel):
        """Export bar chart to axis"""
        if data:
            labels = list(data.keys())
            values = list(data.values())
            bars = ax.bar(labels, values, alpha=0.8)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontweight='bold')
        
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        
        if len(labels) > 3:
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')