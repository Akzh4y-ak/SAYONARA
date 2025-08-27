import { useState } from "react";
import MainPage from "./MainPage";
import VideoChat from "./VideoChat";

function App() {
  const [started, setStarted] = useState(false);
  const [nickname, setNickname] = useState("");

  const handleStart = (name) => {
    // ensure non-empty nickname
    const finalName = name?.trim() || "Guest_" + Math.floor(1000 + Math.random() * 9000);
    setNickname(finalName);
    setStarted(true); // Switch to VideoChat
  };

  const handleExit = () => {
    // Reset state when exiting chat
    setNickname("");
    setStarted(false);
  };

  return (
    <>
      {!started ? (
        <MainPage onStart={handleStart} />
      ) : (
        <VideoChat userName={nickname} onExit={handleExit} />
      )}
    </>
  );
}

export default App;
