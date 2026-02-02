#!/usr/bin/env python3
"""
Stock Market Simulation Game
Main entry point for the game.
"""

from ui import StockGameUI


def main():
    """Start the stock market simulation game."""
    app = StockGameUI()
    app.run()


if __name__ == "__main__":
    main()
