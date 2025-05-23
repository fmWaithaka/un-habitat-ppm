# un-habitat-ppm

A web application designed to streamline the management and visualization of UN-Habitat project data. It offers robust CRUD operations, a well-defined JSON API, an interactive dashboard for data insights, and integrates Gemini AI for advanced analysis or features.

---

## Table of Contents
- Features  
- Technologies Used  
- Installation  
  - Backend Setup  
  - Frontend Setup  
- API Endpoints  
- Dashboard  
- AI Integration  
- Video Demo  
- Contributing  
- License  

---

## Features
- **Project Management**: Full CRUD (Create, Read, Update, Delete) operations for managing project data.  
- **JSON API**: A clean and documented API for interacting with project data programmatically.  
- **Interactive Dashboard**: Visualize key project metrics and data distributions through various charts (Bar Charts, Pie Chart).  
- **Geographic Data Visualization**: See project distribution by individual countries and combined regions/global data.  
- **Organizational and Thematic Insights**: Analyze project value distribution by Lead Organizational Unit and project Themes.  
- **Gemini AI Integration**: Leverage Gemini AI capabilities (e.g., for insights, reporting, or data analysis - depending on implementation).  
- **Responsive Design**: A user interface that adapts to various screen sizes.  

---

## Technologies Used

- **Backend**:
  - Django   

- **Frontend**: 
  - Vue.js (using Composition API with `<script setup>`)  
  - ECharts (for data visualization)  
- **Database**: PostgreSQL 

---

## Installation

Follow these steps to set up the project locally.

---

### Backend Setup

1. Clone the repository:  
   ```bash
   git clone https://github.com/fmWaithaka/un-habitat-ppm.git
   cd un-habitat-ppm
    ````

2. Navigate to the backend directory:

   ```bash
   cd backend 
   ```

3. Create and activate a virtual environment (recommended):

   **Using venv:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

   **Using conda:**

   ```bash
   conda create -n unhabitat-ppm python=3.9  # Use your desired Python version
   conda activate unhabitat-ppm
   ```

4. Install backend dependencies:

   ```bash
   pip install -r requirements.txt  
   ```

5. Configure environment variables:

   * Create a `.env` file in the backend directory.
   * Add necessary variables (e.g., database connection string, API keys - especially for Gemini AI).

     ```env
      # backend/.env
      DEBUG=True
      SECRET_KEY = "django_key"
      DATABASE_NAME='db_name'
      DATABASE_USER='db_user'
      DATABASE_PASSWORD='db_strong_password' 
      DATABASE_HOST='localhost' 
      DATABASE_PORT='5432' 
      DJANGO_SETTINGS_MODULE='project_portfolio.settings' 
      VITE_API_BASE_URL=http://127.0.0.1:8000/api/
     ```
     (Replace the placeholder with the actual valuess

6. Run database migrations (if applicable):

   ```bash
   python manage.py migrate
   ```

7. Start the backend server:

   ```bash
    python manage.py runserver
   ```

---

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd ../frontend  # Adjust path based on your structure
   ```

2. Install frontend dependencies:

   ```bash
   npm install  # Or yarn install
   ```

3. Configure environment variables:

   * Create a `.env` file in the frontend directory.
   * Add necessary variables (e.g., backend API URL).

     ```env
     VITE_API_BASE_URL=http://localhost:5000  # Or your backend URL
     ```

4. Start the frontend development server:

   ```bash
   npm run dev  # Or yarn dev
   ```

   The application should now be running and accessible in your web browser, typically at [http://localhost:5173](http://localhost:5173) (or the port specified by your frontend framework).

---

## API Endpoints
* `GET /api/projects`: Get all projects.

* `GET /api/projects/<id>`: Get a specific project by ID.

* `POST /api/projects`: Create a new project.

* `PUT /api/projects/<id>`: Update a project.

* `DELETE /api/projects/<id>`: Delete a project.

* `GET /api/dashboard/kpis`: Get key performance indicators.

* `GET /api/dashboard/value_by_country`: Get project value by country (split into single and combined).

* `GET /api/dashboard/value_by_lead_org`: Get project value by lead organizational unit.

* `GET /api/dashboard/value_by_theme`: Get project value by theme.

* `GET /api/ai/insights`: Get AI-generated insights (if implemented).

> (Note: Adjust endpoints based on your actual backend implementation.)

---

## Dashboard

The dashboard provides a visual summary of the project data, including:

* Overall KPIs (Total Projects, Total PAG Value, etc.)
* Geographic distribution (Top Countries by Value, Combined/Regional/Global distribution)
* Distribution by Lead Organizational Unit
* Distribution by Theme

The charts are arranged neatly in a grid layout for easy viewing.

---

## Video Demo

Watch a short video demonstration of the application:
🎥 [Watch Video Demo](https://drive.google.com/file/d/15J9APx8vlbN9QQQJuThi47i69e1IJ0mw/view)

---

## GitHub Repository

🔗 [https://github.com/fmWaithaka/un-habitat-ppm.git](https://github.com/fmWaithaka/un-habitat-ppm.git)
