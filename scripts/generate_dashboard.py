"""
Sovereign Dashboard v3 — Script de análisis técnico
Genera public/data/dashboard.json para el dashboard web
Ejecutado por GitHub Actions cada madrugada a las 04:30 UTC
"""

import json
import os
import sys
import warnings
from datetime import datetime, timezone

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator

# ============================================================
# HELPERS
# ============================================================

def clean_yf_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    needed = ["Open", "High", "Low", "Close", "Volume"]
    for c in needed:
        if c not in df.columns:
            return pd.DataFrame()
    return df[needed].dropna().copy()


def mcginley_dynamic(close, period=25):
    md = close.copy().astype(float)
    k = 0.6
    for i in range(1, len(close)):
        prev = md.iloc[i - 1]
        if prev == 0 or pd.isna(prev):
            md.iloc[i] = close.iloc[i]
        else:
            md.iloc[i] = prev + ((close.iloc[i] - prev) /
                                  (k * period * (close.iloc[i] / prev) ** 4))
    return md


def calculate_pvi(close, volume):
    pvi = pd.Series(index=close.index, dtype=float)
    pvi.iloc[0] = 1000.0
    for i in range(1, len(close)):
        if volume.iloc[i] > volume.iloc[i - 1]:
            pct = (close.iloc[i] - close.iloc[i - 1]) / close.iloc[i - 1]
            pvi.iloc[i] = pvi.iloc[i - 1] * (1 + pct)
        else:
            pvi.iloc[i] = pvi.iloc[i - 1]
    return pvi


def calculate_nvi(close, volume):
    nvi = pd.Series(index=close.index, dtype=float)
    nvi.iloc[0] = 1000.0
    for i in range(1, len(close)):
        if volume.iloc[i] < volume.iloc[i - 1]:
            pct = (close.iloc[i] - close.iloc[i - 1]) / close.iloc[i - 1]
            nvi.iloc[i] = nvi.iloc[i - 1] * (1 + pct)
        else:
            nvi.iloc[i] = nvi.iloc[i - 1]
    return nvi


def calc_mfi_blai5(high, low, close, volume, length=14):
    src = (high + low + close) / 3.0
    up  = (volume * np.where(src.diff() > 0, src, 0)).rolling(length).sum()
    dn  = (volume * np.where(src.diff() < 0, src, 0)).rolling(length).sum()
    rs  = up / dn.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_stoch(src, high, low, length=21, smooth_fast_d=3):
    ll = low.rolling(length).min()
    hh = high.rolling(length).max()
    k  = 100 * (src - ll) / (hh - ll)
    return k.rolling(smooth_fast_d).mean()


def velas_desde_activacion(serie_bool):
    vals = serie_bool.fillna(False).values
    n = len(vals)
    if n == 0 or not vals[-1]:
        return 999
    count = 0
    for i in range(n - 1, -1, -1):
        if vals[i]:
            count += 1
        else:
            break
    return count


def calculate_bbwp(close, bb_len=13, lookback=252):
    basis = close.rolling(bb_len).mean()
    dev   = close.rolling(bb_len).std(ddof=0)
    bbw   = 2.0 * dev / basis.replace(0, np.nan)

    arr  = bbw.values
    n    = len(arr)
    bbwp = np.full(n, np.nan)

    for i in range(bb_len, n):
        cur = arr[i]
        if np.isnan(cur):
            continue
        start  = max(0, i - lookback)
        window = arr[start:i]
        valid  = window[~np.isnan(window)]
        if len(valid) < 5:
            continue
        bbwp[i] = np.sum(valid <= cur) / len(valid) * 100.0

    return pd.Series(bbw, index=close.index), pd.Series(bbwp, index=close.index)


def bbwp_signal(bbwp_pct, bbwp_series):
    if pd.isna(bbwp_pct):
        return "⚪", "normal", "→", "nan%"

    if bbwp_pct < 20:
        punto = "🟢"; zona = "compresion"
    elif bbwp_pct > 80:
        punto = "🔴"; zona = "expansion"
    else:
        punto = "⚪"; zona = "normal"

    reciente = bbwp_series.dropna().iloc[-3:]
    if len(reciente) >= 2:
        slope = reciente.iloc[-1] - reciente.iloc[0]
        pendiente = "↑" if slope > 3 else ("↓" if slope < -3 else "→")
    else:
        pendiente = "→"

    return punto, zona, pendiente, f"{bbwp_pct:.1f}%"


# ============================================================
# BLAI5 KONCORDE
# ============================================================

