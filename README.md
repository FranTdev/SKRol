# El Haz - Plataforma de Rol de Stephen King (SK Rol)

Este proyecto es una aplicación web integral diseñada para gestionar partidas de rol ambientadas en el vasto multiverso de Stephen King (La Torre Oscura, El Resplandor, It, etc.). 

El objetivo principal fue crear una herramienta que no solo sirva como hoja de personaje digital, sino que automatice mecánicas complejas como la generación de habilidades psíquicas ("El Resplandor") y la gestión de estados físicos y académicos de los personajes, permitiendo al Director de Juego centrarse en la narrativa.

## 🌌 Características Principales

- **Gestión de Mundos (Campañas)**: Sistema centralizado para que el Director administre múltiples campañas simultáneas, controlando participantes y reglas específicas para cada "nivel de la Torre".
- **The Touch Machine (Máquina del Toque)**: Un algoritmo procedimental que genera habilidades únicas basadas en probabilidades y niveles de poder ("El Resplandor"), asignando rangos (S, A, B, C, D) e impactos narrativos automáticamente.
- **Hojas de Personaje Vivas**: 
  - Gestión en tiempo real de inventario y equipamiento.
  - Sistema de estados (Vivo, Muerto, Trascendido).
  - Rastreo visual de condiciones (Heridas, Locura, etc.).
- **Banco de Objetos Global**: Una base de datos de ítems que pueden ser importados a cualquier campaña, facilitando la consistencia entre partidas.
- **Interfaz Inmersiva**: Diseño UI moderno con estética "Glassmorphism" y tipografías temáticas para mantener la atmósfera de misterio.

## 🛠️ Stack Tecnológico

Este proyecto demuestra capacidades Full Stack utilizando tecnologías modernas y ligeras:

- **Backend**: Python con **FastAPI**. Arquitectura RESTful rápida y eficiente.
- **Base de Datos**: **Supabase** (PostgreSQL) con Row Level Security (RLS) para la gestión segura de datos.
- **Frontend**: **Vanilla JavaScript**, HTML5 y CSS3 puro. Sin frameworks pesados en el cliente para garantizar un control total sobre el DOM y el rendimiento.
- **Testing**: Scripts automatizados con `requests` y `unittest` para validar endpoints y lógica de negocio.

## 🚀 Instalación y Despliegue

### Requisitos Previos

- Python 3.9 o superior
- Cuenta en Supabase (para la base de datos)

### Pasos

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/sk-rol.git
   cd sk-rol
   ```

2. **Instalar Dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Variables de Entorno**:
   Crea un archivo `.env` en la carpeta `backend/` con tus credenciales:
   ```ini
   SUPABASE_URL=tu_url_de_proyecto
   SUPABASE_KEY=tu_clave_anonima
   ```
   *Nota: Asegúrate de ejecutar los scripts SQL ubicados en `backend/database/migrations` en tu consola SQL de Supabase para crear las tablas necesarias.*

### Ejecución Local

1. **Levantar el Servidor (Backend)**:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   La API estará escuchando en `http://127.0.0.1:8000`.

2. **Iniciar Cliente (Frontend)**:
   Abre el archivo `frontend/index.html` o `frontend/login.html` en tu navegador.
   Recomiendo usar una extensión como "Live Server" en VS Code para evitar problemas de CORS locales.

## 📂 Estructura del Proyecto

```
SKRol/
├── backend/            # Lógica del servidor y API
│   ├── app/            # Routers, Modelos y Servicios
│   └── database/       # Migraciones y esquemas SQL
├── frontend/           # Cliente Web
│   ├── css/            # Estilos y temas visuales
│   ├── js/             # Lógica de cliente (SPA ligera)
│   └── *.html          # Vistas
├── scripts/            # Scripts de utilidad, testing y verificación
└── requirements.txt    # Dependencias de Python
```

## 🛡️ Licencia

Proyecto personal desarrollado con fines educativos y de portafolio.
Inspirado en la obra de Stephen King.
