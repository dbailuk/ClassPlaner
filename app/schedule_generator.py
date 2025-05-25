from ortools.sat.python import cp_model
from datetime import datetime
from app import db
from app.models import (
    ScheduleAssignment, Teacher, ClassGroup, Room, Period
)


def generate_schedule(user_id):
    # 1) Load assignments and metadata
    assigns = ScheduleAssignment.query.filter_by(user_id=user_id).all()
    # Load teacher objects for preferences
    teacher_objs = {t.id: t for t in Teacher.query.filter_by(user_id=user_id).all()}

    # Build teacher preference lookups (days 1-5, period IDs)
    days = list(range(1, 6))
    all_periods = Period.query.filter_by(user_id=user_id).all()
    period_ids = [p.id for p in all_periods]

    teacher_pref_days = {}
    teacher_pref_periods = {}
    for t_id, t in teacher_objs.items():
        if t.preferred_days:
            teacher_pref_days[t_id] = list(map(int, t.preferred_days.split(',')))
        else:
            teacher_pref_days[t_id] = days
        if t.preferred_periods:
            teacher_pref_periods[t_id] = list(map(int, t.preferred_periods.split(',')))
        else:
            teacher_pref_periods[t_id] = period_ids

    # Build assignment dicts
    assignments = []
    for a in assigns:
        if a.class_group.allowed_periods:
            group_allowed = list(map(int, a.class_group.allowed_periods.split(',')))
        else:
            group_allowed = period_ids.copy()
        assignments.append({
            'id': a.id,
            'group': a.class_group_id,
            'subject': a.subject_id,
            'teacher': a.teacher_id,
            'hours': a.hours_per_week,
            'room': a.room_id or a.class_group.default_room_id,
            'group_allowed': group_allowed
        })

    # 2) Build CP-SAT model
    model = cp_model.CpModel()
    x = {}  # decision var x[(assignment_id, day, period)]

    # Create variables with both class-group and teacher hard constraints
    for a in assignments:
        t_id = a['teacher']
        # determine allowed days and periods per teacher preferences
        if t_id and t_id in teacher_pref_days:
            allowed_days = teacher_pref_days[t_id]
        else:
            allowed_days = days
        if t_id and t_id in teacher_pref_periods:
            allowed_periods = teacher_pref_periods[t_id]
        else:
            allowed_periods = period_ids
        # intersect with group_allowed
        allowed_periods = [p for p in a['group_allowed'] if p in allowed_periods]

        for d in allowed_days:
            for p in allowed_periods:
                x[(a['id'], d, p)] = model.NewBoolVar(f"x_{a['id']}_{d}_{p}")

    # 2.1 Coverage: each assignment appears exactly its required hours per week
    for a in assignments:
        vars_all = [x[(a['id'], d, p)]
                    for (aid, d, p) in x if aid == a['id']]
        model.Add(sum(vars_all) == a['hours'])

    # 2.2 No same class more than once per day
    for a in assignments:
        for d in days:
            vars_day = [x[(a['id'], d, p)] for p in period_ids if (a['id'], d, p) in x]
            if vars_day:
                model.Add(sum(vars_day) <= 1)

    # 2.3 No double-booking: group, teacher, room per slot
    for d in days:
        for p in period_ids:
            # class group
            for g in set(a['group'] for a in assignments):
                vars_g = [x[(a['id'], d, p)] for a in assignments if a['group']==g and (a['id'], d, p) in x]
                if vars_g:
                    model.Add(sum(vars_g) <= 1)
            # teacher
            for t_id in teacher_objs.keys():
                vars_t = [x[(a['id'], d, p)] for a in assignments if a['teacher']==t_id and (a['id'], d, p) in x]
                if vars_t:
                    model.Add(sum(vars_t) <= 1)
            # room
            for r in set(a['room'] for a in assignments):
                vars_r = [x[(a['id'], d, p)] for a in assignments if a['room']==r and (a['id'], d, p) in x]
                if vars_r:
                    model.Add(sum(vars_r) <= 1)

    # 2.4 Teacher max weekly hours
    for t_id, teacher in teacher_objs.items():
        vars_t = [x[(a['id'], d, p)]
                  for a in assignments
                  for (aid, d, p) in x if aid == a['id'] and a['teacher']==t_id]
        if vars_t:
            model.Add(sum(vars_t) <= teacher.week_hours)

    # 3) Solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return False, []

    # 4) Extract schedule
    schedule = []
    for (aid, d, p), var in x.items():
        if solver.Value(var) == 1:
            # find assignment a
            a = next(a for a in assignments if a['id']==aid)
            schedule.append({
                'assignment_id': aid,
                'group_id': a['group'],
                'subject_id': a['subject'],
                'teacher_id': a['teacher'],
                'room_id': a['room'],
                'period_id': p,
                'weekday': d
            })
    return True, schedule