def compute_blai5_koncorde(df, m=15):
    df = clean_yf_df(df)
    if df.empty or len(df) < 100:
        return pd.DataFrame()

    ohlc4 = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4.0
    pvi   = calculate_pvi(df["Close"], df["Volume"])
    nvi   = calculate_nvi(df["Close"], df["Volume"])
    pvim  = pvi.ewm(span=m, adjust=False).mean()
    nvim  = nvi.ewm(span=m, adjust=False).mean()

    oscp = (pvi - pvim) * 100 / (pvim.rolling(90).max() - pvim.rolling(90).min()).replace(0, np.nan)
    azul = (nvi - nvim) * 100 / (nvim.rolling(90).max() - nvim.rolling(90).min()).replace(0, np.nan)

    xmf     = calc_mfi_blai5(df["High"], df["Low"], df["Close"], df["Volume"], 14)
    basis   = ohlc4.rolling(25).mean()
    dev     = 2.0 * ohlc4.rolling(25).std()
    bollosc = ((ohlc4 - basis) / dev).replace([np.inf, -np.inf], np.nan) * 100
    xrsi    = RSIIndicator(close=ohlc4, window=14).rsi()
    stoc    = calc_stoch(ohlc4, df["High"], df["Low"], 21, 3)

    marron = (xrsi + xmf + bollosc + stoc / 3.0) / 2.0
    verde  = marron + oscp
    media  = marron.ewm(span=m, adjust=False).mean()

    out = pd.DataFrame(index=df.index)
    out["azul"]   = azul
    out["marron"] = marron
    out["verde"]  = verde
    out["media"]  = media
    return out


def blai5_signals(kdf):
    kdf      = kdf.copy()
    valid    = kdf[["verde", "marron", "azul", "media"]].notna().all(axis=1)
    area_max = kdf[["verde", "marron", "azul"]].max(axis=1)
    area_min = kdf[["verde", "marron", "azul"]].min(axis=1)
    inside   = valid & (kdf["media"] >= area_min) & (kdf["media"] <= area_max)

    punto_media, velas_konk = [], []
    estado, conteo = None, 0
    for i in range(len(kdf)):
        if not valid.iloc[i]:
            punto_media.append(False); velas_konk.append(0); continue
        if inside.iloc[i]:
            if estado != "inside": estado, conteo = "inside", 1
            else: conteo += 1
            punto_media.append(True)
        else:
            if estado != "outside": estado, conteo = "outside", 1
            else: conteo += 1
            punto_media.append(False)
        velas_konk.append(conteo)

    kdf["punto_media_verde"] = punto_media
    kdf["velas_konk"]        = velas_konk
    return kdf


# ============================================================
# BITMAN
# ============================================================

def calcular_ao(df, fast=5, slow=34):
    mid = (df["High"] + df["Low"]) / 2.0
    return mid.rolling(fast).mean() - mid.rolling(slow).mean()


