"""
Investor generation logic for stock market simulation game.
"""
import random


class InvestorOffer:
    """Represents an investor offer."""
    
    def __init__(self, name, equity_percent, valuation_boost):
        """
        name: Investor name
        equity_percent: Percentage of company investor wants
        valuation_boost: Dollar amount added to valuation
        """
        self.name = name
        self.equity_percent = equity_percent
        self.valuation_boost = valuation_boost


def generate_investor_offers(current_valuation, difficulty):
    """
    Generate 3 investor offers scaled to current valuation and difficulty.
    
    current_valuation: Current company valuation
    difficulty: 'Easy', 'Medium', 'Hard'
    
    Returns list of 3 InvestorOffer objects
    """
    
    # Difficulty affects how good the offers are
    difficulty_multipliers = {
        'Easy': 1.3,      # Better offers
        'Medium': 1.0,    # Standard offers
        'Hard': 0.7       # Worse offers
    }
    multiplier = difficulty_multipliers.get(difficulty, 1.0)
    
    # Investor names
    investor_names = [
        "Sequoia Capital",
        "Andreessen Horowitz",
        "Tiger Global",
        "Softbank Vision Fund",
        "Benchmark Capital",
        "Accel Partners",
        "Kleiner Perkins",
        "Greylock Partners",
        "Index Ventures",
        "Lightspeed Venture Partners",
        "NEA (New Enterprise Associates)",
        "Founders Fund",
        "GGV Capital",
        "Insight Partners",
        "Bessemer Venture Partners",
        "Wellington Management",
        "Fidelity Investments",
        "BlackRock",
        "Vanguard",
        "T. Rowe Price",
        "Strategic Angel Investor",
        "Private Equity Group",
        "Family Office",
        "Sovereign Wealth Fund"
    ]
    
    offers = []
    used_names = set()
    
    # Generate 3 different types of offers
    offer_templates = [
        # Conservative offer - less equity, less money
        {
            'equity_base': 8,
            'equity_variance': 3,
            'boost_multiplier': 0.3
        },
        # Moderate offer - balanced
        {
            'equity_base': 15,
            'equity_variance': 5,
            'boost_multiplier': 0.6
        },
        # Aggressive offer - more equity, more money
        {
            'equity_base': 25,
            'equity_variance': 7,
            'boost_multiplier': 1.2
        }
    ]
    
    # Shuffle templates for variety
    random.shuffle(offer_templates)
    
    for template in offer_templates:
        # Select unique investor name
        available_names = [n for n in investor_names if n not in used_names]
        if not available_names:
            available_names = investor_names
        name = random.choice(available_names)
        used_names.add(name)
        
        # Calculate equity percentage
        equity = template['equity_base'] + random.randint(-template['equity_variance'], 
                                                           template['equity_variance'])
        equity = max(5, min(40, equity))  # Clamp between 5-40%
        
        # Calculate valuation boost (scales with current valuation)
        base_boost = current_valuation * template['boost_multiplier']
        variance = base_boost * 0.3  # ±30% variance
        boost = base_boost + random.uniform(-variance, variance)
        boost = boost * multiplier  # Apply difficulty multiplier
        boost = max(1000, boost)  # Minimum $1000 boost
        
        offers.append(InvestorOffer(name, round(equity, 1), round(boost, 2)))
    
    return offers


def format_offer_description(offer, current_valuation):
    """
    Format an investor offer for display.
    
    offer: InvestorOffer object
    current_valuation: Current company valuation
    
    Returns formatted string
    """
    new_valuation = current_valuation + offer.valuation_boost
    roi = (offer.valuation_boost / current_valuation) * 100
    
    return (f"{offer.name}\n"
            f"Takes: {offer.equity_percent}% equity\n"
            f"Gives: ${offer.valuation_boost:,.0f}\n"
            f"New Valuation: ${new_valuation:,.0f}\n"
            f"Valuation Boost: +{roi:.1f}%")
