# %load quizz.py
try:
    from ipywidgets import widgets
except ImportError:
    widgets = None
from metakernel import Magic, option
import os
import getpass
import datetime

from collections import OrderedDict
from IPython.display import Markdown
import re
from functools import reduce
from random import shuffle

from datetime import datetime, timedelta
from metakernel.display import display, Javascript
import threading

try:
    from .c2qf import typeset_quizzes1, extract_quizzes
except:
    from quizzer.c2qf import typeset_quizzes1, extract_quizzes

           

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)
        
        
class QuizTimeOut(Exception):
    def __init__(self, body):
        DialogBox('Quiz Time Out', body)
        
class DialogBox():
    
    def __init__(self, title, body):
        
        self.js = """require(["base/js/dialog"],function(dialog) {{dialog.modal({{title: "{0}",body: "{1}",buttons: {{'OK': {{}}}} }});}});""".format(title, body)
                
        self.display()
        
    def display(self):
        display(Javascript(self.js))

        
class Activity(object):
    def __init__(self, datetime, alloted_time):
        self.questions = []
        self.filename = None
        self.results_filename = None
        self.instructors = []
        self.show_initial = True
        self.last_id = None
        self.start_datetime = datetime
        self.alloted_time = alloted_time
        
        self.quiz_container = []
        self.results = []
        self.overall_right_options = []
        self.mark = None
        self.submit_button = False
        self.timer = None

    def load(self, filename):
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        self.filename = filename
        
#         if self.quiz_filename is None:
#             self.quiz_filename = filename + ".quiz"
#         touch(self.quiz_filename)
        
        with open(self.filename, 'r') as f:
            filestr = f.read()
            filestr, num_quizzes = typeset_quizzes1(filestr, insert_missing_quiz_header=False)
            json_quiz, _, _ = extract_quizzes(filestr, 'python')            
#         with open(filename, "w") as fp:
#             fp.write(self.code)
        self.load_json(json_quiz)
                
        if self.results_filename is None:
            self.results_filename = filename + ".results"
            
        touch(self.results_filename)


    def load_json(self, json_text):
        # Allow use of widgets:
        if widgets is None:
            return

#         json = eval(json_text.strip())
        json = json_text

        if json.get("results_filename", None):
            self.results_filename = json["results_filename"]

        if json.get("instructors", []):
            for instructor in json["instructors"]:
                self.instructors.append(instructor)

        if json["activity"] == "poll":
            self.index = 0
            for item in json["items"]:
                #if item["type"] == "multiple choice":
                # FIXME: allow widgets; need to rewrite create/show:
                question = item["question"]
                keywords = item.get("keywords", None)
                #if isinstance(question, str):
                #    question = widgets.HTML(question)
                options = item["choices"]
                #for pos in range(len(options)):
                #    option = options[pos]
                #    if isinstance(option, str):
                #        options[pos] = widgets.HTML(option)
                q = Question(item["no"], question, options, keywords)
                self.questions.append(q)
#                 else:
#                     raise Exception("not a valid question 'type': use ['multiple choice']")
#             self.create_widget()
#             self.use_question(self.index)
            self.build_quiz_env()
        else:
            raise Exception("not a valid 'activity': use ['poll']")

#     def use_question(self, index):
# #         self.questions[index].set_question(self.questions[index].question)
# #         self.questions[index].set_id(self.questions[index].id)
#         self.set_question(self.questions[index].question)
#         self.set_id(self.questions[index].id)
# #         self.questions[index].results_html.layout.visibility = "hidden"
#         self.results_html.layout.visibility = "hidden"
#         #get the name of the login user and find in the instructors list
# #         self.questions[index].results_button.layout.visibility = "visible" if (getpass.getuser() in self.instructors) else "hidden"
#         self.results_button.layout.visibility = "visible" if (getpass.getuser() in self.instructors) else "hidden"
# #         self.questions[index].prev_button.disabled = index == 0
# #         self.questions[index].next_button.disabled = index == len(self.questions) - 1
        
#         self.prev_button.disabled = index == 0
#         self.next_button.disabled = index == len(self.questions) - 1
        
