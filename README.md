# 🎮 **Plataforma de Juegos Arduino**

Una plataforma elegante y modular para ejecutar juegos interactivos con Arduino, desarrollada con una **arquitectura profesional completamente modularizada**.

## 🏗️ **Arquitectura Modularizada**

### **Eliminación Completa de Monolitos**

La plataforma ha sido **refactorizada completamente** para eliminar archivos monolíticos y seguir el principio de **responsabilidad única**:

#### **🎮 GameController (Antes: 637 líneas → Ahora: 213 líneas)**
- **Eliminado el monolito original** que mezclaba UI, lógica, estado y manejo de juegos
- **Refactorizado como coordinador ligero** que solo maneja interacciones entre componentes
- **Componentes especializados creados:**
  - `GameRegistry` (78 líneas): Registro de juegos y metadatos
  - `GameLifecycle` (154 líneas): Ciclo de vida e inicio/parada
  - `GameUIManager` (239 líneas): Interfaz de usuario y widgets
  - `GameStatusManager` (191 líneas): Ventanas de estado detallado

#### **📊 GameAnalytics (Antes: 628 líneas → Ahora: 124 líneas)**
- **Eliminado el monolito de analytics** que mezclaba parseo, visualización y reportes
- **Refactorizado como coordinador de componentes especializados:**
  - `LogParser` (152 líneas): Solo carga y parseo de logs
  - `DataVisualizer` (258 líneas): Solo visualizaciones matplotlib
  - `ReportGenerator` (243 líneas): Solo reportes y exportación

#### **🖥️ MainWindow (Previamente modularizado: 97 líneas)**
- Coordinador ligero usando componentes UI especializados
- `TitleSection`, `StatsSection`, `GamesSection`, `ControlSection`, `AnalyticsManager`

## 🎨 **Paleta de Colores Elegante**

Se eliminó la **paleta negra horrible** y se implementó una paleta elegante y profesional:

```python
# Colores de fondo elegantes (NO MÁS NEGRO!)
BACKGROUND_PRIMARY = "#f8f9fa"      # Gris muy claro elegante
BACKGROUND_SECONDARY = "#e9ecef"    # Gris claro suave
BACKGROUND_TERTIARY = "#dee2e6"     # Gris medio

# Colores de texto legibles
TEXT_PRIMARY = "#212529"            # Negro suave para texto
TEXT_SECONDARY = "#495057"          # Gris oscuro para texto

# Colores semánticos elegantes
SUCCESS = "#28a745"                 # Verde éxito
WARNING = "#ffc107"                 # Amarillo advertencia
ERROR = "#dc3545"                   # Rojo error
INFO = "#17a2b8"                    # Azul información
```

## 🎯 **Juegos Disponibles**

### **🏓 Ping Pong**
- Juego clásico de ping pong con dos palas
- Controles con sensores de movimiento
- Sistema de puntuación integrado

### **🏃 Two Lane Runner**
- Juego de carreras en dos carriles
- Evita obstáculos usando sensores de distancia
- Velocidad progresiva

### **🎹 Piano Digital**
- Piano con 8 teclas táctiles (pines 2-9)
- Modo de juego Simon Says
- **Modo de prueba independiente** para calibración
- Notas musicales: Do, Re, Mi, Fa, Sol, La, Si, Do8

## 🔧 **Requisitos Técnicos**

### **Hardware Arduino**
- **Arduino UNO/Nano/Mega**
- **Pines 2-9**: Botones táctiles para piano
- **Pines analógicos**: Sensores de distancia para runner
- **Pines PWM**: Control de servos para ping pong
- **Display LCD 16x2** (opcional para información)

### **Software**
```
Python 3.8+
tkinter (incluido en Python)
pyserial==3.5
pygame==2.6.1
matplotlib==3.10.1
pandas==2.2.3
numpy==1.26.4
opencv-python==4.11.0.86
mediapipe==0.10.21
```

## 🚀 **Instalación y Uso**

### **1. Clonar Repositorio**
```bash
git clone [repository-url]
cd main
```

### **2. Crear Entorno Virtual**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **4. Configurar Arduino**
1. Conectar Arduino al puerto USB
2. Cargar el sketch correspondiente para cada juego
3. Configurar sensores según el juego seleccionado

### **5. Ejecutar Aplicación**
```bash
cd app
python main.py
```

## 📈 **Sistema de Analytics Avanzado**

