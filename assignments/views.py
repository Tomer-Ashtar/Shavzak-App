from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from datetime import date
from .models import Assignment, TaskQueue
from workers.models import Worker
from .counter_logic import check_multi_department_slot
import json


def calendar_view(request):
    """Main calendar view for creating and viewing assignments."""
    
    # Get selected date from query params or use today
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get all time slots
    time_slots = [choice[0] for choice in Assignment.TIME_SLOT_CHOICES]
    
    # Get all workers for selection
    all_workers = Worker.objects.all().order_by('title', 'name')
    
    # Get queue suggestions for each task type
    queue_suggestions = {}
    for task_type, _ in Assignment.TASK_TYPE_CHOICES:
        suggested_worker = TaskQueue.get_next_worker(task_type)
        if suggested_worker:
            queue_suggestions[task_type] = {
                'id': suggested_worker.id,
                'name': suggested_worker.name,
                'title': suggested_worker.get_title_display(),
            }
        else:
            queue_suggestions[task_type] = None
    
    # Get full queue for display
    task_queues = {}
    for task_type, _ in Assignment.TASK_TYPE_CHOICES:
        task_queues[task_type] = TaskQueue.get_queue_for_task(task_type)
    
    # Build guard duty schedule
    schedule_data = []
    for time_slot in time_slots:
        guard_workers = Assignment.objects.filter(
            date=selected_date,
            time_slot=time_slot,
            task_type='guard_duty'
        ).select_related('worker')
        
        required_workers = Assignment.get_required_workers_for_slot(time_slot)
        
        schedule_data.append({
            'time_slot': time_slot,
            'guard_workers': guard_workers,
            'required_workers': required_workers,
        })
    
    # Get full-day task assignments
    kitchen_workers = Assignment.objects.filter(
        date=selected_date,
        task_type='kitchen',
        time_slot__isnull=True
    ).select_related('worker')
    
    patrol_a_workers = Assignment.objects.filter(
        date=selected_date,
        task_type='patrol_a',
        time_slot__isnull=True
    ).select_related('worker')
    
    patrol_b_workers = Assignment.objects.filter(
        date=selected_date,
        task_type='patrol_b',
        time_slot__isnull=True
    ).select_related('worker')
    
    context = {
        'selected_date': selected_date,
        'schedule_data': schedule_data,
        'kitchen_workers': kitchen_workers,
        'patrol_a_workers': patrol_a_workers,
        'patrol_b_workers': patrol_b_workers,
        'all_workers': all_workers,
        'queue_suggestions': queue_suggestions,
        'queue_suggestions_json': json.dumps(queue_suggestions),
        'task_queues': task_queues,
        'today': date.today(),
    }
    
    return render(request, 'assignments/calendar.html', context)


def assign_worker(request):
    """Assign a worker to a task and update queue."""
    if request.method == 'POST':
        selected_date_str = request.POST.get('date')
        task_type = request.POST.get('task_type')
        time_slot = request.POST.get('time_slot', None) or None
        worker_id = request.POST.get('worker_id')
        is_commander = request.POST.get('is_commander') == 'on'
        
        try:
            selected_date = date.fromisoformat(selected_date_str)
            worker = Worker.objects.get(id=worker_id)
            
            # Create the assignment
            Assignment.objects.create(
                date=selected_date,
                time_slot=time_slot,
                task_type=task_type,
                worker=worker,
                is_commander=is_commander
            )
            
            # Check if this is a night shift (01:00-03:00 or 03:00-05:00)
            night_shift_slots = ['01:00-03:00', '03:00-05:00']
            is_night_shift = task_type == 'guard_duty' and time_slot in night_shift_slots
            
            if is_night_shift:
                worker.hard_chores_counter += 1
                worker.save()
            
            # Check for multi-department bonus (guard duty only)
            if task_type == 'guard_duty' and time_slot:
                has_diff_depts, worker_ids = check_multi_department_slot(selected_date, time_slot)
                
                if has_diff_depts:
                    # Increment outer_partner_counter for all workers with departments in this slot
                    for wid in worker_ids:
                        w = Worker.objects.get(id=wid)
                        w.outer_partner_counter += 1
                        w.save()
                    
                    if is_night_shift:
                        messages.success(request, f'{worker.name} שובץ למשמרת לילה עם שותפים ממחלקות שונות! מונים עודכנו.')
                    else:
                        messages.success(request, f'{worker.name} שובץ עם שותפים ממחלקות שונות! מונה שותף חיצוני עלה.')
                elif is_night_shift:
                    messages.success(request, f'{worker.name} שובץ למשמרת לילה! מונה משימות קשות עלה.')
                else:
                    messages.success(request, f'{worker.name} שובץ בהצלחה!')
            elif is_night_shift:
                messages.success(request, f'{worker.name} שובץ למשמרת לילה! מונה משימות קשות עלה.')
            else:
                messages.success(request, f'{worker.name} שובץ בהצלחה!')
            
            # Move worker to end of queue for this task type
            TaskQueue.move_to_end(worker, task_type)
            
        except (ValueError, Worker.DoesNotExist) as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect(f"{reverse('assignments:calendar')}?date={selected_date_str}")
    
    return redirect('assignments:calendar')


def remove_assignment(request, assignment_id):
    """Remove an assignment and move worker back to front of queue."""
    if request.method == 'POST':
        try:
            assignment = get_object_or_404(Assignment, id=assignment_id)
            date_param = assignment.date.isoformat()
            worker = assignment.worker
            task_type = assignment.task_type
            time_slot = assignment.time_slot
            
            # Check if this was a night shift
            night_shift_slots = ['01:00-03:00', '03:00-05:00']
            is_night_shift = task_type == 'guard_duty' and time_slot in night_shift_slots
            
            # For guard duty, check multi-department status BEFORE deletion
            had_different_depts_before = False
            workers_with_dept_before = []
            
            if task_type == 'guard_duty' and time_slot:
                had_different_depts_before, workers_with_dept_before = check_multi_department_slot(
                    assignment.date, time_slot
                )
            
            # Delete the assignment
            assignment.delete()
            
            # Check multi-department status AFTER deletion
            if task_type == 'guard_duty' and time_slot:
                has_different_depts_after, workers_with_dept_after = check_multi_department_slot(
                    assignment.date, time_slot
                )
                
                # If we had bonus before but not after, decrement remaining workers
                if had_different_depts_before and not has_different_depts_after:
                    for wid in workers_with_dept_after:
                        w = Worker.objects.get(id=wid)
                        w.outer_partner_counter = max(0, w.outer_partner_counter - 1)
                        w.save()
                
                # Decrement the removed worker if they had the bonus
                if worker and worker.id in workers_with_dept_before and had_different_depts_before:
                    worker.outer_partner_counter = max(0, worker.outer_partner_counter - 1)
                    worker.save()
            
            # Move worker back to front of queue for this task
            if worker:
                TaskQueue.move_to_front(worker, task_type)
                
                # Decrement hard chores counter if it was night shift
                if is_night_shift:
                    worker.hard_chores_counter = max(0, worker.hard_chores_counter - 1)
                    worker.save()
                    messages.success(request, f'{worker.name} הוסר ממשמרת לילה! מונים עודכנו.')
                else:
                    messages.success(request, f'{worker.name} הוסר והועבר לראש תור {task_type}!')
            else:
                messages.success(request, 'השיבוץ הוסר!')
            
            return redirect(f"{reverse('assignments:calendar')}?date={date_param}")
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('assignments:calendar')
