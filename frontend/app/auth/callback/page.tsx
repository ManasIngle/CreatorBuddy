"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authApi } from "@/lib/api";
import { storeToken } from "@/lib/auth";
import { useStore } from "@/store/useStore";

/**
 * OAuth callback page.
 * Google redirects here with ?code=… after the user grants permission.
 * We exchange the code for our JWT, hydrate the user, then redirect to the app.
 */
export default function AuthCallbackPage() {
  const router = useRouter();
  const params = useSearchParams();
  const { setUser, setAccessToken } = useStore();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = params.get("code");
    const oauthError = params.get("error");

    if (oauthError) {
      setError(`Sign in cancelled: ${oauthError}`);
      return;
    }
    if (!code) {
      setError("Missing authorization code from Google.");
      return;
    }

    let cancelled = false;
    (async () => {
      try {
        const exchange = await authApi.googleCallback(code);
        const { access_token } = exchange.data;
        if (cancelled) return;

        // Persist token + state
        storeToken(access_token);
        setAccessToken(access_token);

        // Hydrate user
        const me = await authApi.me();
        if (cancelled) return;
        setUser(me.data);

        router.replace("/dashboard");
      } catch (e) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : "Sign in failed";
        setError(msg);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [params, router, setUser, setAccessToken]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <div className="max-w-md w-full text-center space-y-4">
        {error ? (
          <>
            <h1 className="text-2xl font-semibold text-red-400">Sign in failed</h1>
            <p className="text-sm text-gray-400">{error}</p>
            <button
              onClick={() => router.push("/login")}
              className="px-4 py-2 rounded bg-brand-600 text-white hover:bg-brand-500 transition"
            >
              Back to login
            </button>
          </>
        ) : (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-500 mx-auto" />
            <h1 className="text-xl font-medium text-white">Signing you in…</h1>
            <p className="text-sm text-gray-400">Hold tight, finishing up with Google.</p>
          </>
        )}
      </div>
    </div>
  );
}
