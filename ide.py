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
import sys
import os
import sys
from ConfigParser import SafeConfigParser

import syntax_highlighter


'''Initialize global variables.'''
# I used Tcl() instead of Top() so that I could use tk::mac::.
top = tk.Tcl()
top.loadtk()

editor_list = [] # Initialize a list of text editor windows.
font_size_stringvar = tk.StringVar()
prefs_parser = SafeConfigParser()


def close_bracket(bracket, text):
    '''Insert a closing bracket when an opening bracket is typed.'''
    text.widget.mark_gravity(tk.INSERT, tk.LEFT)
    text.widget.insert(tk.INSERT, bracket)
    text.widget.mark_gravity(tk.INSERT, tk.RIGHT)


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
        self.text_widget = tk.Text(self.edit_frame, wrap=tk.NONE,
                                   font = (prefs_dict['font'],
                                           prefs_dict['font_size']))
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
        self.run_btn = tk.Button(self.edit_top,
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
        self.output_disp = tk.Text(self.output_frame, wrap=tk.NONE,
                                   font = (prefs_dict['font'],
                                           prefs_dict['font_size']))
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
        if sys.platform == 'darwin':
            self.apple_menu = tk.Menu(self.menubar, name = 'apple')
            self.menubar.add_cascade(menu = self.apple_menu)
            self.apple_menu.add_command(label='About ide')
            top.createcommand('tk::mac::ShowPreferences', show_prefs_window)
            top.createcommand('tk::mac::Quit', partial(next_quit_prompt, 0))
        self.file_menu = tk.Menu(self.menubar)
        self.edit_menu = tk.Menu(self.menubar)
        self.file_menu.add_command(label = 'Save',
                                   command = partial(save, self))
        self.file_menu.add_command(label = 'Save As',
                                   command = partial(save_as, self))
        self.file_menu.add_command(label = 'New',
                                   command = new_file)
        self.file_menu.add_command(label = 'Load',
                                   command = load_file)
        if sys.platform != 'darwin':
            self.file_menu.add_command(label = 'Preferences',
                                       command = show_prefs_window)
        self.edit_menu.add_command(label = 'Cut',
                                   command = partial(cut, self))
        self.edit_menu.add_command(label = 'Copy',
                                   command = partial(copy, self))
        self.edit_menu.add_command(label = 'Paste',
                                   command = partial(paste, self))
        self.menubar.add_cascade(label = "File", menu = self.file_menu)
        self.menubar.add_cascade(label = "Edit", menu = self.edit_menu)
        self.edit_top.config(menu = self.menubar)
        self.edit_top.bind('<Configure>', partial(change_size, self))
        self.edit_frame.pack(expand = True, side = tk.LEFT)
        self.edit_scroll_y.pack(side = tk.RIGHT, fill = tk.Y)
        self.edit_scroll_x.pack(side = tk.BOTTOM, fill = tk.X)
        self.text_widget.pack(expand = True, fill = tk.BOTH)
        self.run_btn.pack()
        self.find_btn.pack()
        self.row_label.pack()
        self.col_label.pack()
        self.output_frame.pack(expand = True, side = tk.RIGHT)
        self.output_scroll_y.pack(side = tk.RIGHT, fill = tk.Y)
        self.output_disp.pack(fill = tk.BOTH, expand = True)
        self.time_init = time.time()


class PrefsWindow():
    '''Initialize a window for changing preferences.'''
    def __init__(self):
        self.prefs_top = tk.Toplevel(top)
        self.prefs_top.title('Preferences')
        self.prefs_frame = tk.Frame(self.prefs_top)
        
        self.size_label_stringvar = tk.StringVar()
        self.size_label_stringvar.set('Font Size:')
        self.size_label = tk.Label(self.prefs_top,
                                   textvariable = self.size_label_stringvar)
        font_size_stringvar.set(str(prefs_dict['font_size']))
        self.size_entry = tk.Entry(self.prefs_frame,
                                   textvariable = font_size_stringvar)
        
        self.font_label_stringvar = tk.StringVar()
        self.font_label_stringvar.set('Font:')
        self.font_label = tk.Label(self.prefs_top,
                                   textvariable = self.font_label_stringvar)
        self.font_listbox = tk.Listbox(self.prefs_top, exportselection = 0)
        list_of_fonts = ['Arial', 'Courier New', 'Comic Sans MS', 'Fixedsys',
                         'Symbol', 'Times New Roman', 'Verdana']
        for font_name in list_of_fonts:
            self.font_listbox.insert(tk.END, font_name)
        # Select the font currently in use.
        current_font_index = 0
        while current_font_index < len(list_of_fonts):
            if list_of_fonts[current_font_index] == prefs_dict['font']:
                self.font_listbox.select_set(current_font_index)
                break
            current_font_index += 1

        self.update_btn = tk.Button(self.prefs_top,
                                    text = 'Update',
                                    command = partial(change_prefs, self))
        
        self.size_entry.pack()
        self.size_label.pack()
        self.prefs_frame.pack()
        self.font_label.pack()
        self.font_listbox.pack()
        self.update_btn.pack()


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


class SavePrompt():
    '''Initialize a window for changing preferences.'''
    def __init__(self, editor, index):
        self.top = tk.Toplevel(top)
        self.top.title('Save Before Quitting?')
        self.top.wm_attributes("-topmost", 1)
        self.save_label_stringvar = tk.StringVar()
        self.save_label_stringvar.set('You are about to quit.'
                                      '  Do you want to save %s first?'
                                      %(editor.file_path))
        self.save_label = tk.Label(self.top,
                                   textvariable = self.save_label_stringvar)
        self.save_label.pack()
        self.index = index
        self.save_button = tk.Button(self.top, text = 'Save File and Quit',
                                     command = partial(save_and_close,
                                                       editor, self,
                                                       self.index))        
        self.save_button.pack()
        self.no_save_button = tk.Button(self.top, text = 'Quit Without Saving',
                                     command = partial(quit_no_save,
                                                       editor, self,
                                                       self.index))
        self.no_save_button.pack()
        self.cancel_button = tk.Button(self.top, text = 'Cancel',
                                       command = partial(cancel_quit, self))
        self.cancel_button.pack()


def save_and_close(editor, prompt_instance, index):
    '''py2app only: Save and close a window while quitting program.'''
    save(editor)
    editor.edit_top.withdraw()
    prompt_instance.top.withdraw()
    next_quit_prompt(index)


def quit_no_save(editor, prompt_instance, index):
    '''py2app only: Close a window without saving while quitting program.'''
    editor.edit_top.withdraw()
    prompt_instance.top.withdraw()
    next_quit_prompt(index)


def cancel_quit(prompt_instance):
    '''Stop the process of quitting program.'''
    prompt_instance.top.withdraw()


def new_file():
    '''Open a new window for writing a new file of code.'''
    new_window = TextEditor(filler_text = 'Your code goes here.',
                            new_file = True, path = '')
    new_window.edit_top.title('New Document')
    editor_list.append(new_window)


def load_file():
    '''Load an existing file from a location specified by the user.'''
    file_path = tkFileDialog.askopenfilename(title = 'Select file')
    if file_path != '':
        file_opened = open(file_path, 'r')
        file_contents = file_opened.read()
        file_opened.close()
        new_window = TextEditor(filler_text = file_contents, new_file = False,
                                path = file_path)
        new_window.edit_top.title(new_window.file_path)
        editor_list.append(new_window)


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
                # Display additional lines that haven't been printed when
                # the computer gets the poll signal.
                for line in output.stdout.readlines():
                    editor.output_disp.insert(tk.END, line)
                    editor.output_disp.see(tk.END)
                break


def save(editor):
    '''Save a file.'''
    if editor.file_path == '':
        editor.file_path = tkFileDialog.asksaveasfilename(title = 'Save File')
        editor.edit_top.title(editor.file_path)
    if editor.file_path != '':
        with open(editor.file_path, 'w') as code_file:
            code_file.write(editor.text_widget.get(1.0, tk.END)
                            .encode('ascii'))


def save_as(editor):
    '''Save a file as a new document.'''
    editor.file_path = tkFileDialog.asksaveasfilename(title = 'Save File')
    editor.edit_top.title(editor.file_path)
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
    print editor, editor.text_widget.get('1.0', tk.END), event.widget.index(tk.INSERT), 'all text in key press'
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
    current_line_index = ''
    iterator_index = 0
    while event.widget.index(tk.INSERT)[iterator_index] != '.':
        current_line_index += event.widget.index(tk.INSERT)[iterator_index]
        iterator_index += 1
    previous_line_index = current_line_index + '.0 -1 lines'
    print previous_line_index, event
    previous_line = event.widget.get(previous_line_index,
                                     '%s lineend' %(previous_line_index))
    indent = ''
    next_char = ' '
    index = 0
    print previous_line, 'line_in_auto_indent'
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


def copy (editor):
    '''Copy text when menubar copy button pressed.'''
    editor.edit_top.focus_get().event_generate('<<Copy>>')


def paste (editor):
    '''Paste text when menubar paste button pressed.'''
    editor.edit_top.focus_get().event_generate('<<Paste>>')


def show_prefs_window():
    '''Show a window allowing the user to change preferences.'''
    PrefsWindow()


def change_prefs(window):
    '''Update preferences based on user input'''
    try:
        prefs_dict['font_size'] = int(font_size_stringvar.get())
        selected_font_index = window.font_listbox.curselection()
        try:
            selected_font =  window.font_listbox.get(selected_font_index)
        except tk.TclError:
            return
        prefs_dict['font'] = selected_font
        for editor in editor_list:
            editor.text_widget.config(font = (prefs_dict['font'],
                                              prefs_dict['font_size']))
            editor.output_disp.config(font = (prefs_dict['font'],
                                              prefs_dict['font_size']))
        prefs_parser.set('text_editor', 'font', prefs_dict['font'])
        prefs_parser.set('text_editor', 'font_size',
                         str(prefs_dict['font_size']))
        with open('preferences.ini', 'w') as prefs_file:
            prefs_parser.write(prefs_file)
    except ValueError:
        font_size_stringvar.set(str(prefs_dict['font_size']))


def get_prefs():
    '''Get preferenes when program opens.'''
    prefs_dict = {}
    prefs_parser.read('preferences.ini')
    font_name = prefs_parser.get('text_editor', 'font')
    prefs_dict['font'] = font_name
    font_size = prefs_parser.get('text_editor', 'font_size')
    prefs_dict['font_size'] = font_size
    return prefs_dict


def next_quit_prompt(index):
    '''py2app only: Prompt user to save a file before quitting.'''
    if index >= len(editor_list):
        top.quit()
    editor = editor_list[index]
    if 'normal' == editor.edit_top.state():
        index += 1
        SavePrompt(editor, index)
    else:
        index += 1
        next_quit_prompt(index)


prefs_dict = get_prefs()
new_file()


def load_Apple_event(*paths):
    '''py2app only: load files..'''
    for path in paths:
        file_opened = open(str(path), 'r')
        file_contents = file_opened.read()
        file_opened.close()
        new_window = TextEditor(filler_text = file_contents, new_file = False,
                                path = str(path))
        new_window.edit_top.title(new_window.file_path)
        editor_list.append(new_window)


# Enable OpenDocument Event handling.
top.createcommand("::tk::mac::OpenDocument", load_Apple_event)

# py2app only: open file(s) at start of program.
for file_name in sys.argv[1:]:
    load_Apple_event(file_name)

# py2app only: Move app to frontmost.
if sys.platform == 'darwin':
    os.system("/usr/bin/osascript -e 'tell app \"Finder\" to set frontmost of "
              "process \"ide\" to true'")

top.withdraw()
top.mainloop()

