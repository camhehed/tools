# Stock Market Simulation Game - Game Flow Diagram

## Sample Game Session

```
┌─────────────────────────────────────────────────────────────┐
│                     GAME START                              │
│                                                             │
│  Setup Screen:                                              │
│  • Company Name: "TechStartup"                              │
│  • Founder: "Alice Johnson"                                 │
│  • Industry: Tech                                           │
│  • Difficulty: Medium                                       │
│                                                             │
│  Initial State:                                             │
│  • Valuation: $100,000                                      │
│  • Shares: 1,000,000                                        │
│  • Price: $0.10                                             │
│  • Ownership: 100%                                          │
│  • Status: Private                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      TURN 1                                 │
│                                                             │
│  Player Action: Skip Turn                                   │
│                                                             │
│  Event: "Product Launch"                                    │
│  • Choice: "Aggressive marketing campaign"                  │
│  • Impact: +8% valuation                                    │
│                                                             │
│  New State:                                                 │
│  • Valuation: $108,000 (+8%)                                │
│  • Price: $0.1080                                           │
│  • Ownership: 100%                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      TURN 2                                 │
│                                                             │
│  Player Action: Skip Turn                                   │
│                                                             │
│  Event: "Viral Social Media"                                │
│  • Choice: "Capitalize with aggressive expansion"          │
│  • Impact: +12% valuation                                   │
│                                                             │
│  New State:                                                 │
│  • Valuation: $120,960 (+12%)                               │
│  • Price: $0.1210                                           │
│  • Ownership: 100%                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      TURN 3                                 │
│                                                             │
│  Player Action: Seek Investors (now available!)            │
│                                                             │
│  Investor Options:                                          │
│  1. Sequoia Capital: 15% equity for $60,000                 │
│  2. Tiger Global: 8% equity for $30,000                     │
│  3. Softbank: 25% equity for $120,000                       │
│                                                             │
│  Player Chooses: Sequoia Capital                            │
│                                                             │
│  After Investment:                                          │
│  • Valuation: $180,960 (+$60,000)                           │
│  • Shares: 1,176,471 (new shares issued)                    │
│  • Price: $0.1538                                           │
│  • Ownership: 85% (diluted from 100%)                       │
│                                                             │
│  Event: "Competitor Emerges"                                │
│  • Choice: "Improve product quality"                        │
│  • Impact: +3% valuation                                    │
│                                                             │
│  New State:                                                 │
│  • Valuation: $186,389                                      │
│  • Price: $0.1584                                           │
│  • Ownership: 85%                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    [Turns 4-9...]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      TURN 10                                │
│                                                             │
│  Current State:                                             │
│  • Valuation: $310,000                                      │
│  • Price: $0.2634                                           │
│  • Ownership: 72% (after 2 investor rounds)                 │
│                                                             │
│  Player Action: Go IPO!                                     │
│  • Offer 20% of shares to public                            │
│                                                             │
│  After IPO:                                                 │
│  • Status: Private → Public                                 │
│  • Ownership: 72% → 52%                                     │
│  • Price: $0.2634 (now "real" market price)                 │
│  • Expectations: Will be checked in 10 turns                │
│                                                             │
│  Event: "Earnings Call"                                     │
│  • Choice: "Balanced and realistic"                         │
│  • Impact: +4% valuation                                    │
│                                                             │
│  New State:                                                 │
│  • Valuation: $322,400                                      │
│  • Price: $0.2739                                           │
│  • Status: Public                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    [Turns 11-19...]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      TURN 20                                │
│                                                             │
│  EXPECTATIONS CHECK! (10 turns after IPO)                   │
│                                                             │
│  Past Performance:                                          │
│  • Price at IPO (Turn 10): $0.2634                          │
│  • Price now (Turn 20): $0.3512                             │
│  • Growth: +33.3%                                           │
│                                                             │
│  Expected Performance:                                      │
│  • Difficulty: Medium (1.3x multiplier)                     │
│  • Expected growth: 33.3% × 1.3 = 43.3%                     │
│  • Expected price: $0.2634 × 1.433 = $0.3775                │
│                                                             │
│  Result: MISSED EXPECTATIONS!                               │
│  • Expected: $0.3775                                        │
│  • Actual: $0.3512                                          │
│  • Penalty: -10% stock price                                │
│                                                             │
│  After Penalty:                                             │
│  • Price: $0.3512 → $0.3161                                 │
│  • Valuation: $436,000 → $392,400                           │
│                                                             │
│  Player Action: Skip Turn                                   │
│                                                             │
│  Event: "Market Expansion"                                  │
│  • Choice: "Careful expansion to one country first"         │
│  • Impact: +5% valuation                                    │
│                                                             │
│  New State:                                                 │
│  • Valuation: $412,020                                      │
│  • Price: $0.3319                                           │
│  • Ownership: 52%                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    [Game continues...]
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   GAME OVER SCENARIO                        │
│                                                             │
│  Turn 47: Economic crisis hits                              │
│  • Series of bad events                                     │
│  • Valuation drops dramatically                             │
│  • Market cap reaches $0                                    │
│                                                             │
│  GAME OVER!                                                 │
│  • Survived: 47 turns                                       │
│  • Final ownership: 52%                                     │
│  • Peak valuation: $856,000 (Turn 35)                       │
│                                                             │
│  Better luck next time!                                     │
└─────────────────────────────────────────────────────────────┘
```

## Key Mechanics Illustrated

### 1. Investor System
- Available every 3 turns
- Dilutes ownership but boosts valuation
- 3 options with different equity/money trade-offs

### 2. IPO Process
- Take company public anytime
- Player chooses % of shares to offer
- Ownership permanently reduced
- Triggers expectations system

### 3. Expectations System
- Only for public companies
- Check every 10 turns
- Based on past performance × difficulty multiplier
- Penalty for missing targets

### 4. Events
- One per turn
- Multiple choices with different impacts
- Can be positive or negative
- Some events only appear when public

### 5. Win/Lose
- No "win" condition - survive as long as possible
- Lose when market cap = $0
- Track turns survived and peak valuation

## Strategy Tips from Sample Game

✓ **Good Moves:**
- Took investors to grow (Turns 3, 6)
- Went IPO after growing to $310K
- Made mostly good event choices

✗ **Mistakes:**
- Missed expectations at Turn 20
- Could have taken more investor money earlier
- Some suboptimal event choices

💡 **Lessons:**
- Balance growth vs. ownership
- Time your IPO carefully
- After going public, focus on steady growth
- Some bad events are unavoidable - choose wisely
