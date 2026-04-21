interface Props {
  score: number;
  size?: "sm" | "md" | "lg";
}

const sizes = {
  sm: { outer: 52, inner: 40, text: "text-sm" },
  md: { outer: 72, inner: 56, text: "text-lg" },
  lg: { outer: 96, inner: 76, text: "text-2xl" },
};

export function AriaScoreRing({ score, size = "md" }: Props) {
  const pct = Math.min(100, Math.max(0, score));
  const { outer, inner, text } = sizes[size];
  const deg = (pct / 100) * 360;

  return (
    <div
      className="inline-flex items-center justify-center rounded-full"
      style={{
        width: outer,
        height: outer,
        background: `conic-gradient(#7c3aed ${deg}deg, #1d1d26 0deg)`,
        padding: 3,
      }}
    >
      <div
        className="rounded-full bg-bg-base flex items-center justify-center"
        style={{ width: inner, height: inner }}
      >
        <span className={`font-bold text-white ${text}`}>{pct}</span>
      </div>
    </div>
  );
}
