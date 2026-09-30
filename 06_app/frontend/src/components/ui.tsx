import type { ReactNode } from 'react';
import { ArrowRightLeft, PackagePlus, Timer } from 'lucide-react';
import type { ActionType, Severity } from '../lib/api';

export function Kicker({ children, tone = 'amber' }: { children: ReactNode; tone?: 'amber' | 'teal' | 'zinc' | 'red' }) {
  const c = { amber: 'text-amber-400/90', teal: 'text-teal-300', zinc: 'text-zinc-500', red: 'text-red-400' }[tone];
  return <div className={`text-[10px] uppercase tracking-[0.25em] font-bold ${c}`}>{children}</div>;
}

export function PageTitle({ kicker, title, sub, right, tone }: { kicker: string; title: ReactNode; sub?: ReactNode; right?: ReactNode; tone?: 'amber' | 'teal' | 'zinc' | 'red' }) {
  return (
    <div className="flex items-end justify-between gap-4 flex-wrap mb-6">
      <div>
        <Kicker tone={tone}>{kicker}</Kicker>
        <h1 className="text-2xl font-semibold text-zinc-100 leading-tight mt-1">{title}</h1>
        {sub && <div className="text-xs text-zinc-500 mt-1">{sub}</div>}
      </div>
      {right}
    </div>
  );
}

export function Panel({ title, hint, right, children, className = '', bodyClassName = '', pad = true }: { title?: ReactNode; hint?: ReactNode; right?: ReactNode; children: ReactNode; className?: string; bodyClassName?: string; pad?: boolean }) {
  return (
    <section className={`rounded-xl border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm ${className}`}>
      {(title || right) && (
        <header className="flex items-start justify-between gap-3 px-5 pt-4 pb-3 border-b border-zinc-800/80">
          <div>
            {title && <div className="text-[11px] uppercase tracking-[0.22em] text-zinc-300 font-bold">{title}</div>}
            {hint && <div className="text-[11px] text-zinc-500 mt-0.5">{hint}</div>}
          </div>
          {right}
        </header>
      )}
      <div className={`${pad ? 'p-5' : ''} ${bodyClassName}`}>{children}</div>
    </section>
  );
}

/** Databricks product that powers a panel, shown like the War Room tags. */
export function ProductTag({ children }: { children: ReactNode }) {
  return <span className="text-[9.5px] uppercase tracking-[0.18em] text-zinc-500 font-semibold">{children}</span>;
}

export function Kpi({ label, value, sub, tone = 'default', icon }: { label: string; value: ReactNode; sub?: ReactNode; tone?: 'default' | 'amber' | 'emerald' | 'red'; icon?: ReactNode }) {
  const ring = { default: 'border-zinc-800 bg-zinc-900/60', amber: 'border-amber-500/40 bg-amber-500/[0.06]', emerald: 'border-emerald-500/40 bg-emerald-500/[0.06]', red: 'border-red-500/40 bg-red-500/[0.07]' }[tone];
  const val = { default: 'text-zinc-100', amber: 'text-amber-300', emerald: 'text-emerald-300', red: 'text-red-300' }[tone];
  return (
    <div className={`rounded-xl border px-4 py-3.5 ${ring}`}>
      <div className="flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-semibold">
        <span>{label}</span>{icon}
      </div>
      <div className={`font-mono text-[26px] font-bold tabular-nums mt-1.5 leading-none ${val}`}>{value}</div>
      {sub && <div className="text-[11px] text-zinc-500 mt-2">{sub}</div>}
    </div>
  );
}

export const SEV: Record<Severity, { label: string; chip: string; bar: string }> = {
  CRITICAL: { label: 'CRÍTICO', chip: 'bg-red-500/15 text-red-300 border-red-500/40', bar: 'border-l-red-500' },
  HIGH: { label: 'ALTO', chip: 'bg-orange-500/15 text-orange-300 border-orange-500/40', bar: 'border-l-orange-500' },
  MEDIUM: { label: 'MÉDIO', chip: 'bg-amber-500/10 text-amber-300 border-amber-500/30', bar: 'border-l-amber-500/70' },
};
export function SeverityBadge({ s }: { s: Severity }) {
  return <span className={`px-1.5 py-0.5 rounded border text-[10px] font-bold tracking-wider ${SEV[s].chip}`}>{SEV[s].label}</span>;
}

export const ACTION: Record<ActionType, { label: string; short: string; icon: typeof Timer; tone: string }> = {
  TRANSFER: { label: 'Transferir entre lojas', short: 'Transferir', icon: ArrowRightLeft, tone: 'text-teal-300' },
  EXPEDITE: { label: 'Antecipar pedido', short: 'Antecipar', icon: Timer, tone: 'text-sky-300' },
  URGENT_ORDER: { label: 'Pedido urgente', short: 'Pedido urgente', icon: PackagePlus, tone: 'text-amber-300' },
};
export function ActionLabel({ t }: { t: ActionType }) {
  const A = ACTION[t];
  return <span className={`inline-flex items-center gap-1.5 text-[11px] font-semibold ${A.tone}`}><A.icon className="w-3.5 h-3.5" />{A.label}</span>;
}

export function LiveDot({ color = 'bg-emerald-400' }: { color?: string }) {
  return (
    <span className="relative flex h-2 w-2">
      <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 ${color}`} />
      <span className={`relative inline-flex h-2 w-2 rounded-full ${color}`} />
    </span>
  );
}

export function Loading({ label = 'carregando da Lakebase…' }: { label?: string }) {
  return <div className="text-[12px] text-zinc-500 italic py-6 text-center">{label}</div>;
}

export function ErrorBox({ err }: { err: string | null }) {
  if (!err) return null;
  return <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-[12px] text-red-300">Falha ao carregar: {err}</div>;
}

/** Renders **bold** from Genie / agent text without pulling in a markdown lib. */
export function RichText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return <>{parts.map((p, i) => (p.startsWith('**') ? <strong key={i} className="text-zinc-100 font-semibold">{p.slice(2, -2)}</strong> : <span key={i}>{p}</span>))}</>;
}
