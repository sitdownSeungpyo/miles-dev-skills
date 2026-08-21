---
name: web-frontend
description: Modern web frontend engineering — React 19 / Next.js App Router, TypeScript, state management, robot dashboards with WebSocket/live data, accessibility, performance. Use when building or editing React/Next.js/TypeScript UI code, dashboards, or web-based robot control panels.
---

# Web Frontend Engineering

Production React/Next.js + TypeScript standards, with patterns for real-time robot/device dashboards.

## Stack defaults (when the user hasn't chosen)

- Next.js (App Router) + TypeScript strict + Tailwind CSS; Vite + React for pure SPAs.
- Server state: TanStack Query. Client state: Zustand (small) — avoid Redux unless it already exists.
- Forms: react-hook-form + zod. Check `package.json` first and match the existing stack.

## React rules

- Server Components by default in Next.js; `"use client"` only where interactivity is needed, pushed to leaf components.
- Derive state, don't sync it: no `useEffect` that copies props to state. Most `useEffect`s are avoidable — events belong in handlers, derived data in render/`useMemo`.
- Keys must be stable IDs, never array indices for mutable lists.
- Co-locate: component + hook + test in one folder; extract a custom hook when logic (not JSX) is reused.
- TypeScript: no `any`; discriminated unions for UI states (`{status:'loading'} | {status:'error', error} | {status:'ok', data}`) instead of boolean flag soup.

## Real-time / device dashboards

- WebSocket: one connection in a context/provider or a store, not per component. Auto-reconnect with exponential backoff + jitter; surface connection state in the UI.
- High-rate telemetry (IMU, joint states): throttle renders — buffer messages in a ref, flush to state at 10–15 Hz with `requestAnimationFrame` or an interval; render charts on canvas (uPlot/lightweight-charts) rather than SVG for >1k points.
- ROS integration: `roslibjs` + rosbridge for quick dashboards; use typed message interfaces and a single `Ros` instance.
- Command paths (e-stop, teleop): optimistic UI is forbidden — reflect only acknowledged state, and design for stale/disconnected states explicitly.
- Video: WebRTC for low-latency camera streams; MJPEG only for bench tools.

## Performance

- Measure first (React DevTools Profiler, Lighthouse). Then: `next/image`, dynamic imports for heavy panels, `React.memo` only on proven hot leaves, virtualize long lists (`@tanstack/react-virtual`).

## Accessibility & quality bar

- Interactive = real `<button>`/`<a>`, keyboard reachable, visible focus; labels on all inputs; 4.5:1 contrast.
- Every async view has loading / empty / error states designed — not just the happy path.
- Tests: Vitest + React Testing Library; test behavior via roles/labels, not implementation details. Playwright for critical flows.
