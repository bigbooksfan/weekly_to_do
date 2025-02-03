import json
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class DummyScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_screen)
    
    def switch_screen(self, dt):
        #sm.transition = FadeTransition()
        sm.current = "main_screen"

class MainScreen(Screen):
    def LoadTasks(self):
        tasks = self.ids.tasks
        tasks.clear_widgets()
        finished_tasks_list = self.ids.finished_tasks
        finished_tasks_list.clear_widgets()

        with open('tasks.json', 'r') as file:
            data = json.load(file)
        
        week_tasks = data['tasks']
        done_tasks = data['this_week_tasks']

        tasks_list = []
        task_names = []
        finished_tasks = []

        for task_to_do in week_tasks:
            new_task = {
                "name": task_to_do['name'],
                "duration": task_to_do['duration'],
                "times_to_do": task_to_do['times_in_week'],
                "times_done": "0"
            }
            task_names.append(task_to_do['name'])
            for task_done in done_tasks:
                if task_done['name'] == task_to_do['name']:
                    new_task['times_done'] = task_done['done']
            if new_task['times_to_do'] == new_task['times_done']:
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

        print(tasks_list)
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
            tasks.add_widget(new_task)

        for task in finished_tasks:
            new_task = GridLayout(cols=4, height=50, size_hint=(1,None))
            new_task.add_widget(Label(text=task['name']))
            
            desc = 'Finished! Done {} times'.format(task['times_done'])
            new_task.add_widget(Label(text=desc))
            
            finished_tasks_list.add_widget(new_task)


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
        
        new_data.append(data['this_week_tasks'])
                
        with open('tasks.json', 'w') as file:
            json.dump(new_data, file, indent=4)
            file.close()
        
        self.LoadTasks()

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
            
            delete_button = Button(
                    text='Delete', 
                    size=(50,50), 
                    size_hint=(None, None))
            new_task.add_widget(delete_button)
            delete_button.bind(on_release=partial(self.RemoveTask, task['name']))
            tasks.add_widget(new_task)

        file.close()

class AddTaskScreen(Screen):
    task_name = ObjectProperty(None)
    task_duration = ObjectProperty(None)
    task_times = ObjectProperty(None)

    def add_new_task(self):
        new_task = {
            "name": self.task_name.text,
            "duration": self.task_duration.text,
            "times_in_week": self.task_times.text
        }
        # TODO: add check if name not unique
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()
        
        data['tasks'].append(new_task)
        with open('tasks.json', 'w') as file:
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

sm.current = "dummy_screen"

class WTDApp(App):
    def build(self):
        return sm
    
if __name__ == "__main__":
    WTDApp().run()