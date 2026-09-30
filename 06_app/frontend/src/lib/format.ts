const nf0 = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 });
const nf1 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
const nf2 = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** Compact BRL: R$ 2,45 mi · R$ 18,8 mil · R$ 771 */
export function brl(v: number | null | undefined): string {
  const n = Number(v || 0);
  if (Math.abs(n) >= 1e6) return `R$ ${nf2.format(n / 1e6)} mi`;
  if (Math.abs(n) >= 1e4) return `R$ ${nf1.format(n / 1e3)} mil`;
  return `R$ ${nf0.format(n)}`;
}
export const brlFull = (v: number | null | undefined) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(Number(v || 0));
export const pct = (v: number | null | undefined, d = 1) =>
  `${new Intl.NumberFormat('pt-BR', { minimumFractionDigits: d, maximumFractionDigits: d }).format(Number(v || 0) * 100)}%`;
export const num = (v: number | null | undefined) => nf0.format(Number(v || 0));
export const dec1 = (v: number | null | undefined) => nf1.format(Number(v || 0));
export function dateBR(iso?: string | null, opts: Intl.DateTimeFormatOptions = { day: '2-digit', month: 'short' }) {
  if (!iso) return '—';
  const d = new Date(iso.length === 10 ? `${iso}T12:00:00` : iso);
  return d.toLocaleDateString('pt-BR', opts).replace('.', '');
}
export const timeBR = (iso?: string | null) =>
  iso ? new Date(iso).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '—';

/** Time only for today's events, "dd/mm hh:mm" for older ones. */
export function whenBR(iso?: string | null) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toDateString() === new Date().toDateString() ? timeBR(iso)
    : `${d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })} ${timeBR(iso)}`;
}
