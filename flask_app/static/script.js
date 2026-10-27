const $ = (id) => document.getElementById(id);

$("steps").addEventListener("input", (e) => ($("stepsVal").textContent = e.target.value));
$("guidance").addEventListener("input", (e) => ($("guidanceVal").textContent = e.target.value));

$("generateBtn").addEventListener("click", async () => {
  const prompt = $("prompt").value.trim();
  const status = $("status");
  status.className = "status";

  if (!prompt) {
    status.textContent = "Please enter a prompt.";
    status.classList.add("error");
    return;
  }

  const btn = $("generateBtn");
  btn.disabled = true;
  status.textContent = "Generating image... this can take 20-60 seconds.";

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt,
        negative: $("negative").value,
        steps: parseInt($("steps").value),
        guidance: parseFloat($("guidance").value),
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Generation failed");

    $("outputImg").src = data.image;
    $("downloadLink").href = data.image;
    $("resultBox").hidden = false;
    status.textContent = "Done!";
  } catch (err) {
    status.textContent = "Error: " + err.message;
    status.classList.add("error");
  } finally {
    btn.disabled = false;
  }
});
