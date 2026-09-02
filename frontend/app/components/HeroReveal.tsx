type HeroLine = {
  text: string;
  accent?: boolean;
};

export function HeroReveal({ lines, className = "" }: { lines: HeroLine[]; className?: string }) {
  return (
    <h1 className={`font-display text-4xl font-semibold leading-[1.12] tracking-tight md:text-5xl lg:text-[3.25rem] ${className}`}>
      {lines.map((line, i) => (
        <span key={line.text} className="hero-line-wrapper">
          <span className={`hero-line-inner ${i > 0 ? `delay-${i}` : ""}`}>
            {line.accent ? (
              <span className="text-accent">{line.text}</span>
            ) : (
              line.text
            )}
          </span>
        </span>
      ))}
    </h1>
  );
}
