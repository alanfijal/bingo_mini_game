# Multiplayer Bingo

A real-time, multiplayer Bingo game you can play in the browser. Players join rooms, get unique cards, and race to complete lines as numbers are called live by the host or auto-caller. Built for low-latency fun with WebSockets and a clean, responsive UI.

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

## Tech Stack

* **Frontend:** React + Vite, TypeScript, Tailwind CSS
* **State/Networking:** Zustand or Redux Toolkit Query, Socket.IO client
* **Backend:** Node.js (Express) + Socket.IO, TypeScript
* **Database:** PostgreSQL (Prisma ORM) or MongoDB (Mongoose)
* **Auth:** JWT (access/refresh) with cookie storage (httpOnly), or Magic Links
* **Build/Dev:** pnpm, ESLint, Prettier, Vitest/Jest, Playwright
* **Deployment:** Docker, Fly.io/Render/Vercel (frontend), Railway/Supabase (backend+DB)

> You can swap in NestJS, Next.js App Router, or a serverless backend. The API/event contract below stays the same.

---

## Monorepo Layout (recommended)

```
MINI-BINGO/
├── docs/
│   ├── architecture.md
│   └── README.md
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

## Quick Start

### Prerequisites

* Node.js ≥ 18, pnpm ≥ 8
* Docker (optional but recommended)

### Environment Variables

Create `.env` files in each app directory.

**apps/server/.env**

```
PORT=4000
NODE_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/bingo
JWT_SECRET=change-me
CORS_ORIGIN=http://localhost:5173
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX=200
```

**apps/web/.env**

```
VITE_API_URL=http://localhost:4000
VITE_SOCKET_URL=http://localhost:4000
```

### Run Locally (without Docker)

```bash
pnpm i
pnpm -C apps/server prisma migrate dev        # if using Prisma/Postgres
pnpm -C apps/server dev
pnpm -C apps/web dev
```

Open the web app at **[http://localhost:5173](http://localhost:5173)**.

### Run with Docker

```bash
docker compose up --build
```

This starts the server, database, and web UI.

---

## How to Play

1. **Create or join** a room. Public rooms have codes; private rooms need a PIN.
2. The **host** chooses: auto-caller interval or manual calling.
3. Each player receives a **unique 5×5 card** (default range 1–75, free center optional).
4. Mark numbers when called. The server validates each mark.
5. When you think you’ve won, press **BINGO!** The server verifies against configured patterns.
6. The room displays winners; the host can **start a new round** or **rotate host**.

---

## Game Rules (defaults)

* Card: 5×5, numbers 1–75 distributed by column (B=1–15, I=16–30, etc.)
* Free center: configurable (default on)
* Win conditions: any row, column, or main diagonal
* Multi-winner: allowed; first to call is highlighted
* Duplicate calls: prevented; server tracks global call history

---

## Data Models (TypeScript)

```ts
// Shared types
export type PlayerID = string;
export type RoomID = string;

export interface Player {
  id: PlayerID;
  name: string;
  isHost: boolean;
  connected: boolean;
  avatar?: string;
}

export interface Cell { n: number; marked: boolean; }
export type Card = Cell[][]; // 5x5

export interface Room {
  id: RoomID;
  code: string;      // public code like "ABCD"
  pin?: string;      // private PIN if locked
  players: Player[];
  state: 'lobby' | 'in-progress' | 'complete';
  callHistory: number[];       // numbers already called
  config: GameConfig;
  winners: PlayerID[];
}

export interface GameConfig {
  freeCenter: boolean;
  autoCaller: boolean;
  callIntervalMs: number; // if autoCaller
  numberRange: [number, number];
  winPatterns: 'lines' | 'full-house' | 'custom';
}
```

---

## REST API (minimal)

```
POST   /api/rooms                # create room {name, private?}
POST   /api/rooms/:id/join       # join room {name, pin?}
POST   /api/rooms/:id/start      # host starts round
POST   /api/rooms/:id/rotate     # transfer host
GET    /api/rooms/:id            # room summary (no secrets)
```

### WebSocket Events (Socket.IO)

#### Client → Server

* `room:create` { name, private?: boolean }
* `room:join` { roomId|code, name, pin? }
* `game:start` { roomId }
* `call:next` { roomId } // manual
* `card:mark` { roomId, row, col }
* `bingo:claim` { roomId }
* `chat:send` { roomId, message }

#### Server → Client

* `room:state` { room }
* `player:joined` { player }
* `game:started` { callHistory, config, card }
* `call:update` { number, callHistory }
* `card:update` { row, col, markedBy }
* `bingo:result` { valid, winners, pattern }
* `chat:new` { message, from }
* `error` { code, message }

> **Idempotency:** All mutating events should carry a `clientMsgId` so retries don’t double-apply.

---

## Security & Fair Play

* **Server is source of truth** for card generation, marking, and win checks
* **JWT + httpOnly cookies** for session security
* **Rate limiting** on joins, chat, and claims
* **Room PIN hashing**; never store plaintext
* **Spectator isolation** from game-altering events

---

## Testing

* **Unit:** Vitest/Jest for utils (card gen, win detection)
* **Integration:** Supertest for REST endpoints
* **E2E:** Playwright for multi-client flows
* **Load:** Artillery/K6 for socket throughput

Run tests:

```bash
pnpm test
pnpm -C apps/web test
pnpm -C apps/server test
```

---

## Accessibility

* Semantic HTML (roles/aria where needed)
* Focus management on dialogs and route changes
* Keyboard-first controls for marking cells
* High-contrast theme option and reduced motion

---

## Internationalization (i18n)

* Client uses a translation framework (e.g., i18next)
* Locale detection and RTL support
* Server sends only codes/ids; client localizes strings

---

## Observability

* Structured logs (pino/winston)
* Request IDs + clientMsgId correlation
* Metrics: connected users, join failure rate, socket latency, time-to-bingo
* Error tracking: Sentry

---

## Deployment

* **One-click:** `docker compose up -d`
* **Production:**

  * Use managed Postgres (Supabase/Neon/RDS)
  * Configure CORS, HTTPS, and secure cookies
  * Horizontal scale: sticky sessions (or Socket.IO adapter with Redis)
  * Health checks on `/healthz`

---

## Roadmap

* Custom board sizes and patterns
* Tournaments & leaderboards
* Friends list and invitations
* Voice chat and host soundboard
* Offline-first PWA with background sync

---

## Contributing

1. Fork & create a feature branch
2. Write tests and docs
3. Run lint/format: `pnpm lint && pnpm format`
4. Open a PR with a clear description and screenshots/gifs

---

## License

MIT. See `License`.

---

## Acknowledgments

Inspired by classic community bingo nights. Numbers are fun; fairness is mandatory.
