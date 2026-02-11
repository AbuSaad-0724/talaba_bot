#!/usr/bin/env python3
"""
Database Charts Generator
Creates statistical charts from database data
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from database import get_detailed_stats, get_function_stats, get_source_stats, get_conn
import os
from datetime import datetime, timedelta

def create_database_charts():
    """Generate charts from database statistics"""
    print("📊 Generating Database Charts...\n")
    
    os.makedirs("temp/charts", exist_ok=True)
    
    # Chart 1: User Statistics
    print("Chart 1: User Statistics")
    print("-" * 60)
    try:
        stats = get_detailed_stats()
        
        labels = ['Total\nUsers', 'Premium\nUsers', 'New\nToday', 'Active\nDeadlines']
        values = [
            stats.get('total', 0),
            stats.get('premium', 0),
            stats.get('new_today', 0),
            stats.get('deadlines', 0)
        ]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#3498db', '#f39c12', '#2ecc71', '#e74c3c']
        bars = ax.bar(labels, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_ylabel('Count', fontsize=14, fontweight='bold')
        ax.set_title('Bot User Statistics', fontsize=18, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        output1 = "temp/charts/user_stats.png"
        plt.savefig(output1, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Created: {output1}")
        print(f"   Total Users: {stats.get('total', 0)}")
        print(f"   Premium: {stats.get('premium', 0)}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Chart 2: Function Usage
    print("Chart 2: Function Usage")
    print("-" * 60)
    try:
        func_stats = get_function_stats()
        
        if func_stats:
            sorted_funcs = sorted(func_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            labels = [f[0] for f in sorted_funcs]
            values = [f[1] for f in sorted_funcs]
            
            fig, ax = plt.subplots(figsize=(12, 7))
            bars = ax.barh(labels, values, color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
            
            ax.set_xlabel('Usage Count', fontsize=14, fontweight='bold')
            ax.set_title('Top 10 Most Used Features', fontsize=18, fontweight='bold', pad=20)
            ax.grid(axis='x', alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)
            
            # Add value labels
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f' {int(width)}',
                        ha='left', va='center', fontsize=10, fontweight='bold')
            
            plt.tight_layout()
            output2 = "temp/charts/function_usage.png"
            plt.savefig(output2, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Created: {output2}")
            print(f"   Top function: {sorted_funcs[0][0]} ({sorted_funcs[0][1]} uses)\n")
        else:
            print("⚠️  No function statistics available\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Chart 3: User Sources
    print("Chart 3: User Sources")
    print("-" * 60)
    try:
        source_stats = get_source_stats()
        
        if source_stats:
            labels = list(source_stats.keys())
            sizes = list(source_stats.values())
            
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = plt.cm.Set3(range(len(labels)))
            
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                colors=colors, startangle=90,
                textprops={'fontsize': 12, 'fontweight': 'bold'}
            )
            
            ax.set_title('User Sources Distribution', fontsize=18, fontweight='bold', pad=20)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
            
            plt.tight_layout()
            output3 = "temp/charts/source_distribution.png"
            plt.savefig(output3, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Created: {output3}")
            print(f"   Sources: {len(source_stats)}\n")
        else:
            print("⚠️  No source statistics available\n")
            
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    # Chart 4: Daily Activity (last 7 days)
    print("Chart 4: Daily Activity")
    print("-" * 60)
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # Get activity for last 7 days
        days = []
        counts = []
        
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            cursor.execute("""
                SELECT COUNT(DISTINCT tg_id) 
                FROM event_log 
                WHERE created LIKE ?
            """, (f"{date}%",))
            count = cursor.fetchone()[0]
            
            days.append(date[-5:])  # MM-DD
            counts.append(count)
        
        conn.close()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(days, counts, marker='o', linewidth=2.5, markersize=10, 
                color='#3498db', markerfacecolor='#e74c3c', markeredgewidth=2, markeredgecolor='#c0392b')
        ax.fill_between(days, counts, alpha=0.3, color='#3498db')
        
        ax.set_xlabel('Date', fontsize=14, fontweight='bold')
        ax.set_ylabel('Active Users', fontsize=14, fontweight='bold')
        ax.set_title('Daily Active Users (Last 7 Days)', fontsize=18, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Add value labels
        for i, (day, count) in enumerate(zip(days, counts)):
            ax.text(i, count, f'{count}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        output4 = "temp/charts/daily_activity.png"
        plt.savefig(output4, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Created: {output4}")
        print(f"   Peak day: {days[counts.index(max(counts))]} ({max(counts)} users)\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
    
    print("=" * 60)
    print("✅ All charts generated successfully!")
    print(f"📁 Charts saved in: temp/charts/")

if __name__ == "__main__":
    create_database_charts()
