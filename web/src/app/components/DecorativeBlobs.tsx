'use client';

export default function DecorativeBlobs() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
      <div
        className="absolute -top-40 -right-40 w-[500px] h-[500px] rounded-full opacity-[0.06]"
        style={{ background: 'radial-gradient(circle, #ff6b6b, transparent 70%)' }}
      />
      <div
        className="absolute top-1/3 -left-32 w-[400px] h-[400px] rounded-full opacity-[0.05]"
        style={{ background: 'radial-gradient(circle, #a78bfa, transparent 70%)' }}
      />
      <div
        className="absolute -bottom-40 right-1/4 w-[450px] h-[450px] rounded-full opacity-[0.05]"
        style={{ background: 'radial-gradient(circle, #ffa07a, transparent 70%)' }}
      />
    </div>
  );
}
