# AHP Portfolio Selector

Selección de portafolios de inversión mediante el Proceso Analítico Jerárquico (AHP).

Aplicación web full-stack que analiza acciones del S&P 500, Eurostoxx 600 y Nikkei 225,
construye portafolios óptimos con Markowitz, y los rankea según el perfil del inversor usando AHP.

---

## Requisitos

- **Python 3.10 o superior** — [descargar](https://www.python.org/downloads/)
  - En Windows: marcar **"Add Python to PATH"** durante la instalación
- **Node.js 18 o superior** — [descargar](https://nodejs.org/)
- **Conexión a internet** (para datos reales de Yahoo Finance; tiene fallback a datos sintéticos)

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/jcarlostornero2004-sys/AHP_Portfolio.git
cd AHP_Portfolio

# 2. Instalar dependencias Python
pip install -r requirements.txt

# 3. Instalar dependencias Node
npm install
cd apps/web && npm install && cd ../..
```

---

## Iniciar la aplicación

```bash
npm run dev
```

Esto arranca **ambos** servicios en paralelo:
- **API** (FastAPI) → `http://127.0.0.1:8000`
- **Web** (Next.js) → `http://localhost:3000`

Abre `http://localhost:3000` en el navegador.

---

## Uso

1. Completa el **cuestionario** de perfil inversor (15 preguntas)
2. El sistema determina tu perfil (conservador / moderado / agresivo)
3. Se ejecuta el pipeline completo: descarga de datos → análisis de 60+ acciones → construcción de portafolios Markowitz → ranking AHP
4. El **dashboard** muestra el portafolio ganador, composición, métricas y comparativa
5. Puedes descargar el informe en Word o los datos en Excel

---

## Solución de problemas

**"python no se reconoce"** → Reinstala Python marcando "Add to PATH", o usa `python3`

**"No module named fastapi/uvicorn"** → Ejecuta `pip install -r requirements.txt`

**"npm: command not found"** → Instala Node.js desde https://nodejs.org/

**El análisis tarda mucho** → Normal la primera vez; descarga datos de 60+ acciones.
Si no hay internet, usará datos sintéticos automáticamente.

**Puerto 8000 o 3000 ya en uso** → Cierra otras aplicaciones que usen esos puertos o reinicia el terminal.

---

## Estructura del proyecto

```
AHP_Portfolio/
├── apps/
│   ├── api/            ← FastAPI backend (puerto 8000)
│   │   ├── routers/    ← Endpoints REST
│   │   ├── services/   ← Pipeline AHP y datos de mercado
│   │   └── main.py     ← Entrada de la API
│   └── web/            ← Next.js frontend (puerto 3000)
│       └── src/
│           ├── app/    ← Páginas (cuestionario, dashboard)
│           ├── components/
│           └── hooks/
├── modules/            ← Lógica AHP reutilizable
│   ├── data_loader.py      ← Módulo 2: descarga yfinance
│   ├── stock_analysis.py   ← Módulo 3: 15 indicadores por acción
│   ├── stock_filter.py     ← Módulo 4: filtrado por perfil
│   ├── portfolio_builder.py← Módulo 5: Markowitz + selección
│   ├── ahp_engine_v2.py    ← Módulo 6: motor AHP
│   ├── profiles.py         ← Perfiles de inversor y pesos
│   └── questionnaire.py    ← Cuestionario de perfil
├── requirements.txt    ← Dependencias Python
├── package.json        ← Scripts npm
└── start_api.js        ← Arranque cross-platform de uvicorn
```

---

## Referencias

- Saaty, T.L. (1990). How to make a decision: The Analytic Hierarchy Process.
- Escobar, J.W. (2015). Metodología para la toma de decisiones de inversión en portafolio de acciones utilizando la técnica multicriterio AHP.
- Markowitz, H. (1952). Portfolio selection.
- Sharpe, W.F. (1966). Mutual fund performance.
- Sortino, F.A. y Price, L.N. (1994). Performance measurement in a downside risk framework.
