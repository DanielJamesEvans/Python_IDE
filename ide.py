__author__ = 'Daniel James Evans'
__copyright__ = 'Copyright (c) 2017 Daniel James Evans'
__license__ = 'MIT'

import Tkinter as tk
import tkFileDialog
import keyword
from functools import partial
import subprocess
import pipes

import syntax_highlighter


top = tk.Tk()


def close_bracket(bracket, text):
    '''Insert a closing bracket when an opening bracket is typed.'''
    text.widget.mark_gravity(tk.INSERT, tk.LEFT)
    text.widget.insert(tk.INSERT, bracket)
    text.widget.mark_gravity(tk.INSERT, tk.RIGHT)


class IntroWindow():
    '''Initialize a window that prompts user to load or create file.'''
    def __init__(self, *args, **kwargs):
        self.intro_top = tk.Toplevel(top)
        self.intro_top.new_button = tk.Button(self.intro_top,
                                              text = 'New File',
                                              command = new_file)
        self.intro_top.new_button.pack()
        self.intro_top.load_button = tk.Button(self.intro_top,
                                               text = 'Load File',
                                               command = load_file)
        self.intro_top.load_button.pack()


class TextEditor():
    '''Initialize a window for editing a code file.'''
    def __init__(self, *args, **kwargs):
        self.edit_top = tk.Toplevel(top)
        self.edit_top.edit_canvas = tk.Canvas(self.edit_top)
        self.edit_top.text_widget = tk.Text(self.edit_top.edit_canvas)
        self.edit_top.text_widget.insert(tk.INSERT, kwargs['filler_text'])
        syntax_highlighter.create_tags(self.edit_top.text_widget)
        self.edit_top.text_widget.bind('<KeyRelease>',
                                       syntax_highlighter.key_is_pressed)
        self.edit_top.text_widget.bind('{', partial(close_bracket, '}'))
        self.edit_top.text_widget.bind('[', partial(close_bracket, ']'))
        self.edit_top.text_widget.bind('(', partial(close_bracket, ')'))
        if kwargs['new_file'] == False:
            syntax_highlighter.highlight_loaded_file(self.edit_top.text_widget)
        self.edit_top.edit_scroll = tk.Scrollbar(self.edit_top.edit_canvas,
                                                 command = (self.edit_top
                                                            .text_widget
                                                            .yview))
        self.edit_top.text_widget['yscrollcommand'] = (self.edit_top
                                                       .edit_scroll.set)
        self.edit_top.run_btn = tk.Button(self.edit_top,
                                          text = 'Save File and Run Code',
                                          command = partial(run_code, self))
        self.edit_top.find_btn = tk.Button(self.edit_top, text = 'Find',
                                           command = partial(FindWindow,
                                                             editor = self))
        self.file_path = kwargs['path']
        self.edit_top.output_canvas = tk.Canvas(self.edit_top)
        self.edit_top.output_disp = tk.Text(self.edit_top.output_canvas)
        self.edit_top.output_scroll = tk.Scrollbar((self.edit_top
                                                    .output_canvas),
                                                    command = (self.edit_top
                                                               .output_disp
                                                               .yview))
        self.edit_top.output_disp['yscrollcommand'] = (self.edit_top
                                                       .output_scroll.set)
        
        self.edit_top.edit_canvas.pack()
        self.edit_top.edit_scroll.pack(side = tk.RIGHT,
                                       fill = tk.Y)
        self.edit_top.text_widget.pack()
        self.edit_top.run_btn.pack()
        self.edit_top.find_btn.pack()
        self.edit_top.output_canvas.pack()
        self.edit_top.output_scroll.pack(side = tk.RIGHT,
                                         fill = tk.Y)
        self.edit_top.output_disp.pack()


