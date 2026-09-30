import { useEffect, useState, type ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { Bot, Database, LayoutDashboard, ListChecks, MapPinned, Sparkles, Workflow } from 'lucide-react';
import { LiveDot } from './ui';
import GenieDrawer from './GenieDrawer';
import ArchitectureView from '../architecture/ArchitectureView';
import { dateBR } from '../lib/format';

const NAV = [
  { to: '/', label: 'Início', icon: LayoutDashboard, end: true },
  { to: '/rede', label: 'Rede de lojas', icon: MapPinned },
  { to: '/fila', label: 'Fila de ação', icon: ListChecks },
  { to: '/agente', label: 'Agente', icon: Bot },
  { to: '/lakebase', label: 'Lakebase', icon: Database },
];

function Clock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 1000); return () => clearInterval(t); }, []);
  return (
    <>
      <span className="hidden md:block text-[11px] tracking-widest text-zinc-500 font-mono uppercase">
        {now.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: 'short' }).replace(/\./g, '')}
      </span>
      <span className="font-mono text-base tabular-nums text-zinc-200 tracking-wide">
        {now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
      </span>
    </>
  );
}

export default function Shell({ children, asOf }: { children: ReactNode; asOf?: string | null }) {
  const [genie, setGenie] = useState(false);
  const [arch, setArch] = useState(false);
  return (
    <div className="min-h-screen relative overflow-x-hidden">
      {/* backdrop: slow drifting blobs + moving grid */}
      <div aria-hidden className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-grid animate-grid-shift opacity-60" />
        <div className="absolute -top-40 -right-40 w-[46rem] h-[46rem] rounded-full bg-amber-500/10 blur-3xl animate-blob-drift-a" />
        <div className="absolute top-[40%] -left-52 w-[40rem] h-[40rem] rounded-full bg-orange-600/[0.07] blur-3xl animate-blob-drift-b" />
        <div className="absolute bottom-0 right-1/3 w-[30rem] h-[30rem] rounded-full bg-teal-500/[0.05] blur-3xl animate-blob-pulse" />
      </div>

      <header className="sticky top-0 z-30 border-b border-zinc-800/80 bg-zinc-950/85 backdrop-blur-md">
        <div className="max-w-[1400px] mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 shrink-0 rounded-lg bg-gradient-to-br from-amber-300 to-orange-500 grid place-items-center shadow-[0_0_18px_-4px_rgba(251,191,36,0.6)]">
              <span className="text-zinc-950 font-black text-lg leading-none">L</span>
            </div>
            <div className="leading-tight">
              <div className="text-zinc-100 font-semibold tracking-tight text-[15px]">
                <span className="text-amber-400">LojaBR</span> <span className="text-zinc-400 font-normal">· Centro de Abastecimento</span>
              </div>
              <div className="text-[10px] uppercase tracking-[0.22em] text-zinc-500 mt-0.5">previsão de ruptura · ação antes da gôndola esvaziar</div>
            </div>
          </div>
          <div className="flex items-center gap-6">
            {/* glowing entry point to the live architecture (Databricks orange, like the diagram) */}
            <button onClick={() => setArch(true)} title="Ver a arquitetura: cada estágio abre no workspace"
              className="relative inline-flex items-center gap-2 rounded-full border border-[#EF5B3F]/60 bg-gradient-to-r from-[#EF5B3F]/25 to-orange-400/10 px-3.5 py-1.5 text-[10.5px] font-bold uppercase tracking-[0.18em] text-orange-100 animate-arch-glow hover:from-[#EF5B3F]/40 transition-colors">
              <span className="relative flex w-2 h-2">
                <span className="absolute inset-0 rounded-full bg-[#EF5B3F] animate-ping opacity-75" />
                <span className="relative w-2 h-2 rounded-full bg-[#EF5B3F] shadow-[0_0_8px_#EF5B3F]" />
              </span>
              <Workflow className="w-3.5 h-3.5" /><span className="hidden sm:inline">arquitetura</span>
            </button>
            {asOf && (
              <span className="hidden lg:block text-[10px] uppercase tracking-[0.2em] text-zinc-500">
                dados até <span className="text-zinc-300 font-mono">{dateBR(asOf)}</span>
              </span>
            )}
            <Clock />
            <span className="flex items-center gap-2 px-2.5 py-1 rounded-full border border-zinc-700/70 bg-zinc-800/60">
              <LiveDot /><span className="text-[10px] uppercase tracking-[0.2em] text-zinc-300 font-medium">ao vivo</span>
            </span>
          </div>
        </div>
        <nav className="max-w-[1400px] mx-auto px-6 flex gap-1 overflow-x-auto scrollbar-thin">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end}
              className={({ isActive }) => `flex items-center gap-2 px-3.5 py-2.5 text-[12px] uppercase tracking-[0.14em] font-medium border-b-2 whitespace-nowrap transition-colors ${
                isActive ? 'border-amber-400 text-amber-300' : 'border-transparent text-zinc-400 hover:text-zinc-200'}`}>
              <n.icon className="w-4 h-4" />{n.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <main className="max-w-[1400px] mx-auto px-6 py-8">{children}</main>

      <footer className="max-w-[1400px] mx-auto px-6 pb-10 pt-4 text-center text-[10px] uppercase tracking-[0.3em] text-zinc-600">
        LojaBR · Centro de Abastecimento · dados sintéticos · powered by Databricks
      </footer>

      <button onClick={() => setGenie(true)} title="Perguntar ao Genie"
        className="fixed bottom-7 right-7 z-40 w-14 h-14 rounded-full bg-gradient-to-br from-amber-300 to-orange-500 text-zinc-950 grid place-items-center animate-agent-glow hover:scale-105 transition-transform">
        <Sparkles className="w-6 h-6 animate-agent-sparkle" />
      </button>
      <GenieDrawer open={genie} onClose={() => setGenie(false)} />
      <ArchitectureView open={arch} onClose={() => setArch(false)} />
    </div>
  );
}