#         for i in range(5):
# #             self.questions[index].choice_row_list[i].layout.visibility = "hidden"
#             self.choice_row_list[i].layout.visibility = "hidden"
# #             self.buttons[i].layout.visibility = "hidden"
#         for i in range(len(self.questions[index].options)):
#             self.questions[index].widget.choice_widgets[i].value = self.questions[index].options[i][1]
# #             self.choice_widgets[i].value = self.questions[index].options[i][1]
# #             self.choice_row_list[i].children[0].description = '{}_{}'.format(index, i)
#             self.questions[index].widget.choice_row_list[i].layout.visibility = "visible"
# #             self.choice_row_list[i].layout.visibility = "visible"
# #             self.buttons[i].layout.visibility = "visible"


#     def create_widget(self):
# #         self.id_widget = widgets.HTML("")
# #         self.question_widget = widgets.HTML("")
# #         self.choice_widgets = []
# #         self.choice_row_list = []
# #         for count in range(1, 5 + 1):
# #             self.choice_widgets.append(widgets.HTML(""))
# #             self.choice_row_list.append(widgets.HBox([widgets.Checkbox(value=False, disabled=False),
# #                                                       self.choice_widgets[-1]]))
#         #the selection buttons
# #         self.buttons = []
# #         for i in range(1, 5 + 1):
# #             button = widgets.Button(description = str(i))
# #             button.on_click(self.handle_submit)
# #             button.layout.margin = "20px"
# #             self.buttons.append(button)
# #         self.respond_row_widgets = widgets.HBox([widgets.HTML("""<br/><br clear="all"/><b>Respond</b>: """)] + self.buttons)
        
#         self.next_button = widgets.Button(description="Next")
#         self.next_button.on_click(self.handle_next)
#         self.results_button = widgets.Button(description="Results")
#         self.results_button.on_click(self.handle_results)
#         self.prev_button = widgets.Button(description="Previous")
#         self.prev_button.on_click(self.handle_prev)
#         self.results_html = widgets.HTML("")
#         self.top_margin = widgets.HTML("")
#         #self.top_margin.layout.height = "100px"
#         right_stack = widgets.VBox([self.top_margin, self.results_html])
#         self.stack = widgets.VBox([self.id_widget, self.question_widget] + self.choice_row_list +
#                                    [widgets.HBox([self.prev_button, self.results_button, self.next_button])])
#         self.output = widgets.Output()
#         self.top_level = widgets.VBox([widgets.HBox([self.stack, right_stack]),
#                                        self.output])

#     def set_question(self, question):
#         self.question_widget.value = "<h1>%s</h1>" % question

#     def set_id(self, id):
#         self.id_widget.value = "<p><b>Question ID</b>: %s</p>" % id
#         self.id = id

#     def handle_results(self, sender):
#         # write out when we show the Results:
#         self.handle_submit(sender)
#         if self.last_id == self.questions[self.index].id:
#             self.show_initial = not self.show_initial
#         else:
#             self.show_initial = True
#             self.last_id = self.questions[self.index].id
#         data = {}
#         with open(self.results_filename) as fp:
#             line = fp.readline()
#             while line:
#                 if "::" in line:
#                     id, user, time, choice = line.split("::")
#                     if self.questions[self.index].id == id:
#                         if choice.strip() != "Results":
#                             if self.show_initial:
#                                 if user.strip() not in data:
#                                     data[user.strip()] = choice.strip()
#                             else: # shows last
#                                 data[user.strip()] = choice.strip()
#                 line = fp.readline()
#         choices = {str(i): 0 for i in range(1, len(self.questions[self.index].options) + 1)}
#         for datum in data.values():
#             if datum not in choices:
#                 choices[datum] = 0
#             choices[datum] += 1
#         barvalues = [int(value) for key,value in sorted(choices.items())]
#         self.stack.layout.width = "55%"
#         try:
#             from calysto.graphics import BarChart
#             barchart = BarChart(size=(300, 400), data=barvalues, labels=sorted(choices.keys()))
#             self.results_html.value = str(barchart)
#             self.results_html.layout.visibility = "visible"
#         except:
#             with self.output:
#                 print(sorted(choices.keys()))
#                 print(barvalues)

    def handle_submit(self, sender):

        for item in self.quiz_container[:-1]:
            results = {}
            answers = []
            
            id = item.children[0].children[0].children[0].children[1].get_state()['outputs'][0]['data']['text/markdown'].split(':')[1].strip('**')
            results['no'] = int(id)
