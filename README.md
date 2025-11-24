# Multiplayer Bingo

A real-time, multiplayer Bingo game you can play in the terminal. Players join lobbies, receive unique cards, and compete to complete winning patterns as numbers are called. The game includes a WebSocket-based server architecture with Docker support for easy deployment.

---

## Features

* **Real-time multiplayer** - WebSocket-based communication with lobby system
* **Unique bingo cards** - Each player receives a randomly generated 5x5 card
* **Multiple win patterns** - Single line, multiple lines, four corners, X pattern, T pattern, L pattern, and full house
* **Points-based scoring** - Progressive points system rewards more complex patterns
* **Number validation** - Players can only mark numbers that have been called
* **Docker deployment** - Containerized server and client with Redis support

---

## Quick Start

### Using Docker (Recommended)

Start the server and play:
```bash
./play.sh
```

This script automatically starts the server if needed and launches a multiplayer client.

### Manual Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python src/multiplayer/server.py
```

3. Connect clients (in separate terminals):
```bash
python src/interfaces/multiplayer_cli.py
```

For single-player mode:
```bash
python src/main.py
```

---

## Scoring System

The game awards points based on the complexity of completed patterns:

* **Full House** - 50 points (all 25 squares marked)
* **Four Lines** - 40 points (4 complete lines)
* **Three Lines** - 32 points (3 complete lines)
* **Two Lines** - 25 points (2 complete lines)
* **X Pattern** - 20 points (both diagonals)
* **T Pattern** - 20 points (top row and middle column)
* **L Pattern** - 20 points (top row and left column)
* **Four Corners** - 15 points (all corner squares)
* **Single Line** - 10 points (any row, column, or diagonal)

Lines can be horizontal rows, vertical columns, or diagonals. The system automatically awards the highest-value pattern achieved.

---

## Repo Layout

```
mini_bingo_game/
├── docs/
│   ├── architecture.md
│   ├── README.md
│   └── License.md
├── src/
│   ├── domain/
│   │   ├── bingo_card.py      # Card generation and marking
│   │   ├── number_pool.py      # Number draw management
│   │   ├── rules.py            # Game rule configurations
│   │   └── types.py
│   ├── game_logic/
│   │   ├── auto_check.py       # Line completion detection
│   │   ├── draw_and_mark.py    # Number drawing utilities
│   │   ├── game_session.py     # Single-player game flow
│   │   ├── start_game.py
│   │   └── win_con.py          # Win condition validation
│   ├── multiplayer/
│   │   ├── game_coordinator.py # Multiplayer game orchestration
│   │   ├── lobby.py            # Player lobby management
│   │   ├── message_protocol.py # WebSocket message definitions
│   │   ├── player.py           # Player state and scoring
│   │   ├── points_system.py    # Points calculation
│   │   ├── redis_store.py      # Redis integration
│   │   └── server.py           # WebSocket server
│   ├── interfaces/
│   │   ├── cli_controller.py   # Single-player CLI
│   │   ├── cli_presenter.py    # Terminal output formatting
│   │   ├── multiplayer_cli.py  # Multiplayer client
│   │   ├── data_storage.py
│   │   └── random_numbers.py
│   └── main.py                 # Single-player entry point
├── tests/
│   ├── domain/
│   │   └── test_domain.py
│   ├── game_logic/
│   │   ├── test_game_logic.py
│   │   └── test_win_conditions.py
│   ├── integration/
│   │   └── test_integration.py
│   └── interfaces/
│       └── test_interfaces.py
├── Dockerfile
├── docker-compose.yml
├── play.sh                     # Quick-start script
├── requirements.txt
└── README.md
```

---

## Architecture

The game follows a clean architecture pattern with clear separation between domain logic, game rules, and interface layers.

**Domain Layer** - Pure business logic for cards, rules, and number pools
**Game Logic Layer** - Win condition checking, game state management
**Multiplayer Layer** - WebSocket server, lobby system, message protocol
**Interface Layer** - CLI presentation and user input handling

The multiplayer system uses WebSockets for real-time communication and supports multiple concurrent games through isolated lobby instances.

---

## Testing

Run the test suite:
```bash
python -m unittest discover tests
```

Run specific test files:
```bash
python tests/game_logic/test_win_conditions.py
```

---

## License

MIT. See `License`.

---
