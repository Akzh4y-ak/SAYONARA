// src/VideoChat.jsx
import { useEffect, useRef, useState } from "react";

const DEFAULT_ICE = [
  { urls: ["stun:stun.l.google.com:19302"] },
];

export default function VideoChat({ userName, onExit }) {
  const myVideo = useRef(null);
  const partnerVideo = useRef(null);
  const pcRef = useRef(null);
  const socketRef = useRef(null);
  const localStreamRef = useRef(null);
  const [status, setStatus] = useState("Connecting…");

  // WebSocket URL (adjust if backend runs elsewhere)
  const wsUrl = (() => {
    const proto = window.location.protocol === "https:" ? "wss" : "ws";
    return `${proto}://${window.location.hostname}:8000/chat/ws`;
  })();

  useEffect(() => {
    let mounted = true;

    const start = async () => {
      try {
        // Local media
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (!mounted) return;
        localStreamRef.current = stream;
        if (myVideo.current) myVideo.current.srcObject = stream;

        // WebSocket
        const ws = new WebSocket(wsUrl);
        socketRef.current = ws;

        ws.onopen = () => setStatus("Waiting for partner…");

        ws.onmessage = async (event) => {
          const msg = JSON.parse(event.data);
          const { event: type, data } = msg || {};
          console.log("📩 WS message:", msg);

          switch (type) {
            case "system":
              setStatus(data?.message || "System update");
              break;

            case "chat":
              console.log("💬 Chat:", data.text);
              break;

            case "offer":
              ensurePC();
              await pcRef.current.setRemoteDescription(new RTCSessionDescription(data));
              const answer = await pcRef.current.createAnswer();
              await pcRef.current.setLocalDescription(answer);
              send({ type: "answer", data: answer });
              break;

            case "answer":
              await pcRef.current?.setRemoteDescription(new RTCSessionDescription(data));
              break;

            case "ice-candidate":
              try {
                await pcRef.current?.addIceCandidate(data);
              } catch (e) {
                console.warn("ICE add failed:", e);
              }
              break;

            default:
              break;
          }
        };

        ws.onclose = () => setStatus("Disconnected");
      } catch (e) {
        console.error("getUserMedia error:", e);
        setStatus("Camera/Mic permission needed.");
      }
    };

    start();

    return () => {
      mounted = false;
      localStreamRef.current?.getTracks().forEach((t) => t.stop());
      try { pcRef.current?.close(); } catch {}
      pcRef.current = null;
      try { socketRef.current?.close(); } catch {}
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [wsUrl]);

  const send = (obj) => {
    try { socketRef.current?.send(JSON.stringify(obj)); } catch {}
  };

  const ensurePC = () => {
    if (pcRef.current) return pcRef.current;

    const pc = new RTCPeerConnection({ iceServers: DEFAULT_ICE });
    pcRef.current = pc;

    // Add local tracks
    localStreamRef.current?.getTracks().forEach((t) => pc.addTrack(t, localStreamRef.current));

    // Remote track
    pc.ontrack = (e) => {
      if (partnerVideo.current) {
        partnerVideo.current.srcObject = e.streams[0];
      }
    };

    // ICE
    pc.onicecandidate = (e) => {
      if (e.candidate) send({ type: "ice-candidate", data: e.candidate });
    };

    // Connection state
    pc.onconnectionstatechange = () => setStatus(pc.connectionState);

    return pc;
  };

  const resetRemote = () => {
    if (partnerVideo.current) partnerVideo.current.srcObject = null;
    try { pcRef.current?.close(); } catch {}
    pcRef.current = null;
  };

  const handleNext = () => {
    resetRemote();
    send({ type: "next" });
    setStatus("Searching for next…");
  };

  const handleStop = () => {
    send({ type: "disconnect" });
    try { socketRef.current?.close(); } catch {}
    resetRemote();
    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    if (onExit) onExit();
  };

  return (
    <div className="min-h-screen w-full bg-black text-white flex flex-col items-center justify-center gap-4 p-4">
      <div className="flex items-center gap-3">
        <span className="px-2 py-1 rounded bg-white/10 border border-white/20 text-xs">{status}</span>
        <span className="text-sm opacity-80">You: <b>{userName}</b></span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-5xl">
        <video ref={myVideo} autoPlay playsInline muted className="w-full aspect-video bg-gray-900 rounded-xl border border-white/10" />
        <video ref={partnerVideo} autoPlay playsInline className="w-full aspect-video bg-gray-900 rounded-xl border border-white/10" />
      </div>

      <div className="mt-4 flex gap-3">
        <button onClick={handleNext} className="px-5 py-2 rounded-lg bg-white text-black font-semibold hover:bg-white/90">
          Next
        </button>
        <button onClick={handleStop} className="px-5 py-2 rounded-lg bg-white/10 border border-white/20 font-semibold hover:bg-white/15">
          Stop & Home
        </button>
      </div>
    </div>
  );
}
