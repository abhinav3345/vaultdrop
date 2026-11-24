const form = document.querySelector("#sender-form");
const fields = form.querySelector("fieldset");
const status = document.querySelector("#sender-status");
const result = document.querySelector("#drop-result");
const link = document.querySelector("#share-link");
const copy = document.querySelector("#copy-link");
const copyStatus = document.querySelector("#copy-status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (fields.disabled) return;

  const data = new FormData(form);
  fields.disabled = true;
  result.hidden = true;
  link.value = "";
  copyStatus.textContent = "";
  status.textContent = "Creating drop…";

  try {
    const response = await fetch("/drops", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        secret: data.get("secret"),
        max_views: Number(data.get("max_views")),
        ttl_seconds: Number(data.get("ttl_seconds")),
      }),
    });

    if (response.status === 400) {
      status.textContent = "Check your secret and drop settings, then try again.";
      return;
    }
    if (response.status !== 201) throw new Error("Unexpected response");

    const { token } = await response.json();
    if (typeof token !== "string" || !/^[\w-]{20,100}$/.test(token)) {
      throw new Error("Invalid token");
    }
    const url = new URL("/open/", window.location.origin);
    url.hash = token;
    link.value = url.href;
    form.reset();
    result.hidden = false;
    status.textContent = "Drop created.";
  } catch {
    status.textContent = "Could not confirm creation. Check your connection before trying again.";
  } finally {
    fields.disabled = false;
  }
});

copy.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(link.value);
    copyStatus.textContent = "Link copied.";
  } catch {
    link.focus();
    link.select();
    copyStatus.textContent = "Copy the selected link using your keyboard or browser menu.";
  }
});

fields.disabled = false;
