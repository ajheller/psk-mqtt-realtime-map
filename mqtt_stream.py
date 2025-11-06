import os
import json
import re
import subprocess
from typing import Dict, Optional
from maidenhead import maidenhead_to_latlon

KV_RE = re.compile(r"(\w+)=([^\s]+)")


def mqtt_line_stream(cmd: str, host: str, port: str, topic: str):
    args = [cmd, "-h", host, "-p", str(port), "-t", topic, "-v"]
    username = os.environ.get("MOSQUITTO_USERNAME")
    password = os.environ.get("MOSQUITTO_PASSWORD")
    if username:
        args += ["-u", username]
    if password:
        args += ["-P", password]
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    try:
        for line in proc.stdout:
            if line.strip():
                yield line.strip()
    finally:
        try:
            proc.kill()
        except Exception:
            pass


def parse_kv_pairs(s: str) -> Dict[str, str]:
    return {k: v for k, v in KV_RE.findall(s)}


def as_float(v):
    try:
        return float(v)
    except:
        return None


def parse_spot(raw_line: str) -> Optional[Dict]:
    parts = raw_line.split(" ", 1)
    payload = parts[1] if len(parts) == 2 and "/" in parts[0] else raw_line
    try:
        data = json.loads(payload)
        if isinstance(data, str):
            data = json.loads(data)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = parse_kv_pairs(payload)

    low = {str(k).lower(): v for k, v in data.items()}

    rx_loc = low.get("rl") or low.get("rxlocator") or low.get("rxgrid")
    tx_loc = low.get("sl") or low.get("txlocator") or low.get("txgrid")

    rx_lat = rx_lon = tx_lat = tx_lon = None
    if rx_loc:
        rx_lat, rx_lon = maidenhead_to_latlon(rx_loc)
    if tx_loc:
        tx_lat, tx_lon = maidenhead_to_latlon(tx_loc)

    primary = None
    if rx_lat is not None and rx_lon is not None:
        primary = ("rx", rx_lat, rx_lon)
    elif tx_lat is not None and tx_lon is not None:
        primary = ("tx", tx_lat, tx_lon)
    else:
        return None

    rx_call = low.get("rc") or low.get("rxcall")
    tx_call = low.get("sc") or low.get("txcall")
    freq = low.get("f") or low.get("freq")
    mode = low.get("md") or low.get("mode")
    snr = low.get("rp") or low.get("snr")
    band = low.get("b")
    ts = low.get("t") or low.get("timestamp")

    label_parts = []
    if tx_call and rx_call:
        label_parts.append(f"{tx_call} → {rx_call}")
    elif tx_call:
        label_parts.append(tx_call)
    elif rx_call:
        label_parts.append(rx_call)
    if band:
        label_parts.append(band)
    if mode:
        label_parts.append(mode)
    if freq:
        label_parts.append(str(freq))
    if snr:
        label_parts.append(f"SNR {snr}")
    if ts:
        label_parts.append(str(ts))
    label = " · ".join(label_parts)

    return {
        "label": label,
        "lat": primary[1],
        "lon": primary[2],
        "rx_lat": rx_lat,
        "rx_lon": rx_lon,
        "tx_lat": tx_lat,
        "tx_lon": tx_lon,
        "rx_locator": rx_loc,
        "tx_locator": tx_loc,
        "snr": snr,
        "freq": freq,
        "mode": mode,
        "band": band,
        "ts": ts,
    }
