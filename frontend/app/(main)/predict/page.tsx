"use client";

import { useState } from "react";
import api from "@/lib/api";
import PredictionBadge from "@/components/PredictionBadge";
import {
  DEFAULT_SQUAD, VENUES, OPPONENTS, SquadPlayer, Prediction,
} from "@/lib/types";
import { Trash2, Plus, Sparkles } from "lucide-react";

export default function PredictPage() {
  const [venue, setVenue] = useState(VENUES[0]);
  const [opponent, setOpponent] = useState(OPPONENTS[0]);
  const [season, setSeason] = useState(2025);
  const [squad, setSquad] = useState<SquadPlayer[]>(DEFAULT_SQUAD);
  const [newName, setNewName] = useState("");
  const [newRole, setNewRole] = useState<SquadPlayer["role"]>("BAT");
  const [newPos, setNewPos] = useState(7);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [playing11, setPlaying11] = useState<Prediction[]>([]);
  const [ranking, setRanking] = useState<Prediction[]>([]);

  const isHome = venue.includes("Wankhede");

  const addPlayer = () => {
    if (!newName.trim()) return;
    setSquad([...squad, { name: newName.trim(), role: newRole, batting_pos: newPos }]);
    setNewName("");
  };

  const removePlayer = (name: string) =>
    setSquad(squad.filter((p) => p.name !== name));

  const runPrediction = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/api/predict/playing11", {
        venue, opponent, season, is_home: isHome, squad,
      });
      setPlaying11(res.data.data.playing11);
      setRanking(res.data.data.ranking);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Predict Playing XI</h1>
        <p className="text-sm text-neutral-400">
          Set up the next match, edit the squad, and let the model recommend the best XI
        </p>
      </div>

      {/* Match setup */}
      <div className="grid grid-cols-1 gap-4 rounded-xl border border-neutral-800 bg-neutral-900 p-5 sm:grid-cols-3">
        <div>
          <label className="mb-1 block text-xs text-neutral-400">Venue</label>
          <select
            value={venue}
            onChange={(e) => setVenue(e.target.value)}
            className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white"
          >
            {VENUES.map((v) => <option key={v}>{v}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs text-neutral-400">Opponent</label>
          <select
            value={opponent}
            onChange={(e) => setOpponent(e.target.value)}
            className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white"
          >
            {OPPONENTS.map((o) => <option key={o}>{o}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs text-neutral-400">Season</label>
          <input
            type="number"
            value={season}
            onChange={(e) => setSeason(Number(e.target.value))}
            className="w-full rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white"
          />
        </div>
      </div>

      {/* Squad editor */}
      <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
        <h2 className="mb-4 font-semibold text-white">
          Squad ({squad.length} players)
        </h2>
        <div className="mb-4 flex flex-wrap gap-2">
          {squad.map((p) => (
            <span
              key={p.name}
              className="flex items-center gap-2 rounded-full border border-neutral-700 bg-neutral-800 px-3 py-1 text-sm text-white"
            >
              {p.name}
              <span className="text-xs text-neutral-500">{p.role}</span>
              <button onClick={() => removePlayer(p.name)} className="text-neutral-500 hover:text-red-400">
                <Trash2 size={13} />
              </button>
            </span>
          ))}
        </div>

        <div className="flex flex-wrap items-end gap-2">
          <input
            placeholder="Player name (e.g. RG Sharma)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            className="rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white placeholder-neutral-500"
          />
          <select
            value={newRole}
            onChange={(e) => setNewRole(e.target.value as SquadPlayer["role"])}
            className="rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white"
          >
            <option>BAT</option><option>WK</option><option>ALLR</option><option>BOWL</option>
          </select>
          <input
            type="number" min={1} max={11}
            value={newPos}
            onChange={(e) => setNewPos(Number(e.target.value))}
            className="w-20 rounded-lg border border-neutral-700 bg-neutral-800 px-3 py-2 text-sm text-white"
          />
          <button
            onClick={addPlayer}
            className="flex items-center gap-1 rounded-lg bg-neutral-700 px-3 py-2 text-sm text-white hover:bg-neutral-600"
          >
            <Plus size={15} /> Add
          </button>
        </div>
      </div>

      <button
        onClick={runPrediction}
        disabled={loading || squad.length < 11}
        className="flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:opacity-50"
      >
        <Sparkles size={16} />
        {loading ? "Predicting..." : "Predict Playing XI"}
      </button>

      {error && (
        <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400">{error}</p>
      )}

      {/* Results */}
      {playing11.length > 0 && (
        <>
          <div className="rounded-xl border border-blue-500/30 bg-neutral-900 p-5">
            <h2 className="mb-4 font-semibold text-blue-400">
              ⭐ Recommended Playing XI — vs {opponent}
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-800 text-left text-neutral-400">
                    <th className="pb-2 pr-4">#</th>
                    <th className="pb-2 pr-4">Player</th>
                    <th className="pb-2 pr-4">Role</th>
                    <th className="pb-2 pr-4">Prediction</th>
                    <th className="pb-2 pr-4">Score</th>
                    <th className="pb-2 pr-4">High %</th>
                    <th className="pb-2">Last 5 avg</th>
                  </tr>
                </thead>
                <tbody>
                  {playing11.map((p, i) => (
                    <tr key={p.name} className="border-b border-neutral-800/50 text-white">
                      <td className="py-2.5 pr-4 text-neutral-500">{i + 1}</td>
                      <td className="py-2.5 pr-4 font-medium">{p.name}</td>
                      <td className="py-2.5 pr-4 text-neutral-400">{p.role}</td>
                      <td className="py-2.5 pr-4"><PredictionBadge value={p.prediction} /></td>
                      <td className="py-2.5 pr-4">{p.composite_score}</td>
                      <td className="py-2.5 pr-4">{p.prob_high}%</td>
                      <td className="py-2.5">{p.avg_runs_last5}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-xl border border-neutral-800 bg-neutral-900 p-5">
            <h2 className="mb-4 font-semibold text-white">Full squad ranking</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-neutral-800 text-left text-neutral-400">
                    <th className="pb-2 pr-4">Rank</th>
                    <th className="pb-2 pr-4">Player</th>
                    <th className="pb-2 pr-4">Role</th>
                    <th className="pb-2 pr-4">Prediction</th>
                    <th className="pb-2">Composite score</th>
                  </tr>
                </thead>
                <tbody>
                  {ranking.map((p, i) => (
                    <tr key={p.name} className="border-b border-neutral-800/50 text-white">
                      <td className="py-2.5 pr-4 text-neutral-500">{i + 1}</td>
                      <td className="py-2.5 pr-4">{p.name}</td>
                      <td className="py-2.5 pr-4 text-neutral-400">{p.role}</td>
                      <td className="py-2.5 pr-4"><PredictionBadge value={p.prediction} /></td>
                      <td className="py-2.5">{p.composite_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
