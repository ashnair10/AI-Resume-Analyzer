"use client";

import { AnimatePresence, motion } from "motion/react";
import { ChevronDown, CheckCircle2, CircleAlert, CircleX, MinusCircle } from "lucide-react";
import { useState } from "react";
import type { EvidenceItem } from "@/lib/types";

const meta = {
  strong: { icon: CheckCircle2, text: "Strong", cls: "text-emerald-300 border-emerald-400/20 bg-emerald-400/[.06]" },
  moderate: { icon: MinusCircle, text: "Moderate", cls: "text-sky-300 border-sky-400/20 bg-sky-400/[.06]" },
  weak: { icon: CircleAlert, text: "Weak", cls: "text-amber-300 border-amber-400/20 bg-amber-400/[.06]" },
  missing: { icon: CircleX, text: "Missing", cls: "text-rose-300 border-rose-400/20 bg-rose-400/[.06]" },
};

export function EvidenceCard({ item, index }: { item: EvidenceItem; index: number }) {
  const [open, setOpen] = useState(false);
  const M = meta[item.status];
  const Icon = M.icon;
  return (
    <motion.div layout initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .035 }} className="overflow-hidden rounded-xl border border-slate-300/15 bg-slate-950/30">
      <button onClick={() => setOpen(v => !v)} className="flex w-full items-center gap-3 p-3.5 text-left">
        <Icon className="h-4 w-4 shrink-0 text-zinc-400" />
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium capitalize text-slate-100">{item.requirement}</div>
          <div className="mt-1 text-xs text-slate-300">{item.evidence.length ? `${item.evidence.length} matching resume line${item.evidence.length > 1 ? "s" : ""}` : "No direct keyword match found"}</div>
        </div>
        <span className={`rounded-full border px-2 py-1 text-[11px] ${M.cls}`}>{M.text}</span>
        <motion.span animate={{ rotate: open ? 180 : 0 }}><ChevronDown className="h-4 w-4 text-zinc-600" /></motion.span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: .22 }}>
            <div className="border-t border-slate-300/15 px-4 py-3">
              {item.evidence.length ? item.evidence.map((e, i) => (
                <div key={i} className="mb-2 rounded-lg bg-slate-800/70 px-3 py-2 text-xs leading-5 text-slate-200 last:mb-0">{e}</div>
              )) : <p className="text-xs text-slate-300">No direct wording match was found. Check whether you have equivalent experience expressed another way before treating this as a gap.</p>}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
