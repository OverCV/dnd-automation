<!-- # 🎮 Arduino Game Platform - Análisis de Rendimiento

Sistema completo de análisis de logs y visualización de rendimiento para juegos de Arduino.

## 📊 Nuevas Características Implementadas

### 1. **Sistema de Logging Avanzado**
- **Logging específico por juego**: Cada juego genera su propio archivo de log
- **Eventos detallados**: Se registran inputs, colisiones, scores, velocidades, duraciones
- **Logging de muertes**: Información completa cuando el jugador pierde
- **Formato estructurado**: Logs parseables con timestamps, niveles y categorías

### 2. **Análisis Visual con Matplotlib**
- **Dashboard general**: Vista panorámica de todos los juegos
- **Análisis detallado**: Gráficos específicos por juego
- **Timeline de eventos**: Visualización temporal de actividad
- **Distribución de errores**: Análisis de tipos y frecuencia de errores
- **Tendencias de rendimiento**: Progresión de scores y habilidades
- **Heatmaps de actividad**: Patrones de uso por hora del día

### 3. **Reportes y Exportación**
- **Reportes textuales**: Estadísticas y recomendaciones automáticas
- **Exportación CSV**: Datos estructurados para análisis externo
- **Métricas avanzadas**: Duración de sesiones, velocidad vs rendimiento
- **Progresión de habilidad**: Análisis de mejora a lo largo del tiempo

### 4. **Mejoras en Two Lanes**
- **Logging completo**: Implementación similar a Ping Pong
- **Eventos específicos**: Cambios de carril, obstáculos esquivados, colisiones
- **Renderer mejorado**: Visualización completa con Pygame
- **Manejo de eventos**: Controles de teclado y cierre seguro de ventanas

### 5. **Cierre Seguro de Ventanas**
- **Pygame mejorado**: Cierre controlado sin errores
- **Tkinter robusto**: Manejo de excepciones en cierre de aplicación
- **Cleanup automático**: Liberación de recursos y desconexión de Arduino
- **Manejo de errores**: Recuperación graceful ante fallos

## 🚀 Cómo Usar el Análisis

### Desde la Aplicación Principal
1. Ejecuta `python main.py`
2. Juega algunos juegos para generar logs
3. Haz clic en "📈 Análisis de Logs" en la interfaz
4. Selecciona el tipo de análisis que deseas ver

### Análisis Independiente
```bash
cd main
python test_analytics.py
```

### Análisis Programático
```python
from core.game_analytics import GameAnalytics

# Crear analizador
analytics = GameAnalytics()

# Dashboard general
analytics.show_performance_dashboard()

# Análisis detallado
analytics.show_detailed_game_analysis("Ping Pong")

# Reporte textual
report = analytics.generate_performance_report("Two Lane Runner")
print(report)

# Exportar datos
analytics.export_data_to_csv("Ping Pong", "mi_analisis.csv")
```

## 📈 Tipos de Gráficos Disponibles

### Dashboard General (3 columnas)
1. **Timeline de Eventos**: Cronología de actividad con códigos de color por severidad
2. **Distribución de Errores**: Barras mostrando frecuencia de cada tipo de error
3. **Tendencias de Rendimiento**: Línea de scores con marcadores de Game Over

### Análisis Detallado (2x2)
1. **Heatmap de Actividad**: Actividad por hora del día
2. **Duración de Sesiones**: Histograma de duración de partidas
3. **Velocidad vs Rendimiento**: Scatter plot correlacionando dificultad y score
4. **Progresión de Habilidad**: Evolución de scores finales en el tiempo

## 📁 Estructura de Logs

Los logs se guardan en `main/data/` con formato:
```
2025-05-25 22:57:24 | INFO | [EVENT_TYPE] mensaje
```

### Tipos de Eventos Registrados
- **HARDWARE**: Inicialización y manejo de componentes
- **GAME**: Inicio, pausa, reinicio, fin de juego
- **INPUT**: Botones presionados, cambios de carril
- **SCORE**: Puntuaciones, hits exitosos, obstáculos esquivados
- **COLLISION**: Rebotes, choques
- **BALL/OBSTACLE**: Movimiento de elementos del juego
- **SPEED**: Cambios de velocidad/dificultad
- **UI**: Cambios de pantalla

### Archivos de Log por Juego
- `pingponggame.log` - Logs del Ping Pong
- `twolanerunner.log` - Logs del Two Lane Runner
- Otros juegos generan sus propios archivos automáticamente

## 🎯 Métricas Analizadas

### Ping Pong
- Total de hits (izquierda/derecha)
- Duración de partidas
- Velocidad final alcanzada
- Precisión de palas
- Progresión de puntuación

### Two Lane Runner
- Obstáculos esquivados
- Cambios de carril
- Velocidad máxima alcanzada
- Tiempo de supervivencia
- Eficiencia de movimiento

### Métricas Generales
- Tasa de errores
- Tiempo total jugado
- Sesiones por día/hora
- Scores máximos y promedios
- Tendencias de mejora

## 🛠 Dependencias Nuevas

Asegúrate de instalar:
```bash
pip install matplotlib pandas numpy
```

## 🔧 Configuración

### Personalizar Directorio de Logs
```python
analytics = GameAnalytics(log_dir="ruta/personalizada")
```

### Configurar Gráficos
Los gráficos usan matplotlib y son completamente personalizables modificando los métodos `_plot_*` en `GameAnalytics`.

## 📊 Ejemplos de Uso

### Análisis de Rendimiento Individual
```python
# Obtener resumen rápido
summary = analytics.get_game_summary("Ping Pong")
print(f"Partidas jugadas: {summary['deaths']}")
print(f"Score máximo: {summary['max_score']}")
```

### Comparación entre Juegos
```python
# Dashboard comparativo
analytics.show_performance_dashboard()  # Todos los juegos
```

### Exportación para Análisis Externo
```python
# Datos estructurados para Excel/R/Python
analytics.export_data_to_csv("Two Lane Runner", "analisis_detallado.csv")
```

## 🎨 Personalización

### Añadir Nuevas Métricas
1. Modifica `_extract_specific_data()` en `GameAnalytics`
2. Agrega patrones regex para extraer datos específicos
3. Crea nuevos métodos `_plot_*` para visualizaciones personalizadas

### Nuevos Tipos de Gráficos
Extiende la clase `GameAnalytics` con métodos adicionales:
```python
def _plot_custom_metric(self, events, ax, title):
    # Tu gráfico personalizado aquí
    pass
```

## 🐛 Solución de Problemas

### "No se encontraron logs"
- Ejecuta algunos juegos primero
- Verifica que el directorio `main/data/` existe
- Asegúrate de que los juegos están generando logs correctamente

### Error con matplotlib
```bash
pip install --upgrade matplotlib
# En algunos sistemas:
sudo apt-get install python3-tk
```

### Errores de pandas
```bash
pip install --upgrade pandas numpy
```

## 🔮 Próximas Características

- [ ] Análisis predictivo de rendimiento
- [ ] Comparación entre jugadores
- [ ] Gráficos interactivos con plotly
- [ ] Dashboard web en tiempo real
- [ ] Machine learning para detección de patrones
- [ ] Alertas automáticas de regresión en rendimiento

---

¡El sistema está listo para analizar tu rendimiento en los juegos de Arduino! 🎮📊 -->
