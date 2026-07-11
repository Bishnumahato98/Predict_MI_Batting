"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { PlayerStats } from "@/lib/types";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid,
} from "recharts";

interface Season {
  season_year: number;
  total_runs: number;
  avg_runs: number;
  avg_sr: number;
  players: number;
}

export default function DashboardPage() {
  const [seasons, setSeasons] = useState<Season[]>([]);
  const [players, setPlayers] = useState<PlayerStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get("/api/stats/seasons"), api.get("/api/stats/players")])
      .then(([s, p]) => {
        setSeasons(s.data.data);
        setPlayers(p.data.data.slice(0, 10));
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading)
    return <p className="text-neutral-500">Loading dashboard...</p>;

  const totalRuns = seasons.reduce((sum, s) => sum + s.total_runs, 0);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-neutral-400">
          Mumbai Indians batting analytics · 2008–2025
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
          <p className="text-sm text-neutral-400">Total MI runs</p>
          <p className="mt-1 text-3xl font-bold text-white">
            {totalRuns.toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
          <p className="text-sm text-neutral-400">Seasons covered</p>
          <p className="mt-1 text-3xl font-bold text-white">{seasons.length}</p>
        </div>
        <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
          <p className="text-sm text-neutral-400">Model accuracy</p>
          <p className="mt-1 text-3xl font-bold text-green-400">98%</p>
        </div>
      </div>

      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
        <h2 className="mb-4 font-semibold text-white">Season-wise total runs</h2>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={seasons}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis dataKey="season_year" stroke="#737373" fontSize={12} />
            <YAxis stroke="#737373" fontSize={12} />
            <Tooltip
              contentStyle={{ background: "#171717", border: "1px solid #404040", borderRadius: 8 }}
              labelStyle={{ color: "#fff" }}
            />
            <Line type="monotone" dataKey="total_runs" stroke="#3b82f6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
        <h2 className="mb-4 font-semibold text-white">Top 10 run scorers (all time)</h2>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={players} layout="vertical" margin={{ left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis type="number" stroke="#737373" fontSize={12} />
            <YAxis type="category" dataKey="batter" stroke="#737373" fontSize={12} width={100} />
            <Tooltip
              contentStyle={{ background: "#171717", border: "1px solid #404040", borderRadius: 8 }}
              labelStyle={{ color: "#fff" }}
            />
            <Bar dataKey="total_runs" fill="#3b82f6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
