__author__ = 'Daniel James Evans'
__copyright__ = 'Copyright (c) 2017 Daniel James Evans'
__license__ = 'MIT'

import Tkinter as tk
import tkFileDialog
import keyword
from functools import partial
import subprocess
import pipes
import time

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
        self.new_button = tk.Button(self.intro_top, text = 'New File',
                                    command = new_file)
        self.new_button.pack()
        self.load_button = tk.Button(self.intro_top, text = 'Load File',
                                     command = load_file)
        self.load_button.pack()


class TextEditor():
    '''Initialize a window for editing a code file.'''
    def __init__(self, *args, **kwargs):
        self.edit_top = tk.Toplevel(top)
        self.edit_frame_width = self.edit_top.winfo_screenwidth() / 4
        self.edit_frame_height = self.edit_top.winfo_screenheight() / 2
        self.edit_frame = tk.Frame(self.edit_top,
                                   width = self.edit_frame_width,
                                   height = self.edit_frame_height)
        self.edit_frame.pack_propagate(False)
        self.text_widget = tk.Text(self.edit_frame, wrap=tk.NONE)
        self.text_widget.insert(tk.INSERT, kwargs['filler_text'])
        syntax_highlighter.create_tags(self.text_widget)

        self.text_widget.bind('<KeyRelease>', partial(key_is_pressed, self))
        self.text_widget.bind('<ButtonRelease-1>', partial(mouse_is_pressed,
                                                           self))
        self.text_widget.bind('{', partial(close_bracket, '}'))
        self.text_widget.bind('[', partial(close_bracket, ']'))
        self.text_widget.bind('(', partial(close_bracket, ')'))
        if kwargs['new_file'] == False:
            syntax_highlighter.highlight_loaded_file(self.text_widget)
        self.edit_scroll_y = tk.Scrollbar(self.edit_frame,
                                          command = self.text_widget.yview,
                                          orient = tk.VERTICAL)
        self.edit_scroll_x = tk.Scrollbar(self.edit_frame,
                                          command = self.text_widget.xview,
                                          orient = tk.HORIZONTAL)
        self.text_widget['yscrollcommand'] = self.edit_scroll_y.set
        self.text_widget['xscrollcommand'] = self.edit_scroll_x.set        
        self.edit_top.run_btn = tk.Button(self.edit_top,
                                          text = 'Save File and Run Code',
                                          command = partial(run_code, self))
        self.find_btn = tk.Button(self.edit_top, text = 'Find',
                                  command = partial(FindWindow, editor = self))
        self.file_path = kwargs['path']
        self.output_frame_width = self.edit_top.winfo_screenwidth() / 4
        self.output_frame_height = self.edit_top.winfo_screenheight() / 2 - 200
        self.output_frame = tk.Frame(self.edit_top,
                                     width = self.output_frame_width,
                                     height = self.output_frame_height)
        self.output_frame.pack_propagate(False)
        self.output_disp = tk.Text(self.output_frame, wrap=tk.NONE)
        self.output_disp.insert(tk.INSERT, 'Code output goes here.\n')
        self.output_scroll_y = tk.Scrollbar(self.output_frame,
                                            command = self.output_disp.yview,
                                            orient = tk.VERTICAL)
        self.output_disp['yscrollcommand'] =  self.output_scroll_y.set
        self.row_label_text = tk.StringVar()
        self.row_label_text.set('Row:')
        self.row_label = tk.Label(self.edit_top,
                                  textvariable = self.row_label_text)
        self.col_label_text = tk.StringVar()
        self.col_label_text.set('Col:')
        self.col_label = tk.Label(self.edit_top,
                                  textvariable = self.col_label_text)
        self.menubar = tk.Menu(self.edit_top)
        self.file_menu = tk.Menu(self.menubar)
        self.edit_menu = tk.Menu(self.menubar)
        self.file_menu.add_command(label = 'Save',
                                   command = partial(save, self))
        self.edit_menu.add_command(label = 'Cut',
                                   command = partial(cut, self))
        self.menubar.add_cascade(label = "File", menu = self.file_menu)
        self.menubar.add_cascade(label = "Edit", menu = self.edit_menu)
        self.edit_top.config(menu = self.menubar)
        self.edit_top.bind('<Configure>', partial(change_size, self))
        self.edit_frame.pack(expand = True, side = tk.LEFT)
        self.edit_scroll_y.pack(side = tk.RIGHT, fill = tk.Y)
        self.edit_scroll_x.pack(side = tk.BOTTOM, fill = tk.X)
        self.text_widget.pack(expand = True, fill = tk.BOTH)
        self.edit_top.run_btn.pack()
        self.find_btn.pack()
        self.row_label.pack()
        self.col_label.pack()
        self.output_frame.pack(expand = True, side = tk.RIGHT)
        self.output_scroll_y.pack(side = tk.RIGHT, fill = tk.Y)
        self.output_disp.pack(fill = tk.BOTH, expand = True)
        print self.edit_top.winfo_width()
        self.time_init = time.time()