def clasificar_bitman(df):
    if df is None or df.empty or len(df) < 60:
        return pd.DataFrame()

    out = df.copy()
    adx_ind = ADXIndicator(high=out["High"], low=out["Low"], close=out["Close"], window=14)
    out["ADX"]       = adx_ind.adx()
    out["ADX_Slope"] = out["ADX"].diff().rolling(3).mean()
    out["AO"]        = calcular_ao(out)

    diff            = out["AO"] - out["AO"].shift(1)
    out["AO_Color"] = np.where(diff <= 0, "rojo", "verde")

    slope_mean_abs = out["ADX_Slope"].abs().rolling(20).mean()
    weak_thr       = (slope_mean_abs * 0.25).fillna(np.nan)

    out["ADX_Giro"]        = False
    out["Bitman_Color"]    = out["AO_Color"]
    out["Bitman_Etiqueta"] = "INDEFINICIÓN"
    out["Bitman_Velas"]    = 0

    last_turn_idx = None
    current_color = "verde"
    counter       = 0

    for i in range(len(out)):
        adx_slope_now = out["ADX_Slope"].iloc[i]
        ao_color_now  = out["AO_Color"].iloc[i]

        if (pd.isna(adx_slope_now) or pd.isna(weak_thr.iloc[i]) or
                abs(adx_slope_now) <= weak_thr.iloc[i]):
            counter += 1
            out.iloc[i, out.columns.get_loc("Bitman_Etiqueta")] = "INDEFINICIÓN"
            out.iloc[i, out.columns.get_loc("Bitman_Color")]    = ao_color_now
            out.iloc[i, out.columns.get_loc("Bitman_Velas")]    = counter
            continue

        adx_dir    = "impulso" if adx_slope_now > 0 else "retroceso"
        prev_slope = out["ADX_Slope"].iloc[i - 1] if i > 0 else np.nan
        prev_weak  = weak_thr.iloc[i - 1] if i > 0 else np.nan
        giro = (i > 0 and not pd.isna(prev_slope) and
                np.sign(prev_slope) != np.sign(adx_slope_now) and
                (pd.isna(prev_weak) or abs(prev_slope) > prev_weak))

        if giro:
            out.iloc[i, out.columns.get_loc("ADX_Giro")] = True
            last_turn_idx = i
            counter       = 1
            ao_w    = out["AO_Color"].iloc[max(0, i - 4): i + 1]
            changes = ao_w[ao_w != ao_w.shift(1)].dropna()
            if len(changes) >= 1:
                current_color = changes.iloc[-1]
        else:
            if last_turn_idx is not None and 0 < (i - last_turn_idx) <= 4:
                ao_w    = out["AO_Color"].iloc[last_turn_idx: i + 1]
                changes = ao_w[ao_w != ao_w.shift(1)].dropna()
                if len(changes) > 0:
                    current_color = changes.iloc[-1]
            counter = (i - last_turn_idx + 1) if last_turn_idx is not None else counter + 1

        etiqueta = ("IMPULSO ALCISTA"   if adx_dir == "impulso"   and current_color == "verde" else
                    "IMPULSO BAJISTA"   if adx_dir == "impulso"   and current_color == "rojo"  else
                    "RETROCESO ALCISTA" if adx_dir == "retroceso" and current_color == "verde" else
                    "RETROCESO BAJISTA")

        out.iloc[i, out.columns.get_loc("Bitman_Color")]    = current_color
        out.iloc[i, out.columns.get_loc("Bitman_Etiqueta")] = etiqueta
        out.iloc[i, out.columns.get_loc("Bitman_Velas")]    = counter

    return out


# ============================================================
# DIVERGENCIAS RSI
# ============================================================

def detectar_divergencia_simple(df, lookback=80, order=3, max_gap=20, tol=0.005):
    close = df["Close"].copy()
    rsi   = RSIIndicator(close=close, window=14).rsi()
    p, o  = close.values, rsi.values
    n     = len(p)

    def pivots(vals, kind="low"):
        idxs = []
        for i in range(order, n - order):
            if np.isnan(vals[i]): continue
            w = vals[i - order: i + order + 1]
            if kind == "low":
                if vals[i] <= np.nanmin(w) * (1 + tol) and vals[i] <= vals[i-1] and vals[i] <= vals[i+1]:
                    idxs.append(i)
            else:
                if vals[i] >= np.nanmax(w) * (1 - tol) and vals[i] >= vals[i-1] and vals[i] >= vals[i+1]:
                    idxs.append(i)
        return idxs

    def nearest(ref, cands):
        best, best_d = None, 10**9
        for c in cands:
            d = abs(c - ref)
            if d <= max_gap and d < best_d:
                best, best_d = c, d
        return best

    pl = pivots(p, "low");  ph = pivots(p, "high")
    ol = pivots(o, "low");  oh = pivots(o, "high")
    alc_idx = baj_idx = None

    for j in range(1, len(pl)):
        p1, p2 = pl[j-1], pl[j]
        if p2 - p1 > lookback: continue
        i1, i2 = nearest(p1, ol), nearest(p2, ol)
        if i1 is None or i2 is None or i1 == i2: continue
        if p[p2] < p[p1] and o[i2] > o[i1]: alc_idx = p2

    for j in range(1, len(ph)):
        p1, p2 = ph[j-1], ph[j]
        if p2 - p1 > lookback: continue
        i1, i2 = nearest(p1, oh), nearest(p2, oh)
        if i1 is None or i2 is None or i1 == i2: continue
        if p[p2] > p[p1] and o[i2] < o[i1]: baj_idx = p2

    if alc_idx is not None and baj_idx is not None:
        div_tipo, div_idx = ("alcista", alc_idx) if alc_idx >= baj_idx else ("bajista", baj_idx)
    elif alc_idx is not None:
        div_tipo, div_idx = "alcista", alc_idx
    elif baj_idx is not None:
        div_tipo, div_idx = "bajista", baj_idx
    else:
        div_tipo, div_idx = "ninguna", None

    out = df.copy()
    out["divergencia_tipo"] = "ninguna"
    out["divergencia"]      = "⚪"
    if div_idx is not None:
        out.iloc[div_idx, out.columns.get_loc("divergencia_tipo")] = div_tipo
        out.iloc[div_idx, out.columns.get_loc("divergencia")]      = "🟢" if div_tipo == "alcista" else "🔴"
    return out


