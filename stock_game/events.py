"""
Event system for stock market simulation game.
"""
import random


class Event:
    """Represents a single event with multiple choice options."""
    
    def __init__(self, title, description, choices):
        """
        title: Event title
        description: Event description
        choices: List of tuples (choice_text, valuation_change_percent)
        """
        self.title = title
        self.description = description
        self.choices = choices  # [(text, percentage), ...]


def get_random_event(difficulty, is_public):
    """
    Get a random event based on game state.
    difficulty: 'Easy', 'Medium', 'Hard'
    is_public: Whether company is public
    """
    
    # Difficulty affects event severity
    severity_multipliers = {
        'Easy': 0.7,
        'Medium': 1.0,
        'Hard': 1.3
    }
    multiplier = severity_multipliers.get(difficulty, 1.0)
    
    all_events = [
        Event(
            "Product Launch",
            "Your company is launching a new product. How will you market it?",
            [
                ("Aggressive marketing campaign", 8 * multiplier),
                ("Moderate marketing with focus on quality", 5 * multiplier),
                ("Minimal marketing, let word-of-mouth spread", 2 * multiplier),
                ("Delay launch for more testing", -3 * multiplier)
            ]
        ),
        Event(
            "Economic Downturn",
            "The economy is entering a recession. How will your company respond?",
            [
                ("Cut costs and lay off employees", -5 * multiplier),
                ("Maintain current operations", -8 * multiplier),
                ("Invest in growth despite recession", -12 * multiplier),
                ("Pivot to recession-proof products", -3 * multiplier)
            ]
        ),
        Event(
            "Competitor Emerges",
            "A well-funded competitor has entered your market. Your response?",
            [
                ("Price war - slash prices", -7 * multiplier),
                ("Improve product quality", 3 * multiplier),
                ("Ignore them and focus on existing customers", -4 * multiplier),
                ("Acquire the competitor", 6 * multiplier)
            ]
        ),
        Event(
            "Data Breach",
            "Your company experienced a data breach. How do you handle it?",
            [
                ("Cover it up and hope no one notices", -15 * multiplier),
                ("Minimal disclosure, quiet fix", -10 * multiplier),
                ("Full transparency and immediate action", -5 * multiplier),
                ("Hire top security firm and overhaul systems", -3 * multiplier)
            ]
        ),
        Event(
            "Viral Social Media",
            "Your company went viral on social media. What's your strategy?",
            [
                ("Capitalize with aggressive expansion", 12 * multiplier),
                ("Steady growth, maintain quality", 8 * multiplier),
                ("Stay cautious, it might be a fad", 4 * multiplier),
                ("Ignore the hype completely", 2 * multiplier)
            ]
        ),
        Event(
            "Key Employee Departure",
            "Your top engineer is leaving. How do you respond?",
            [
                ("Counter-offer with huge salary increase", -2 * multiplier),
                ("Let them go, hire replacement", -6 * multiplier),
                ("Promote from within", -3 * multiplier),
                ("Restructure team to compensate", -5 * multiplier)
            ]
        ),
        Event(
            "Regulatory Changes",
            "New regulations affect your industry. What's your approach?",
            [
                ("Fight regulations through lobbying", -8 * multiplier),
                ("Comply immediately, go above and beyond", 5 * multiplier),
                ("Minimal compliance only", -3 * multiplier),
                ("Use as opportunity to differentiate", 7 * multiplier)
            ]
        ),
        Event(
            "Supply Chain Issues",
            "Your suppliers are having major delays. How do you adapt?",
            [
                ("Find alternative suppliers at higher cost", -4 * multiplier),
                ("Wait it out, delay shipments", -8 * multiplier),
                ("Build your own supply chain", -6 * multiplier),
                ("Redesign product to use different materials", -2 * multiplier)
            ]
        ),
        Event(
            "Partnership Opportunity",
            "A large company wants to partner with you. Your decision?",
            [
                ("Full partnership, integrate deeply", 10 * multiplier),
                ("Limited partnership, maintain independence", 6 * multiplier),
                ("Decline, stay fully independent", 2 * multiplier),
                ("Negotiate for acquisition instead", 8 * multiplier)
            ]
        ),
        Event(
            "Technology Breakthrough",
            "Your team made a significant technical breakthrough. How do you use it?",
            [
                ("Patent and license to others", 6 * multiplier),
                ("Build new products around it", 10 * multiplier),
                ("Keep it secret and use internally", 7 * multiplier),
                ("Open source it for goodwill", 4 * multiplier)
            ]
        ),
        Event(
            "Market Expansion",
            "Opportunity to expand to international markets. Your strategy?",
            [
                ("Aggressive expansion to multiple countries", 8 * multiplier),
                ("Careful expansion to one country first", 5 * multiplier),
                ("Stay focused on domestic market", 2 * multiplier),
                ("Partner with local companies for expansion", 7 * multiplier)
            ]
        ),
        Event(
            "Negative Press",
            "Your company received negative press coverage. How do you respond?",
            [
                ("Ignore it completely", -10 * multiplier),
                ("Issue a strong denial", -7 * multiplier),
                ("Address concerns transparently", -3 * multiplier),
                ("Launch PR campaign to change narrative", -4 * multiplier)
            ]
        ),
        Event(
            "Employee Strike",
            "Workers are threatening to strike over conditions. Your response?",
            [
                ("Meet all demands immediately", -5 * multiplier),
                ("Negotiate a compromise", -3 * multiplier),
                ("Refuse and hire replacements", -12 * multiplier),
                ("Improve conditions proactively", -2 * multiplier)
            ]
        ),
        Event(
            "Innovation Crisis",
            "Company hasn't innovated in a while. What do you do?",
            [
                ("Massive R&D investment", 7 * multiplier),
                ("Acquire innovative startups", 9 * multiplier),
                ("Hire new talent and leadership", 5 * multiplier),
                ("Continue with current strategy", -4 * multiplier)
            ]
        ),
        Event(
            "Customer Backlash",
            "Customers are unhappy with recent changes. How do you fix it?",
            [
                ("Revert all changes immediately", -2 * multiplier),
                ("Listen to feedback and adjust", 3 * multiplier),
                ("Stand firm, they'll adapt", -8 * multiplier),
                ("Offer compensation and apologize", -1 * multiplier)
            ]
        ),
    ]
    
    # Add public company specific events
    if is_public:
        all_events.extend([
            Event(
                "Analyst Downgrade",
                "A major analyst downgraded your stock. How do you respond?",
                [
                    ("Aggressive PR to dispute claims", -3 * multiplier),
                    ("Address their concerns in next earnings call", -5 * multiplier),
                    ("Ignore and focus on fundamentals", -7 * multiplier),
                    ("Accelerate growth initiatives", -2 * multiplier)
                ]
            ),
            Event(
                "Earnings Call",
                "It's earnings call time. How do you present results?",
                [
                    ("Overly optimistic, hype future", 6 * multiplier),
                    ("Balanced and realistic", 4 * multiplier),
                    ("Conservative, under-promise", 2 * multiplier),
                    ("Avoid call, just release numbers", -3 * multiplier)
                ]
            ),
            Event(
                "Activist Investor",
                "An activist investor is pushing for changes. Your response?",
                [
                    ("Fight them completely", -8 * multiplier),
                    ("Compromise on some demands", -3 * multiplier),
                    ("Embrace their suggestions", 5 * multiplier),
                    ("Buyback shares to reduce their influence", -5 * multiplier)
                ]
            ),
        ])
    
    return random.choice(all_events)
