// Muther dashboard: polls /api/state, acts through /api/engine.
const ENGINES = { "1": "swift 120k", "2": "coder strata", "3": "swift 64k" };
let last = null;

const $ = (id) => document.getElementById(id);

function clock() {
  const d = new Date();
  $("clock").textContent = d.toTimeString().slice(0, 8);
}

function bar(el, used, total) {
  const pct = total > 0 ? Math.max(0, Math.min(100, (used / total) * 100)) : 0;
  el.style.width = pct + "%";
}

function toast(message, bad) {
  const t = $("toast");
  t.textContent = message || "";
  t.style.color = bad ? "var(--bad)" : "var(--amber-soft)";
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => { t.textContent = ""; }, 6000);
}

async function act(key, action) {
  try {
    const res = await fetch(`/api/engine?key=${key}&action=${action}`, { method: "POST" });
    const data = await res.json();
    toast(data.message, !data.ok);
    poll();
  } catch (err) {
    toast("interface lost the server: " + err, true);
  }
}

function renderEngines(state) {
  const ports = $("ports");
  ports.innerHTML = state.ports.map((p) =>
    `<span class="port ${p.open ? "on" : ""}">:${p.port} ${p.name || p.what}</span>`).join("");

  const managed = $("managed");
  const rows = Object.entries(state.managed || {}).map(([key, rec]) => {
    const up = rec.alive;
    return `<div class="engine">
      <span class="name">[${key}] ${rec.name}</span>
      <span class="state ${up ? "up" : ""}">${up ? "running" : "stopped"}</span>
      <span class="port">pid ${rec.pid ?? "-"}</span>
      ${up ? `<button class="stop" onclick="act('${key}','stop')">stop</button>`
           : `<button onclick="act('${key}','start')">start</button>`}
    </div>`;
  });
  const idle = Object.entries(ENGINES)
    .filter(([key]) => !(state.managed || {})[key])
    .map(([key, name]) => `<div class="engine">
      <span class="name">[${key}] ${name}</span>
      <span class="state">stopped</span>
      <button onclick="act('${key}','start')">start</button>
    </div>`);
  managed.innerHTML = [...rows, ...idle].join("");
}

function render(state) {
  last = state;
  const g = state.gpu, r = state.ram, m = state.memory;

  if (g.present) {
    $("vram-free").textContent = g.free_mib.toLocaleString();
    bar($("vram-bar"), g.used_mib, g.total_mib);
    $("vram-row").textContent =
      `${g.name} — ${g.used_mib} / ${g.total_mib} MiB · util ${g.util_pct}% · power ${g.power_w ?? "--"} W`;
  } else {
    $("vram-free").textContent = "--";
    $("vram-row").textContent = "no NVIDIA device reported";
  }

  $("ram-free").textContent = r.available_mib.toLocaleString();
  bar($("ram-bar"), r.total_mib - r.available_mib, r.total_mib);
  $("ram-row").textContent = `${r.total_mib.toLocaleString()} MiB total · load ${r.load_pct}%`;

  $("disk-free").textContent = state.disk.free_gib;
  $("disk-row").textContent = `${state.disk.drive} volume`;

  $("notes").textContent = m.notes;
  $("map-row").textContent = `map ${m.map_chars} chars`;
  $("inject").textContent = (m.last_injection || "no injection logged").slice(0, 96);

  const alerts = state.alerts.length
    ? state.alerts.map((a) => `<div class="bad">${a}</div>`).join("")
    : `<div class="ok">all systems within limits</div>`;
  $("alerts").innerHTML = alerts;

  $("log").textContent = (m.log_lines || []).slice(-6).join("\n") || "idle";

  renderEngines(state);

  const warn = state.alerts.length > 0;
  $("dot").className = "dot" + (warn ? " bad" : "");
}

async function poll() {
  try {
    const res = await fetch("/api/state", { cache: "no-store" });
    render(await res.json());
  } catch (err) {
    $("log").textContent = "collector unreachable: " + err;
    $("dot").className = "dot bad";
  }
}

document.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (ENGINES[key]) {
    const rec = (last?.managed || {})[key];
    act(key, rec && rec.alive ? "stop" : "start");
  } else if (key === "s") {
    Object.keys(last?.managed || {}).forEach((k) => act(k, "stop"));
  } else if (key === "r") {
    poll();
  }
});

clock();
setInterval(clock, 1000);
poll();
setInterval(poll, 2000);
