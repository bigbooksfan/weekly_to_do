import json
from functools import partial

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty

class MainScreen(Screen):
    pass

class EditTaskList(Screen):
    tasks_map = {}

    def RemoveTask(self, name, instance):
        new_data = json.loads("{ \"tasks\": []}")
        with open('tasks.json', 'r') as file:
            data = json.load(file)
            file.close()

        print(data)
        print(new_data)
        sz = len(data['tasks'])
        for i in range(sz):
            if data['tasks'][i]['name'] != name:
                new_data['tasks'].append(data['tasks'][i])
                
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
            self.tasks_map[edit_button] = task['name']
            new_task.add_widget(edit_button)
            
            delete_button = Button(
                    text='Delete', 
                    size=(50,50), 
                    size_hint=(None, None))
            new_task.add_widget(delete_button)
            self.tasks_map[delete_button] = task['name']
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
sm.add_widget(MainScreen(name='main_screen'))
sm.add_widget(EditTaskList(name='edit_task_list'))
sm.add_widget(AddTaskScreen(name='add_task_screen'))

sm.current = "main_screen"

class WTDApp(App):
    def build(self):
        return sm
    
if __name__ == "__main__":
    WTDApp().run()