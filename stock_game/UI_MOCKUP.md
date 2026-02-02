# Stock Market Simulation Game - UI Mockup

## Game Setup Screen
```
┌─────────────────────────────────────────────────┐
│                                                 │
│          Stock Market Simulation                │
│                                                 │
│  Company Name:                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ TechCorp                                  │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Founder Name:                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ John Doe                                  │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Industry:                                      │
│  ┌──────────────────────────────────────────┐  │
│  │ Tech                              ▼      │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  Difficulty:                                    │
│  ○ Easy    ●  Medium    ○  Hard                │
│                                                 │
│          ┌──────────────────┐                  │
│          │   Start Game     │                  │
│          └──────────────────┘                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Main Game Screen
```
┌──────────────────────────────────────────────────────────────────┐
│ TechCorp (Private)   Turn: 5   Share Price: $0.1234   Your: 85% │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                   Stock Price History                            │
│   $                                                              │
│   0.15 ┼                                      ╭─╮                │
│        │                                   ╭──╯ ╰─╮              │
│   0.12 ┼                          ╭───────╯      ╰─╮            │
│        │                     ╭────╯                 ╰─╮          │
│   0.10 ┼────────────────────╯                         ╰─        │
│        │                                                         │
│   0.08 ┼─────────────────────────────────────────────────────   │
│        │                                                         │
│        └┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼──  │
│         0    5    10   15   20   25   30   35   40   45   50   │
│                           Turn                                   │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │  Seek    │  │   Skip   │  │ Analyze  │  │  Go IPO  │        │
│  │Investors │  │   Turn   │  │          │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Event Modal
```
┌─────────────────────────────────────────────────┐
│                                                 │
│              Product Launch                     │
│                                                 │
│  Your company is launching a new product.       │
│  How will you market it?                        │
│                                                 │
│  Choose your response:                          │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Aggressive marketing campaign             │ │
│  │ +8.0% valuation                           │ │
│  │              [Select]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Moderate marketing with focus on quality  │ │
│  │ +5.0% valuation                           │ │
│  │              [Select]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Minimal marketing, let word-of-mouth      │ │
│  │ +2.0% valuation                           │ │
│  │              [Select]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Delay launch for more testing             │ │
│  │ -3.0% valuation                           │ │
│  │              [Select]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Investor Selection Modal
```
┌─────────────────────────────────────────────────┐
│                                                 │
│            Select an Investor                   │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Sequoia Capital                           │ │
│  │ Takes: 15.0% equity                       │ │
│  │ Gives: $80,000                            │ │
│  │ New Valuation: $180,000                   │ │
│  │ Valuation Boost: +80.0%                   │ │
│  │              [Accept]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Andreessen Horowitz                       │ │
│  │ Takes: 8.0% equity                        │ │
│  │ Gives: $35,000                            │ │
│  │ New Valuation: $135,000                   │ │
│  │ Valuation Boost: +35.0%                   │ │
│  │              [Accept]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ Tiger Global                              │ │
│  │ Takes: 25.0% equity                       │ │
│  │ Gives: $150,000                           │ │
│  │ New Valuation: $250,000                   │ │
│  │ Valuation Boost: +150.0%                  │ │
│  │              [Accept]                     │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│              [Cancel]                           │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Analysis Modal
```
┌─────────────────────────────────────────────────┐
│                                                 │
│            Company Analysis                     │
│                                                 │
│  Company Name:      TechCorp                    │
│  Founder:           John Doe                    │
│  Industry:          Tech                        │
│  Difficulty:        Medium                      │
│  Status:            Private                     │
│  Turn:              15                          │
│  Market Cap:        $245,678.90                 │
│  Valuation:         $245,678.90                 │
│  Total Shares:      1,234,567                   │
│  Your Shares:       987,654                     │
│  Your Ownership:    80.00%                      │
│  Share Price:       $0.1990                     │
│                                                 │
│              [Close]                            │
│                                                 │
└─────────────────────────────────────────────────┘
```

## IPO Modal
```
┌─────────────────────────────────────────────────┐
│                                                 │
│         Initial Public Offering                 │
│                                                 │
│  What percentage of shares do you want to       │
│  offer?                                         │
│                                                 │
│  (Minimum: 10%, Maximum: 100%)                  │
│                                                 │
│  Current Ownership: 85.0%                       │
│                                                 │
│  New Ownership: 65.0%                           │
│                                                 │
│  ┌───────────────────────────────────────────┐ │
│  │ 10        [===========○          ]   100  │ │
│  └───────────────────────────────────────────┘ │
│                      20%                        │
│                                                 │
│       [Go Public]          [Cancel]             │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Color Scheme

- **Background**: Dark blue/black (#0a0e27)
- **Foreground Text**: White (#ffffff)
- **Buttons**: Blue (#1e3a8a)
- **Button Hover**: Lighter blue (#2563eb)
- **Accent/Highlights**: Bright blue (#3b82f6)
- **Graph Line**: Light blue (#60a5fa)
- **Positive Changes**: Green (#10b981)
- **Negative Changes**: Red (#ef4444)

## Features Implemented

1. **Game Setup Screen**: Choose company name, founder, industry, and difficulty
2. **Main Game Screen**: Large stock price graph with info bar and action buttons
3. **Event System**: 15+ unique events with multiple choices
4. **Investor System**: 3 scaled investor offers every 3 turns
5. **IPO Modal**: Slider to choose percentage of shares to offer
6. **Analysis Modal**: Detailed company statistics
7. **Expectations**: Every 10 turns for public companies
8. **Game Over**: When market cap reaches $0
