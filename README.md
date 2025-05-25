# ClassPlaner

**ClassPlaner** is a Flask-based web application that helps schools and administrators automatically generate and manage weekly class timetables. It supports defining class groups, subjects, teachers (with working hours and preferences), rooms, and periods. Using a CP-SAT solver (Google OR-Tools), it produces conflict-free schedules that respect all hard constraints, and offers a drag-and-drop interface for manual adjustments. App can be accessed trough [link](https://classplanner-v1oj.onrender.com/dashboard)

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

* Python 3.9+
* Flask & Flask-WTF, Flask-Login, Flask-Migrate, Flask-Babel
* SQLAlchemy for ORM with SQLite
* Google OR-Tools CP-SAT solver
* Bootstrap 5 for styling
* HTML5 Drag & Drop + Fetch API for interactive timetable

## Installation

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/ClassPlaner.git
   cd ClassPlaner
   ```

2. **Create & activate a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
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

* All settings live in `app/__init__.py`. Customize:

  * `SECRET_KEY`
  * `SQLALCHEMY_DATABASE_URI`
  * `BABEL_DEFAULT_LOCALE`

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

---

*Happy scheduling!*
