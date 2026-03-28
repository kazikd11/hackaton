import { motion } from "framer-motion";
import type { PropsWithChildren } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { guidedWaypoints } from "../fixtures/demoData";
import { appMode } from "../lib/env";

const navItems = [
  { label: "Overview", to: "/" },
  { label: "Process", to: `/processes/${guidedWaypoints.processId}` },
  {
    label: "Opportunity",
    to: `/opportunities/${guidedWaypoints.opportunityId}`,
  },
  { label: "Workflow", to: `/workflow/${guidedWaypoints.opportunityId}` },
];

export function AppShell({ children }: PropsWithChildren) {
  const location = useLocation();

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[320px_minmax(0,1fr)]">
      <aside className="hidden border-r border-black/10 lg:block">
        <div className="sticky top-0 flex h-screen flex-col justify-between px-8 py-10">
          <div>
            <p className="eyebrow">Hackathon prototype</p>
            <h1 className="display-text mt-3 text-4xl leading-none text-ink">
              Process-to-Automation Copilot
            </h1>
            <p className="mt-5 text-sm leading-7 text-[color:var(--muted)]">
              One guided story for judges, with enough exploration to prove the
              product is grounded in evidence.
            </p>

            <div className="panel mt-8 rounded-[2rem] p-5">
              <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                Guided path
              </p>
              <div className="mt-4 space-y-3">
                {navItems.map((item, index) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    className={({ isActive }) =>
                      `block rounded-[1.25rem] px-4 py-4 transition ${
                        isActive
                          ? "bg-[color:var(--accent-soft)] text-teal"
                          : "bg-white/65 hover:bg-white"
                      }`
                    }
                  >
                    <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
                      Step 0{index + 1}
                    </p>
                    <p className="mt-1 text-sm font-semibold">{item.label}</p>
                  </NavLink>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded-[1.75rem] border border-black/10 bg-white/70 px-5 py-5">
            <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
              Runtime
            </p>
            <p className="mt-2 text-lg font-semibold text-ink">
              {appMode === "live" ? "Live-first with fixture backup" : "Fixture-first demo"}
            </p>
            <p className="mt-2 text-sm leading-6 text-[color:var(--muted)]">
              The app always preserves a local demo path even if the API or LLM
              endpoints are not available.
            </p>
          </div>
        </div>
      </aside>

      <div className="min-h-screen">
        <header className="border-b border-black/10 bg-white/60 px-5 py-4 backdrop-blur lg:hidden">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="eyebrow">Hackathon prototype</p>
              <p className="display-text mt-2 text-2xl leading-none">
                Process-to-Automation Copilot
              </p>
            </div>
            <span className="rounded-full bg-black px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-white">
              {appMode}
            </span>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `rounded-full px-4 py-2 text-sm font-semibold ${
                    isActive ? "bg-ink text-white" : "bg-white/80"
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </header>

        <motion.main
          key={location.pathname}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          className="px-4 py-6 md:px-8 md:py-8 lg:px-10 lg:py-10"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}
