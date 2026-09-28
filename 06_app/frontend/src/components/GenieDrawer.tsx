import { useEffect, useRef, useState } from 'react';
import { ChevronDown, Loader2, Send, Sparkles, X } from 'lucide-react';
import { api, type GenieAnswer } from '../lib/api';
import { RichText } from './ui';

const SUGGESTIONS = [
  'Quantos itens estão na fila de ação agora?',
  'Qual foi a receita perdida por ruptura nos últimos 7 dias?',
  'Quais fornecedores atrasam mais?',
  'Quais lojas têm a maior taxa de ruptura na última semana?',
  'Quais transferências entre lojas estão recomendadas?',
];

type Turn = { q: string; a?: GenieAnswer; err?: string };

function Result({ a }: { a: GenieAnswer }) {
  const [showSql, setShowSql] = useState(false);
  return (
    <div className="space-y-2">
      {a.answer && <div className="text-[13px] text-zinc-300 leading-relaxed"><RichText text={a.answer} /></div>}
      {a.columns.length > 0 && (
        <div className="overflow-x-auto rounded-lg border border-zinc-800 scrollbar-thin">
          <table className="w-full text-[11.5px]">
            <thead><tr>{a.columns.map((c) => <th key={c} className="text-left px-2.5 py-1.5 text-zinc-500 font-medium bg-zinc-900 whitespace-nowrap">{c}</th>)}</tr></thead>
            <tbody>{a.rows.slice(0, 12).map((r, i) => (
              <tr key={i} className="border-t border-zinc-800/80">{r.map((v, k) => <td key={k} className="px-2.5 py-1.5 text-zinc-300 font-mono whitespace-nowrap">{v ?? '—'}</td>)}</tr>
            ))}</tbody>
          </table>
        </div>
      )}
      {a.sql && (
        <div>
          <button onClick={() => setShowSql(!showSql)} className="text-[10px] uppercase tracking-[0.18em] text-zinc-500 hover:text-zinc-300 inline-flex items-center gap-1">
            SQL gerado pelo Genie <ChevronDown className={`w-3 h-3 transition-transform ${showSql ? 'rotate-180' : ''}`} />
          </button>
          {showSql && <pre className="mt-1.5 text-[11px] font-mono text-zinc-400 bg-zinc-950 border border-zinc-800 rounded-lg p-2.5 whitespace-pre-wrap">{a.sql}</pre>}
        </div>
      )}
      <div className="text-[10px] text-zinc-600 font-mono">{(a.duration_ms / 1000).toFixed(1)} s · registrado na Lakebase</div>
    </div>
  );
}

export default function GenieDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [q, setQ] = useState('');
  const [busy, setBusy] = useState(false);
  const [conv, setConv] = useState<string | undefined>();
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }); }, [turns, busy]);

  const ask = async (question: string) => {
    const text = question.trim();
    if (!text || busy) return;
    setQ(''); setBusy(true);
    setTurns((t) => [...t, { q: text }]);
    try {
      const a = await api.genie(text, conv);
      setConv(a.conversation_id);
      setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, a } : x)));
    } catch (e) {
      setTurns((t) => t.map((x, i) => (i === t.length - 1 ? { ...x, err: String(e) } : x)));
    } finally { setBusy(false); }
  };

  return (
    <>
      <div onClick={onClose} className={`fixed inset-0 z-40 bg-black/40 transition-opacity ${open ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} />
      <aside className={`fixed top-0 right-0 z-50 h-full w-full max-w-[460px] bg-zinc-950 border-l border-zinc-800 flex flex-col transition-transform duration-300 ${open ? 'translate-x-0' : 'translate-x-full'}`}>
        <header className="px-5 py-4 border-b border-zinc-800 flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 text-zinc-100 font-semibold"><Sparkles className="w-4 h-4 text-amber-400" /> Genie</div>
            <div className="text-[11px] text-zinc-500 mt-0.5">pergunte em português · SQL governado no Unity Catalog</div>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-200 p-1"><X className="w-4 h-4" /></button>
        </header>
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5 scrollbar-thin">
          {turns.length === 0 && (
            <div className="space-y-2">
              <div className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-semibold">Sugestões</div>
              {SUGGESTIONS.map((s) => (
                <button key={s} onClick={() => ask(s)} className="block w-full text-left text-[12.5px] text-zinc-300 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-2 hover:border-amber-500/40 hover:text-zinc-100">{s}</button>
              ))}
            </div>
          )}
          {turns.map((t, i) => (
            <div key={i} className="space-y-2">
              <div className="ml-10 rounded-xl rounded-tr-sm bg-amber-500/10 border border-amber-500/25 px-3 py-2 text-[13px] text-amber-100">{t.q}</div>
              {t.a && <Result a={t.a} />}
              {t.err && <div className="text-[12px] text-red-300">Genie não respondeu: {t.err}</div>}
            </div>
          ))}
          {busy && <div className="flex items-center gap-2 text-[12px] text-zinc-500"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Genie está escrevendo o SQL e consultando…</div>}
          <div ref={end} />
        </div>
        <form onSubmit={(e) => { e.preventDefault(); ask(q); }} className="p-4 border-t border-zinc-800 flex gap-2">
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="pergunte em português…"
            className="flex-1 bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-2 text-[13px] text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-amber-500/50" />
          <button disabled={busy} className="px-3 rounded-lg bg-amber-400 text-zinc-950 disabled:opacity-40"><Send className="w-4 h-4" /></button>
        </form>
      </aside>
    </>
  );
}