# ============================================================
# NÚCLEO DEL SEMÁFORO
# ============================================================

def azul_z_score(kdf, window=60):
    azul = kdf["azul"].dropna()
    if len(azul) < window + 4:
        return 0.0
    slope = azul.iloc[-1] - azul.iloc[-4]
    std   = azul.rolling(window).std().iloc[-1]
    if pd.isna(std) or std == 0:
        return 0.0
    return slope / std


def calcular_velas_señal(close, volume, kdf, macd_line, macd_signal_line, bitman_df):
    gap   = macd_line - macd_signal_line
    accel = gap.diff()
    macd_activo = (gap > 0) & (accel > 0)
    v_macd = velas_desde_activacion(macd_activo)

    azul = kdf["azul"].fillna(0)
    azul_slope = azul - azul.shift(3).fillna(0)
    azul_activo = (azul > 0) & (azul_slope > 0)
    v_azul = velas_desde_activacion(azul_activo)

    media_activo = pd.Series(kdf["punto_media_verde"].values, index=kdf.index)
    v_media = velas_desde_activacion(media_activo)

    pvi = calculate_pvi(close, volume)
    pvi_ema = pvi.ewm(span=25, adjust=False).mean()
    pvi_gap = pvi - pvi_ema
    pvi_activo = (pvi > pvi_ema) & (pvi_gap.diff() > 0)
    v_pvi = velas_desde_activacion(pvi_activo)

    _, bbwp_s = calculate_bbwp(close, bb_len=13, lookback=252)
    bbwp_comp = bbwp_s < 20
    indices_comp = np.where(bbwp_comp.fillna(False).values)[0]
    if len(indices_comp) == 0:
        v_bbwp_comp = 999
    else:
        v_bbwp_comp = len(bbwp_s) - 1 - indices_comp[-1]

    if bitman_df is not None and not bitman_df.empty:
        bitman_activo = pd.Series(
            (bitman_df["Bitman_Etiqueta"] == "IMPULSO ALCISTA").values,
            index=bitman_df.index
        )
        v_bitman = velas_desde_activacion(bitman_activo)
    else:
        v_bitman = 999

    return {
        "v_macd":      v_macd,
        "v_azul":      v_azul,
        "v_media":     v_media,
        "v_pvi":       v_pvi,
        "v_bbwp_comp": v_bbwp_comp,
        "v_bitman":    v_bitman,
    }


# ============================================================
# SEMÁFORO PRINCIPAL
# ============================================================

