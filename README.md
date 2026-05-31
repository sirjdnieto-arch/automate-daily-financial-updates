# 🚀 Sovereign Dashboard v3

Dashboard de análisis técnico con semáforo automático para +100 tickers.  
**Se actualiza solo cada madrugada** vía GitHub Actions y se publica en GitHub Pages.

---

## 📋 Qué hace

1. **Cada día a las 04:30 UTC** (06:30h España verano / 05:30h invierno), GitHub Actions:
   - Descarga datos de Yahoo Finance con `yfinance`
   - Calcula MACD, Blai5 Koncorde, Bitman, BBWP 13/252, PVI, RSI + divergencias
   - Genera `public/data/dashboard.json`
   - Hace build de la web React
   - Publica en **GitHub Pages** → tu enlace permanente

2. **Tú** abres el enlace y ves el dashboard actualizado cada mañana.

---

## 🛠️ Configuración (una sola vez)

### 1. Crear el repositorio en GitHub

```bash
git init
git add .
git commit -m "🚀 Initial commit"
git remote add origin https://github.com/TU_USUARIO/sovereign-dashboard.git
git push -u origin main
```

### 2. Activar GitHub Pages desde la rama `gh-pages`

En GitHub → tu repo → **Settings** → **Pages**:
- Source: **Deploy from a branch**
- Branch: **gh-pages** / `/ (root)`
- Guardar

### 3. Dar permisos al workflow

En GitHub → tu repo → **Settings** → **Actions** → **General**:
- Workflow permissions → **Read and write permissions** ✅
- Allow GitHub Actions to create and approve pull requests ✅

### 4. Tu enlace

```
https://TU_USUARIO.github.io/sovereign-dashboard/
```

---

## ▶️ Lanzar manualmente (cuando quieras)

GitHub → tu repo → **Actions** → `🌙 Actualizar Dashboard` → **Run workflow**

---

## 💻 Desarrollo local

```bash
# Instalar dependencias
npm install

# Ejecutar el análisis Python (genera el JSON)
pip install -r scripts/requirements.txt
python scripts/generate_dashboard.py

# Iniciar servidor de desarrollo
npm run dev

# Build de producción
npm run build
```

---

## 📊 Indicadores

| Indicador | Descripción |
|-----------|-------------|
| **MACD** | 12/26/9 — GAP positivo y acelerando |
| **Blai5 Koncorde** | Verde/Azul/Marrón — flujo institucional |
| **Bitman** | ADX + Awesome Oscillator — ciclo de mercado |
| **BBWP** | BB Width Percentile 13/252 — compresión/expansión |
| **PVI** | Price Volume Index — dinero inteligente |
| **Divergencias RSI** | Divergencias alcistas/bajistas automáticas |
| **MCG25** | McGinley Dynamic 25 — soporte/resistencia |

---

## ⚠️ Aviso legal

Este dashboard es exclusivamente informativo.  
**No constituye asesoramiento financiero.**  
Opera siempre con responsabilidad y gestión de riesgo.
