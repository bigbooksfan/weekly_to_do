import json
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition, SlideTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.clock import Clock

task_name_to_edit = ""
task_name_to_start = ""

class DummyScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_screen)
    
    def switch_screen(self, dt):
        sm.transition = FadeTransition()
        sm.current = "main_screen"
        sm.transition = SlideTransition()

class MainScreen(Screen):
    def LoadTasks(self):
        tasks = self.ids.tasks
        tasks.clear_widgets()
        finished_tasks_list = self.ids.finished_tasks
        finished_tasks_list.clear_widgets()

        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()
        with open('this_week.json', 'r') as file2:
            weekly_data = json.load(file2)
            file2.close()

        week_tasks = data['tasks']
        done_tasks = weekly_data['this_week_tasks']

        tasks_list = []
        task_names = []
        finished_tasks = []

        for task_to_do in week_tasks:
            new_task = {
                "name": task_to_do['name'],
                "duration": task_to_do['duration'],
                "times_to_do": task_to_do['times_in_week'],
                "times_done": 0
            }
            task_names.append(task_to_do['name'])
            for task_done in done_tasks:
                if task_done['name'] == task_to_do['name']:
                    new_task['times_done'] = task_done['done']
            if new_task['times_to_do'] <= new_task['times_done']:
                finished_tasks.append({
                    "name": task_to_do['name'],
                    "times_done": 
                        '{}/{}'.format(
                            new_task['times_done'],
                            task_to_do['times_in_week']
                        )
                })
            else:
                tasks_list.append(new_task)
        
        # add tasks that was done this week 
        # and then deleted from weekly list
        for task_done in done_tasks:
            if task_names.count(task_done['name']) == 0:
                new_task = {
                    "name": task_done['name'],
                    "times_done": '{}/0'.format(task_done['done'])
                }
                finished_tasks.append(new_task)

        for task in tasks_list:
            new_task = GridLayout(cols=4, height=50, size_hint=(1,None))
            new_task.add_widget(Label(text=task['name']))
            
            desc = '{} minutes, done {}/{} times'.format(task['duration'], task['times_done'], task['times_to_do'])
            new_task.add_widget(Label(text=desc))
            
            start_button = Button(
                    text='Start', 
                    size=(50,50), 
                    size_hint=(None, None))
            new_task.add_widget(start_button)
            #start_button.bind(on_release=partial(self.RemoveTask, task['name']))
            start_button.bind(on_release=partial(self.StartTimer, task['name']))
            tasks.add_widget(new_task)

        for task in finished_tasks:
            new_task = GridLayout(cols=4, height=50, size_hint=(1,None))
            new_task.add_widget(Label(text=task['name']))
            
            desc = 'Finished! Done {} times'.format(task['times_done'])
            new_task.add_widget(Label(text=desc))
            
            finished_tasks_list.add_widget(new_task)

    def StartTimer(self, name, instance):
        global task_name_to_start
        task_name_to_start = name
        sm.transition.direction='up'
        sm.current = "timer_screen"
        
class EditTaskList(Screen):
    def RemoveTask(self, name, instance):
        new_data = json.loads("{ \"tasks\": []}")
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()

        sz = len(data['tasks'])
        for i in range(sz):
            if data['tasks'][i]['name'] != name:
                new_data['tasks'].append(data['tasks'][i])
        
        #new_data['this_week_tasks'] = data['this_week_tasks']
                
        with open('tasks.json', 'w') as file:
            json.dump(new_data, file, indent=4)
            file.close()
        
        self.LoadTasks()
    
    def EditTask(self, name, instance):
        global task_name_to_edit
        task_name_to_edit = name
        sm.transition.direction='left'
        sm.current = "edit_task_screen"

    def LoadTasks(self):
        tasks = self.ids.tasks_list
        tasks.clear_widgets()
        with open('tasks.json', 'r') as file:
            data = json.load(file)

        for task in data['tasks']:
            new_task = GridLayout(cols=4, height=50, size_hint=(1,None))
            new_task.add_widget(Label(text=task['name']))
            
            desc = '{} minutes, {} times'.format(task['duration'], task['times_in_week'])
            new_task.add_widget(Label(text=desc))
            
            edit_button = Button(
                    text='Edit', 
                    size=(50,50), 
                    size_hint=(None, None))
            new_task.add_widget(edit_button)
            edit_button.bind(on_release=partial(self.EditTask, task['name']))
            
            delete_button = Button(
                    text='Delete', 
                    size=(50,50), 
                    size_hint=(None, None))
            new_task.add_widget(delete_button)
            delete_button.bind(on_release=partial(self.RemoveTask, task['name']))

            tasks.add_widget(new_task)

        file.close()

