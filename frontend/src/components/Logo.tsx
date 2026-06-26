export function Logo() {
  return (
    <div className="flex items-center gap-3 select-none">
      <span className="relative flex h-9 w-9 items-center justify-center rounded-lg bg-signal/10 ring-1 ring-signal/30">
        <svg viewBox="0 0 24 24" className="h-5 w-5 text-signal" aria-hidden="true">
          <g fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M3 8h18" opacity="0.35" />
            <path d="M3 16h11" />
            <path d="M17 16h4" />
          </g>
        </svg>
        <span className="absolute -bottom-1 left-1/2 h-px w-5 -translate-x-1/2 bg-signal/60" />
      </span>
      <div className="leading-none">
        <p className="font-display text-lg font-extrabold tracking-tight text-mist">
          Subtitulator
        </p>
        <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-mist-dim">
          subtitle studio
        </p>
      </div>
    </div>
  );
}
