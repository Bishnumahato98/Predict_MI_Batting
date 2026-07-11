"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { PlayerStats } from "@/lib/types";
import { Search } from "lucide-react";

interface PlayerDetail {
  name: string;
  matches: number;
  total_runs: number;
  avg_runs: number;
  avg_sr: number;
  avg_runs_last5: number;
  avg_sr_last5: number;
  best_score: number;
  fifties: number;
  home_avg: number;
  away_avg: number;
}

export default function PlayersPage() {
  const [players, setPlayers] = useState<PlayerStats[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<PlayerDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/api/stats/players")
      .then((res) => setPlayers(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  const openPlayer = async (name: string) => {
    const res = await api.get(`/api/stats/players/${encodeURIComponent(name)}`);
    setSelected(res.data.data);
  };

  const filtered = players.filter((p) =>
    p.batter.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <p className="text-neutral-500">Loading players...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">MI Players</h1>
        <p className="text-sm text-neutral-400">
          {players.length} batters · click any player for full history
        </p>
      </div>

      <div className="relative max-w-sm">
        <Search size={16} className="absolute left-3 top-2.5 text-neutral-500" />
        <input
          placeholder="Search player..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-neutral-700 bg-neutral-800 py-2 pl-9 pr-3 text-sm text-white placeholder-neutral-500 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Table */}
        <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5 lg:col-span-2">
          <div className="max-h-[560px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-neutral-900">
                <tr className="border-b border-neutral-800 text-left text-neutral-400">
                  <th className="pb-2 pr-4">Player</th>
                  <th className="pb-2 pr-4">Matches</th>
                  <th className="pb-2 pr-4">Runs</th>
                  <th className="pb-2 pr-4">Avg</th>
                  <th className="pb-2 pr-4">SR</th>
                  <th className="pb-2">50s</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((p) => (
                  <tr
                    key={p.batter}
                    onClick={() => openPlayer(p.batter)}
                    className="cursor-pointer border-b border-neutral-800/50 text-white transition hover:bg-neutral-800/50"
                  >
                    <td className="py-2.5 pr-4 font-medium">{p.batter}</td>
                    <td className="py-2.5 pr-4">{p.matches}</td>
                    <td className="py-2.5 pr-4">{p.total_runs}</td>
                    <td className="py-2.5 pr-4">{p.avg_runs}</td>
                    <td className="py-2.5 pr-4">{p.avg_sr}</td>
                    <td className="py-2.5">{p.fifties}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Detail panel */}
        <div className="h-fit rounded-xl border border-neutral-800 bg-neutral-900 p-5">
          {selected ? (
            <>
              <h2 className="mb-4 text-lg font-bold text-white">{selected.name}</h2>
              <dl className="space-y-3 text-sm">
                {[
                  ["Matches", selected.matches],
                  ["Total runs", selected.total_runs],
                  ["Career average", selected.avg_runs],
                  ["Career strike rate", selected.avg_sr],
                  ["Last 5 avg", selected.avg_runs_last5],
                  ["Last 5 SR", selected.avg_sr_last5],
                  ["Best score", selected.best_score],
                  ["Fifties", selected.fifties],
                  ["Home (Wankhede) avg", selected.home_avg],
                  ["Away avg", selected.away_avg],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between border-b border-neutral-800/50 pb-2">
                    <dt className="text-neutral-400">{label}</dt>
                    <dd className="font-semibold text-white">{value}</dd>
                  </div>
                ))}
              </dl>
            </>
          ) : (
            <p className="text-sm text-neutral-500">
              Select a player from the table to view full stats
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
