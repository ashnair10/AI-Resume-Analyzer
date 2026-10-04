"use client";

import { motion } from "motion/react";

export function ScoreRing({ score }: { score: number }) {
  const r = 50;
  const c = 2 * Math.PI * r;
  const offset = c - (Math.max(0, Math.min(100, score)) / 100) * c;
  return (
    <div className="relative h-36 w-36">
      <svg className="h-full w-full -rotate-90" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,.07)" strokeWidth="8" />
        <motion.circle
          cx="60" cy="60" r={r} fill="none" stroke="url(#scoreGradient)" strokeWidth="8" strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: offset }}
          transition={{ type: "spring", stiffness: 55, damping: 18, delay: 0.1 }}
        />
        <defs>
          <linearGradient id="scoreGradient" x1="0" x2="1">
            <stop offset="0%" stopColor="#8b5cf6" />
            <stop offset="100%" stopColor="#60a5fa" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.div initial={{ opacity: 0, scale: .8 }} animate={{ opacity: 1, scale: 1 }} className="text-4xl font-semibold tracking-tight">{score}</motion.div>
        <div className="text-xs text-zinc-500">Role Evidence</div>
      </div>
    </div>
  );
}