#             question = item.children[0].children[0].children[1].value.strip('</h1>')
#             results['question'] = question
            
            for q in self.questions:
                if int(q.id) == int(id):
                    for i in range(len(q.options)):
                        if item.children[0].children[0].children[i+2].children[0].value == True:
                            answers.append(item.children[0].children[0].children[i+2].children[1].children[0].\
                                          get_state()['outputs'][0]['data']['text/markdown'])
                           
                        # disable the check button
                        item.children[0].children[0].children[i+2].children[0].disabled = self.submit_button = True
                        self.timer.cancel()
                        
                    results['choices'] = answers
                    
                    self.results.append(results)
                    
#                     print(self.results)
            
            
#         print(self.results)
        self.grader()
                
        import fcntl
        with open(self.results_filename, "a+") as g:
            fcntl.flock(g, fcntl.LOCK_EX)
            g.write("%s::%s::%s\n" % (getpass.getuser(), datetime.today(), str(len(self.mark))))
            fcntl.flock(g, fcntl.LOCK_UN)
        

#     def handle_next(self, sender):
#         if self.index < len(self.questions) - 1:
#             self.index += 1
#             self.use_question(self.index)
#             self.output.clear_output()

#     def handle_prev(self, sender):
#         if self.index > 0:
#             self.index -= 1
#             self.use_question(self.index)
#             self.output.clear_output()
    def callback(self):
        if not self.submit_button:
            self.handle_submit(None)

    def render(self):
        try:

            # if date and time does not => than current time and date display a beautiful message and clear it
            #         datetime1 = datetime.strptime('07/11/2019 02:45PM', '%m/%d/%Y %I:%M%p')
            quiz_time = datetime.strptime(self.start_datetime, '%m/%d/%Y %I:%M%p')

            prep_time = 10 # loading time

            alloted_time = (quiz_time + timedelta(seconds=(int(self.alloted_time) + prep_time)) -  datetime.now()).total_seconds()

            if quiz_time > datetime.today():
                raise QuizTimeOut('There is an active quiz, but please check back at {} prompt!'.format(quiz_time.strftime('%I:%M%p')))

            if alloted_time <= 0:
                raise QuizTimeOut('There is no active quiz at this time')

            display(widgets.VBox(self.quiz_container))

            self.timer = threading.Timer(alloted_time, self.callback)
            self.timer.start() 

        except QuizTimeOut:
            pass


    def build_quiz_env(self):
        # enable pages using Tab widget
        
        for item in self.questions:
            self.results_html = widgets.HTML("")
            self.top_margin = widgets.HTML("")
            #self.top_margin.layout.height = "100px"
            right_stack = widgets.VBox([self.top_margin, self.results_html])
            self.stack = widgets.VBox([widgets.HBox([item.tick_widget, item.id_widget]), widgets.VBox([item.question_widget, item.keywords_widget])] + item.choice_row_list)
#                                        + [widgets.HBox([self.prev_button, self.results_button, self.next_button])])
            self.output = widgets.Output(layout={'border': '1px solid black'})
            self.top_level = widgets.VBox([widgets.HBox([self.stack, right_stack]), self.output])
            
            self.quiz_container.append(self.top_level)
            
            item.tick_widget.layout.visibility = 'hidden'
            item.keywords_widget.layout.visibility = 'hidden'
            for wid in item.explain_buttons:
                wid.layout.visibility = 'hidden'

            
        self.button = widgets.Button(description = "Submit")
        self.button.on_click(self.handle_submit)
        self.button.layout.margin = "20px"
        self.score_widgets = widgets.HTML("""<br/><br clear="all"/><b>Score</b>: """)
        
        shuffle(self.quiz_container)
        
        self.quiz_container.append(widgets.VBox([self.score_widgets, self.button]))
        
        self.score_widgets.layout.visibility = 'hidden'
        
        
    def grader(self):
        for i in self.questions:
            self.overall_right_options += i.right_options
            i.keywords_widget.layout.visibility = 'visible'
            for wid in i.explain_buttons:
                if wid.disabled == False:
                    wid.layout.visibility = 'visible'
                    
