# 📊 Base de Datos - Estructura Cognitiva Organizada

> **Actualizado:** 2025-01-29 - Nueva estructura separada por juegos

## 🗂️ Estructura General

```
data/cognitive/
├── piano_simon/
│   ├── sessions/           # Sesiones CSV del Piano Simon
│   │   ├── PACIENTE1_piano_simon_20250129_143022.csv
│   │   └── PACIENTE2_piano_simon_20250129_151045.csv
│   └── patients.json       # Pacientes específicos del Piano Simon
├── ping_pong/
│   ├── sessions/           # Sesiones futuras del Ping Pong
│   └── patients.json
├── two_lanes/
│   ├── sessions/           # Sesiones futuras del Two Lanes
│   └── patients.json
└── shared/
    └── global_patients.json   # Pacientes compartidos (futuro)
```

## 🎹 Piano Simon Says

### Archivos de Sesión
**Formato:** `{patient_id}_piano_simon_{YYYYMMDD}_{HHMMSS}.csv`

### Headers CSV Piano Simon:
```csv
timestamp,session_id,game_type,level,response_time_ms,accuracy,is_correct,sequence_length,presentation_time_ms,error_type,sequence_shown,sequence_input,reaction_latency_ms,error_position,melody_name
```

### Campos Específicos:
- **melody_name**: Nombre de la melodía famosa (ej: "Frère Jacques", "Happy Birthday")
- **sequence_shown**: Notas mostradas separadas por `|` (ej: "0|1|2|0")
- **sequence_input**: Notas introducidas por el usuario separadas por `|`
- **error_position**: Posición del primer error (-1 si no hay error)
- **presentation_time_ms**: Tiempo total de presentación de la melodía

### Melodías Implementadas (Niveles 1-10):
1. **Frère Jacques** - Do Re Mi Do
2. **Himno de la Alegría** - Mi Mi Fa Sol Sol
3. **Cumpleaños Feliz** - Do Do Re Do Fa Mi
4. **Mary Had a Little Lamb** - Mi Re Do Re Mi Mi Mi
5. **Twinkle Twinkle** - Do Do Sol Sol La La Sol
6. **Happy Birthday** - Do Do Do8 La Fa Mi
7. **Jingle Bells** - Mi Mi Mi Mi Mi Fa Sol Re
8. **London Bridge** - Sol Fa Mi Fa Sol Sol Sol
9. **Old MacDonald** - Do Do Do Sol La La Sol
10. **Final Challenge** - Do Mi Sol La Do8 La Sol Mi Do

### Mapeo de Notas:
```
0 = Do (C4)    |  4 = Sol (G4)
1 = Re (D4)    |  5 = La (A4) 
2 = Mi (E4)    |  6 = Si (B4)
3 = Fa (F4)    |  7 = Do8 (C5)
```

## 🏓 Ping Pong (Futuro)

### Headers CSV Ping Pong:
```csv
timestamp,session_id,game_type,level,response_time_ms,accuracy,is_correct,ball_speed,paddle_position,hit_accuracy,reaction_zone
```

## 🛣️ Two Lanes (Futuro)

### Headers CSV Two Lanes:
```csv
timestamp,session_id,game_type,level,response_time_ms,accuracy,is_correct,lane_changed,obstacle_type,distance_to_obstacle,decision_time_ms
```

## 👤 Gestión de Pacientes

### Archivo: `patients.json`
```json
{
  "PACIENTE_001": {
    "name": "Juan Pérez",
    "age": 25,
    "created": "2025-01-29T14:30:22",
    "notes": "Paciente de prueba"
  },
  "PACIENTE_002": {
    "name": "María García", 
    "age": 30,
    "created": "2025-01-29T15:10:45",
    "notes": "Seguimiento cognitivo"
  }
}
```

### Formato de Patient ID:
- **Automático:** `PACIENTE_{contador:03d}` (ej: PACIENTE_001)
- **Temporal:** `TEMP_PIANO_PLAYER_{timestamp}` (cuando no hay gestión)

## 📈 Métricas Cognitivas

### Campos Comunes (Todos los Juegos):
- **timestamp**: ISO 8601 timestamp del evento
- **session_id**: ID único de la sesión
- **game_type**: Tipo de juego ("piano_simon", "ping_pong", "two_lanes")
- **level**: Nivel de dificultad del juego
- **response_time_ms**: Tiempo de respuesta en millisegundos
- **accuracy**: Precisión del 0.0 a 1.0
- **is_correct**: Booleano si la respuesta fue correcta

### Análisis Disponible:
- ✅ **Piano Simon**: Memoria auditiva y secuencial
- 🔄 **Ping Pong**: Tiempo de reacción y coordinación
- 🔄 **Two Lanes**: Toma de decisiones bajo presión

## 🛠️ Herramientas de Análisis

### SessionManager
```python
from core.cognitive.session_manager import SessionManager

# Listar por juego específico
sessions = SessionManager().list_session_files("piano_simon")

# Estadísticas generales
stats = SessionManager().get_summary_stats()
```

### CognitiveLogger
```python
from core.cognitive.cognitive_logger import CognitiveLogger

# Logger específico por juego
logger = CognitiveLogger("piano_simon", "PACIENTE_001")
logger.log_event({
    'level': 5,
    'response_time_ms': 1200,
    'accuracy': 0.8,
    'is_correct': True,
    'melody_name': 'Twinkle Twinkle'
})
```

## 📁 Migración de Datos

### Estructura Anterior → Nueva
```bash
# Antes (mezclado)
data/cognitive/
├── PACIENTE1_piano_simon_20250129.csv
├── PACIENTE1_ping_pong_20250129.csv
└── patients.json

# Después (organizado)
data/cognitive/
├── piano_simon/
│   ├── sessions/PACIENTE1_piano_simon_20250129.csv
│   └── patients.json
└── ping_pong/
    ├── sessions/PACIENTE1_ping_pong_20250129.csv
    └── patients.json
```

## 🔄 Próximas Actualizaciones

### Version 2.0 (Planeado):
- [ ] Sistema de pacientes compartido global
- [ ] Análisis comparativo entre juegos
- [ ] Exportación a formatos científicos (BIDS, EDF)
- [ ] Dashboard de progreso temporal
- [ ] Alertas de rendimiento cognitivo

---

**Nota:** Mantener este archivo actualizado cada vez que se modifique la estructura de datos o se añadan nuevos juegos cognitivos. 