### **Análisis de Logs Inteligente**
- **Parseo automático** de logs de juegos
- **Visualizaciones matplotlib** profesionales
- **Reportes textuales** con recomendaciones inteligentes
- **Exportación a CSV/Excel** para análisis externo

### **Métricas Disponibles**
- **Timeline de eventos** por juego
- **Distribución de errores** y análisis de causas
- **Tendencias de rendimiento** a lo largo del tiempo
- **Heatmaps de actividad** por horas del día
- **Progresión de habilidad** del jugador
- **Análisis de velocidad vs rendimiento**

### **Reportes Inteligentes**
```python
# Ejemplo de reporte generado automáticamente
🎮 REPORTE DE RENDIMIENTO: PIANO DIGITAL
• Score máximo alcanzado: 1850
• Duración promedio: 45.3 segundos
• Tasa de errores: 8.2% (Excelente control)
💡 RECOMENDACIONES:
• Excelente control de errores (<10%): ¡sigue así!
• Sesiones moderadas: intenta jugar por más tiempo
```

## 🔄 **Flujo de Ejecución**

### **Inicio de Aplicación**
1. **Inicialización** de componentes Arduino y UI
2. **Carga automática** de juegos disponibles
3. **Detección** automática de puerto Arduino
4. **Interface elegante** con colores profesionales

### **Ejecución de Juegos**
1. **Selección** de juego desde interfaz
2. **Validación** de conexión Arduino
3. **Inicialización** segura del juego
4. **Monitoreo** en tiempo real del estado
5. **Detención segura** con limpieza de recursos

### **Analytics Post-Juego**
1. **Registro automático** de eventos en logs
2. **Procesamiento** de datos de rendimiento
3. **Generación** de métricas y estadísticas
4. **Visualización** de resultados

## 📁 **Estructura de Proyecto Modularizada**

```
app/
├── main.py                 # Punto de entrada principal
├── managers/               # Controladores de alto nivel
│   ├── game_controller.py  # Coordinador de juegos (213 líneas)
│   └── components/         # Componentes especializados
│       ├── game_registry.py     # Registro de juegos (78 líneas)
│       ├── game_lifecycle.py    # Ciclo de vida (154 líneas)
│       ├── game_ui_manager.py   # UI de juegos (239 líneas)
│       └── game_status_manager.py # Estado detallado (191 líneas)
├── ui/                     # Interfaz de usuario
│   ├── main_window.py      # Coordinador UI (97 líneas)
│   └── components/         # Componentes UI especializados
│       ├── title_section.py
│       ├── stats_section.py
│       ├── games_section.py
│       ├── control_section.py
│       ├── analytics_manager.py
│       └── arduino_colors.py  # Paleta elegante
├── core/                   # Funcionalidades centrales
│   ├── arduino_manager.py  # Comunicación Arduino
│   ├── base_game.py        # Clase base para juegos
│   ├── safe_game_manager.py # Manejo seguro de recursos
│   └── analytics/          # Sistema de analytics modularizado
│       ├── game_analytics.py    # Coordinador (124 líneas)
│       └── components/     # Componentes especializados
│           ├── log_parser.py      # Parseo de logs (152 líneas)
│           ├── data_visualizer.py # Visualización (258 líneas)
│           └── report_generator.py # Reportes (243 líneas)
└── games/                  # Juegos individuales
    ├── ping_pong/
    ├── two_lanes/
    └── piano/
```

## 🏆 **Logros de la Refactorización**

### **Métricas de Transformación**
- **GameController**: 637 → 213 líneas (**66% reducción**)
- **GameAnalytics**: 628 → 124 líneas (**80% reducción**)
- **MainWindow**: Previamente modularizado a 97 líneas
- **Total de archivos especializados**: 8 componentes nuevos
- **Principio de responsabilidad única**: ✅ Aplicado
- **Código testeable independientemente**: ✅ Logrado
- **Arquitectura escalable**: ✅ Implementada

### **Beneficios Arquitectónicos**
- **Mantenimiento simplificado**: Cada componente tiene una responsabilidad clara
- **Extensibilidad mejorada**: Agregar nuevos juegos o funciones es trivial
- **Testeo independiente**: Cada componente puede probarse por separado
- **Código reutilizable**: Componentes pueden usarse en otros proyectos
- **Legibilidad profesional**: Estructura clara y organizada

## 🎨 **Características de UI/UX**

