# 🧠 History Sidepanel Chrome Extension

## 🎯 Assessment Context

A fullstack Chrome extension that displays browsing history and real-time page analytics in a side panel.
Built with **React + TypeScript frontend**, **FastAPI backend**, and **PostgreSQL** data layer, packaged via **Docker**.

---

## 🚀 Quick Start

### Backend & Database

```bash
cd backend
docker-compose up -d  # Starts FastAPI + PostgreSQL
```

### Chrome Extension

```bash
cd extension
npm install && npm run build
# Load `dist/` folder as unpacked extension in Chrome
```

---

## 🏗️ System Architecture

![System Architecture](docs/system-design.png)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Chrome        │    │   FastAPI        │    │   PostgreSQL    │
│   Extension     │────│   Backend        │────│   Database      │
│                 │    │                  │    │                 │
│  • Side Panel   │    │  • REST API      │    │  • Visit Data   │
│  • Background   │    │  • Async/await   │    │  • Analytics    │
│  • Content      │    │  • SQLAlchemy    │    │  • Metrics      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Data Flow**

```
Page Load → Content Script → Background Worker → FastAPI → PostgreSQL  
User Action → Side Panel ← Live Updates ← Backend API
```

---

## ⚙️ Key Technical Decisions

| Decision                          | Rationale                                     | Impact                           |
|-----------------------------------|-----------------------------------------------| -------------------------------- |
| **FastAPI + Async SQLAlchemy**    | Native async stack                            | Non-blocking, high concurrency   |
| **PostgreSQL**                    | Performance and  compatibility | Fast lookups, structured metrics |
| **Vite/Bun + React (Side Panel)** | Hot reload & modular multi-entry build        | Developer efficiency             |
| **Event-Driven Messaging**        | Content ↔ Background ↔ UI communication       | Real-time updates                |
| **Dockerized Services**           | Environment consistency                       | Easy deployment and isolation    |

---

## ⚡ Performance & Reliability

### Backend

* Async I/O and connection pooling
* Indexed URLs and timestamps
* Structured logging for low-latency debugging

### Extension

* Selective DOM parsing (visible elements only)
* SPA detection via MutationObserver + History API
* Debounced updates to reduce polling and API chatter

---

## 🧩 Data Model

```python
PageVisit:
  - url (indexed)
  - word_count
  - link_count, internal_links, external_links
  - image_count, content_images, decorative_images
  - created_at (indexed)
```

---

## 🔒 Security & Constraints

* Chrome sandbox ensures **isolated script execution**
* Backend runs on **localhost only**
* **No sensitive data** persisted (analytics only)
* Planned extensions: **OAuth** and **API key validation**

---

## 🔌 Core API Endpoints

| Method | Endpoint                          | Description          |
| ------ | --------------------------------- | -------------------- |
| `POST` | `/api/v1/visits`                  | Record page visit    |
| `GET`  | `/api/v1/visits?url={url}`        | Get history for URL  |
| `GET`  | `/api/v1/visits/latest?url={url}` | Latest visit data    |
| `GET`  | `/api/v1/visits/stats`            | Aggregated analytics |
| `GET`  | `/api/v1/visits/recent`           | Recent visits        |

---

## ⚖️ Trade-offs & Limitations

* No authentication layer (local-only usage)
* SPA detection may miss custom routers
* API batching not yet implemented
* Extension scripts cannot share global context (isolated world)

---
