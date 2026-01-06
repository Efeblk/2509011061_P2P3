"""
EventGraph Desktop Dashboard with Graphs

Interactive GUI with statistical visualizations using Tkinter + Matplotlib.

Features:
- Real-time database statistics
- Interactive bar charts (category distribution, price analysis)
- Box plot for price distribution
- Run scraping and analysis with buttons
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
import asyncio
import threading
import subprocess
from pathlib import Path
import numpy as np

# Project root
project_root = Path(__file__).parent.parent.parent

# --- MODERN DARK THEME ---
THEME = {
    "bg_main": "#1e1e2e",        # Deep dark blue/grey
    "bg_card": "#2b2b40",        # Slightly lighter panel
    "fg_text": "#ffffff",        # White text
    "fg_sub": "#a6a6c0",         # Muted purple-ish grey
    "accent_1": "#00d2ff",       # Cyan
    "accent_2": "#3a7bd5",       # Blue
    "accent_warm": "#ff9f43",    # Orange
    "accent_danger": "#ff6b6b",  # Red
    "accent_success": "#43e97b", # Green
    "accent_purple": "#a55eea",  # Purple
}

class EventGraphDashboard:
    """Dashboard with graphs and statistics."""

    def __init__(self, root):
        """Initialize dashboard."""
        self.root = root
        self.root.title("EventGraph Dashboard")
        self.root.geometry("1300x850")
        self.root.configure(bg=THEME["bg_main"])

        # Data
        self.stats = None
        self.categories = None

        self.setup_mpl_theme()
        self.setup_ui()
        self.load_data()

    def setup_mpl_theme(self):
        """Configure Matplotlib to match the dark theme."""
        plt.style.use('dark_background')
        plt.rcParams.update({
            "figure.facecolor": THEME["bg_main"],
            "axes.facecolor": THEME["bg_main"],
            "axes.edgecolor": THEME["fg_sub"],
            "axes.labelcolor": THEME["fg_text"],
            "xtick.color": THEME["fg_sub"],
            "ytick.color": THEME["fg_sub"],
            "text.color": THEME["fg_text"],
            "grid.color": "#444444",
            "grid.alpha": 0.3,
            "font.family": "sans-serif",
            "font.size": 10
        })

    def setup_ui(self):
        """Setup the user interface."""
        # Custom Styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook (Tab) Style
        style.configure("TNotebook", background=THEME["bg_main"], borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background=THEME["bg_card"], 
                       foreground=THEME["fg_sub"],
                       padding=[15, 5],
                       font=("Helvetica", 10))
        style.map("TNotebook.Tab", 
                 background=[("selected", THEME["accent_2"])],
                 foreground=[("selected", "white")])

        # Header
        header = tk.Frame(self.root, bg=THEME["bg_card"], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Title Label
        title_frame = tk.Frame(header, bg=THEME["bg_card"])
        title_frame.pack(side=tk.LEFT, padx=25, pady=20)
        
        tk.Label(
            title_frame,
            text="EventGraph",
            font=("Helvetica", 24, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["accent_1"]
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_frame,
            text="Analytics",
            font=("Helvetica", 24),
            bg=THEME["bg_card"],
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        # Refresh button
        refresh_btn = tk.Button(
            header,
            text="RELOAD DATA",
            command=self.load_data,
            font=("Helvetica", 9, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["accent_1"],
            activebackground=THEME["accent_1"],
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10
        )
        refresh_btn.pack(side=tk.RIGHT, padx=25)

        # Main container
        main = tk.Frame(self.root, bg=THEME["bg_main"])
        main.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # Left panel - Stats & Actions
        left_panel = tk.Frame(main, bg=THEME["bg_main"], width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        left_panel.pack_propagate(False)

        # Stats Section
        tk.Label(
            left_panel,
            text="OVERVIEW",
            font=("Helvetica", 11, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["fg_sub"]
        ).pack(anchor="w", pady=(0, 15))

        self.stats_container = tk.Frame(left_panel, bg=THEME["bg_main"])
        self.stats_container.pack(fill=tk.X)

        # Actions Section
        tk.Label(
            left_panel,
            text="CONTROLS",
            font=("Helvetica", 11, "bold"),
            bg=THEME["bg_main"],
            fg=THEME["fg_sub"]
        ).pack(anchor="w", pady=(40, 15))

        self.create_action_btn(left_panel, "START SCRAPING", "🕷️", self.start_scraping, THEME["accent_2"])
        self.create_action_btn(left_panel, "RUN AI ENRICHMENT", "🧠", self.run_ai, THEME["accent_purple"])
        self.create_action_btn(left_panel, "GENERATE REPORT", "📊", self.run_analysis, THEME["accent_success"])
        self.create_action_btn(left_panel, "CLEAR DATABASE", "🗑️", self.clear_data, THEME["accent_danger"])

        # Right panel - Graphs
        right_panel = tk.Frame(main, bg=THEME["bg_main"])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Notebook
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.tab1 = tk.Frame(self.notebook, bg=THEME["bg_main"])
        self.notebook.add(self.tab1, text="Category Mix")

        self.tab2 = tk.Frame(self.notebook, bg=THEME["bg_main"])
        self.notebook.add(self.tab2, text="Price Analysis")

        self.tab3 = tk.Frame(self.notebook, bg=THEME["bg_main"])
        self.notebook.add(self.tab3, text="Distribution")

    def create_action_btn(self, parent, text, icon, command, color):
        """Create a stylish action button."""
        frame = tk.Frame(parent, bg=THEME["bg_main"])
        frame.pack(fill=tk.X, pady=8)

        btn = tk.Button(
            frame,
            text=f"{icon}  {text}",
            command=command,
            font=("Helvetica", 10, "bold"),
            bg=THEME["bg_card"],
            fg=color,
            activebackground=color,
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=12,
            anchor="w",
            cursor="hand2"
        )
        btn.pack(fill=tk.X)
        
        # Bottom border accent
        tk.Frame(frame, bg=color, height=2).pack(fill=tk.X)
        return btn

    def create_stat_card(self, parent, label, value, sub_label=""):
        """Create a modern stat card."""
        card = tk.Frame(parent, bg=THEME["bg_card"], height=100)
        card.pack(fill=tk.X, pady=6)
        card.pack_propagate(False)

        # Left accent stripe
        stripe = tk.Frame(card, bg=THEME["accent_1"], width=4)
        stripe.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(card, bg=THEME["bg_card"])
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15)

        tk.Label(
            content,
            text=label.upper(),
            font=("Helvetica", 9),
            bg=THEME["bg_card"],
            fg=THEME["fg_sub"]
        ).pack(anchor="w", pady=(15, 5))

        tk.Label(
            content,
            text=str(value),
            font=("Helvetica", 24, "bold"),
            bg=THEME["bg_card"],
            fg="white"
        ).pack(anchor="w")
        
        if sub_label:
            tk.Label(
                content,
                text=sub_label,
                font=("Helvetica", 8),
                bg=THEME["bg_card"],
                fg=THEME["accent_success"]
            ).pack(anchor="w", pady=(2, 0))

    def load_data(self):
        """Load data from database asynchronously."""
        def load_async():
            try:
                import sys
                sys.path.insert(0, str(project_root))
                from src.models.event import EventNode

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                events = loop.run_until_complete(EventNode.get_all_events())

                # Statistics
                total = len(events)
                priced = [e for e in events if e.price and e.price > 0]
                prices = [e.price for e in priced]

                mean_price = np.mean(prices) if prices else 0
                median_price = np.median(prices) if prices else 0
                
                # Simple growth mock (for UI demo)
                growth = "+12% this week"

                # Category data
                from collections import Counter
                categories = Counter(e.category for e in events if e.category)

                self.stats = {
                    'total_events': total,
                    'mean_price': mean_price,
                    'median_price': median_price,
                    'categories': len(categories),
                    'venues': len(set(e.venue for e in events if e.venue))
                }
                self.categories = dict(categories.most_common(10))

                self.root.after(0, self.update_ui)

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load data:\n{str(e)}"))

        thread = threading.Thread(target=load_async, daemon=True)
        thread.start()

    def update_ui(self):
        """Update UI elements with new data."""
        # Clear stats
        for widget in self.stats_container.winfo_children():
            widget.destroy()

        if self.stats:
            self.create_stat_card(self.stats_container, "Total Events", f"{self.stats['total_events']:,}")
            self.create_stat_card(self.stats_container, "Avg Price", f"{self.stats['mean_price']:.0f} TL")
            self.create_stat_card(self.stats_container, "Categories", str(self.stats['categories']))
            self.create_stat_card(self.stats_container, "Venues", str(self.stats['venues']))

        # Update Graphs
        self.plot_category_distribution()
        self.plot_price_analysis()
        self.plot_box_plot()

    def plot_category_distribution(self):
        """Plot vibrant horizontal bar chart."""
        for widget in self.tab1.winfo_children():
            widget.destroy()

        if not self.categories:
            tk.Label(self.tab1, text="No Data", bg=THEME["bg_main"], fg="white").pack(pady=50)
            return

        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Data
        cats = list(self.categories.keys())[:8]
        vals = [self.categories[c] for c in cats]
        y_pos = np.arange(len(cats))

        # Horizontal bars with gradient-like colors
        colors = [THEME["accent_1"], THEME["accent_2"], THEME["accent_purple"], THEME["accent_success"]]
        # Cycle colors
        color_map = [colors[i % len(colors)] for i in range(len(cats))]

        bars = ax.barh(y_pos, vals, align='center', color=color_map, alpha=0.8, height=0.6)
        
        # Style
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cats, color="white", fontsize=11)
        ax.invert_yaxis()  # labels read top-to-bottom
        ax.set_xlabel('Event Count', fontweight='bold')
        ax.set_title('Top Categories', fontweight='bold', pad=20, fontsize=14)
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(THEME["fg_sub"])
        ax.spines['left'].set_visible(False)

        # Add values inside/end of bars
        for i, v in enumerate(vals):
            ax.text(v + (max(vals)*0.01), i, str(v), color='white', va='center', fontweight='bold')

        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.tab1)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    def plot_price_analysis(self):
        """Plot area chart (filled line)."""
        for widget in self.tab2.winfo_children():
            widget.destroy()

        # Loading indicator
        loader = tk.Label(self.tab2, text="Loading...", bg=THEME["bg_main"], fg=THEME["fg_text"])
        loader.pack(pady=50)

        def fetch_data():
            try:
                import sys
                sys.path.insert(0, str(project_root))
                from src.models.event import EventNode
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                events = loop.run_until_complete(EventNode.get_all_events())
                
                # Processing
                category_prices = {}
                valid_cats = list(self.categories.keys())[:8] if self.categories else []
                
                for cat in valid_cats:
                    cat_events = [e for e in events if e.category == cat and e.price and e.price > 0]
                    if cat_events:
                        category_prices[cat] = np.mean([e.price for e in cat_events])
                
                # Sort
                sorted_cats = sorted(category_prices.items(), key=lambda x: x[1], reverse=True)
                cats = [c[0] for c in sorted_cats]
                prices = [c[1] for c in sorted_cats]
                
                # Plot in main thread
                self.root.after(0, lambda: self._draw_price_chart(cats, prices))
            except Exception as e:
                print(f"Error fetching price analysis: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to load price analysis"))

        threading.Thread(target=fetch_data, daemon=True).start()

    def _draw_price_chart(self, cats, prices):
        """Draw price chart in main thread."""
        for widget in self.tab2.winfo_children():
            widget.destroy()

        if not cats:
             tk.Label(self.tab2, text="No Data", bg=THEME["bg_main"], fg="white").pack(pady=50)
             return

        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Fill Between (Area Chart)
        x = range(len(cats))
        ax.plot(x, prices, color=THEME["accent_1"], linewidth=3, marker='o')
        ax.fill_between(x, prices, color=THEME["accent_1"], alpha=0.2)
        
        ax.set_xticks(x)
        ax.set_xticklabels(cats, rotation=45, ha='right')
        ax.set_title('Average Price by Category', fontweight='bold', pad=20)
        ax.grid(True, linestyle='--', alpha=0.1)
        
        # Remove spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        self._embed_plot(fig, self.tab2)

    def plot_box_plot(self):
        """Plot stylish box plot."""
        for widget in self.tab3.winfo_children():
            widget.destroy()

        loader = tk.Label(self.tab3, text="Loading...", bg=THEME["bg_main"], fg=THEME["fg_text"])
        loader.pack(pady=50)

        def fetch_data():
            try:
                import sys
                sys.path.insert(0, str(project_root))
                from src.models.event import EventNode

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                events = loop.run_until_complete(EventNode.get_all_events())
                prices = [float(e.price) for e in events if e.price and str(e.price).replace('.', '', 1).isdigit() and float(e.price) > 0]
                
                self.root.after(0, lambda: self._draw_box_plot(prices))
            except Exception as e:
                print(f"Error fetching box plot data: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", "Failed to load price distribution"))

        threading.Thread(target=fetch_data, daemon=True).start()

    def _draw_box_plot(self, prices):
        """Draw box plot in main thread."""
        for widget in self.tab3.winfo_children():
            widget.destroy()

        if not prices:
             tk.Label(self.tab3, text="No Data", bg=THEME["bg_main"], fg="white").pack(pady=50)
             return

        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Custom Box Plot
        boxprops = dict(linestyle='-', linewidth=2, color=THEME["accent_2"], facecolor=THEME["accent_2"], alpha=0.5)
        medianprops = dict(linestyle='-', linewidth=2.5, color=THEME["accent_warm"])
        whiskerprops = dict(color="white", linewidth=1.5)
        capprops = dict(color="white", linewidth=1.5)
        flierprops = dict(marker='o', markerfacecolor=THEME["accent_danger"], markersize=5, linestyle='none')

        ax.boxplot([prices], vert=False, patch_artist=True, 
                  boxprops=boxprops, medianprops=medianprops,
                  whiskerprops=whiskerprops, capprops=capprops,
                  flierprops=flierprops, widths=0.5)
        
        ax.set_yticklabels([])
        ax.set_xlabel('Price (TL)')
        ax.set_title('Price Distribution', fontweight='bold', pad=20)
        
        plt.tight_layout()
        self._embed_plot(fig, self.tab3)

    def _embed_plot(self, fig, parent):
        """Helper to embed plot."""
        for widget in parent.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # --- Actions ---
    def start_scraping(self):
        if messagebox.askyesno("Start Scraping", "Start web scraping?\n\nThis may take several minutes."):
            def run():
                subprocess.run(["make", "scrape"], cwd=str(project_root))
                self.root.after(0, lambda: messagebox.showinfo("Complete", "Scraping completed!"))
                self.root.after(0, self.load_data)
            threading.Thread(target=run, daemon=True).start()
            messagebox.showinfo("Started", "Scraping started in background...")

    def run_ai(self):
        if messagebox.askyesno("AI Enrichment", "Generate AI summaries?\n\nThis takes time using Ollama."):
            def run():
                subprocess.run(["make", "ai-enrich"], cwd=str(project_root))
                self.root.after(0, lambda: messagebox.showinfo("Complete", "AI enrichment completed!"))
                self.root.after(0, self.load_data)
            threading.Thread(target=run, daemon=True).start()
            messagebox.showinfo("Started", "AI enrichment started...")

    def run_analysis(self):
        if messagebox.askyesno("Analysis", "Run statistical analysis?"):
            def run():
                subprocess.run(["make", "analyze"], cwd=str(project_root))
                self.root.after(0, lambda: messagebox.showinfo("Complete", "Analysis Report Generated!"))
            threading.Thread(target=run, daemon=True).start()
    
    def clear_data(self):
        if messagebox.askyesno("Clear Data", "Are you sure you want to delete ALL data?"):
            def run():
                subprocess.run(["make", "clean-data"], cwd=str(project_root))
                self.root.after(0, lambda: messagebox.showinfo("Complete", "Database cleared."))
                self.root.after(0, self.load_data)
            threading.Thread(target=run, daemon=True).start()

def main():
    try:
        root = tk.Tk()
        app = EventGraphDashboard(root)
        root.mainloop()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
