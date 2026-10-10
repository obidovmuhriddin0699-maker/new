"use client";

import { useEffect, useState } from "react";

import { getMe } from "./api";
import type { User } from "./types";

/**
 * The signed-in user (null while loading). `readOnly` is true for VIEWER: the UI hides
 * actions the backend would refuse anyway (it enforces roles on every request).
 */
export function useMe() {
  const [me, setMe] = useState<User | null>(null);
  useEffect(() => {
    let alive = true;
    void getMe().then((u) => {
      if (alive) setMe(u);
    });
    return () => {
      alive = false;
    };
  }, []);
  return { me, readOnly: me?.role === "VIEWER" };
}
