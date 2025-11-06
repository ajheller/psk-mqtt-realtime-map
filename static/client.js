(function () {
  console.log("Initializing Socket.IO client…");

  const socket = io("http://127.0.0.1:5000/", {
    path: "/socket.io/",
    transports: ["websocket"],   // keep websocket-only to avoid xhr poll error
    upgrade: false,
    reconnection: true,
    reconnectionDelay: 5000,
  });

  socket.on("connect", () => console.log("✅ WebSocket connected"));
  socket.on("connect_error", (err) => console.error("❌ connect_error:", err));

  function getFoliumMap() {
    if (window._folium_map && typeof window._folium_map.addLayer === "function") {
      return window._folium_map;
    }
    for (const k in window) {
      if (k.startsWith("map_") && window[k] && typeof window[k].addLayer === "function") {
        console.log("Found Folium map:", k);
        return window[k];
      }
    }
    console.warn("Could not find a Folium map variable.");
    return null;
  }

  const map = getFoliumMap();
  if (!map) {
    console.error("No Leaflet map available.");
    return;
  }

  // --- Clustering ---
  const cluster = L.markerClusterGroup({
    chunkedLoading: true,
    disableClusteringAtZoom: 7,     // spread out when zoomed in
    spiderfyOnEveryZoom: false,
    showCoverageOnHover: false,
    maxClusterRadius: 60,
  }).addTo(map);

  // Keep polylines separate so they don't cluster
  const polylinesLayer = L.layerGroup().addTo(map);

  const rolling = [];
  let MAX = 2000;

  socket.on("config", (cfg) => {
    if (cfg && typeof cfg.maxMarkers === "number") MAX = cfg.maxMarkers;
  });

  // Band → color mapping
  const BAND_COLORS = {
    "160m": "#6b7280",
    "80m":  "#8b5cf6",
    "60m":  "#ef4444",
    "40m":  "#f59e0b",
    "30m":  "#10b981",
    "20m":  "#3b82f6",
    "17m":  "#0ea5e9",
    "15m":  "#22c55e",
    "12m":  "#a855f7",
    "10m":  "#e11d48",
    "6m":   "#84cc16",
    "2m":   "#06b6d4",
  };
  function colorForBand(band) {
    if (!band) return "#111827"; // default dark gray
    const key = String(band).toLowerCase();
    return BAND_COLORS[key] || "#111827";
  }

  function num(v) {
    const n = (v === null || v === undefined || v === "") ? NaN : Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function addSpot(spot) {
    console.log("📡 raw spot event:", spot);

    const lat = num(spot.lat);
    const lon = num(spot.lon);
    const rx_lat = num(spot.rx_lat);
    const rx_lon = num(spot.rx_lon);
    const tx_lat = num(spot.tx_lat);
    const tx_lon = num(spot.tx_lon);

    if (lat === null || lon === null) return;

    const col = colorForBand(spot.band);
    const marker = L.circleMarker([lat, lon], {
      radius: 4,
      weight: 1,
      opacity: 0.95,
      color: col,
      fillColor: col,
      fillOpacity: 0.85,
    }).bindPopup(spot.label || "spot");

    cluster.addLayer(marker);
    rolling.push(marker);

    if (rx_lat !== null && rx_lon !== null && tx_lat !== null && tx_lon !== null) {
      const line = L.polyline(
        [[rx_lat, rx_lon], [tx_lat, tx_lon]],
        { weight: 1, opacity: 0.6, color: col }
      );
      line.addTo(polylinesLayer);
      rolling.push(line);
    }

    // Simple rolling limit
    while (rolling.length > MAX) {
      const old = rolling.shift();
      if (old) {
        if (cluster.hasLayer(old)) cluster.removeLayer(old);
        if (polylinesLayer.hasLayer(old)) polylinesLayer.removeLayer(old);
      }
    }

    const countEl = document.getElementById("count");
    if (countEl) countEl.textContent = rolling.length.toString();

    console.log("Adding spot:", { lat, lon, label: spot.label, band: spot.band });
  }

  socket.on("spot", addSpot);
})();
