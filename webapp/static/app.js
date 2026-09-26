(() => {
  "use strict";

  const PALETTE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"];
  const INK_SECONDARY = "#52514e";
  const GRIDLINE = "#e1e0d9";
  const BASELINE = "#c3c2b7";

  const heroEl = document.getElementById("hero");
  const chatEl = document.getElementById("chat");
  const chatScrollEl = document.getElementById("chat-scroll");
  const composerHero = document.getElementById("composer-hero");
  const composerDock = document.getElementById("composer-dock");
  const inputHero = document.getElementById("input-hero");
  const inputDock = document.getElementById("input-dock");
  const chipRow = document.getElementById("chip-row");
  const resetBtn = document.getElementById("reset-btn");

  let messages = [];
  let started = false;
  let busy = false;

  marked.setOptions({ breaks: true });

  function autoGrow(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 160) + "px";
  }

  [inputHero, inputDock].forEach((el) => {
    el.addEventListener("input", () => autoGrow(el));
    el.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter" && !ev.shiftKey) {
        ev.preventDefault();
        el.closest("form").requestSubmit();
      }
    });
  });

  composerHero.addEventListener("submit", (ev) => {
    ev.preventDefault();
    submitText(inputHero.value);
    inputHero.value = "";
    autoGrow(inputHero);
  });

  composerDock.addEventListener("submit", (ev) => {
    ev.preventDefault();
    submitText(inputDock.value);
    inputDock.value = "";
    autoGrow(inputDock);
  });

  chipRow.addEventListener("click", (ev) => {
    const btn = ev.target.closest(".chip");
    if (!btn) return;
    submitText(btn.dataset.q);
  });

  resetBtn.addEventListener("click", () => window.location.reload());

  function submitText(text) {
    text = (text || "").trim();
    if (!text || busy) return;
    ensureStarted();
    appendUserMessage(text);
    messages.push({ role: "user", content: text });
    streamAssistantReply();
  }

  function ensureStarted() {
    if (started) return;
    started = true;
    heroEl.hidden = true;
    chatEl.hidden = false;
    composerDock.hidden = false;
    inputDock.focus();
  }

  function scrollToBottom() {
    chatScrollEl.scrollTop = chatScrollEl.scrollHeight;
  }

  function appendUserMessage(text) {
    const group = document.createElement("div");
    group.className = "msg-group msg-user";
    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.textContent = text;
    group.appendChild(bubble);
    chatScrollEl.appendChild(group);
    scrollToBottom();
  }

  function createAssistantMessage() {
    const group = document.createElement("div");
    group.className = "msg-group msg-assistant";

    const label = document.createElement("div");
    label.className = "msg-label";
    const dot = document.createElement("span");
    dot.className = "msg-label-dot thinking";
    label.appendChild(dot);
    label.appendChild(document.createTextNode("SoroIA"));
    group.appendChild(label);

    const content = document.createElement("div");
    content.className = "msg-content";
    group.appendChild(content);

    chatScrollEl.appendChild(group);
    scrollToBottom();
    return { group, dot, content };
  }

  async function streamAssistantReply() {
    busy = true;
    setInputsDisabled(true);
    const { dot, content } = createAssistantMessage();
    let fullText = "";
    let errored = false;

    try {
      const resp = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages }),
      });
      if (!resp.ok || !resp.body) {
        throw new Error(`Servidor respondeu ${resp.status}`);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop();
        for (const evt of events) {
          const line = evt.trim();
          if (!line.startsWith("data:")) continue;
          const payload = JSON.parse(line.slice(5).trim());
          if (payload.error) {
            throw new Error(payload.error);
          }
          if (payload.delta) {
            if (dot.classList.contains("thinking")) dot.classList.remove("thinking");
            fullText += payload.delta;
            content.innerHTML = marked.parse(fullText);
            scrollToBottom();
          }
        }
      }
    } catch (err) {
      errored = true;
      dot.classList.remove("thinking");
      content.innerHTML = "";
      const errBox = document.createElement("div");
      errBox.className = "msg-error";
      errBox.textContent =
        "Não consegui responder agora (" + err.message + "). Verifique a internet " +
        "do notebook e se a chave da API está configurada em webapp/.env, e tente de novo.";
      content.appendChild(errBox);
    }

    setInputsDisabled(false);
    busy = false;

    if (!errored) {
      content.innerHTML = marked.parse(fullText);
      renderCharts(content);
      messages.push({ role: "assistant", content: fullText });
    }
    scrollToBottom();
  }

  function setInputsDisabled(disabled) {
    [inputHero, inputDock].forEach((el) => (el.disabled = disabled));
    document.querySelectorAll(".composer-send").forEach((btn) => (btn.disabled = disabled));
  }

  function renderCharts(container) {
    const blocks = container.querySelectorAll("code.language-chart");
    blocks.forEach((codeEl) => {
      let spec;
      try {
        spec = JSON.parse(codeEl.textContent);
      } catch (e) {
        return; // leave as a plain code block if it's not valid JSON
      }
      const pre = codeEl.closest("pre");
      if (!pre) return;
      const card = buildChartCard(spec);
      pre.replaceWith(card);
    });
  }

  function buildChartCard(spec) {
    const card = document.createElement("div");
    card.className = "chart-card";

    if (spec.title) {
      const title = document.createElement("div");
      title.className = "chart-card-title";
      title.textContent = spec.title;
      card.appendChild(title);
    }

    const canvas = document.createElement("canvas");
    card.appendChild(canvas);

    if (spec.source) {
      const source = document.createElement("div");
      source.className = "chart-card-source";
      source.textContent = "Fonte: " + spec.source;
      card.appendChild(source);
    }

    const type = spec.type === "pie" ? "pie" : spec.type === "line" ? "line" : "bar";
    const labels = spec.labels || [];
    const series = spec.series || [];

    let datasets;
    if (type === "pie") {
      datasets = [
        {
          data: (series[0] && series[0].data) || [],
          backgroundColor: labels.map((_, i) => PALETTE[i % PALETTE.length]),
          borderColor: "#fcfcfb",
          borderWidth: 2,
        },
      ];
    } else {
      datasets = series.map((s, i) => ({
        label: s.name || `Série ${i + 1}`,
        data: s.data || [],
        backgroundColor: type === "bar" ? PALETTE[i % PALETTE.length] : "transparent",
        borderColor: PALETTE[i % PALETTE.length],
        borderWidth: 2,
        borderRadius: type === "bar" ? 4 : 0,
        tension: 0.25,
        pointRadius: type === "line" ? 3 : 0,
      }));
    }

    const showLegend = type === "pie" || series.length > 1;

    new Chart(canvas.getContext("2d"), {
      type,
      data: { labels, datasets },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: showLegend,
            position: "bottom",
            labels: { color: INK_SECONDARY, font: { family: "Inter", size: 12 } },
          },
        },
        scales:
          type === "pie"
            ? {}
            : {
                x: {
                  title: spec.xLabel ? { display: true, text: spec.xLabel, color: INK_SECONDARY } : undefined,
                  grid: { color: GRIDLINE },
                  ticks: { color: INK_SECONDARY, font: { family: "Inter", size: 11 } },
                },
                y: {
                  title: spec.yLabel ? { display: true, text: spec.yLabel, color: INK_SECONDARY } : undefined,
                  grid: { color: GRIDLINE },
                  ticks: { color: INK_SECONDARY, font: { family: "Inter", size: 11 } },
                  border: { color: BASELINE },
                },
              },
      },
    });

    return card;
  }
})();