### **Interfaz Elegante**
- **Paleta de colores profesional** (eliminado el negro horrible)
- **Layout responsivo** con grid de 3 juegos por fila
- **Highlighting inteligente** para juegos activos
- **Ventanas de estado detallado** con pestañas organizadas
- **Controles intuitivos** con iconos descriptivos

### **Experiencia de Usuario**
- **Inicio rápido** de juegos con validación previa
- **Feedback visual** inmediato del estado de conexión
- **Modo de prueba** para calibración de hardware
- **Analytics en tiempo real** con visualizaciones profesionales
- **Detención segura** con limpieza automática de recursos

## 📊 **Funcionalidades Avanzadas**

### **Gestión de Estado Inteligente**
- **Monitoreo en tiempo real** del estado de juegos
- **Validación automática** de conexión Arduino
- **Manejo de errores robusto** con fallback a parada de emergencia
- **Limpieza automática** de recursos al cerrar

### **Sistema de Logs Profesional**
- **Formato estructurado** con timestamps y niveles
- **Parseo inteligente** de eventos de juego
- **Detección automática** de patrones y métricas
- **Almacenamiento persistente** para análisis histórico

## 🔧 **Desarrollo y Extensión**

### **Agregar Nuevos Juegos**
1. Crear clase que herede de `BaseGame`
2. Registrar en `GameRegistry`
3. Implementar lógica específica del juego
4. ¡El sistema se encarga del resto automáticamente!

### **Personalizar Analytics**
- Agregar nuevos tipos de eventos en `LogParser`
- Crear visualizaciones custom en `DataVisualizer`
- Generar reportes específicos en `ReportGenerator`

### **Extender UI**
- Crear nuevos componentes en `ui/components/`
- Usar la paleta elegante de `ArduinoColors`
- Seguir el patrón de responsabilidad única

## 🚀 **Próximas Funcionalidades**

### **Juegos en Desarrollo**
- **🐍 Snake Game**: Juego clásico de serpiente
- **🧩 Tetris**: Implementación de Tetris con Arduino
- **🔴 Simon Says**: Juego de memoria con LEDs
- **🧱 Breakout**: Rompecabezas con sensores

### **Mejoras Técnicas**
- **🔗 Conectividad WiFi**: Control remoto via web
- **☁️ Cloud Analytics**: Almacenamiento en la nube
- **🎵 Audio Avanzado**: Efectos de sonido mejorados
- **🎯 Achievements**: Sistema de logros y puntuaciones

## 🚀 Características Principales

### 🎯 Juegos Disponibles
- **🎹 Piano Simon**: Juego de memoria y secuencias musicales con evaluación neurocognitiva
- **🏃 Two-Lane Runner**: Juego de esquivar obstáculos en dos carriles
- **🏓 Ping Pong**: Clásico juego de ping pong

### 📊 **NUEVO: Análisis Neurocognitivo**
- **Gráficas en tiempo real** de rendimiento cognitivo
- **Análisis de progreso** a lo largo de múltiples sesiones
- **Métricas de tiempo de reacción** y patrones de error
- **Reportes detallados** con recomendaciones personalizadas
- **Exportación de datos** a Excel para análisis adicional

## 🧠 Evaluación Neurocognitiva

### Piano Simon - Análisis Cognitivo
El Piano Simon no es solo un juego, es una **herramienta de evaluación neurocognitiva** que mide:

- **Memoria de trabajo**: Capacidad de recordar secuencias
- **Atención sostenida**: Concentración durante la sesión
- **Tiempo de reacción**: Velocidad de respuesta
- **Control de errores**: Precisión en la ejecución
- **Progreso temporal**: Mejora a lo largo del tiempo

### 📈 Gráficas Disponibles

1. **🎯 Rendimiento**:
   - Progreso de nivel por sesión
   - Distribución de tipos de eventos
   - Tendencia de errores
   - Duración de sesiones

2. **⚡ Tiempos de Reacción**:
   - Distribución de tiempos de respuesta
   - Evolución temporal de velocidad

3. **❌ Análisis de Errores**:
   - Tipos de errores más frecuentes
   - Patrones temporales de errores
   - Proporción éxito vs error

4. **📈 Progreso**:
   - Evolución de métricas por sesión
   - Análisis de tendencias de mejora
   - Interpretación automática del progreso

## 🔧 Instalación

```bash
# Clonar repositorio
git clone [url-del-repositorio]
cd main

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app/main.py
```

## 📋 Dependencias