def semaforo(data, velas):
    macd_gap   = data["macd_gap"]
    macd_accel = data["macd_accel"]

    if macd_gap >= 0 and macd_accel > 0:
        c1 = "🟢"; c1_txt = f"MACD 🟢 acelerando ({velas['v_macd']}v)"
    elif macd_gap >= 0:
        c1 = "⚪"; c1_txt = "MACD ⚪ decelerando"
    else:
        c1 = "🔴"; c1_txt = "MACD 🔴 negativo"

    azul_verde = data["konk_azul_verde"]
    azul_slope = data.get("azul_slope", 0.0)
    if azul_verde and azul_slope > 0:
        c2 = "🟢"; c2_txt = f"Azul K 🟢 positivo↑ ({velas['v_azul']}v)"
    elif azul_verde:
        c2 = "⚪"; c2_txt = "Azul K ⚪ positivo plano"
    else:
        c2 = "🔴"; c2_txt = "Azul K 🔴 negativo"

    if data["konk_punto_verde"]:
        c3 = "🟢"; c3_txt = f"Media K 🟢 en área ({velas['v_media']}v)"
    else:
        c3 = "🔴"; c3_txt = "Media K 🔴 fuera"

    bbwp_pct       = data.get("bbwp_pct", 50.0)
    bbwp_pendiente = data.get("bbwp_pendiente", "→")
    v_bbwp_comp    = velas["v_bbwp_comp"]
    bbwp_comp_txt  = f" (compresión hace {v_bbwp_comp}v)" if v_bbwp_comp < 40 else ""

    if bbwp_pct > 60:
        c4 = "🟢"; c4_txt = f"BBWP 🟢 alto {bbwp_pct:.0f}%{bbwp_comp_txt}"
    elif bbwp_pct < 40 and bbwp_pendiente == "↑":
        c4 = "🟢"; c4_txt = f"BBWP 🟢 cargando {bbwp_pct:.0f}%↑"
    elif bbwp_pct < 40:
        c4 = "🔴"; c4_txt = f"BBWP 🔴 compresión plana {bbwp_pct:.0f}%"
    else:
        c4 = "⚪"; c4_txt = f"BBWP ⚪ zona media {bbwp_pct:.0f}%"

    pvi_activo = data.get("pvi_activo", False)
    pvi_accel  = data.get("pvi_accel",  False)
    if pvi_activo and pvi_accel:
        c8 = "🟢"; c8_txt = f"PVI 🟢 sobre EMA25 y acelerando ({velas['v_pvi']}v)"
    elif pvi_activo:
        c8 = "⚪"; c8_txt = f"PVI ⚪ sobre EMA25 decelerando"
    else:
        c8 = "🔴"; c8_txt = "PVI 🔴 bajo EMA25"

    if data.get("cerca_mcg25") or data.get("cerca_e200"):
        c5 = "🟠"; c5_txt = "🟠 precio en zona soporte MCG25/EMA200"
    else:
        precio = data.get("precio", 0)
        e200   = data.get("e200", 0)
        c5     = "⚪" if precio > e200 else "🔴"
        c5_txt = "sobre EMA200" if precio > e200 else "🔴 bajo EMA200 — precaución"

    b_etiq  = data.get("bitman_etiqueta", "")
    b_velas = data.get("bitman_velas", 999)
    v_bfresh = velas["v_bitman"]

    if b_etiq == "IMPULSO ALCISTA":
        c6 = "🟢"
        c6_txt = f"Bitman 🟢 impulso alcista (ciclo {b_velas}v / fresco {v_bfresh}v)"
    elif b_etiq == "RETROCESO ALCISTA":
        c6 = "⚪"; c6_txt = f"Bitman ⚪ retroceso alcista ({b_velas}v)"
    elif "BAJISTA" in b_etiq:
        c6 = "🔴"; c6_txt = f"Bitman 🔴 {b_etiq.lower()} ({b_velas}v)"
    else:
        c6 = "⚪"; c6_txt = f"Bitman ⚪ indefinición ({b_velas}v)"

    azul_z = data.get("azul_z", 0.0)
    if azul_z > 1.5:
        c7 = "⚡"; c7_txt = f"⚡ Azul pendiente fuerte (z={azul_z:.1f}) — movimiento violento probable"
    else:
        c7 = "⚪"; c7_txt = ""

    verde_val = data.get("konk_verde_val", 0.0)
    azul_val  = data.get("konk_azul_val",  0.0)
    atención_konk = (verde_val < 0) and (azul_val > 0)

    div       = data.get("divergencia_tipo",  "ninguna")
    div_velas = data.get("divergencia_velas", 999)

    n_activas = sum([c1 == "🟢", c2 == "🟢", c3 == "🟢", c4 == "🟢", c8 == "🟢"])
    n_rojas   = sum([c1 == "🔴", c2 == "🔴", c3 == "🔴", c4 == "🔴", c8 == "🔴"])

    confluencia_fresca = (
        velas["v_macd"] <= 5 and
        velas["v_media"] <= 5 and
        c1 == "🟢" and
        c3 == "🟢"
    )

    señal_tardia = (n_activas >= 4 and not confluencia_fresca)
    inicio_desact = (n_activas >= 3 and n_rojas >= 1 and (c1 == "🔴" or c3 == "🔴"))
    mayoria_desact = n_rojas >= 3

    if atención_konk and n_activas < 4:
        decision  = "⚠️ ATENCIÓN KONKORDE"
        score_str = "K!"
    elif n_activas == 5 and confluencia_fresca and c6 == "🟢":
        decision  = "🚀 COMPRA 100%"
        score_str = "5/5 + B"
    elif n_activas >= 4 and confluencia_fresca:
        decision  = "🟡 COMPRA 50%"
        score_str = f"{n_activas}/5"
    elif n_activas >= 4 and señal_tardia:
        decision  = "⏰ LLEGAS TARDE"
        score_str = f"tarde {n_activas}/5"
    elif inicio_desact:
        decision  = "⚠️ VIGILAR SALIDA"
        score_str = f"sal {n_activas}/5"
    elif mayoria_desact:
        decision  = "🔴 VENTA"
        score_str = f"{n_activas}/5"
    elif n_activas == 3:
        decision  = "👀 VIGILAR"
        score_str = "3/5"
    elif n_activas <= 1 and n_rojas >= 3:
        decision  = "⛔ NI DE COÑA"
        score_str = f"{n_activas}/5"
    else:
        decision  = "⛔ SIN SETUP"
        score_str = f"{n_activas}/5"

    razones = [c1_txt, c2_txt, c3_txt, c4_txt, c8_txt, c5_txt, c6_txt]

    if c7 == "⚡":
        razones.append(c7_txt)

    if v_bbwp_comp < 30:
        razones.append(f"BBWP tuvo compresión hace {v_bbwp_comp}v — energía acumulada")

    if div == "alcista":
        if div_velas <= 5:
            razones.append(f"🟢 Div alcista RSI FRESCA ({div_velas}v)")
        elif div_velas <= 20:
            razones.append(f"🟢 Div alcista RSI válida ({div_velas}v)")
        elif div_velas <= 50:
            razones.append(f"Div alcista RSI contexto ({div_velas}v)")
    elif div == "bajista" and div_velas <= 20:
        razones.append(f"🔴 Div bajista RSI ({div_velas}v) — cautela")

    precio = data.get("precio", 0)
    e200   = data.get("e200", 0)
    if precio < e200:
        razones.append("🔴 Precio bajo EMA200 — contexto bajista")

    if atención_konk:
        razones.append("⚠️ Verde K negativa + Azul K positivo — señal independiente potente")

    return {
        "decision": decision,
        "score":    score_str,
        "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c8": c8,
        "c5": c5, "c6": c6, "c7": c7,
        "atención_konk": atención_konk,
        "razones": " | ".join(r for r in razones if r),
    }


