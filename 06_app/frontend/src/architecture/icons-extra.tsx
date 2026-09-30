/**
 * icons-extra.tsx — additional Databricks product/glyph icons in the same
 * two-tone house style as icons.tsx (SOLID #EF5B3F + LIGHT #F5C5BC, viewBox
 * "0 0 48 48"). These cover the ML / MLOps / streaming surface that the
 * original set didn't include, so a diagram for a model-serving or
 * feature-engineering architecture has proper tiles.
 *
 * Same contract as icons.tsx: each is a self-contained <svg>; the caller sizes
 * it via a wrapper. Add more here as new architectures need them — keep the
 * two-tone convention so everything reads as one system.
 */

const SOLID = '#EF5B3F';
const LIGHT = '#F5C5BC';

/** Model Serving — a stack of endpoints with a signal arrow leaving the top. */
export const ModelServingIcon = () => (
  <svg viewBox="0 0 48 48">
    <rect x="8" y="28" width="32" height="8" rx="2" fill={LIGHT} />
    <rect x="8" y="38" width="32" height="6" rx="2" fill={LIGHT} opacity=".7" />
    <circle cx="24" cy="16" r="8" fill={SOLID} />
    <path d="M24 4v6M24 4l-3 3M24 4l3 3" stroke={SOLID} strokeWidth="2.4"
          strokeLinecap="round" strokeLinejoin="round" fill="none" />
  </svg>
);

/** Feature Store — a grid of feature cells with one highlighted column. */
export const FeatureStoreIcon = () => (
  <svg viewBox="0 0 48 48">
    <rect x="7"  y="8"  width="10" height="10" rx="2" fill={LIGHT} />
    <rect x="19" y="8"  width="10" height="10" rx="2" fill={SOLID} />
    <rect x="31" y="8"  width="10" height="10" rx="2" fill={LIGHT} />
    <rect x="7"  y="20" width="10" height="10" rx="2" fill={LIGHT} />
    <rect x="19" y="20" width="10" height="10" rx="2" fill={SOLID} />
    <rect x="31" y="20" width="10" height="10" rx="2" fill={LIGHT} />
    <rect x="7"  y="32" width="10" height="10" rx="2" fill={LIGHT} opacity=".7" />
    <rect x="19" y="32" width="10" height="10" rx="2" fill={SOLID} />
    <rect x="31" y="32" width="10" height="10" rx="2" fill={LIGHT} opacity=".7" />
  </svg>
);

/** Vector Search — points in space with a query radius ring. */
export const VectorSearchIcon = () => (
  <svg viewBox="0 0 48 48">
    <circle cx="20" cy="20" r="13" fill="none" stroke={LIGHT} strokeWidth="3" />
    <circle cx="14" cy="16" r="2.4" fill={SOLID} />
    <circle cx="24" cy="13" r="2.4" fill={SOLID} />
    <circle cx="27" cy="24" r="2.4" fill={SOLID} />
    <circle cx="16" cy="26" r="2.4" fill={SOLID} />
    <path d="M30 30l10 10" stroke={SOLID} strokeWidth="3.2" strokeLinecap="round" />
  </svg>
);

/** MLflow Model Registry — a versioned model card stack with a check. */
export const MLflowRegistryIcon = () => (
  <svg viewBox="0 0 48 48">
    <rect x="10" y="6"  width="28" height="30" rx="3" fill={LIGHT} />
    <rect x="6"  y="12" width="28" height="30" rx="3" fill={SOLID} />
    <path d="M13 27l4 4 8-8" stroke="#fff" strokeWidth="3"
          strokeLinecap="round" strokeLinejoin="round" fill="none" />
  </svg>
);

/** Workflows / Jobs — three connected task nodes (DAG). */
export const WorkflowsIcon = () => (
  <svg viewBox="0 0 48 48">
    <path d="M14 14h9M27 14c0 6 -6 14 0 20h5" stroke={LIGHT} strokeWidth="3"
          fill="none" strokeLinecap="round" />
    <circle cx="11" cy="14" r="6" fill={SOLID} />
    <circle cx="30" cy="14" r="6" fill={LIGHT} />
    <circle cx="36" cy="34" r="6" fill={SOLID} />
  </svg>
);

/** Structured Streaming — three chevrons flowing right (continuous micro-batch). */
export const StreamingIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" stroke={SOLID} strokeWidth="4"
       strokeLinecap="round" strokeLinejoin="round">
    <path d="M10 12l8 12-8 12" opacity=".45" />
    <path d="M22 12l8 12-8 12" opacity=".7" />
    <path d="M34 12l4 6" />
  </svg>
);

/** Foundation Model / LLM endpoint — a spark/asterisk in a rounded chip,
 *  for a "served LLM" tile (Claude via Databricks Foundation Model API). */
export const FoundationModelIcon = () => (
  <svg viewBox="0 0 48 48">
    <rect x="7" y="7" width="34" height="34" rx="9" fill={LIGHT} />
    <path fill={SOLID} d="M24 12c1.6 6 3.4 7.8 9.4 9.4-6 1.6-7.8 3.4-9.4 9.4-1.6-6-3.4-7.8-9.4-9.4 6-1.6 7.8-3.4 9.4-9.4Z" transform="translate(0 2.6)" />
  </svg>
);

/** External source / cloud API — a cloud with a down-arrow (3rd-party feed
 *  like INMET weather, market data, etc.). Line style, single tone. */
export const ExternalApiIcon = () => (
  <svg viewBox="0 0 48 48" fill="none" stroke={SOLID} strokeWidth="2.6"
       strokeLinecap="round" strokeLinejoin="round">
    <path d="M15 30a7 7 0 0 1 .8-14 9 9 0 0 1 17 2.2A6.5 6.5 0 0 1 33 30z" fill={LIGHT} stroke="none" />
    <path d="M15 30a7 7 0 0 1 .8-14 9 9 0 0 1 17 2.2A6.5 6.5 0 0 1 33 30" />
    <path d="M24 24v11M24 35l-4-4M24 35l4-4" />
  </svg>
);

/** Document intelligence / FNOL — a document with lines and a small spark,
 *  for an unstructured-doc-in tile (claim notes, wordings, PDFs). */
export const DocIntelIcon = () => (
  <svg viewBox="0 0 48 48">
    <path d="M13 5h16l6 6v32H13z" fill={LIGHT} />
    <path d="M29 5l6 6h-6z" fill={SOLID} opacity=".7" />
    <path d="M18 20h12M18 26h12M18 32h8" stroke={SOLID} strokeWidth="2.2" strokeLinecap="round" />
  </svg>
);

/** Alerting / Monitor — a bell with a live pulse dot (for a monitoring tile). */
export const MonitorIcon = () => (
  <svg viewBox="0 0 48 48">
    <path d="M14 32V22a10 10 0 0 1 20 0v10l3 4H11z" fill={LIGHT} />
    <path d="M20 40a4 4 0 0 0 8 0" fill="none" stroke={SOLID} strokeWidth="2.6"
          strokeLinecap="round" />
    <circle cx="34" cy="14" r="5" fill={SOLID} />
  </svg>
);
