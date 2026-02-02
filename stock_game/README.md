# Stock Market Simulation Game

A stock market simulation game where players control a company and make decisions that affect their stock price over time. Features a clean, modern UI with a blue and black theme.

## Features

- **Dynamic Stock Market**: Watch your company's stock price change based on your decisions
- **Event System**: Face multiple-choice events each turn that affect your company's valuation
- **Investor System**: Seek funding from investors who take equity in exchange for valuation boosts
- **IPO Option**: Take your company public when ready
- **Expectations**: Meet investor expectations or face penalties (public companies only)
- **Beautiful UI**: Modern interface with real-time stock price graphing

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)
- matplotlib

## Installation

1. Navigate to the `stock_game` directory:
   ```bash
   cd stock_game
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

Run the game using Python:

```bash
python main.py
```

Or make it executable and run directly (Unix/Linux/Mac):

```bash
chmod +x main.py
./main.py
```

## How to Play

### Game Setup

When you start the game, you'll be asked to:
1. Enter your **Company Name**
2. Enter your **Founder Name**
3. Select an **Industry** (Tech, Retail, Pharma, Finance, Manufacturing, or Media)
4. Choose a **Difficulty Level**:
   - **Easy**: Better investor offers, lower expectations
   - **Medium**: Standard game balance
   - **Hard**: Worse investor offers, higher expectations

### Starting Conditions

- **Valuation**: $100,000
- **Shares**: 1,000,000
- **Share Price**: ~$0.10
- **Your Ownership**: 100%
- **Status**: Private

### Gameplay

Each turn represents a short period of time. You can take one of these actions:

1. **Seek Investors** (available every 3 turns)
   - Choose from 3 investor offers
   - Each investor takes a percentage of your company and boosts your valuation
   - Dilutes your ownership but increases company value

2. **Skip Turn**
   - Advance to the next turn without taking action

3. **Analyze**
   - View detailed company statistics
   - Check your ownership percentage, market cap, share count, etc.

4. **Go IPO** (only when private)
   - Take your company public
   - Choose what percentage of shares to offer (minimum 10%)
   - After IPO, you'll face investor expectations every 10 turns

### Events

After each action, you'll face an event with multiple choices:
- **Product launches**
- **Economic changes**
- **Competitor actions**
- **Data breaches**
- **And many more!**

Each choice affects your stock price/valuation differently. Choose wisely!

### Investor Expectations (Public Companies)

Once you go public, every 10 turns:
- The game calculates an **expected stock price** based on:
  - Your past performance
  - Difficulty level
- If your actual stock price is **below expectations**: -10% penalty
- If you meet or exceed expectations: No penalty

### Win/Lose Conditions

- **Lose**: Your market cap reaches $0 (Game Over)
- **Win**: Survive as long as possible and grow your company!

## Tips

- Early on, focus on growing your valuation before going public
- Don't dilute your ownership too much - keep control of your company
- Pay attention to event choices - some are clearly better than others
- Once public, manage expectations carefully
- Balance risk and reward in your decisions

## Game Controls

- Use mouse to click buttons and make selections
- The graph automatically updates to show your stock price history
- All game actions are done through intuitive modal windows

## Troubleshooting

### Tkinter not found
If you get an error about Tkinter not being found:

- **Ubuntu/Debian**: `sudo apt-get install python3-tk`
- **Fedora**: `sudo dnf install python3-tkinter`
- **macOS**: Tkinter should be included with Python
- **Windows**: Tkinter should be included with Python

### matplotlib not found
Install it with:
```bash
pip install matplotlib
```

## Technical Details

- **Language**: Python 3
- **GUI Framework**: Tkinter
- **Graphing**: matplotlib
- **Architecture**: Modular design with separate files for game logic, UI, events, and investors

## File Structure

```
stock_game/
├── main.py          # Entry point
├── game.py          # Core game logic
├── ui.py            # UI/GUI code
├── events.py        # Event definitions and logic
├── investors.py     # Investor generation logic
├── README.md        # This file
└── requirements.txt # Dependencies
```

## Credits

Created as a stock market simulation game with educational and entertainment purposes.