class AddTaskScreen(Screen):
    def ClearForm(self):
        self.ids.task_name.text = ""
        self.ids.task_duration.text = ""
        self.ids.task_times.text = ""

    def add_new_task(self):
        new_task = {
            "name": self.ids.task_name.text,
            "duration": self.ids.task_duration.text,
            "times_in_week": self.ids.task_times.text
        }
        # TODO: add check if name not unique
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()
        
        data['tasks'].append(new_task)
        with open('tasks.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()

class EditTaskScreen(Screen):
    def FillForm(self):
        global task_name_to_edit
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()
        for task in data['tasks']:
            if task['name'] == task_name_to_edit:
                self.ids.task_name.text = task['name']
                self.ids.task_duration.text = task['duration']
                self.ids.task_times.text = task['times_in_week']
                break
    
    def edit_task(self):
        global task_name_to_edit
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()
        
        new_data = json.loads("{ \"tasks\": []}")
        for task in data['tasks']:
            if task['name'] == task_name_to_edit:
                new_task = {
                    "name": self.ids.task_name.text,
                    "duration": self.ids.task_duration.text,
                    "times_in_week": self.ids.task_times.text
                    }
                new_data['tasks'].append(new_task)
            else:
                new_data['tasks'].append(task)
        
        with open('tasks.json', 'w') as file:
            json.dump(new_data, file, indent=4)
            file.close()

class TimerScreen(Screen):
    mins = 1
    secs = 0
    timer = None

    def update_clock(screen, dt):
        TimerScreen.secs -= 1
        if TimerScreen.secs == -1:
            TimerScreen.mins -= 1
            TimerScreen.secs = 59
        if TimerScreen.mins < 0:
            TimerScreen.timer.cancel()
            screen.ids.countdown_timer.text = 'Done'
            return
        timer = '{}:{}'.format(TimerScreen.mins, TimerScreen.secs)
        screen.ids.countdown_timer.text = timer
    
    def cancel_timer(self):
        TimerScreen.timer.cancel()
    
    def start_timer(self):
        TimerScreen.secs = 0
        global task_name_to_start

        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()

        for task in data['tasks']:
            if task['name'] == task_name_to_start:
                TimerScreen.mins = int(task['duration'])
                break

        self.ids.task_name.text = task_name_to_start
        self.ids.countdown_timer.text = '{}:00'.format(TimerScreen.mins)
        TimerScreen.timer = Clock.schedule_interval(partial(self.update_clock), 1)            

    def finish_task(self):
        with open('this_week.json', 'r') as file:
            data = json.load(file)
            file.close()

        flag = False
        for task in data['this_week_tasks']:
            if task['name'] == task_name_to_start:
                task['done'] += 1
                flag = True
                break
        
        if flag is False:
            new_task = {
                "name": task_name_to_start,
                "done": 1
            }
            data['this_week_tasks'].append(new_task)
        
        with open('this_week.json', 'w') as file:
            json.dump(data, file, indent=4)
            file.close()


class WindowManager(ScreenManager):
    pass

kv = Builder.load_file("wtd.kv")

sm = ScreenManager()
sm.add_widget(DummyScreen(name='dummy_screen'))
sm.add_widget(MainScreen(name='main_screen'))
sm.add_widget(EditTaskList(name='edit_task_list'))
sm.add_widget(AddTaskScreen(name='add_task_screen'))
sm.add_widget(EditTaskScreen(name='edit_task_screen'))
sm.add_widget(TimerScreen(name='timer_screen'))

sm.current = "dummy_screen"

class WTDApp(App):
    def build(self):
        return sm
    
if __name__ == "__main__":
    WTDApp().run()