# The Touch Machine - Stephen King RPG Platform

A comprehensive role-playing game management system inspired by the multiverse of Stephen King (The Dark Tower, The Shining, etc.). 
This platform is designed to facilitate the "Director's" (Game Master) work and enhance the players' experience through a digital interface for campaigns, character sheets, and automated mechanics.

## 🌌 Features

- **Campaign Management**: Create and manage multiple campaigns ("Worlds").
- **Dynamic Character Sheets**: Track stats, inventories, and conditions (Physical/Academic).
- **The Touch Machine**: Automate randomness for unique "Shining" abilities generated procedurally.
- **Item Pool**: Global database of items that can be imported into any campaign.
- **Real-time Mechanics**: Backend-validated actions and state management.

## 🛠️ Technology Stack

- **Backend**: Python (FastAPI)
- **Database**: Supabase (PostgreSQL + RLS)
- **Frontend**: Vanilla JS / HTML5 / CSS3 (Glassmorphism UI)
- **Testing**: Python requests & unittest

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- A Supabase project (for database connection)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/sk-rol.git
   cd sk-rol
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration**:
   Create a `.env` file in the `backend` directory containing your Supabase credentials:
   ```ini
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
   ```
   *Note: Ensure you have run the migration scripts located in `backend/database/migrations` on your Supabase instance.*

### Running the Application

1. **Start the Backend Server**:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

2. **Launch the Frontend**:
   Simply open `frontend/index.html` or `frontend/login.html` in your preferred web browser. 
   *(For best compatibility, use a local server like Live Server in VS Code).*

## 📂 Project Structure

```
SKRol/
├── backend/            # API Source Code
│   ├── app/            # Main application logic (Routers, Models, Services)
│   └── database/       # Migrations and Schema definitions
├── frontend/           # Client-side application
│   ├── css/            # Stylesheets
│   ├── js/             # Application Logic
│   └── *.html          # Views
├── scripts/            # Utility and testing scripts
└── requirements.txt    # Python dependencies
```

## 🛡️ License

This project is for educational and portfolio purposes.
