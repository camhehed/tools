"""
GUI for stock market simulation game using Tkinter and matplotlib.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from game import GameState
from events import get_random_event
from investors import generate_investor_offers, format_offer_description


# Color scheme - blue and black
BG_COLOR = "#0a0e27"
FG_COLOR = "#ffffff"
BUTTON_COLOR = "#1e3a8a"
BUTTON_HOVER = "#2563eb"
ACCENT_COLOR = "#3b82f6"
GRAPH_COLOR = "#60a5fa"


class StockGameUI:
    """Main UI class for the stock market simulation game."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Stock Market Simulation Game")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_COLOR)
        
        self.game = None
        self.canvas_widget = None
        
        # Show setup screen
        self.show_setup_screen()
        
    def show_setup_screen(self):
        """Display game setup screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        setup_frame = tk.Frame(self.root, bg=BG_COLOR)
        setup_frame.pack(expand=True)
        
        # Title
        title = tk.Label(setup_frame, text="Stock Market Simulation", 
                        font=("Arial", 32, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        title.pack(pady=20)
        
        # Company name
        tk.Label(setup_frame, text="Company Name:", font=("Arial", 14),
                bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        company_entry = tk.Entry(setup_frame, font=("Arial", 12), width=30)
        company_entry.pack(pady=5)
        company_entry.insert(0, "TechCorp")
        
        # Founder name
        tk.Label(setup_frame, text="Founder Name:", font=("Arial", 14),
                bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        founder_entry = tk.Entry(setup_frame, font=("Arial", 12), width=30)
        founder_entry.pack(pady=5)
        founder_entry.insert(0, "John Doe")
        
        # Industry
        tk.Label(setup_frame, text="Industry:", font=("Arial", 14),
                bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        industry_var = tk.StringVar(value="Tech")
        industries = ["Tech", "Retail", "Pharma", "Finance", "Manufacturing", "Media"]
        industry_menu = ttk.Combobox(setup_frame, textvariable=industry_var,
                                    values=industries, font=("Arial", 12), 
                                    state="readonly", width=28)
        industry_menu.pack(pady=5)
        
        # Difficulty
        tk.Label(setup_frame, text="Difficulty:", font=("Arial", 14),
                bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        difficulty_var = tk.StringVar(value="Medium")
        difficulty_frame = tk.Frame(setup_frame, bg=BG_COLOR)
        difficulty_frame.pack(pady=5)
        
        for diff in ["Easy", "Medium", "Hard"]:
            rb = tk.Radiobutton(difficulty_frame, text=diff, variable=difficulty_var,
                              value=diff, font=("Arial", 12), bg=BG_COLOR, 
                              fg=FG_COLOR, selectcolor=BG_COLOR, 
                              activebackground=BG_COLOR, activeforeground=ACCENT_COLOR)
            rb.pack(side=tk.LEFT, padx=10)
        
        # Start button
        def start_game():
            company = company_entry.get().strip()
            founder = founder_entry.get().strip()
            industry = industry_var.get()
            difficulty = difficulty_var.get()
            
            if not company or not founder:
                messagebox.showerror("Error", "Please enter company and founder names")
                return
            
            self.game = GameState(company, founder, industry, difficulty)
            self.show_game_screen()
        
        start_btn = tk.Button(setup_frame, text="Start Game", font=("Arial", 16, "bold"),
                             bg=BUTTON_COLOR, fg=FG_COLOR, command=start_game,
                             padx=30, pady=10, relief=tk.FLAT,
                             activebackground=BUTTON_HOVER, activeforeground=FG_COLOR)
        start_btn.pack(pady=30)
    
    def show_game_screen(self):
        """Display main game screen."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top info bar
        info_frame = tk.Frame(main_frame, bg=BG_COLOR)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_labels = {}
        
        # Company name and status
        company_text = f"{self.game.company_name} ({'Public' if self.game.is_public else 'Private'})"
        self.info_labels['company'] = tk.Label(info_frame, text=company_text,
                                               font=("Arial", 16, "bold"),
                                               bg=BG_COLOR, fg=ACCENT_COLOR)
        self.info_labels['company'].pack(side=tk.LEFT, padx=10)
        
        # Turn
        self.info_labels['turn'] = tk.Label(info_frame, text=f"Turn: {self.game.turn}",
                                           font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR)
        self.info_labels['turn'].pack(side=tk.LEFT, padx=10)
        
        # Share price
        price = self.game.get_share_price()
        self.info_labels['price'] = tk.Label(info_frame, 
                                             text=f"Share Price: ${price:.4f}",
                                             font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR)
        self.info_labels['price'].pack(side=tk.LEFT, padx=10)
        
        # Ownership
        ownership = self.game.get_player_ownership()
        self.info_labels['ownership'] = tk.Label(info_frame,
                                                 text=f"Your Ownership: {ownership:.1f}%",
                                                 font=("Arial", 14), bg=BG_COLOR, fg=FG_COLOR)
        self.info_labels['ownership'].pack(side=tk.LEFT, padx=10)
        
        # Graph frame
        graph_frame = tk.Frame(main_frame, bg=BG_COLOR, relief=tk.SOLID, borderwidth=1)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.setup_graph(graph_frame)
        
        # Action buttons frame
        button_frame = tk.Frame(main_frame, bg=BG_COLOR)
        button_frame.pack(fill=tk.X)
        
        # Investors button
        self.investors_btn = tk.Button(button_frame, text="Seek Investors",
                                       font=("Arial", 12, "bold"), bg=BUTTON_COLOR,
                                       fg=FG_COLOR, command=self.show_investors_modal,
                                       padx=20, pady=10, relief=tk.FLAT,
                                       activebackground=BUTTON_HOVER,
                                       activeforeground=FG_COLOR)
        self.investors_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Skip button
        skip_btn = tk.Button(button_frame, text="Skip Turn",
                            font=("Arial", 12, "bold"), bg=BUTTON_COLOR,
                            fg=FG_COLOR, command=self.skip_turn,
                            padx=20, pady=10, relief=tk.FLAT,
                            activebackground=BUTTON_HOVER,
                            activeforeground=FG_COLOR)
        skip_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Analyze button
        analyze_btn = tk.Button(button_frame, text="Analyze",
                               font=("Arial", 12, "bold"), bg=BUTTON_COLOR,
                               fg=FG_COLOR, command=self.show_analyze_modal,
                               padx=20, pady=10, relief=tk.FLAT,
                               activebackground=BUTTON_HOVER,
                               activeforeground=FG_COLOR)
        analyze_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # IPO button
        self.ipo_btn = tk.Button(button_frame, text="Go IPO",
                                font=("Arial", 12, "bold"), bg=BUTTON_COLOR,
                                fg=FG_COLOR, command=self.show_ipo_modal,
                                padx=20, pady=10, relief=tk.FLAT,
                                activebackground=BUTTON_HOVER,
                                activeforeground=FG_COLOR)
        self.ipo_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.update_ui()
    
    def setup_graph(self, parent):
        """Setup matplotlib graph for stock price."""
        fig = Figure(figsize=(10, 5), facecolor=BG_COLOR)
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor(BG_COLOR)
        self.ax.set_title("Stock Price History", color=FG_COLOR, fontsize=16, pad=20)
        self.ax.set_xlabel("Turn", color=FG_COLOR, fontsize=12)
        self.ax.set_ylabel("Share Price ($)", color=FG_COLOR, fontsize=12)
        self.ax.tick_params(colors=FG_COLOR)
        self.ax.spines['bottom'].set_color(FG_COLOR)
        self.ax.spines['left'].set_color(FG_COLOR)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(True, alpha=0.2, color=FG_COLOR)
        
        self.canvas_widget = FigureCanvasTkAgg(fig, parent)
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.update_graph()
    
    def update_graph(self):
        """Update the stock price graph."""
        self.ax.clear()
        self.ax.set_facecolor(BG_COLOR)
        self.ax.set_title("Stock Price History", color=FG_COLOR, fontsize=16, pad=20)
        self.ax.set_xlabel("Turn", color=FG_COLOR, fontsize=12)
        self.ax.set_ylabel("Share Price ($)", color=FG_COLOR, fontsize=12)
        self.ax.tick_params(colors=FG_COLOR)
        self.ax.spines['bottom'].set_color(FG_COLOR)
        self.ax.spines['left'].set_color(FG_COLOR)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.grid(True, alpha=0.2, color=FG_COLOR)
        
        self.ax.plot(self.game.turn_history, self.game.price_history,
                    color=GRAPH_COLOR, linewidth=2, marker='o', markersize=4)
        
        self.canvas_widget.draw()
    
    def update_ui(self):
        """Update all UI elements."""
        # Update info labels
        company_text = f"{self.game.company_name} ({'Public' if self.game.is_public else 'Private'})"
        self.info_labels['company'].config(text=company_text)
        self.info_labels['turn'].config(text=f"Turn: {self.game.turn}")
        
        price = self.game.get_share_price()
        self.info_labels['price'].config(text=f"Share Price: ${price:.4f}")
        
        ownership = self.game.get_player_ownership()
        self.info_labels['ownership'].config(text=f"Your Ownership: {ownership:.1f}%")
        
        # Update button states
        if self.game.can_seek_investors():
            self.investors_btn.config(state=tk.NORMAL)
        else:
            self.investors_btn.config(state=tk.DISABLED)
        
        if self.game.is_public:
            self.ipo_btn.config(state=tk.DISABLED)
        else:
            self.ipo_btn.config(state=tk.NORMAL)
        
        # Update graph
        self.update_graph()
        
        # Check game over
        if self.game.is_game_over():
            self.show_game_over()
    
    def show_investors_modal(self):
        """Show modal for selecting investors."""
        modal = tk.Toplevel(self.root)
        modal.title("Seek Investors")
        modal.geometry("600x500")
        modal.configure(bg=BG_COLOR)
        modal.transient(self.root)
        modal.grab_set()
        
        tk.Label(modal, text="Select an Investor", font=("Arial", 18, "bold"),
                bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        
        offers = generate_investor_offers(self.game.valuation, self.game.difficulty)
        
        for i, offer in enumerate(offers):
            offer_frame = tk.Frame(modal, bg=BG_COLOR, relief=tk.SOLID, borderwidth=1)
            offer_frame.pack(fill=tk.X, padx=20, pady=10)
            
            desc = format_offer_description(offer, self.game.valuation)
            tk.Label(offer_frame, text=desc, font=("Arial", 11),
                    bg=BG_COLOR, fg=FG_COLOR, justify=tk.LEFT).pack(pady=10, padx=10)
            
            def accept_offer(o=offer):
                self.game.seek_investor(o.equity_percent, o.valuation_boost)
                modal.destroy()
                self.process_turn()
            
            tk.Button(offer_frame, text="Accept", font=("Arial", 11, "bold"),
                     bg=BUTTON_COLOR, fg=FG_COLOR, command=accept_offer,
                     padx=15, pady=5, relief=tk.FLAT,
                     activebackground=BUTTON_HOVER,
                     activeforeground=FG_COLOR).pack(pady=5)
        
        # Cancel button
        tk.Button(modal, text="Cancel", font=("Arial", 12, "bold"),
                 bg="#6b7280", fg=FG_COLOR, command=modal.destroy,
                 padx=20, pady=8, relief=tk.FLAT).pack(pady=10)
    
    def show_ipo_modal(self):
        """Show modal for going public."""
        modal = tk.Toplevel(self.root)
        modal.title("Go Public (IPO)")
        modal.geometry("500x400")
        modal.configure(bg=BG_COLOR)
        modal.transient(self.root)
        modal.grab_set()
        
        tk.Label(modal, text="Initial Public Offering", font=("Arial", 18, "bold"),
                bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        
        tk.Label(modal, text="What percentage of shares do you want to offer?",
                font=("Arial", 12), bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)
        
        tk.Label(modal, text="(Minimum: 10%, Maximum: 100%)",
                font=("Arial", 10), bg=BG_COLOR, fg="#9ca3af").pack(pady=5)
        
        # Current stats
        ownership = self.game.get_player_ownership()
        tk.Label(modal, text=f"Current Ownership: {ownership:.1f}%",
                font=("Arial", 11), bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)
        
        # Slider
        percent_var = tk.DoubleVar(value=20)
        
        def update_label(*args):
            new_ownership = ownership - percent_var.get()
            result_label.config(text=f"New Ownership: {new_ownership:.1f}%")
        
        result_label = tk.Label(modal, text=f"New Ownership: {ownership - 20:.1f}%",
                               font=("Arial", 11, "bold"), bg=BG_COLOR, fg=ACCENT_COLOR)
        result_label.pack(pady=10)
        
        scale = tk.Scale(modal, from_=10, to=100, orient=tk.HORIZONTAL,
                        variable=percent_var, font=("Arial", 10),
                        bg=BG_COLOR, fg=FG_COLOR, troughcolor=BUTTON_COLOR,
                        highlightbackground=BG_COLOR, command=update_label,
                        length=300)
        scale.pack(pady=10)
        
        def go_public():
            percent = percent_var.get()
            if self.game.go_public(percent):
                modal.destroy()
                messagebox.showinfo("IPO Success", 
                                  f"Congratulations! Your company is now public!\n"
                                  f"You offered {percent:.1f}% of shares.")
                self.process_turn()
            else:
                messagebox.showerror("IPO Failed", 
                                   "IPO failed! You would lose control of the company.")
        
        # Buttons
        btn_frame = tk.Frame(modal, bg=BG_COLOR)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Go Public", font=("Arial", 12, "bold"),
                 bg=BUTTON_COLOR, fg=FG_COLOR, command=go_public,
                 padx=20, pady=8, relief=tk.FLAT,
                 activebackground=BUTTON_HOVER,
                 activeforeground=FG_COLOR).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", font=("Arial", 12, "bold"),
                 bg="#6b7280", fg=FG_COLOR, command=modal.destroy,
                 padx=20, pady=8, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
    
    def show_analyze_modal(self):
        """Show detailed analysis modal."""
        modal = tk.Toplevel(self.root)
        modal.title("Company Analysis")
        modal.geometry("500x400")
        modal.configure(bg=BG_COLOR)
        modal.transient(self.root)
        modal.grab_set()
        
        tk.Label(modal, text="Company Analysis", font=("Arial", 18, "bold"),
                bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        
        # Stats
        stats_frame = tk.Frame(modal, bg=BG_COLOR)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        stats = [
            ("Company Name:", self.game.company_name),
            ("Founder:", self.game.founder_name),
            ("Industry:", self.game.industry),
            ("Difficulty:", self.game.difficulty),
            ("Status:", "Public" if self.game.is_public else "Private"),
            ("Turn:", str(self.game.turn)),
            ("Market Cap:", f"${self.game.get_market_cap():,.2f}"),
            ("Valuation:", f"${self.game.valuation:,.2f}"),
            ("Total Shares:", f"{self.game.shares:,.0f}"),
            ("Your Shares:", f"{self.game.player_shares:,.0f}"),
            ("Your Ownership:", f"{self.game.get_player_ownership():.2f}%"),
            ("Share Price:", f"${self.game.get_share_price():.4f}"),
        ]
        
        for label, value in stats:
            row = tk.Frame(stats_frame, bg=BG_COLOR)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=label, font=("Arial", 11), bg=BG_COLOR,
                    fg="#9ca3af", anchor=tk.W, width=15).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 11, "bold"), bg=BG_COLOR,
                    fg=FG_COLOR, anchor=tk.W).pack(side=tk.LEFT)
        
        tk.Button(modal, text="Close", font=("Arial", 12, "bold"),
                 bg=BUTTON_COLOR, fg=FG_COLOR, command=modal.destroy,
                 padx=30, pady=8, relief=tk.FLAT,
                 activebackground=BUTTON_HOVER,
                 activeforeground=FG_COLOR).pack(pady=20)
    
    def skip_turn(self):
        """Skip turn without action."""
        self.process_turn()
    
    def process_turn(self):
        """Process a turn - show event, apply changes, advance turn."""
        # Get random event
        event = get_random_event(self.game.difficulty, self.game.is_public)
        self.show_event_modal(event)
    
    def show_event_modal(self, event):
        """Show event modal with choices."""
        modal = tk.Toplevel(self.root)
        modal.title("Event")
        modal.geometry("600x500")
        modal.configure(bg=BG_COLOR)
        modal.transient(self.root)
        modal.grab_set()
        
        tk.Label(modal, text=event.title, font=("Arial", 18, "bold"),
                bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=20)
        
        tk.Label(modal, text=event.description, font=("Arial", 12),
                bg=BG_COLOR, fg=FG_COLOR, wraplength=500).pack(pady=10)
        
        tk.Label(modal, text="Choose your response:", font=("Arial", 11, "bold"),
                bg=BG_COLOR, fg=FG_COLOR).pack(pady=10)
        
        for choice_text, impact in event.choices:
            choice_frame = tk.Frame(modal, bg=BG_COLOR, relief=tk.SOLID, borderwidth=1)
            choice_frame.pack(fill=tk.X, padx=30, pady=5)
            
            tk.Label(choice_frame, text=choice_text, font=("Arial", 10),
                    bg=BG_COLOR, fg=FG_COLOR, wraplength=450,
                    justify=tk.LEFT).pack(pady=5, padx=10, anchor=tk.W)
            
            impact_color = "#10b981" if impact > 0 else "#ef4444"
            impact_text = f"{impact:+.1f}% valuation"
            tk.Label(choice_frame, text=impact_text, font=("Arial", 9),
                    bg=BG_COLOR, fg=impact_color).pack(pady=2, padx=10, anchor=tk.W)
            
            def make_choice(imp=impact):
                self.game.apply_valuation_change(imp)
                self.game.advance_turn()
                modal.destroy()
                self.check_expectations_and_update()
            
            tk.Button(choice_frame, text="Select", font=("Arial", 9, "bold"),
                     bg=BUTTON_COLOR, fg=FG_COLOR, command=make_choice,
                     padx=10, pady=3, relief=tk.FLAT,
                     activebackground=BUTTON_HOVER,
                     activeforeground=FG_COLOR).pack(pady=5)
    
    def check_expectations_and_update(self):
        """Check expectations and update UI."""
        should_check, expected_price, penalty = self.game.check_expectations()
        
        if should_check:
            current_price = self.game.get_share_price()
            if penalty:
                messagebox.showwarning(
                    "Missed Expectations",
                    f"Your stock failed to meet investor expectations!\n\n"
                    f"Expected: ${expected_price:.4f}\n"
                    f"Actual: ${current_price:.4f}\n\n"
                    f"Your stock price dropped by 10% as a penalty."
                )
            else:
                messagebox.showinfo(
                    "Met Expectations",
                    f"Great job! You met investor expectations!\n\n"
                    f"Expected: ${expected_price:.4f}\n"
                    f"Actual: ${current_price:.4f}"
                )
        
        self.update_ui()
    
    def show_game_over(self):
        """Show game over screen."""
        messagebox.showerror(
            "Game Over",
            f"Your company's market cap has reached $0!\n\n"
            f"You lasted {self.game.turn} turns.\n"
            f"Final valuation: ${self.game.valuation:,.2f}"
        )
        self.root.quit()
    
    def run(self):
        """Start the UI main loop."""
        self.root.mainloop()
