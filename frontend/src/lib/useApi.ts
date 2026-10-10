"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "./api";

type Result<T> = { path: string; data: T | null; error: unknown };

export function useApi<T>(path: string | null) {
  // The result remembers which path it belongs to: data of a previous path is never
  // shown as current (callers see loading instead while the new path loads).
  const [result, setResult] = useState<Result<T> | null>(null);
  const [busy, setBusy] = useState(false);
  // Only the latest request may write: a slow answer for an old path is dropped.
  const latest = useRef(0);

  const reload = useCallback(async () => {
    if (!path) return;
    const ticket = ++latest.current;
    setBusy(true);
    try {
      const data = await api<T>(path);
      if (ticket === latest.current) setResult({ path, data, error: null });
    } catch (err) {
      // Keep the last good data of this path next to the error (as before).
      if (ticket === latest.current) setResult((r) => ({ path, data: r?.path === path ? r.data : null, error: err }));
    } finally {
      if (ticket === latest.current) setBusy(false);
    }
  }, [path]);

  useEffect(() => {
    void reload();
    const counter = latest; // the ref object itself, not a DOM node
    return () => {
      counter.current++; // unmount / path change: whatever is in flight is stale
    };
  }, [reload]);

  const current = path !== null && result?.path === path ? result : null;
  const setData = useCallback(
    (data: T | null) => {
      if (path) setResult({ path, data, error: null });
    },
    [path],
  );
  return {
    data: current?.data ?? null,
    error: current?.error ?? null,
    loading: path !== null && (busy || current === null),
    reload,
    setData,
  };
}
