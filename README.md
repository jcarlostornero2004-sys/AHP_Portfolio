# AHP Portfolio Selector
## Selección de portafolios de inversión mediante el Proceso Analítico Jerárquico

Herramienta desarrollada como parte de un TFG que aplica la técnica multicriterio AHP
(Saaty, 1990) para seleccionar el mejor portafolio de acciones de entre los mercados
S&P 500, Eurostoxx 600 y Nikkei 225, adaptándose al perfil de cada inversor.

---

## Requisitos previos

- **Python 3.9 o superior** (recomendado 3.11+)
- **Conexión a internet** (solo para descargar datos reales con yfinance)

### ¿No tienes Python instalado?

1. Ve a https://www.python.org/downloads/
2. Descarga la versión más reciente (3.12+)
3. **IMPORTANTE**: durante la instalación, marca la casilla "Add Python to PATH"
4. Reinicia el terminal/PowerShell después de instalar

Para verificar que funciona, abre un terminal y escribe:
```
python --version
```
Debería mostrar algo como `Python 3.12.x`

---

## Instalación paso a paso

### 1. Descargar el proyecto

Descomprime el archivo `ahp_portfolio_project.tar.gz` que has descargado.

**En Windows (PowerShell):**
```powershell
# Si tienes 7-Zip o WinRAR, haz clic derecho → Extraer aquí
# O desde PowerShell:
tar -xzf ahp_portfolio_project.tar.gz
```

**En Mac/Linux:**
```bash
tar -xzf ahp_portfolio_project.tar.gz
```

Esto creará una carpeta `ahp_portfolio/` con estos archivos:
```
ahp_portfolio/
├── main.py              ← Orquestador principal
├── questionnaire.py     ← Módulo 0: Cuestionario de perfil
├── profiles.py          ← Módulo 1: Motor de perfiles (15 criterios × 7 perfiles)
├── data_loader.py       ← Módulo 2: Descarga de datos (yfinance)
├── stock_analysis.py    ← Módulo 3: Análisis individual (13 indicadores)
├── ahp_engine.py        ← Módulo 6: Motor AHP
├── requirements.txt     ← Dependencias Python
└── README.md            ← Este archivo
```

### 2. Abrir terminal en la carpeta del proyecto

**Windows:** Abre la carpeta en el Explorador → escribe `cmd` o `powershell` en la barra de direcciones → Enter

**Mac:** Abre Terminal → escribe `cd ` (con espacio) → arrastra la carpeta al terminal → Enter

**Linux:** Abre terminal → `cd ruta/a/ahp_portfolio`

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Si te da error de permisos, usa:
```bash
pip install --user -r requirements.txt
```

Esto instalará:
- `yfinance` → descarga de datos financieros de Yahoo Finance
- `scipy` → cálculos estadísticos (autovectores, distribuciones)
- `numpy` → operaciones numéricas
- `pandas` → manejo de tablas de datos
- `openpyxl` → exportación a Excel

### 4. Verificar la instalación

```bash
python -c "import yfinance, scipy, numpy, pandas, openpyxl; print('Todo instalado correctamente')"
```

---

## Cómo usar la herramienta

### Opción A: Demo rápida (sin internet)

Ejecuta la demo con datos sintéticos para comprobar que todo funciona:

```bash
python main.py --demo
```

Esto genera 5 acciones ficticias, calcula los 13 indicadores y muestra los resultados.
No necesita conexión a internet.

### Opción B: Pipeline completo con cuestionario (sin internet)

```bash
python main.py
```

1. Te hará 12 preguntas para determinar tu perfil de inversor
2. Mostrará tu perfil, pesos AHP y filtros de universo
3. Ejecutará el análisis con datos sintéticos (por ahora)

### Opción C: Pipeline con datos reales (necesita internet)

```bash
python main.py --live
```

Esto descargará datos reales de Yahoo Finance para ~115 acciones de los 3 índices.
Tarda unos 2-3 minutos dependiendo de tu conexión.

### Opción D: Saltar el cuestionario (perfil directo)

```bash
python main.py --profile agresivo
python main.py --profile conservador --live
python main.py --profile tecnologico --live
```

Perfiles disponibles: `conservador`, `moderado`, `agresivo`, `muy_agresivo`,
`dividendos`, `tecnologico`, `esg`

---

## Probar módulos individuales

Cada módulo se puede ejecutar por separado:

```bash
# Solo el cuestionario
python questionnaire.py

# Ver todos los perfiles y sus configuraciones
python profiles.py

# Análisis con datos sintéticos
python stock_analysis.py

# Motor AHP con datos de ejemplo (Escobar 2015)
python ahp_engine.py
```

---

## Solución de problemas comunes

### "python no se reconoce como comando"
→ Python no está en el PATH. Reinstala marcando "Add to PATH" o usa `python3` en lugar de `python`.

### "No module named yfinance"
→ Las dependencias no están instaladas. Ejecuta `pip install -r requirements.txt`

### "pip no se reconoce"
→ Prueba con `python -m pip install -r requirements.txt`

### Error de conexión al usar --live
→ Necesitas internet. yfinance descarga datos de Yahoo Finance.
→ Si estás detrás de un proxy corporativo, puede fallar.

### Los datos tardan mucho en descargar
→ La primera vez descarga ~115 acciones × 2 años. Es normal que tarde 2-3 min.
→ Puedes reducir usando menos acciones: edita `max_per_index` en `main.py`.

---

## Próximos módulos (en desarrollo)

- **Módulo 4**: Filtrado y selección de acciones (razón beta, filtros de perfil)
- **Módulo 5**: Construcción de portafolios (Markowitz, frontera eficiente)
- **Módulo 6 v2**: Motor AHP actualizado a 15 criterios
- **Módulo 7**: Exportación a Excel profesional
- **Módulo 8**: Backtesting (train/test vs benchmark)

---

## Referencias

- Saaty, T.L. (1990). How to make a decision: The Analytic Hierarchy Process.
- Escobar, J.W. (2015). Metodología para la toma de decisiones de inversión en portafolio de acciones utilizando la técnica multicriterio AHP.
- Markowitz, H. (1952). Portfolio selection.
- Sharpe, W.F. (1966). Mutual fund performance.
- Sortino, F.A. y Price, L.N. (1994). Performance measurement in a downside risk framework.
- Artzner, P. et al. (1999). Coherent measures of risk.
