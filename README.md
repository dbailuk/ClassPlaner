# ClassPlaner

**ClassPlaner** is a Flask-based web application that helps schools and administrators automatically generate and manage weekly class timetables. It supports defining class groups, subjects, teachers (with working hours and preferences), rooms, and periods. Using a CP-SAT solver (Google OR-Tools), it produces conflict-free schedules that respect all hard constraints, and offers a drag-and-drop interface for manual adjustments. 
Link [classplaner](https://classplaner.online/)

## Features

* **Manage entities**: CRUD operations for Teachers, Subjects, Class Groups, Rooms, Periods.
* **Teacher preferences**: Optional preferred days & periods enforced as hard constraints.
* **Schedule assignments**: Define how many hours per week each class-group/subject needs, with optional room or teacher overrides.
* **Automatic schedule generation**: CP-SAT based solver builds a master timetable respecting:

  * Class-group once-per-day limits
  * Teacher and room no double-booking
  * Teacher max weekly hours
  * Class-group allowed periods
  * Teacher preferred days & periods
* **Interactive grid**: Dashboard displays the full week grid. Drag any lesson card to a new slot, auto-updating via AJAX.

## Technologies

* Language & Frameworks: Python 3.13, Flask, SQLAlchemy, Flask-Migrate, Flask-Babel
* Solver: Google OR-Tools CP‑SAT
* Frontend: Bootstrap 5, HTML5 Drag & Drop, Fetch API
* Containerization: Docker (multi‑stage builds, environment variables)
* Hosting: AWS EC2, Amazon RDS PostgreSQL
* CI/CD: GitHub Actions for automated build, test, push, and remote deployment

## Local development

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/ClassPlaner.git
   cd ClassPlaner
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate         # Windows
   pip install -r requirements.txt
   ```
3. **Copy .env.example to .env and customize:**

   ```bash
   SECRET_KEY=dev-secret-key
   DATABASE_URL=sqlite:///classplaner.db
   FLASK_ENV=development
   ```

4. **Initialize the database**

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the application**

   ```bash
   flask run
   ```

   Open [http://localhost:5000](http://localhost:5000) and register your first user.

## Configuration

* To change solver timeout or add soft/weighted preferences, see `app/schedule_generator.py`.

## Usage

1. **Define periods** in the desired order (e.g., Period 1 at 08:00–08:45, etc.).
2. **Add rooms** with optional capacities/types.
3. **Add subjects** and default hours per week.
4. **Add teachers**, their max weekly hours, and optional preferred days/periods.
5. **Create class groups** and optionally restrict allowed periods per group.
6. **Assign schedule slots**: for each class-group/subject, set hours per week, and optional teacher or room override.
7. **Generate schedule**: on the Dashboard, click "Generate Schedule" to auto-build the week.
8. **Manual adjustments**: drag any lesson block to a new day/period in the dashboard grid.

## Future Enhancements
1. Possibility to import schedule to pdf
2. Ukrainian language

---

*Happy scheduling!*
