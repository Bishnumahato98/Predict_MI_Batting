"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import PredictionBadge from "@/components/PredictionBadge";

interface HistoryRecord {
  _id: string;
  type: "lineup" | "playing11";
  venue: string;
  opponent: string;
  season: number;
  created_at: string;
  results?: any[];
  playing11?: any[];
}

export default function HistoryPage() {
  const [records, setRecords] = useState<HistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<string | null>(null);

  useEffect(() => {
    api.get("/api/history")
      .then((res) => setRecords(res.data.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-neutral-500">Loading history...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Prediction History</h1>
        <p className="text-sm text-neutral-400">
          Your saved predictions ({records.length})
        </p>
      </div>

      {records.length === 0 && (
        <p className="rounded-xl border border-neutral-800 bg-neutral-900 p-8 text-center text-sm text-neutral-500">
          No predictions yet. Go to the Predict page and run one!
        </p>
      )}

      <div className="space-y-3">
        {records.map((r) => {
          const players = r.playing11 || r.results || [];
          const isOpen = open === r._id;
          return (
            <div key={r._id} className="rounded-xl border border-neutral-800 bg-neutral-900">
              <button
                onClick={() => setOpen(isOpen ? null : r._id)}
                className="flex w-full items-center justify-between px-5 py-4 text-left"
              >
                <div>
                  <p className="font-medium text-white">
                    {r.type === "playing11" ? "Playing XI" : "Lineup"} vs {r.opponent}
                  </p>
                  <p className="text-xs text-neutral-500">
                    {r.venue} · Season {r.season} ·{" "}
                    {new Date(r.created_at).toLocaleString()}
                  </p>
                </div>
                <span className="text-sm text-neutral-500">
                  {isOpen ? "Hide" : `${players.length} players`}
                </span>
              </button>

              {isOpen && (
                <div className="border-t border-neutral-800 px-5 py-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-neutral-400">
                        <th className="pb-2 pr-4">#</th>
                        <th className="pb-2 pr-4">Player</th>
                        <th className="pb-2 pr-4">Prediction</th>
                        <th className="pb-2">High %</th>
                      </tr>
                    </thead>
                    <tbody>
                      {players.map((p: any, i: number) => (
                        <tr key={p.name} className="border-t border-neutral-800/50 text-white">
                          <td className="py-2 pr-4 text-neutral-500">{i + 1}</td>
                          <td className="py-2 pr-4">{p.name}</td>
                          <td className="py-2 pr-4"><PredictionBadge value={p.prediction} /></td>
                          <td className="py-2">{p.prob_high}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
