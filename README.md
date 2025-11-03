# Workers Jobs Manager

A Django-based fullstack application for managing workers and their daily chores schedule.

## Overview

This app manages workers and their daily task assignments with an intelligent queue-based suggestion system.

### Main Features

1. **Workers Management** - Add, edit, delete workers
2. **Calendar (History)** - View past days' schedules and assignments  

## Technical Stack

- **Backend**: Django 4.2.25
- **Frontend**: Django Templates + Bootstrap 5 RTL
- **Database**: SQLite
- **Language**: Hebrew (עברית)
- **Layout**: Right-to-Left (RTL)

## Project Structure

```
Shavzak-App/
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
├── workers_jobs_manager/      # Main Django project
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── workers/                   # Workers CRUD app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   └── migrations/
├── assignments/               # Assignments & queue logic app
│   ├── models.py (Assignment, TaskQueue)
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   ├── test_task_queue.py
│   ├── test_night_shift.py
│   ├── migrations/
│   └── management/
│       └── commands/
│           └── initialize_queues.py
├── templates/                 # Django templates
│   ├── base.html
│   ├── workers/
│   │   ├── list.html
│   │   └── worker_form.html
│   └── assignments/
│       └── calendar.html
├── static/                    # Static files
│   └── css/
│       └── styles.css
├── venv/                      # Virtual environment
└── db.sqlite3                 # SQLite database
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start Development Server

```bash
python manage.py runserver
```

The application will be available at: http://127.0.0.1:8000/

## Development Status

✅ **Step 1 - Project Setup** - Complete
- Django project created
- Apps configured (workers, assignments)
- Base templates and navigation
- Three placeholder pages

✅ **Step 2 - Workers CRUD** - Complete
- Worker model with all fields (name, title, counters)
- Full CRUD operations (Create, Read, Update, Delete)
- Workers list page with table and actions
- Add/Edit worker forms with Bootstrap styling
- Delete confirmation modals
- Admin interface configured
- 8 unit tests (all passing)

✅ **Step 3 - Assignments & Calendar** - Complete
- Assignment model with date, time_slot, task_type, worker, is_commander
- 12 time slots covering 24 hours (07:00-09:00 through 05:00-07:00)
- Guard Duty: Time-slotted task (1 worker for daytime, 2 for nighttime)
- Full-day tasks: Kitchen (2 workers), Patrol A (1 commander + 5), Patrol B (1 commander + 5)
- Calendar view with date picker
- Left side: Time slot table showing guard duty assignments
- Right side: Cards showing Kitchen, Patrol A, and Patrol B workers
- Commander designation for patrol groups
- Admin interface configured
- 9 unit tests (all passing)

✅ **Step 4 - Queue System** - Complete
- QueueManager class for worker suggestions
- Queue ordering per task type based on counters
- get_next_suggestion() - suggests worker with lowest counter
- accept_suggestion() - creates assignment and increments counters
- manual_assign() - assign specific worker
- Excludes already assigned workers
- Guard duty excludes workers from ALL time slots on same date
- Different counter logic per task type (hard_chores for kitchen, outer_partner for patrols)
- 9 unit tests (all passing)

✅ **Step 5 - Create Assignment Page** - Complete
- Assignment interface at /assign/ for today's schedule
- Session-based assignments (no DB writes until Submit)
- Left side: Guard duty time slots with suggestions
- Right side: Full-day tasks (Kitchen, Patrol A, Patrol B) with suggestions
- Worker information panel showing all workers with their counters
- Accept buttons for suggested workers
- Remove buttons for pending (session) assignments
- Submit All button to commit all assignments to database
- Clear All button to reset pending assignments
- Color-coded cards and badges (pending vs committed)
- Commander suggestions for patrol groups
- Real-time availability tracking

✅ **Step 6 - Queue System Implementation** - Complete
- TaskQueue model with worker rotation per task type
- Immediate queue updates on assignment
- Queue position tracking (0 = first in line)
- move_to_end() - Automatic queue rotation
- get_next_worker() - Get suggestion from queue head
- initialize_queues management command
- Auto-initialize queues for new workers
- UI shows suggested worker (pre-selected)
- View Queue Order button in modal
- 7 TaskQueue unit tests (all passing)

✅ **Step 7 - Interface Simplification & Night Shift** - Complete
- Calendar is now the main/home page
- Removed separate assignment page
- Removed session-based assignments
- Direct assignment with queue rotation
- Simple click-to-assign interface
- Modal-based worker selection
- Immediate database persistence
- Night shift bonus (01:00-05:00): +1 to hard_chores_counter
- Revert functionality: Remove assignment → worker to front of queue
- Night shift counter decrement on removal
- Visual highlighting for night shift slots
- All 32 tests passing (including 6 night shift tests)

✅ **Step 8 - Hebrew RTL Interface** - Complete
- Full RTL (Right-to-Left) layout using Bootstrap RTL
- Complete Hebrew translation of all UI elements
- Hebrew model choice labels (מפקד/חייל)
- Hebrew task type names (שמירה, מטבח, סיור)
- Timezone: Asia/Jerusalem
- Language: Hebrew (he)
- All tests updated and passing with Hebrew text

## Navigation

- **Schedule (Calendar)**: http://127.0.0.1:8000/calendar/ or http://127.0.0.1:8000/
- **Workers Management**: http://127.0.0.1:8000/workers/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## How to Use

### First-Time Setup

After creating workers, initialize the task queues:
```bash
python manage.py initialize_queues
```

This creates queue positions for all workers across all task types.

### Managing Workers

1. Go to http://127.0.0.1:8000/workers/
2. Click "Add New Worker" to create workers
3. Fill in name and title (Commander or Soldier)
4. View worker counters in the list
5. Queue entries are automatically created for new workers

### Creating Assignments

1. Go to http://127.0.0.1:8000/calendar/ (or just http://127.0.0.1:8000/)
2. Select a date using the date picker
3. Click "Add Worker" button in any time slot or task
4. Modal opens showing:
   - **💡 Suggested worker** (pre-selected from queue head)
   - **View Queue Order** - Click to see full rotation order
   - Dropdown to select any worker (not restricted to suggestion)
5. For patrol groups, check "Assign as Commander" if needed
6. Click "Assign Worker"
7. Worker is assigned AND moved to end of queue for that task

### Queue System

- **Each task type has its own queue**: guard_duty, kitchen, patrol_a, patrol_b
- **Worker at position 0** = suggested first (pre-selected in modal)
- **After assignment** → worker moves to end of queue (last position)
- **You can pick anyone** from the dropdown, not just the suggestion
- **Anyone picked** → still moves to end of queue
- **Queue persists** across sessions (stored in database)

### Removing Assignments

- Click the X button next to any assigned worker to remove them
- Confirmation dialog will appear before removal
- **Worker moves back to front of queue** (position 0) - gets priority next time!

## Features

### Task Structure
- **Guard Duty Schedule**: 12 time slots covering 24 hours
  - Daytime (07:00-17:00): 1 worker per slot
  - Nighttime (17:00-07:00): 2 workers per slot
- **Full-Day Tasks**: 
  - Kitchen: 2 workers
  - Patrol A: 6 workers (1 commander + 5 soldiers)
  - Patrol B: 6 workers (1 commander + 5 soldiers)

### Queue/Rotation System
- **Automatic worker rotation** - Each task type maintains its own queue
- **Smart suggestions** - Worker at queue head is pre-selected in modal
- **Fair distribution** - Assigned workers automatically move to end of queue
- **View queue order** - Click button in modal to see full rotation
- **Flexible selection** - Can pick any worker, not just suggested
- **Persistent queues** - Queue order stored in database
- **Revert to front** - Removed workers move back to position 0 (front of queue)

### Night Shift Bonus
- **Guard duty 01:00-03:00 and 03:00-05:00** - Special night shifts
- **Assignment** → Hard chores counter +1
- **Removal** → Hard chores counter -1
- **Visual feedback** - Special message when assigning/removing night shift workers
- **Protection** - Counter never goes below 0

### User Interface
- **Simple click-to-assign** - Click "Add Worker" button to assign
- **Modal selection** - Clean modal with worker dropdown
- **Visual feedback** - Badges show assigned workers with remove buttons
- **Worker information** - See counters (HC, OP) in dropdown
- **Date navigation** - Date picker to view/edit any day
- **Responsive design** - Bootstrap 5 styling
