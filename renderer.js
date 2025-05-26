let timeLeft = 25 * 60;
let timerInterval;

function startTimer() {
  timerInterval = setInterval(() => {
    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      new Notification({ title: "Pomodoro", body: "Time's up!" }).show();
    } else {
      timeLeft--;
      document.getElementById("time").textContent = formatTime(timeLeft);
    }
  }, 1000);
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}