#         print(self.overall_right_options)
            
        self.mark = [self.results[k] for k in range(len(self.overall_right_options))\
                     if self.results[k] in self.overall_right_options]
        
#         print(self.mark)
        
        self.score_widgets.value += str(len(self.mark))

        self.score_widgets.layout.visibility = 'visible'
        self.button.disabled = True
        
        mark = [mark.get('no')for mark in self.mark]
            
        for wid in self.quiz_container[:-1]: # removed the last vbox that contained html widget
            
            id = wid.children[0].children[0].children[0].children[1].get_state()['outputs'][0]['data']['text/markdown'].split(':')[1].strip('**')
            
            if int(id) in mark:
                wid.children[0].children[0].children[0].children[0].layout.visibility='visible'
                wid.children[0].children[0].children[0].children[0].value = True
                
            else:
                wid.children[0].children[0].children[0].children[0].layout.visibility='visible'
                wid.children[0].children[0].children[0].children[0].value = False
                


class Question(object):
    def __init__(self, id, question, options, keywords):
        self.id = id
        self.question = question
        self.options = options
        self.keywords = keywords
        
        self.right_options =  [{'no': self.id}]
        
        self.tick_widget = widgets.Valid()
        self.id_widget = widgets.Output(layout={'border': '1px solid black'})
#         self.question_widget = widgets.HTML("")
        self.question_widget = widgets.Output()
        self.keywords_widget = widgets.Output()
                                                    
        
        self.choice_widgets = []
        self.explain_widgets = []
        self.choice_row_list = []
        self.explain_buttons = []
        
        
        
        for count in range(len(self.options)):
#             self.choice_widgets.append(widgets.HTML(""))
            self.choice_widgets.append(widgets.Output())
            self.explain_widgets.append(widgets.Output(layout={'border': '1px solid black'}))
            self.explain_buttons.append(widgets.Button(description='', tooltip='See explanation', \
                            layout=widgets.Layout(flex='0 1 auto', width='auto'), icon='fa-info-circle'))
            checkbox = widgets.Checkbox(value=False, disabled=False, description="{}".format(chr(count+97)))
            self.choice_row_list.append(widgets.HBox([checkbox, widgets.HBox([self.choice_widgets[-1], self.explain_buttons[-1]])]))
#             self.choice_row_list.append(widgets.HBox([checkbox,self.choice_widgets[-1]]))

        self.set_id()
        self.set_question()
        self.set_options()
        self.extract_right_options()

            
    def set_question(self):
#         self.question_widget.value = "<h1>%s</h1>" % self.question
        self.question_widget.append_display_data(Markdown(self.question))
        if self.keywords:
            self.keywords_widget.append_display_data(Markdown('<font color=red>*Read up on: {}*</font>'.\
                                                              format(reduce((lambda x,y: x+', '+y), self.keywords))))
    def set_id(self):
#         self.id_widget.value = "<p><b>Question ID</b>: %s</p>" % self.id
        self.id_widget.append_display_data(Markdown('**Question: {}**'.format(str(self.id))))
    def set_options(self):
        for i in range(len(self.options)):
#             print(self.options[i][1])
#             self.choice_widgets[i].value = self.options[i][1]
            self.choice_widgets[i].append_display_data(Markdown(self.options[i][1]))
            try:
                self.explain_widgets[i].append_display_data\
                (Markdown('<font color=red>{}</font>'.format(self.options[i][2])))
                self.explain_buttons[i].tooltip=str(self.options[i][2])

            except:
                self.explain_buttons[i].disabled=True
                pass
    
    def extract_right_options(self):
        self.right_options[0].update({'choices':[option[1] for option in self.options if option[0] == 'right']})
            

