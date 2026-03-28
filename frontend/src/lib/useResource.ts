import { useEffect, useState } from "react";
import type { ResourceResult } from "../types/contracts";

interface ResourceState<T> {
  loading: boolean;
  error: string | null;
  value: ResourceResult<T> | null;
}

export function useResource<T>(
  loader: () => Promise<ResourceResult<T>>,
  deps: unknown[],
) {
  const [state, setState] = useState<ResourceState<T>>({
    loading: true,
    error: null,
    value: null,
  });

  useEffect(() => {
    let active = true;

    setState((current) => ({
      ...current,
      loading: true,
      error: null,
    }));

    loader()
      .then((value) => {
        if (!active) {
          return;
        }

        setState({
          loading: false,
          error: null,
          value,
        });
      })
      .catch((error: Error) => {
        if (!active) {
          return;
        }

        setState({
          loading: false,
          error: error.message,
          value: null,
        });
      });

    return () => {
      active = false;
    };
  }, deps);

  return state;
}
