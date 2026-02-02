"""
Core game logic for stock market simulation game.
"""
import random


class GameState:
    """Manages the state of the stock market simulation game."""
    
    def __init__(self, company_name, founder_name, industry, difficulty):
        self.company_name = company_name
        self.founder_name = founder_name
        self.industry = industry
        self.difficulty = difficulty  # 'Easy', 'Medium', 'Hard'
        
        # Starting conditions
        self.valuation = 100000
        self.shares = 1000000
        self.player_shares = 1000000
        self.is_public = False
        self.turn = 0
        self.last_investor_turn = -3  # Can seek investor immediately
        
        # Track history for graph
        self.price_history = [self.get_share_price()]
        self.turn_history = [0]
        
        # For expectations (public companies)
        self.last_expectation_turn = 0
        self.last_expectation_price = self.get_share_price()
        
    def get_share_price(self):
        """Calculate current share price."""
        if self.shares == 0:
            return 0
        return self.valuation / self.shares
    
    def get_player_ownership(self):
        """Calculate player ownership percentage."""
        if self.shares == 0:
            return 0
        return (self.player_shares / self.shares) * 100
    
    def get_market_cap(self):
        """Get current market cap (same as valuation)."""
        return self.valuation
    
    def can_seek_investors(self):
        """Check if player can seek investors this turn."""
        return self.turn - self.last_investor_turn >= 3
    
    def advance_turn(self):
        """Advance to next turn and record price history."""
        self.turn += 1
        self.price_history.append(self.get_share_price())
        self.turn_history.append(self.turn)
    
    def apply_valuation_change(self, percentage_change):
        """Apply a percentage change to valuation."""
        self.valuation = max(0, self.valuation * (1 + percentage_change / 100))
        
    def seek_investor(self, equity_percent, valuation_boost):
        """
        Accept an investor's offer.
        equity_percent: percentage of company investor takes
        valuation_boost: amount added to valuation
        """
        self.last_investor_turn = self.turn
        
        # Increase valuation
        self.valuation += valuation_boost
        
        # Calculate new shares to give investor
        investor_shares = (self.shares * equity_percent) / (100 - equity_percent)
        self.shares += investor_shares
        
    def go_public(self, percent_to_offer):
        """
        Take company public by offering a percentage of shares.
        percent_to_offer: percentage of total shares to offer publicly
        """
        if self.is_public:
            return False
        
        if percent_to_offer < 10 or percent_to_offer > 100:
            return False
        
        # Calculate shares to offer
        shares_to_offer = (self.shares * percent_to_offer) / 100
        self.player_shares -= shares_to_offer
        
        # Check if player lost control
        if self.get_player_ownership() < 0:
            return False
        
        self.is_public = True
        self.last_expectation_turn = self.turn
        self.last_expectation_price = self.get_share_price()
        
        return True
    
    def check_expectations(self):
        """
        Check expectations for public companies every 10 turns.
        Returns (should_check, expected_price, penalty_applied)
        """
        if not self.is_public:
            return (False, 0, False)
        
        turns_since_last = self.turn - self.last_expectation_turn
        if turns_since_last < 10:
            return (False, 0, False)
        
        # Calculate expected growth based on past performance
        if self.last_expectation_price > 0:
            actual_growth = ((self.get_share_price() - self.last_expectation_price) 
                           / self.last_expectation_price * 100)
        else:
            actual_growth = 0
        
        # Difficulty affects expectations
        difficulty_multipliers = {'Easy': 1.1, 'Medium': 1.3, 'Hard': 1.5}
        multiplier = difficulty_multipliers.get(self.difficulty, 1.3)
        
        expected_growth = actual_growth * multiplier
        expected_price = self.last_expectation_price * (1 + expected_growth / 100)
        
        # Check if we met expectations
        current_price = self.get_share_price()
        penalty_applied = False
        
        if current_price < expected_price:
            # Apply penalty - drop stock price
            penalty = -10  # 10% penalty
            self.apply_valuation_change(penalty)
            penalty_applied = True
        
        # Update for next expectation period
        self.last_expectation_turn = self.turn
        self.last_expectation_price = self.get_share_price()
        
        return (True, expected_price, penalty_applied)
    
    def is_game_over(self):
        """Check if game is over (market cap reaches 0)."""
        return self.valuation <= 0
