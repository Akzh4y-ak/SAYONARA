import { useState } from "react";
import MainPage from "./MainPage";
import VideoChat from "./VideoChat";

function App() {
  const [started, setStarted] = useState(false);
  const [nickname, setNickname] = useState("");

  const handleStart = (name) => {
    setNickname(name || "Guest_" + Math.floor(1000 + Math.random() * 9000));
    setStarted(true); // Switch to VideoChat
  };

  const handleExit = () => {
    // Allow returning to MainPage after stopping chat
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