class ActivityMagic(Magic):

    def line_activity(self, filename, mode=None):
        """
        %activity FILENAME - run a widget-based activity
          (poll, classroom response, clicker-like activity)
        This magic will load the JSON in the filename.
        Examples:
            %activity /home/teacher/activity1
            %activity /home/teacher/activity1 new
            %activity /home/teacher/activity1 edit
        """
        from IPython import get_ipython
        if mode == "new":
            text = '''
{"activity": "poll",
 "instructors": ["YOUR ID HERE"],
 "items": [
      {"id": "1",
       "question":  """When it comes to learning, metacognition (e.g., thinking about thinking) can be just as important as intelligence.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      },
      {"id": "2",
       "question":  """What is the best way to learn from some text?""",
       "type": "multiple choice",
       "options": ["Read and reread the text.",
                   "Explain key ideas of the text to yourself while reading.",
                   "Underline key concepts.",
                   "Use a highlighter"]
      },
      {"id": "3",
       "question":  """Intelligence is fixed at birth.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      },
      {"id": "4",
       "question":  """You have a test coming up. What's the best way to review the material?""",
       "type": "multiple choice",
       "options": ["Circle key points in the textbook.",
                   "Review relevant points of the lecture in audio format.",
                   "Take an informal quiz based on the material."]
      },
      {"id": "5",
       "question":  """To which of the following should you not tailor your learning?""",
       "type": "multiple choice",
       "options": ["Learning styles (visual, audio, etc.)", "Previous knowledge", "Interests", "Ability"]
      },
      {"id": "6",
       "question":  """Learning should be spaced out over time.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      },
      {"id": "7",
       "question":  """Right-brained people learn differently from left-brained people.""",
       "type": "multiple choice",
       "options": ["True", "False"]
      }
   ]
}'''
            get_ipython().set_next_input(("%%%%activity %s\n\n" % filename) + text)
            return
        elif mode == "edit":
            text = "".join(open(filename, "r").readlines())
            get_ipython().set_next_input(("%%%%activity %s\n\n" % filename) + text)
        else:
            activity = Activity(self.datetime, self.alloted_time)
            activity.load(filename)
            activity.render()

    def cell_activity(self, filename):
        """
        %%activity FILENAME - make an activity from
          a JSON structure
        This magic will construct a Python file from the cell's
        content, a JSON structure.
        Example:
            %%activity /home/teacher/activity1
            {"activity": "poll",
             "instructors": ["teacher01"],
             "results_file": "/home/teacher/activity1.results",
             "items": [{"id": "...",
                        "type": "multiple choice",
                        "question": "...",
                        "options": ["...", ...]
                       }, ...]
            }
        In this example, users will load
        /home/teacher/activity1
        """
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        with open(filename, "w") as fp:
            fp.write(self.code)
        activity = Activity(self.datetime, self.alloted_time)
        activity.load(filename)
        # Make sure results file is writable:
        os.chmod(activity.results_filename, 0o777)
        if getpass.getuser() in activity.instructors:
            # Ok, let's test it (MetaKernel):
            self.line_activity(filename)
        self.evaluate = False

def register_magics(kernel):
    kernel.register_magics(ActivityMagic)

def register_ipython_magics():
    from metakernel import IPythonKernel
    from metakernel.utils import add_docs
    from IPython.core.magic import register_line_magic, register_cell_magic
    kernel = IPythonKernel()
    magic = ActivityMagic(kernel)
    # Make magics callable:
    kernel.line_magics["activity"] = magic
    kernel.cell_magics["activity"] = magic

    @register_line_magic
    @add_docs(magic.line_activity.__doc__)
    def activity(line):
        try:
            line, datetime, alloted_time = line.split('::')
        except:
            line, datetime, alloted_time = os.environ.get('QUIZ_PATH').split('::')
        magic.datetime = datetime
        magic.alloted_time = alloted_time
        kernel.call_magic("%activity " + line)

    @register_cell_magic
    @add_docs(magic.cell_activity.__doc__)
    def activity(line, cell):
        try:
            line, datetime, alloted_time = line.split('::')
        except:
            line, datetime, alloted_time = os.environ.get('QUIZ_PATH').split('::')
        magic.datetime = datetime
        magic.alloted_time = alloted_time
        magic.code = cell
        magic.cell_activity(line)