# SAHOOL Frontend v15.3

## 🚀 لوحة تحكم العمليات | Operations Dashboard

### المكونات | Components

```
frontend/
├── dashboard/           # Next.js 14 Dashboard
│   ├── app/            # App Router pages
│   ├── components/     # React components
│   ├── lib/            # Utilities (API, WebSocket)
│   └── styles/         # Global styles
├── ws-gateway/         # WebSocket Gateway (Python)
├── docker-compose.yml  # Docker setup
└── nginx.conf          # Reverse proxy
```

---

## 🖥️ Dashboard Features

### 🗺️ خريطة الحقول | Map View

- MapLibre GL integration
- Yemen regions & fields
- Status overlay (healthy/warning/critical)
- NDVI visualization (coming)

### 📋 المهام اليومية | Daily Tasks

- Task list with filters
- Priority indicators
- Due date tracking
- Complete with evidence

### 📊 الأحداث المباشرة | Live Timeline

- Real-time event stream
- WebSocket connection
- Event type filtering
- Auto-refresh

### 📈 الإحصائيات | Stats Cards

- Fields count & area
- Health score
- Pending tasks
- Active alerts
- Weather summary
- Water usage

---

## 🏃 Quick Start

### Development

```bash
cd frontend/dashboard
npm install
npm run dev
# Open http://localhost:3000
```

### Docker

```bash
cd frontend
docker compose up -d
# Open http://localhost
```

---

## 🔌 WebSocket Gateway

### Endpoints

- `ws://localhost:8081/events` - Event stream

### Subscribe

```javascript
ws.send(
  JSON.stringify({
    type: "subscribe",
    subjects: ["tasks.*", "weather.*", "diagnosis.*"],
  }),
);
```

### Event Types

| Subject                     | Description       |
| --------------------------- | ----------------- |
| `tasks.task_created`        | New task created  |
| `tasks.task_completed`      | Task completed    |
| `weather.alert_issued`      | Weather alert     |
| `diagnosis.image_diagnosed` | Disease diagnosis |
| `ndvi.processed`            | NDVI analysis     |

---

## 🎨 UI Components

### TaskCard

```tsx
<TaskCard task={task} onComplete={handleComplete} onSelect={handleSelect} />
```

### EventTimeline

```tsx
<EventTimeline />
```

### MapView

```tsx
<MapView onFieldSelect={setSelectedField} />
```

### StatusBadge

```tsx
<StatusBadge status="healthy" />
<StatusBadge status="warning" />
<StatusBadge status="critical" />
```

---

## 🔧 Configuration

### Environment Variables

```env
API_URL=http://localhost:8080
WS_URL=ws://localhost:8081
```

### Ports

| Service    | Port |
| ---------- | ---- |
| Dashboard  | 3000 |
| WS Gateway | 8081 |
| Nginx      | 80   |

---

## 📱 Mobile Ready

Components designed for reuse in Flutter mobile app (PR #4).
