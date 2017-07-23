__author__ = 'Daniel James Evans'
__copyright__ = 'Copyright (c) 2017 Daniel James Evans'
__license__ = 'MIT'

import Tkinter
import tkFileDialog
import keyword
from functools import partial
import subprocess
import pipes

colored_item_list = []
for word in keyword.kwlist:
    colored_item_list.append([word])


def create_tags(text_widget):
    '''Create Tkinter text tags for the syntax highlighter.'''
    for word_entry in colored_item_list:
        text_widget.tag_config(word_entry[0], foreground = 'red')
    text_widget.tag_config('comment', foreground = 'yellow')
    text_widget.tag_config('string', foreground = 'cyan')


def update_highlight(event):
    '''Update syntax highlighting when a key is pressed.'''
    for word_entry in colored_item_list:
        word = word_entry[0]
        event.widget.tag_remove(word, event.widget.index(Tkinter.INSERT)[0]
                               + '.0', Tkinter.INSERT
                               + '+%sc' %(str(len(word))))
        search_starting_position =  event.widget.index(Tkinter.INSERT)[0] + '.0'
        search_ending_position =  (event.widget.index(Tkinter.INSERT)[0]
                                   + '.%s'%(str(len(word))))
        pos = True
        while pos:
            pos = event.widget.search('([^A-Za-z_0-9]|^)%s([^A-Za-z_]|$)'
                                     %(word), search_starting_position,
                                     stopindex = Tkinter.INSERT
                                     + '+%sc' %(str(len(word))), regexp = True)
            if pos:
                pos_carat = event.widget.search('(^)%s([^A-Za-z_]|$)' %(word),
                                               search_starting_position,
                                               stopindex = Tkinter.INSERT
                                               + '+%sc' %(str(len(word))),
                                               regexp = True)
                if pos_carat:
                    event.widget.tag_add(word, pos, pos + '+%sc'
                                        %(str(len(word) + 1)))
                else:
                    event.widget.tag_add(word, pos + '+1c', pos + '+%sc'
                                        %(str(len(word) + 1)))
                search_starting_position = pos + '+%sc' %(str(len(word)))
    current_pos_in_char = 0 #needed for determining when end-of-file is reached
    current_line = 1
    current_column = 0
    code_text = event.widget.get(1.0, Tkinter.END)
    event.widget.tag_remove('string', '1.0', Tkinter.END)
    while current_pos_in_char < len(code_text):
        next_char = code_text[current_pos_in_char]
        current_column += 1
        current_pos_in_char += 1
        if next_char == '\n' or next_char == '\r':
            current_line += 1
            current_column = 0
        if next_char == '#':
            comment_line_number =  current_line
            comment_start_column = current_column - 1
            if current_pos_in_char == len(code_text) - 1:
                comment_end_column = current_column
            while (next_char != '\n' and next_char != '\r'
                   and current_pos_in_char != len(code_text) - 1):
                current_pos_in_char += 1
                current_column += 1
                next_char = code_text[current_pos_in_char]
                if (next_char == '\n' or next_char == '\r'
                    or current_pos_in_char == len(code_text) - 1):
                    comment_end_column = current_column
            event.widget.tag_add('comment', '%d.%d' %(comment_line_number,
                                                     comment_start_column),
                                '%d.%d' %(comment_line_number,
                                          comment_end_column))

        if next_char == '\'' or next_char == '"':
            quote_mark = next_char
            string_start_line_number =  current_line
            string_start_column = current_column - 1
            if current_pos_in_char == len(code_text) - 1:
                string_end_column = current_column
            else:
                next_char = code_text[current_pos_in_char]
                if (next_char == quote_mark
                        and code_text[current_pos_in_char + 1] == quote_mark):
                    docstring = True
                else:
                    docstring = False
                if docstring != True:
                    while (next_char != quote_mark
                           and current_pos_in_char != len(code_text) - 1):
                        current_pos_in_char += 1
                        current_column += 1
                        next_char = code_text[current_pos_in_char]
                else:
                    closing_quote_count = 0
                    #Increase pos because the next char was already checked.
                    current_pos_in_char += 1
                    current_column += 1
                    while closing_quote_count < 3:
                        current_pos_in_char += 1
                        current_column += 1
                        if current_pos_in_char == len(code_text) - 1:
                            break
                        next_char = code_text[current_pos_in_char]
                        if next_char == quote_mark:
                            closing_quote_count += 1
                        else:
                            closing_quote_count = 0
                        if next_char == '\n' or next_char == '\r':
                            current_line += 1
                            #Decrease column pos because of the newline char.
                            current_column = -1
            string_end_line_number = current_line
            string_end_column = current_column
            event.widget.tag_add('string', '%d.%d' %(string_start_line_number,
                                                    string_start_column),
                                '%d.%d' %(string_end_line_number,
                                          string_end_column + 1))
            current_pos_in_char += 1
            current_column += 1


