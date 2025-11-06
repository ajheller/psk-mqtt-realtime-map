(function () {
  console.log("Initializing Socket.IO client…");

  const socket = io("http://127.0.0.1:5000/", {
      path: "/socket.io/",
      transports: ["websocket"],   // <- skip polling
      upgrade: false,              // <- connect straight via WebSocket
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

  const markersLayer = L.layerGroup().addTo(map);
  const polylinesLayer = L.layerGroup().addTo(map);
  const rolling = [];
  let MAX = 2000;

  socket.on("config", (cfg) => {
    if (cfg && typeof cfg.maxMarkers === "number") MAX = cfg.maxMarkers;
  });

  function num(v) {
    const n = (v === null || v === undefined || v === "") ? NaN : Number(v);
    return Number.isFinite(n) ? n : null;
  }

  function addSpot(spot) {
    console.log("📡 raw spot event:", spot);

    // Coerce possibly-string numbers to real numbers
    const lat = num(spot.lat);
    const lon = num(spot.lon);
    const rx_lat = num(spot.rx_lat);
    const rx_lon = num(spot.rx_lon);
    const tx_lat = num(spot.tx_lat);
    const tx_lon = num(spot.tx_lon);

    if (lat === null || lon === null) return;

    const marker = L.circleMarker([lat, lon], { radius: 4, weight: 1, opacity: 0.9 })
      .bindPopup(spot.label || "spot");
    marker.addTo(markersLayer);
    rolling.push(marker);

    if (rx_lat !== null && rx_lon !== null && tx_lat !== null && tx_lon !== null) {
      const line = L.polyline([[rx_lat, rx_lon], [tx_lat, tx_lon]], { weight: 1, opacity: 0.6 });
      line.addTo(polylinesLayer);
      rolling.push(line);
    }

    while (rolling.length > MAX) {
      const old = rolling.shift();
      if (old && map.hasLayer(old)) map.removeLayer(old);
    }

    const countEl = document.getElementById("count");
    if (countEl) countEl.textContent = rolling.length.toString();

    console.log("Adding spot:", { lat, lon, label: spot.label });
  }

  // Ensure we see the raw event even if addSpot returns early
  socket.on("spot", addSpot);
})();