class FindWindow():
    '''Initialize a window for finding and replacing text.'''
    def __init__(self, *args, **kwargs):
        self.editor = kwargs['editor']
        self.edit_top = tk.Toplevel(top)
        self.find_frame = tk.Frame(self.edit_top)
        self.find_entry = tk.Entry(self.find_frame)
        self.find_btn = tk.Button(self.find_frame, text = 'Find',
                                  command = self.find_text)
        self.show_rep = tk.IntVar()
        self.edit_top.rep_chkbtn = tk.Checkbutton(self.find_frame,
                                                  text = 'Replace',
                                                  variable = self.show_rep,
                                                  command = self.toggle_rep)
        
        self.rep_frame = tk.Frame(self.edit_top)
        self.rep_entry = tk.Entry(self.rep_frame)
        self.edit_top.rep_btn = tk.Button(self.rep_frame,
                                          text = 'Replace',
                                          command = self.rep_text)

       
        self.find_frame.pack()
        self.find_entry.pack()
        self.find_btn.pack()
        self.edit_top.rep_chkbtn.pack()


    def find_text(self):
        '''Find and select text specified by the user.'''
        try:
            self.editor.text_widget.tag_remove('sel', tk.SEL_FIRST,
                                               tk.SEL_LAST)
        except tk.TclError:
            pass
        pos = self.editor.text_widget.search(self.find_entry.get(), '1.0',
                                             tk.END)
        if pos != '':
            find_len = str(len(self.find_entry.get()))
            self.editor.text_widget.tag_add('sel', pos,
                                            pos + '+%sc' %(find_len))


    def rep_text(self):
        '''Find and replace text specified by the user.'''
        try:
            self.editor.text_widget.tag_remove('sel', tk.SEL_FIRST,
                                               tk.SEL_LAST)
        except tk.TclError:
            pass
        pos = self.editor.text_widget.search(self.find_entry.get(), '1.0',
                                             tk.END)
        if pos != '':
            find_len = str(len(self.find_entry.get()))
            self.editor.text_widget.delete(pos, pos + '+%sc' %(find_len))
            self.editor.text_widget.insert(pos, self.rep_entry.get())


    def toggle_rep(self):
        '''Show or hide the replace section of the find/replace window.'''
        if self.show_rep.get() == 1:
            self.rep_frame.pack()
            self.rep_entry.pack()
            self.edit_top.rep_btn.pack()
            
        else:
            self.rep_frame.pack_forget()


def new_file():
    '''Open a new window for writing a new file of code.'''
    new_window = TextEditor(filler_text = 'Your code goes here.',
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
            code_file.write(editor.text_widget.get(1.0, tk.END)
                            .encode('ascii'))
        output = subprocess.Popen(['python', '%s' %(editor.file_path)],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        while True:
            next_line = output.stdout.readline()
            editor.output_disp.insert(tk.END, next_line)
            editor.output_disp.see(tk.END)
            editor.edit_top.update_idletasks()
            if output.poll() is not None:
                #Display additional lines that haven't been printed when
                #the computer gets the poll signal.
                for line in output.stdout.readlines():
                    editor.output_disp.insert(tk.END, line)
                    editor.output_disp.see(tk.END)
                break


def save(editor):
    '''Save a file.'''
    if editor.file_path == '':
        editor.file_path = tkFileDialog.asksaveasfilename(title = 'Save File')
    if editor.file_path != '':
        with open(editor.file_path, 'w') as code_file:
            code_file.write(editor.text_widget.get(1.0, tk.END)
                            .encode('ascii'))


def key_is_pressed(editor, event):
    '''Update syntax highlighting, row/col labels and indent as needed.'''
    syntax_highlighter.update_highlight(event)
    row_and_col = event.widget.index(tk.INSERT)
    row_and_col_split = row_and_col.split('.')
    row_num = row_and_col_split[0]
    col_num = row_and_col_split[1]
    editor.row_label_text.set('Row: %s' %(row_num))
    editor.col_label_text.set('Col: %s' %(col_num))
    if event.char == '\n' or event.char == '\r':
        auto_indent(event)

def mouse_is_pressed(editor, event):
    '''Update rwo/col labels when mouse is pressed.'''
    row_and_col = event.widget.index(tk.INSERT)
    row_and_col_split = row_and_col.split('.')
    row_num = row_and_col_split[0]
    col_num = row_and_col_split[1]
    editor.row_label_text.set('Row: %s' %(row_num))
    editor.col_label_text.set('Col: %s' %(col_num))


def auto_indent(event):
    '''Add the correct indentation to a new line.'''
    previous_line_index = event.widget.index(tk.INSERT)[0] + '.0 -1 lines'
    previous_line = event.widget.get(previous_line_index,
                                     '%s lineend' %(previous_line_index))
    indent = ''
    next_char = ' '
    index = 0
    while next_char == ' ' and index < len(previous_line):
        next_char = previous_line[index]
        if next_char == ' ':
            indent += ' '
        index += 1
    if previous_line.endswith(':'):
        indent += '    '
    event.widget.insert(tk.INSERT, indent)


def change_size(editor, event):
    '''Control the proportions of the editor window when it is resized.'''
    if time.time() - editor.time_init > 1:
        new_output_width = editor.edit_top.winfo_width() / 2
        new_output_height = editor.edit_top.winfo_height() - 200
        new_edit_width = editor.edit_top.winfo_width() / 2
        new_edit_height = editor.edit_top.winfo_height()
        editor.output_frame.config(width = new_output_width,
                                   height = new_output_height)
        editor.edit_frame.config(width = new_edit_width,
                                 height = new_edit_height)


def cut (editor):
    '''Cut text when menubar cut button pressed.'''
    editor.edit_top.focus_get().event_generate('<<Cut>>')
    #print top.event_generate("<<Cut>>")
    print 'cut'
    print editor



new_intro_window = IntroWindow()
top.withdraw()
top.mainloop()

