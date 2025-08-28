import { useState } from "react";

function MainPage({ onStart }) {
  const [nickname, setNickname] = useState("");

  // 🔹 Random guest names (rotating adjectives for variety)
  const adjectives = ["Stargazer", "Dreamer", "Wanderer", "Cosmic", "Nomad"];
  const generateGuestName = () => {
    const word = adjectives[Math.floor(Math.random() * adjectives.length)];
    return word + "_" + Math.floor(1000 + Math.random() * 9000);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let finalName = nickname.trim();

    // if empty, fallback to random guest name
    if (!finalName) {
      finalName = generateGuestName();
    }

    // 🚀 pass nickname back to parent (connect to backend here)
    onStart(finalName);
  };

  return (
    <div className="relative flex flex-col items-center justify-center min-h-screen text-white overflow-hidden">

      {/* Background video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover"
      >
        <source src="/bg-video.mp4" type="video/mp4" />
      </video>

      {/* Overlay */}
      <div className="absolute inset-0 bg-black/50"></div>
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-transparent to-black/70" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_30%,rgba(0,0,0,0.6)_100%)]" />
      </div>

      {/* Title */}
      <h1 className="relative text-5xl md:text-7xl font-semibold tracking-wide mb-4 text-white drop-shadow-[0_2px_24px_rgba(0,0,0,0.55)] text-center">
        SAYONARA
      </h1>

      {/* Subtitle */}
      <p className="relative text-slate-200/90 mb-10 text-lg text-center max-w-xl leading-relaxed">
        Meet strangers under the same sky.
      </p>

      {/* Form card */}
      <form
        onSubmit={handleSubmit}
        className="relative w-full max-w-md rounded-2xl border border-white/15 bg-white/8 backdrop-blur-md p-5 md:p-6 shadow-[0_10px_40px_rgba(0,0,0,0.35)]"
      >
        <label className="block text-sm text-slate-200/80 mb-2">
          Your name
        </label>
        <input
          type="text"
          placeholder="Enter a nickname or leave empty"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/60 outline-none focus:border-white/50 focus:ring-2 focus:ring-white/20 transition"
        />

        <div className="mt-5 grid grid-cols-2 gap-3">
          {/* Start button */}
          <button
            type="submit"
            className="px-4 py-3 rounded-xl font-semibold bg-white/90 text-gray-900 hover:bg-white transition shadow"
          >
            Start
          </button>

          {/* Random nickname button */}
          <button
            type="button"
            onClick={() => setNickname(generateGuestName())}
            className="px-4 py-3 rounded-xl font-semibold bg-white/10 border border-white/25 hover:bg-white/15 transition"
          >
            Random
          </button>
        </div>
      </form>

      {/* Footer */}
      <div className="relative mt-8 text-xs text-slate-200/70">
        No login. Just vibe.
      </div>
    </div>
  );
}

export default MainPage;
