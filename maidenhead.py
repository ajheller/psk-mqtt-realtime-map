
def maidenhead_to_latlon(locator: str):
    if not locator:
        return (None, None)
    loc = locator.strip().upper()
    if len(loc) < 2 or len(loc) % 2 != 0:
        return (None, None)
    try:
        lon = -180.0 + (ord(loc[0]) - ord('A')) * 20.0
        lat = -90.0 + (ord(loc[1]) - ord('A')) * 10.0
        if len(loc) >= 4:
            lon += int(loc[2]) * 2.0
            lat += int(loc[3]) * 1.0
        if len(loc) >= 6:
            lon += (ord(loc[4]) - ord('A')) * (5.0/60.0)
            lat += (ord(loc[5]) - ord('A')) * (2.5/60.0)
        lon += 1.0
        lat += 0.5
        return (round(lat, 6), round(lon, 6))
    except Exception:
        return (None, None)
