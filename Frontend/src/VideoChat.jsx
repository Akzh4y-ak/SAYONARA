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
  const iceCandidateQueue = useRef([]);
  const [status, setStatus] = useState("Connecting…");

  const wsUrl =
    import.meta.env.MODE === "development"
      ? `ws://localhost:8000/ws-video/${userName}`
      : `wss://sayonara-3.onrender.com/ws-video/${userName}`; // This line was updated

  useEffect(() => {
    let mounted = true;

    const start = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        if (!mounted) return;
        localStreamRef.current = stream;
        if (myVideo.current) myVideo.current.srcObject = stream;

        const ws = new WebSocket(wsUrl);
        socketRef.current = ws;

        ws.onopen = () => setStatus("Waiting for partner…");

        ws.onmessage = async (event) => {
          const msg = JSON.parse(event.data);
          const { type, data, from_user, is_initiator } = msg || {};
          console.log("📩 WS message:", msg);

          switch (type) {
            case "partnerFound":
              setStatus(`Connected with ${from_user || "partner"}`);
              ensurePC();
              // FIX: Use the flag from the server to determine who creates the offer.
              if (is_initiator) {
                const offer = await pcRef.current.createOffer();
                await pcRef.current.setLocalDescription(offer);
                send({ type: "offer", data: offer });
              }
              break;

            case "offer":
              ensurePC();
              await pcRef.current.setRemoteDescription(new RTCSessionDescription(data));
              await processIceQueue();
              const answer = await pcRef.current.createAnswer();
              await pcRef.current.setLocalDescription(answer);
              send({ type: "answer", data: answer });
              break;

            case "answer":
              await pcRef.current?.setRemoteDescription(new RTCSessionDescription(data));
              await processIceQueue();
              break;

            case "ice-candidate":
              if (pcRef.current?.remoteDescription) {
                await pcRef.current.addIceCandidate(data);
              } else {
                iceCandidateQueue.current.push(data);
              }
              break;
            
            case "partnerSkipped":
            case "partnerDisconnected":
              setStatus("Partner left. Searching for a new one…");
              resetRemote();
              break;

            default:
              console.warn("Unknown message type:", type);
              break;
          }
        };

        ws.onclose = () => setStatus("Disconnected");
      } catch (e) {
        console.error("getUserMedia error:", e);
        setStatus("Camera/Mic permission is required.");
      }
    };

    start();

    return () => {
      mounted = false;
      localStreamRef.current?.getTracks().forEach((t) => t.stop());
      pcRef.current?.close();
      socketRef.current?.close();
    };
  }, [wsUrl]);

  const processIceQueue = async () => {
    while (iceCandidateQueue.current.length > 0) {
      const candidate = iceCandidateQueue.current.shift();
      try {
        await pcRef.current.addIceCandidate(candidate);
      } catch (e) {
        console.warn("ICE add failed:", e);
      }
    }
  };

  const send = (obj) => {
    try {
      socketRef.current?.send(JSON.stringify(obj));
    } catch (e) {
      console.error("Error sending message:", e);
    }
  };

  const ensurePC = () => {
    if (pcRef.current) return;

    const pc = new RTCPeerConnection({ iceServers: DEFAULT_ICE });
    pcRef.current = pc;

    localStreamRef.current?.getTracks().forEach((t) => pc.addTrack(t, localStreamRef.current));

    pc.ontrack = (e) => {
      if (partnerVideo.current) partnerVideo.current.srcObject = e.streams[0];
    };

    pc.onicecandidate = (e) => {
      if (e.candidate) send({ type: "ice-candidate", data: e.candidate });
    };

    pc.onconnectionstatechange = () => {
      const state = pc.connectionState;
      setStatus(state);
      if (state === "failed" || state === "disconnected" || state === "closed") {
          resetRemote();
      }
    };
  };
  
  const resetRemote = () => {
    if (partnerVideo.current) partnerVideo.current.srcObject = null;
    pcRef.current?.close();
    pcRef.current = null;
    iceCandidateQueue.current = [];
  };

  const handleNext = () => {
    resetRemote();
    send({ type: "next" });
    setStatus("Searching for next…");
  };
  
  const handleStop = () => {
    send({ type: "disconnect" });
    resetRemote();
    localStreamRef.current?.getTracks().forEach((t) => t.stop());
    onExit?.();
  };

  return (
    <div className="min-h-screen w-full bg-black text-white flex flex-col items-center justify-center gap-4 p-4">
      <div className="flex items-center gap-3">
        <span className="px-2 py-1 rounded bg-white/10 border border-white/20 text-xs capitalize">{status}</span>
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