class FindWindow():
    '''Initialize a window for finding and replacing text.'''
    def __init__(self, *args, **kwargs):
        self.editor = kwargs['editor']
        self.edit_top = tk.Toplevel(top)
        self.edit_top.find_canvas = tk.Canvas(self.edit_top)
        self.edit_top.find_entry = tk.Entry(self.edit_top.find_canvas)
        self.edit_top.find_btn = tk.Button(self.edit_top.find_canvas,
                                           text = 'Find',
                                           command = self.find_text)
        self.show_rep = tk.IntVar()
        self.edit_top.rep_chkbtn = tk.Checkbutton(self.edit_top.find_canvas,
                                                  text = 'Replace',
                                                  variable = self.show_rep,
                                                  command = self.toggle_rep)
        
        self.edit_top.rep_canvas = tk.Canvas(self.edit_top)
        self.edit_top.rep_entry = tk.Entry(self.edit_top.rep_canvas)
        self.edit_top.rep_btn = tk.Button(self.edit_top.rep_canvas,
                                          text = 'Replace',
                                          command = self.rep_text)
        
        self.edit_top.find_canvas.pack()
        self.edit_top.find_entry.pack()
        self.edit_top.find_btn.pack()
        self.edit_top.rep_chkbtn.pack()


    def find_text(self):
        '''Find and select text specified by the user.'''
        try:
            self.editor.edit_top.text_widget.tag_remove('sel',
                                                        tk.SEL_FIRST,
                                                        tk.SEL_LAST)
        except tk.TclError:
            pass
        pos = self.editor.edit_top.text_widget.search((self.edit_top.find_entry
                                                       .get()),
                                                      '1.0', tk.END)
        if pos != '':
            find_len = str(len(self.edit_top.find_entry.get()))
            self.editor.edit_top.text_widget.tag_add('sel', pos,
                                                     pos + '+%sc' %(find_len))


    def rep_text(self):
        '''Find and replace text specified by the user.'''
        try:
            self.editor.edit_top.text_widget.tag_remove('sel',
                                                        tk.SEL_FIRST,
                                                        tk.SEL_LAST)
        except tk.TclError:
            pass
        pos = self.editor.edit_top.text_widget.search((self.edit_top.find_entry
                                                       .get()),
                                                      '1.0', tk.END)
        if pos != '':
            find_len = str(len(self.edit_top.find_entry.get()))
            self.editor.edit_top.text_widget.delete(pos,
                                                    pos + '+%sc' %(find_len))
            self.editor.edit_top.text_widget.insert(pos,
                                                    (self.edit_top.rep_entry
                                                     .get()))


    def toggle_rep(self):
        '''Show or hide the replace section of the find/replace window.'''
        if self.show_rep.get() == 1:
            self.edit_top.rep_canvas.pack()
            self.edit_top.rep_entry.pack()
            self.edit_top.rep_btn.pack()
            
        else:
            self.edit_top.rep_canvas.pack_forget()


def new_file():
    '''Open a new window for writing a new file of code.'''
    new_window = TextEditor(filler_text = 'Your code goes here',
                            new_file = True, path = '')


def load_file():
    '''Load an existing file from a location specified by the user.'''
    file_path = tkFileDialog.askopenfilename(title = 'Select file')
    if file_path != '':
        file_opened = open(file_path, 'r')
        file_contents = file_opened.read()
        file_opened.close()
        new_window = TextEditor(filler_text = file_contents, new_file = False,
                                path = file_path)


def run_code(editor):
    '''Save a file and run the code it contains.'''
    if editor.file_path == '':
        editor.file_path = tkFileDialog.asksaveasfilename(title = 'Save File')
    if editor.file_path != '':
        with open(editor.file_path, 'w') as code_file:
            code_file.write(editor.edit_top.text_widget.get(1.0, tk.END)
                            .encode('ascii'))
        output = subprocess.Popen(['python', '%s' %(editor.file_path)],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        while True:
            next_line = output.stdout.readline()
            editor.edit_top.output_disp.insert(tk.END, next_line)
            editor.edit_top.output_disp.see(tk.END)
            editor.edit_top.update_idletasks()
            if output.poll() is not None:
                #Display additional lines that haven't been printed when
                #the computer gets the poll signal.
                for line in output.stdout.readlines():
                    editor.edit_top.output_disp.insert(tk.END, line)
                    editor.edit_top.output_disp.see(tk.END)
                break


new_intro_window = IntroWindow()
top.withdraw()
top.mainloop()

