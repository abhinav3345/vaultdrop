const reveal = document.querySelector("#reveal");
const status = document.querySelector("#open-status");
const result = document.querySelector("#opened-drop");
const secret = document.querySelector("#revealed-secret");
const token = window.location.hash.slice(1);

if (/^[\w-]{20,100}$/.test(token)) {
  reveal.disabled = false;
} else {
  status.textContent = "This drop link is invalid.";
}

reveal.addEventListener("click", async () => {
  reveal.disabled = true;
  status.textContent = "Opening drop…";
  try {
    const response = await fetch(`/drops/${token}`, { cache: "no-store" });
    if (response.status === 404 || response.status === 410) {
      status.textContent = "This drop is unavailable. It may have expired or run out of views.";
      return;
    }
    if (!response.ok) throw new Error("Unexpected response");

    const drop = await response.json();
    if (typeof drop.secret !== "string") throw new Error("Invalid response");

    secret.value = drop.secret;
    result.hidden = false;
    reveal.hidden = true;
    status.textContent = "Secret revealed.";
  } catch {
    status.textContent = "Could not confirm whether the drop opened. Trying again may use another view.";
    reveal.disabled = false;
  }
});

window.addEventListener("pagehide", () => {
  if (!result.hidden) {
    secret.value = "";
    result.hidden = true;
    status.textContent = "This view was cleared.";
  }
});
