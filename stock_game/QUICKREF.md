# Stock Market Simulation Game - Quick Reference

## Installation & Running

### Quick Start (Recommended)
```bash
cd stock_game
bash quickstart.sh
```

### Manual Start
```bash
cd stock_game
pip install -r requirements.txt
python3 main.py
```

### System Requirements
- Python 3.7 or higher
- Tkinter (usually included with Python)
- matplotlib (installed via requirements.txt)

## Gameplay Summary

### Starting a Game
1. Enter your company name
2. Enter your founder name
3. Select an industry (cosmetic only)
4. Choose difficulty: Easy, Medium, or Hard

### Actions Each Turn
- **Seek Investors**: Available every 3 turns. Choose from 3 offers that scale with your valuation.
- **Skip Turn**: Advance without taking action.
- **Analyze**: View detailed company statistics.
- **Go IPO**: Take your company public (minimum 10% of shares).

### Events
After each action, you'll face an event with multiple choices. Each choice affects your stock price.

### Going Public
Once public:
- You can no longer seek investors
- Every 10 turns, you'll face investor expectations
- Miss expectations → 10% stock price penalty

### Winning Strategy
- Start by seeking investors to grow valuation
- Make smart event choices
- Go public when you have strong momentum
- Meet or exceed expectations after IPO
- Don't dilute your ownership too much

## Tips
- **Easy Mode**: Better investor offers, lower expectations
- **Medium Mode**: Balanced gameplay
- **Hard Mode**: Worse offers, higher expectations
- Watch your ownership percentage - don't give away too much!
- Some negative events are inevitable - choose the least bad option
- Going public too early can be risky

## Controls
- Use mouse to click buttons
- Type in text fields
- Use slider for IPO percentage
- All interactions through intuitive modal windows

## Troubleshooting

### "No module named 'tkinter'"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS/Windows - should be included with Python
```

### "No module named 'matplotlib'"
```bash
pip install matplotlib
```

## Game Over
Your company fails when market cap reaches $0. Try to survive as long as possible and grow your company!

---

For more details, see the comprehensive README.md file.
