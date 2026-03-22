"use client";

import { useEffect, useRef, useCallback, useState } from "react";

// Compute WS URL from current page location (works through Next.js proxy)
const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ||
  (typeof window !== "undefined"
    ? `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/prices`
    : "ws://localhost:8000/ws/prices");

interface PriceUpdate {
  type: string;
  ticker: string;
  price: number;
  change_1d: number;
  [key: string]: unknown;
}

export function useWebSocket(tickers?: string[]) {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<PriceUpdate | null>(null);
  const [prices, setPrices] = useState<Record<string, PriceUpdate>>({});

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setConnected(true);
      if (tickers?.length) {
        ws.send(JSON.stringify({ subscribe: tickers }));
      }
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as PriceUpdate;
        if (data.type === "price_update") {
          setLastUpdate(data);
          setPrices((prev) => ({ ...prev, [data.ticker]: data }));
        }
      } catch {
        // ignore parse errors
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Auto-reconnect after 3s
      setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };

    wsRef.current = ws;
  }, [tickers]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const subscribe = useCallback((newTickers: string[]) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ subscribe: newTickers }));
    }
  }, []);

  return { connected, lastUpdate, prices, subscribe };
}