# ============================================================
# DASHBOARD PRINCIPAL
# ============================================================

def get_sovereign_dashboard(tickers):
    report = []

    for t in tickers:
        try:
            print(f"  Analizando {t}...", flush=True)
            df = yf.download(t, period="2y", interval="1d",
                             auto_adjust=True, progress=False,
                             multi_level_index=False)
            df = clean_yf_df(df)
            if df.empty or len(df) < 150:
                continue

            close  = df["Close"]
            volume = df["Volume"]
            precio = close.iloc[-1]

            mcg25     = mcginley_dynamic(close, period=25)
            mcg25_val = mcg25.iloc[-1]
            e200_val  = EMAIndicator(close=close, window=200).ema_indicator().iloc[-1]

            offset_mcg  = 0.012
            offset_e200 = 0.015
            cerca_mcg   = mcg25_val * (1 - offset_mcg)  <= precio <= mcg25_val * (1 + offset_mcg)
            cerca_e200  = e200_val  * (1 - offset_e200) <= precio <= e200_val  * (1 + offset_e200)

            status_mcg  = "🟡" if cerca_mcg  else ("🟢" if precio > mcg25_val else "🔴")
            status_e200 = "🟡" if cerca_e200 else ("🟢" if precio > e200_val  else "🔴")
            trend_str   = f"MD25:{status_mcg} E200:{status_e200}"

            rsi = RSIIndicator(close=close).rsi()
            cruce_30_up   = (rsi > 30) & (rsi.shift(1) <= 30)
            cruce_70_down = (rsi < 70) & (rsi.shift(1) >= 70)
            is_active, velas_rsi = False, 0
            for i in range(len(rsi)):
                if cruce_30_up.iloc[i]:
                    is_active = True; velas_rsi = 1
                elif is_active:
                    if cruce_70_down.iloc[i] or velas_rsi >= 10:
                        is_active = False; velas_rsi = 0
                    else:
                        velas_rsi += 1
            rsi_icon = "🟢" if is_active else "🔴"
            rsi_str  = f"{rsi_icon} {velas_rsi}v {'➕' if rsi.iloc[-1] > 50 else '➖'}"

            macd_obj         = MACD(close=close)
            macd_line        = macd_obj.macd()
            macd_signal_line = macd_obj.macd_signal()
            macd_diff        = macd_obj.macd_diff()
            gap              = macd_line - macd_signal_line
            gap_vol          = gap.abs().rolling(20).mean()
            accel            = (gap.diff() / gap_vol).fillna(0).iloc[-1]
            macd_gap_v       = gap.iloc[-1]
            estado_macd      = "Sep" if (gap.iloc[-1] * accel) >= 0 else "Jun"
            macd_icon        = "🟢" if macd_diff.iloc[-1] > 0 else "🔴"
            signo_linea      = "➕" if macd_line.iloc[-1] >= 0 else "➖"
            macd_str         = f"{macd_icon} {signo_linea} {accel:.2f} {estado_macd}"

            kdf = compute_blai5_koncorde(df, m=15)
            if kdf.empty:
                continue
            kdf = blai5_signals(kdf)

            azul_verde    = kdf["azul"].iloc[-1] > 0
            azul_val_now  = float(kdf["azul"].iloc[-1])
            verde_val_now = float(kdf["verde"].iloc[-1])
            punto_verde   = kdf["punto_media_verde"].iloc[-1]
            velas_konk_v  = int(kdf["velas_konk"].iloc[-1])
            azul_icon     = "🟢" if azul_verde  else "🔴"
            punto_icon    = "🟢" if punto_verde else "🔴"
            konk_str      = f"{azul_icon}{punto_icon} {velas_konk_v}v"

            azul_z_val = azul_z_score(kdf)
            azul_slope_v = 1.0 if (
                len(kdf["azul"].dropna()) >= 4 and
                kdf["azul"].iloc[-1] - kdf["azul"].iloc[-4] > 0
            ) else -1.0

            bitman_df = clasificar_bitman(df)
            if bitman_df.empty:
                continue
            bitman_row     = bitman_df.iloc[-1]
            bitman_etiq    = bitman_row["Bitman_Etiqueta"]
            bitman_velas_v = int(bitman_row["Bitman_Velas"])
            bitman_alcista = bitman_etiq in ("IMPULSO ALCISTA", "RETROCESO ALCISTA")
            emoji_bitman   = "📈" if bitman_alcista else ("📉" if "BAJISTA" in bitman_etiq else "⬜")

            div_df = detectar_divergencia_simple(df)
            hits   = div_df[div_df["divergencia_tipo"] != "ninguna"]
            if not hits.empty:
                div_tipo  = hits.iloc[-1]["divergencia_tipo"]
                div_idx   = div_df.index.get_loc(hits.index[-1])
                div_velas = len(div_df) - 1 - div_idx
            else:
                div_tipo  = "ninguna"
                div_velas = 999

            if div_tipo != "ninguna":
                emoji     = "🟢" if div_tipo == "alcista" else "🔴"
                emoji_ctx = "🟡" if div_tipo == "alcista" else "🟠"
                if div_velas <= 5:
                    div_str = f"{emoji} {div_tipo.upper()} FRESCA ({div_velas}v)"
                elif div_velas <= 20:
                    div_str = f"{emoji} {div_tipo.upper()} válida ({div_velas}v)"
                elif div_velas <= 50:
                    div_str = f"{emoji_ctx} {div_tipo.upper()} ctx ({div_velas}v)"
                else:
                    div_str = f"⚪ {div_tipo} caduc ({div_velas}v)"
            else:
                div_str = "⚪"

            _, bbwp_s = calculate_bbwp(close, bb_len=13, lookback=252)
            bbwp_last = bbwp_s.iloc[-1]
            punto_bbwp, bbwp_zona, pendiente_bbwp, nivel_bbwp = bbwp_signal(bbwp_last, bbwp_s)
            bbwp_str = f"{punto_bbwp} {pendiente_bbwp} {nivel_bbwp}"

            pvi_s       = calculate_pvi(close, volume)
            pvi_ema     = pvi_s.ewm(span=25, adjust=False).mean()
            pvi_gap     = pvi_s - pvi_ema
            pvi_activo  = bool(pvi_s.iloc[-1] > pvi_ema.iloc[-1])
            pvi_accel   = bool(pvi_gap.diff().iloc[-1] > 0)

            velas_señal = calcular_velas_señal(
                close, volume, kdf,
                macd_line, macd_signal_line,
                bitman_df
            )

            pvi_icon = "🟢" if (pvi_activo and pvi_accel) else ("⚪" if pvi_activo else "🔴")
            pvi_v = velas_señal["v_pvi"]
            pvi_v_str = f"{pvi_v}v" if pvi_v < 999 else "—"
            pvi_str = f"{pvi_icon} {pvi_v_str}"

            def fv(v):
                return f"{v}v" if v < 999 else "—"

            velas_str = (
                f"M:{fv(velas_señal['v_macd'])} "
                f"Az:{fv(velas_señal['v_azul'])} "
                f"Me:{fv(velas_señal['v_media'])} "
                f"B:{fv(velas_señal['v_bitman'])}"
            )

            bitman_str = (
                f"{bitman_etiq} "
                f"(ciclo {bitman_velas_v}v / fresco {fv(velas_señal['v_bitman'])}) "
                f"{emoji_bitman}"
            )

            input_data = {
                "precio":            float(precio),
                "e200":              float(e200_val),
                "cerca_mcg25":       bool(cerca_mcg),
                "cerca_e200":        bool(cerca_e200),
                "bitman_etiqueta":   bitman_etiq,
                "bitman_velas":      bitman_velas_v,
                "konk_azul_verde":   bool(azul_verde),
                "konk_azul_val":     float(azul_val_now),
                "konk_verde_val":    float(verde_val_now),
                "konk_punto_verde":  bool(punto_verde),
                "konk_velas":        velas_konk_v,
                "azul_z":            float(azul_z_val),
                "azul_slope":        float(azul_slope_v),
                "macd_gap":          float(macd_gap_v),
                "macd_accel":        float(accel),
                "pvi_activo":        pvi_activo,
                "pvi_accel":         pvi_accel,
                "divergencia_tipo":  div_tipo,
                "divergencia_velas": int(div_velas),
                "bbwp_pct":          float(bbwp_last) if not pd.isna(bbwp_last) else 50.0,
                "bbwp_zona":         bbwp_zona,
                "bbwp_pendiente":    pendiente_bbwp,
            }

            analisis = semaforo(input_data, velas_señal)

            report.append({
                "Ticker":    t,
                "Tendencia": trend_str,
                "RSI":       rsi_str,
                "MACD":      macd_str,
                "Koncorde":  konk_str,
                "PVI":       pvi_str,
                "Bitman":    bitman_str,
                "Div":       div_str,
                "BBWP":      bbwp_str,
                "Velas⏱":   velas_str,
                "Score":     analisis["score"],
                "Señal":     analisis["decision"],
                "Razones":   analisis["razones"],
            })

        except Exception as e:
            print(f"❌ {t}: {e}", flush=True)
            continue

    result = pd.DataFrame(report)
    if not result.empty:
        orden = {
            "⚠️ ATENCIÓN KONKORDE": 0,
            "🚀 COMPRA 100%":       1,
            "🟡 COMPRA 50%":        2,
            "👀 VIGILAR":           3,
            "⏰ LLEGAS TARDE":      4,
            "⚠️ VIGILAR SALIDA":   5,
            "🔴 VENTA":             6,
            "⛔ SIN SETUP":         7,
            "⛔ NI DE COÑA":        8,
        }
        result["_sort"] = result["Señal"].map(orden).fillna(9)
        result = (
            result
            .sort_values(["_sort", "Ticker"])
            .drop(columns="_sort")
            .reset_index(drop=True)
        )
    return result