```
pyfirmata          # Comunicación con Arduino
pygame             # Audio y gráficos de juegos
numpy              # Cálculos numéricos
pandas             # Análisis de datos
matplotlib         # Gráficas y visualizaciones
cvzone             # Visión por computadora (opcional)
opencv-python      # Procesamiento de imágenes (opcional)
mediapipe          # Análisis de gestos (opcional)
```

## 🎮 Uso

### Iniciar Juegos
1. **▶️ Iniciar**: Ejecuta el juego completo
2. **🧪 Probar**: Modo de prueba libre (solo Piano Simon)
3. **⏹️ Detener**: Termina el juego actual

### Análisis Cognitivo (Piano Simon)
1. **📈 Análisis**: Abre ventana con gráficas de evaluación neurocognitiva
2. **📊 Exportar Datos**: Guarda datos en Excel
3. **📋 Generar Reporte**: Crea reporte textual con recomendaciones
4. **🔄 Actualizar**: Recarga datos más recientes

### Datos de Sesión
Los datos se guardan automáticamente en:
```
data/cognitive/piano_simon/sessions/
├── session_YYYYMMDD_HHMMSS.csv
├── session_YYYYMMDD_HHMMSS.csv
└── ...
```

## 🔬 Interpretación de Resultados

### Métricas Cognitivas
- **Eficiencia > 85%**: Rendimiento excelente
- **Eficiencia 70-85%**: Buen rendimiento con espacio para mejora
- **Eficiencia < 70%**: Requiere atención y práctica adicional

### Tendencias de Progreso
- **📈 Mejora Positiva**: Pendiente ascendente en eficiencia
- **📊 Estable**: Rendimiento consistente
- **📉 Necesita Atención**: Tendencia descendente

## 🔧 Hardware Soportado

- **Arduino Uno/Nano** con Firmata
- **LCD Keypad Shield** para interfaz
- **Botones externos** para Piano Simon (pines 2-9)
- **Buzzer/Speaker** para audio (opcional)

## 📁 Estructura del Proyecto

```
main/
├── app/
│   ├── core/                    # Clases base y Arduino
│   ├── games/                   # Implementación de juegos
│   ├── managers/                # Gestores de componentes
│   ├── ui/                      # Interfaz de usuario
│   │   ├── cognitive/           # 🆕 Análisis neurocognitivo
│   │   └── components/          # Componentes UI
│   └── main.py                  # Punto de entrada
├── data/
│   └── cognitive/               # 🆕 Datos de evaluación
│       └── piano_simon/
│           └── sessions/        # Archivos CSV de sesiones
├── requirements.txt
└── README.md
```

## 🧪 Pruebas

```bash
# Probar análisis cognitivo
python test_cognitive_analytics.py

# Probar funcionalidad específica
python test_piano_test_mode.py
```

## 🎯 Casos de Uso

### 🏥 Evaluación Clínica
- Evaluación de memoria de trabajo
- Seguimiento de rehabilitación cognitiva
- Detección temprana de deterioro

### 🎓 Investigación Educativa
- Análisis de capacidades de aprendizaje
- Seguimiento de progreso académico
- Personalización de métodos de enseñanza

### 🏋️ Entrenamiento Cognitivo
- Mejora de tiempo de reacción
- Fortalecimiento de memoria
- Desarrollo de concentración

## 📊 Ejemplo de Datos

```csv
timestamp,level,event_type,message,score,player_level,game_duration,session_notes
2025-01-08 12:00:00,INFO,GAME_START,Inicio de sesión Piano Simon,,1,,Sesión de prueba inicial
2025-01-08 12:00:15,INFO,NOTE_PLAYED,Reproduciendo Do,10,1,15,Primer botón presionado
2025-01-08 12:00:25,ERROR,WRONG_NOTE,Error: Se esperaba Mi pero se presionó Fa,20,1,25,Error de memoria
2025-01-08 12:00:30,INFO,LEVEL_COMPLETE,Nivel 1 completado,50,2,30,Avance de nivel
```

## 🤝 Contribuir

1. Fork del proyecto
2. Crear rama para nueva funcionalidad
3. Commit de cambios
4. Push a la rama
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆕 Novedades v2.1

- ✅ **Análisis neurocognitivo completo** con gráficas interactivas
- ✅ **Exportación de datos** a Excel
- ✅ **Reportes automáticos** con recomendaciones
- ✅ **Interfaz mejorada** con pestañas especializadas
- ✅ **Datos de ejemplo** para pruebas inmediatas

---

**🎮 ¡Disfruta explorando las capacidades cognitivas con Arduino!** 🧠📊 