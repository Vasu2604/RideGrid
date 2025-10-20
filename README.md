[![RideGrid Banner](https://via.placeholder.com/1200x300/0B1021/7C3AED?text=RideGrid+%7C+Planet-Scale+Ride-Hailing)](https://github.com/)

# RideGrid — A Playbook for Planet-Scale Ride-Hailing

> Compact, confident, and curious: this README teaches you what RideGrid is, why it matters, how it works, and how to run or contribute to it. Read fast, dig deep where you want.

---

## ✨ Elevator pitch

RideGrid is a realistic, production-focused reference implementation of a distributed ride-hailing platform. It showcases event-driven design, exactly-once processing, CQRS-style read models, real-time telemetry, and robust deployment patterns (Docker, Kubernetes, Helm, Argo).

This repository is meant to be a learning vehicle and a starting point for teams building geo-real-time services that must be correct, observable, and deployable at scale.

## Why this project matters (in plain terms)

- Real-world systems must handle concurrent events, partial failures, and skewed loads. RideGrid demonstrates patterns that make such systems predictable.
- It pairs clear, pragmatic code with infra and observability so you can reproduce the whole lifecycle: local dev → test → canary → prod.
- You’ll learn to reason about correctness (idempotency, EOS), latency, throughput, and operational visibility.

## Core concepts (short, concrete definitions)

- Event-Driven: services communicate by publishing and consuming immutable events (Kafka/Redpanda). This decouples producers and consumers and enables retries, replay, and auditability.
- Exactly-Once Semantics (EOS): the system strives to process each business event once and only once (outbox pattern + transactional commits + consumer-side dedupe).
- CQRS: writes (commands/events) flow through the event bus; read models are independently built for low-latency queries.
- Streaming Telemetry: driver location is streamed (gRPC) into telemetry ingest, then propagated as events to matching and state-query services.

## High-level architecture (one image, one sentence each component)

Gateway — public HTTP/gRPC surface and auth layer.
Telemetry Ingest — receives driver streams and publishes canonical telemetry events.
Kafka Topics — the durable event backbone for business events and telemetry.
Matching Engine — consumes telemetry + rider intents and emits assignments.
Assignment Orchestrator — ensures assignment correctness with EOS and compensating actions.
State Query — materialized read models for fast lookups (Postgres/PostGIS + Redis).

## Quick start — get the full stack running locally (5 minutes)

1) Clone repository

```bash
git clone <your-clone-url-or-local-path>
cd RIdeGrid
```

2) Start infra (Docker Compose)

```bash
cd deploy/docker-compose
docker-compose up -d postgres redis redpanda otel-collector prometheus grafana
```

3) Install Python deps and local libs

```bash
python3 -m pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -e libs/ridegrid-common
```

4) (Optional) Generate protobuf bindings

```bash
python -m grpc_tools.protoc --proto_path=proto \
  --python_out=libs/ridegrid-proto/ridegrid_proto \
  --grpc_python_out=libs/ridegrid-proto/ridegrid_proto \
  proto/ridegrid.proto
```

5) Start the essential services (example)

Open a terminal tab per service or use a process manager.

```bash
# from repo root
python services/gateway/main.py &
python services/telemetry-ingest/main.py &
python services/matching-engine/main.py &
python services/assignment-orchestrator/main.py &
python services/state-query/main.py &
```

6) Start the frontend (ops console)

```bash
cd web/ops-console
npm install
npm run dev
```

7) Useful endpoints

- Frontend: http://localhost:3000
- Gateway API: http://localhost:8001
- Grafana: http://localhost:3001 (default: admin/admin)
- Prometheus: http://localhost:9090

---

## Development workflow — make a change the right way

1. Create a topic branch: `git checkout -b feat/<short-desc>`
2. Run unit tests locally: `pytest tests/ -q`
3. Lint & format: `tox` or `pre-commit run --all-files` (if configured)
4. Push your branch and open a PR. Use small, focused commits and a descriptive PR title.

Tips:
- Keep changes to one service or library per PR.
- Add tests for behavior (happy path + one edge case).
- When changing message schemas, bump protobuf and communicate versioning to consumers.

## Observability & troubleshooting (practical recipes)

- If matching is slow: check `matching_duration_seconds` and `kafka_consumer_lag` in Prometheus.
- If telemetry is missing: ensure Telemetry Ingest is connected to Kafka and the gRPC connection is healthy (check logs + traces).
- For dedupe problems: validate event ids and outbox delivery logs.

Pro tip: use the OpenTelemetry traces to follow a request end-to-end — it reveals retries, time spent in queues, and where backpressure occurs.

## Commands cheat-sheet (copyable)

Start infra: `cd deploy/docker-compose && docker-compose up -d`
Run tests: `pytest tests/ -q`
Generate protos: see Quick start step 4
Format: `black .`  Lint: `flake8` (if present)

## How to contribute

- Read `CONTRIBUTING.md` (if present) for code style and PR process.
- Fork, create a branch, implement, add tests, push, open PR.
- Be explicit in PR descriptions: what you changed, why, risk, testing performed.

## Security & operational notes

- Use mTLS for inter-service comms in production.
- Store secrets in Kubernetes secrets or Vault; never commit them.
- Rate limit public endpoints via the Gateway using Redis token buckets.

## Files and where to look (map for new contributors)

- Services: `services/*/src/<service_name>` — business logic and service entry points
- Shared libs: `libs/ridegrid-common` — utilities, tracing, metrics
- Protobuf: `proto/ridegrid.proto` and generated code in `libs/ridegrid-proto`
- Infra: `deploy/docker-compose` and `helm/ridegrid`
- Dashboards: `dashboards/` (Grafana json)

## Want to deploy to Kubernetes?

Use the Helm chart in `helm/ridegrid`. Minimal example:

```bash
helm install ridegrid helm/ridegrid --set postgresql.auth.password=<secret>
kubectl apply -f infra/argo-rollouts/  # if you want progressive delivery
```

## Attribution & license

This repository is licensed under MIT. See `LICENSE`.

---

If you want, I can also write a short companion `CONTRIBUTING.md` and a one-page architecture diagram — tell me which you'd like next.
# Assignment Orchestrator

cd services/assignment-orchestrator && python main.py



# State Query

cd services/state-query && python main.py