# ============================================================
# EXPORTAR JSON
# ============================================================

def export_json(df, output_path="public/data/dashboard.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    records = df.to_dict(orient="records")

    payload = {
        "generated_at":      datetime.now(timezone.utc).isoformat(),
        "tickers_analyzed":  len(records),
        "results":           records,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n✅ JSON exportado → {output_path}  ({len(records)} tickers)")


# ============================================================
# EJECUCIÓN
# ============================================================

TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOG", "META", "BRK-B", "TSLA", "JNJ", "V",
    "PG", "XOM", "UNH", "JPM", "HD", "LLY", "MA", "CVX", "ABBV", "KO", "PEP",
    "COST", "BAC", "CRM", "NFLX", "ABT", "MCD", "LMT", "EL", "NEE", "CAT", "MRK",
    "TPL", "ASML", "ADBE", "AVGO", "CSCO", "CMCSA", "AMD", "TXN", "QCOM", "AMAT", "LITE", "LRCX",
    "INTU", "VRTX", "ZS", "PLTR", "CSU.TO", "MU", "LVMUY", "SAP", "OR.PA", "TTE", "SATS", "ON",
    "MC.PA", "SIE.DE", "ENGI.PA", "AIR.PA", "ALV.DE", "EL.PA", "AI.PA", "BNP.PA",
    "SAN.PA", "KER.PA", "SU.PA", "NESN.SW", "LIN.DE", "VOW3.DE", "BMW.DE", "ADS.DE",
    "IFX.DE", "MUV2.DE", "FRE.DE", "DTE.DE", "RWE.DE", "ITX.MC", "BBVA.MC", "SAN.MC",
    "TEF.MC", "IBE.MC", "REP.MC", "FER.MC", "ACX.MC", "ACS.MC", "AENA.MC", "ANA.MC",
    "IAG.MC", "LOG.MC", "MAP.MC", "PUIG.MC", "NTGY.MC", "ELE.MC", "IDR.MC", "PDD",
    "NIO", "TCEHY", "BZUN", "FUTU", "MOMO", "MNSO", "TAL", "EDU", "WB", "XPEV",
    "GC=F", "SI=F", "BTC-USD", "ETH-USD", "XRP-USD"
]

if __name__ == "__main__":
    print("🚀 Sovereign Dashboard v3 — Generando análisis...\n")
    df = get_sovereign_dashboard(TICKERS)

    # Ruta de salida: por defecto public/data/dashboard.json
    # Si se llama desde GitHub Actions en la raíz del repo, la ruta es correcta
    output = sys.argv[1] if len(sys.argv) > 1 else "public/data/dashboard.json"
    export_json(df, output)
