#!/usr/bin/env python3
"""
Database Charts Generator
Creates visual charts for bot statistics using matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from database import get_conn, get_detailed_stats, get_source_stats, get_function_stats
import os

CHARTS_DIR = "temp/charts"

def ensure_charts_dir():
    """Create charts directory if it doesn't exist"""
    os.makedirs(CHARTS_DIR, exist_ok=True)

def create_user_stats_chart():
    """Create a chart showing user statistics"""
    ensure_charts_dir()
    
    stats = get_detailed_stats()
    
    labels = ['Total Users', 'Premium Users', 'New Today', 'Active Deadlines']
    values = [
        stats['total'],
        stats['premium'],
        stats['new_today'],
        stats['deadlines']
    ]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=['#3498db', '#f39c12', '#2ecc71', '#e74c3c'])
    
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Bot User Statistics', fontsize=16, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    output_path = os.path.join(CHARTS_DIR, 'user_stats.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_source_chart():
    """Create a pie chart showing user sources"""
    ensure_charts_dir()
    
    source_stats = get_source_stats()
    
    if not source_stats:
        return None
    
    labels = list(source_stats.keys())
    sizes = list(source_stats.values())
    
    # Create colors
    colors = plt.cm.Set3(range(len(labels)))
    
    fig, ax = plt.subplots(figsize=(10, 8))
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                        colors=colors, startangle=90)
    
    ax.set_title('User Sources Distribution', fontsize=16, fontweight='bold')
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    output_path = os.path.join(CHARTS_DIR, 'source_stats.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_function_usage_chart():
    """Create a bar chart showing function usage"""
    ensure_charts_dir()
    
    func_stats = get_function_stats()
    
    if not func_stats:
        return None
    
    # Sort by usage count
    sorted_stats = sorted(func_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    
    labels = [item[0] for item in sorted_stats]
    values = [item[1] for item in sorted_stats]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(labels, values, color='#3498db')
    
    ax.set_xlabel('Usage Count', fontsize=12)
    ax.set_title('Top 10 Most Used Features', fontsize=16, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width)}',
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(CHARTS_DIR, 'function_usage.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_all_charts():
    """Create all available charts"""
    charts = {}
    
    try:
        charts['user_stats'] = create_user_stats_chart()
        print("✅ User stats chart created")
    except Exception as e:
        print(f"❌ User stats chart failed: {e}")
    
    try:
        source_chart = create_source_chart()
        if source_chart:
            charts['source_stats'] = source_chart
            print("✅ Source stats chart created")
    except Exception as e:
        print(f"❌ Source stats chart failed: {e}")
    
    try:
        func_chart = create_function_usage_chart()
        if func_chart:
            charts['function_usage'] = func_chart
            print("✅ Function usage chart created")
    except Exception as e:
        print(f"❌ Function usage chart failed: {e}")
    
    return charts

if __name__ == "__main__":
    print("📊 Generating charts...\n")
    charts = create_all_charts()
    print(f"\n✅ Generated {len(charts)} charts")
    for name, path in charts.items():
        print(f"  - {name}: {path}")
