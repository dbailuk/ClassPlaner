from ortools.sat.python import cp_model
from datetime import datetime
from app import db
from app.models import (
    ScheduleAssignment, Teacher, ClassGroup, Room, Period
)


def generate_schedule(user_id):
    # 1) Load data
    # Assignments
    assigns = ScheduleAssignment.query.filter_by(user_id=user_id).all()
    assignments = []
    for a in assigns:
        allowed = []
        if a.class_group.allowed_periods:
            allowed = [int(p) for p in a.class_group.allowed_periods.split(',')]
        else:
            # if no restriction, all periods
            allowed = [p.id for p in Period.query.filter_by(user_id=user_id)]
        assignments.append({
            'id': a.id,
            'group': a.class_group_id,
            'subject': a.subject_id,
            'teacher': a.teacher_id,
            'hours': a.hours_per_week,
            'room': a.room_id or a.class_group.default_room_id,
            'allowed_periods': allowed
        })

    # Period slots: days 1-5 and period ids
    periods = Period.query.filter_by(user_id=user_id).order_by(Period.start_time).all()
    period_ids = [p.id for p in periods]
    days = list(range(1,6))

    # Teachers
    t_rows = Teacher.query.filter_by(user_id=user_id).all()
    teachers = {t.id: t for t in t_rows}

    # 2) Build model
    model = cp_model.CpModel()
    x = {}  # x[a_id, d, p] boolean
    for a in assignments:
        for d in days:
            for p in period_ids:
                if p in a['allowed_periods']:
                    x[(a['id'], d, p)] = model.NewBoolVar(f"x_{a['id']}_{d}_{p}")

    # 2.1 coverage: each assignment gets exactly its hours
    for a in assignments:
        vars_ = [x[(a['id'], d, p)]
                 for d in days for p in period_ids
                 if (a['id'], d, p) in x]
        model.Add(sum(vars_) == a['hours'])

    # 2.2 no double booking: group/teacher/room
    for d in days:
        for p in period_ids:
            # group conflict
            for g in set(a['group'] for a in assignments):
                vars_g = [x[(a['id'], d, p)] for a in assignments
                          if a['group']==g and (a['id'],d,p) in x]
                if vars_g:
                    model.Add(sum(vars_g) <= 1)
            # teacher conflict
            for t in [a['teacher'] for a in assignments if a['teacher']]:
                vars_t = [x[(a['id'], d, p)] for a in assignments
                          if a['teacher']==t and (a['id'],d,p) in x]
                if vars_t:
                    model.Add(sum(vars_t) <= 1)
            # room conflict
            for r in set(a['room'] for a in assignments):
                vars_r = [x[(a['id'], d, p)] for a in assignments
                          if a['room']==r and (a['id'],d,p) in x]
                if vars_r:
                    model.Add(sum(vars_r) <= 1)

    # 2.3 teacher max hours
    for t_id, teacher in teachers.items():
        vars_t = [x[(a['id'], d, p)] for a in assignments
                  for d in days for p in period_ids
                  if a['teacher']==t_id and (a['id'],d,p) in x]
        if vars_t:
            model.Add(sum(vars_t) <= teacher.week_hours)

    # 2.4 optional: teacher preferences as soft constraints
    # (not implemented here)

    # 3) Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return False, []

    # 4) Extract schedule
    schedule = []
    for a in assignments:
        for d in days:
            for p in period_ids:
                if (a['id'], d, p) in x and solver.Value(x[(a['id'],d,p)])==1:
                    schedule.append({
                        'assignment_id': a['id'],
                        'group_id': a['group'],
                        'subject_id': a['subject'],
                        'teacher_id': a['teacher'],
                        'room_id': a['room'],
                        'period_id': p,
                        'weekday': d
                    })
    return True, schedule
