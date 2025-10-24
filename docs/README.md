# Multiplayer Bingo

A real-time, multiplayer Bingo game you can play in the terminal. Players join rooms, get unique cards, and race to complete lines as numbers are called live by the host or auto-caller.

---

## Features

* **Realtime multiplayer** with rooms/lobbies
* **Unique bingo cards** per player, free center optional
* **Auto-caller** or **manual host** mode
* **Line detection**: rows, columns, diagonals; configurable win patterns
* **Spectator mode** and host transfer
* **Chat** (room-level) and emojis
* **Mobile-first UI**, keyboard and screen reader friendly
* **Persistence** with reconnect support
* **Private rooms** with PINs, public rooms with codes
* **Anti-cheat** server-side validation

---

## Repo Layout

```
MINI-BINGO/
├── docs/
│   ├── architecture.md
│   └── README.md
|   └── License.md
├── src/
│   ├── domain/
│   │   ├── bingo_card.py
│   │   ├── rules.py
│   │   └── types.py
│   ├── game_logic/
│   │   ├── draw_and_mark.py
│   │   └── start_game.py
│   ├── interfaces/
│   │   ├── cli_controller.py
│   │   ├── cli_presenter.py
│   │   ├── data_storage.py
│   │   └── random_numbers.py
│   └── main.py
├── tests/
│   ├── domain/
│   │   └── test_domain.py
│   ├── game_logic/
│   │   └── test_game_logic.py
│   └── interfaces/
│       └── test_interfaces.py
├── venv/
│   ├── bin/
│   ├── include/
│   └── lib/
├── pyvenv.cfg
├── pyproject.toml
└── requirements.txt
```

---

## License

MIT. See `License`.

---

## Acknowledgments

Inspired by classic community bingo nights. Numbers are fun; fairness is mandatory.