def highlight_loaded_file(text_entry):
    '''Highlight the syntax of a newly opened document.'''
    for word_entry in colored_item_list:
        word = word_entry[0]
        search_starting_position =  '1.0'
        search_ending_position =  '1.0 + %sc' %(str(len(word)))
        pos = True
        while pos:
            pos = text_entry.search('([^A-Za-z_0-9]|\n|\r|^)%s([^A-Za-z_]|$)'
                                    %(word), search_starting_position,
                                    stopindex = Tkinter.END, regexp = True)
            if pos:
                #Put the tag in the right place, depending on if pos has ^.
                pos_carat = text_entry.search('(^)%s([^A-Za-z_]|$)' %(word),
                                              search_starting_position,
                                              stopindex = Tkinter.END,
                                              regexp = True)
                if pos_carat:
                    text_entry.tag_add(word, pos, pos + '+%sc'
                                       %(str(len(word) + 1)))
                else:
                    text_entry.tag_add(word, pos + '+1c', pos + '+%sc'
                                       %(str(len(word) + 1)))
                search_starting_position = pos + '+%sc' %(str(len(word)))

    current_pos_in_char = 0 #needed for determining when end-of-file is reached
    current_line = 1
    current_column = 0
    code_text = text_entry.get(1.0,Tkinter.END)
    text_entry.tag_remove('string', '1.0', Tkinter.END)
    while current_pos_in_char < len(code_text):
        next_char = code_text[current_pos_in_char]
        current_column += 1
        current_pos_in_char += 1
        if next_char == '\n' or next_char == '\r':
            current_line += 1
            current_column = 0
        if next_char == '#':
            comment_line_number =  current_line
            comment_start_column = current_column - 1
            if current_pos_in_char == len(code_text) - 1:
                comment_end_column = current_column
            while (next_char != '\n' and next_char != '\r'
                   and current_pos_in_char != len(code_text) - 1):
                current_pos_in_char += 1
                current_column += 1
                next_char = code_text[current_pos_in_char]
                if (next_char == '\n' or next_char == '\r'
                    or current_pos_in_char == len(code_text) - 1):
                    comment_end_column = current_column
            text_entry.tag_add('comment', '%d.%d' %(comment_line_number,
                                                    comment_start_column),
                               '%d.%d' %(comment_line_number,
                                         comment_end_column))


        if next_char == '\'' or next_char == '"':
            quote_mark = next_char
            string_start_line_number =  current_line
            string_start_column = current_column - 1
            if current_pos_in_char == len(code_text) - 1:
                string_end_column = current_column
            else:
                next_char = code_text[current_pos_in_char]
                if (next_char == quote_mark
                        and code_text[current_pos_in_char + 1] == quote_mark):
                    docstring = True
                else:
                    docstring = False
                if docstring != True:
                    while (next_char != quote_mark
                           and current_pos_in_char != len(code_text) - 1):
                        current_pos_in_char += 1
                        current_column += 1
                        next_char = code_text[current_pos_in_char]
                else:
                    closing_quote_count = 0
                    #Increase pos because the next char was already checked.
                    current_pos_in_char += 1
                    current_column += 1
                    while closing_quote_count < 3:
                        current_pos_in_char += 1
                        current_column += 1
                        if current_pos_in_char == len(code_text) - 1:
                            break
                        next_char = code_text[current_pos_in_char]
                        if next_char == quote_mark:
                            closing_quote_count += 1
                        else:
                            closing_quote_count = 0
                        if next_char == '\n' or next_char == '\r':
                            current_line += 1
                            #Correctly place tag, depending on if pos has ^.
                            current_column = -1
            string_end_line_number = current_line
            string_end_column = current_column
            text_entry.tag_add('string', '%d.%d' %(string_start_line_number,
                                                   string_start_column),
                               '%d.%d' %(string_end_line_number,
                                         string_end_column + 1))
            current_pos_in_char += 1
            current_column += 1
