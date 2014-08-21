from Tkinter import Menu

##############################################################################
#
# Collects all the application menus
#
##############################################################################
class Menus:

    def __init__(self, application):#, frame):
#    def __init__(self, tkroot, application):#, frame):

        # Keep a reference to the input frame
#        frame = frame

#        d = Detector(Detector.SOUTH_SMALL)

        # Create the menu bar and add it to the tkroot

        menu = Menu(application)
        application.config(menu = menu)
#        menu = Menu(tkroot)
#        tkroot.config(menu = menu)

        # Create the various drop-downs - file, edit...

        # Create the "file" menu, with commands like "Open" and "Quit"
        file_menu = Menu(menu)
#        file_menu.add_command(label = 'greeting', command = application.say_hi)
#        file_menu.add_command(label = 'insult', command = application.say_insult)
        file_menu.add_command(label = 'Save', command=application.save_all)
        file_menu.add_command(label = 'Export ROOT file', command=application.save_root)
        file_menu.add_command(label = 'Export PostScript file', command=application.save_postscript)
        file_menu.add_command(label = 'Open', command=application.read_input)
        file_menu.add_separator()
        file_menu.add_command(label = 'Quit', command = application.exit)
#        file_menu.add_command(label='Dialog', menu=open_dialog)

        # Creates the "edit" menu
        edit_menu = Menu(menu)
#        edit_menu.add_command(label='Change small cells',
#                                   command = application.calibrate_all_small)
        edit_menu.add_command(label = 'Show voltage', command = application.image_window.display_voltage)
        edit_menu.add_command(label = 'Show detector', command = application.image_window.display_detector)
        edit_menu.add_command(label = 'Show QT', command = application.image_window.display_qt_boards)
        edit_menu.add_command(label='Modify gains', command=application.apply_corrections_from_file)
        # Add a drop-down sub-menu to edit allowing to change
        # either all the small or all the large voltages using
        # an input file.
#        edit_change_submenu = Menu(edit_menu);
#        edit_change_submenu.add_command(label='Change small cells',
#                                   command = application.calibrate_all_small)
#        edit_change_submenu.add_command(label='Change large cells',
#                                   command = application.calibrate_all_small)

        # Add each drop-down to its parent
        menu.add_cascade(label = 'File', menu = file_menu)
        menu.add_cascade(label = 'Edit', menu = edit_menu)
#        edit_menu.add_cascade(label='Change', menu=edit_change_submenu)

#    def ask_to_quit(self):
#        if tkMessageBox.askyesno(title='Exit?', message='Are you sure?', default='no'):
#            frame.quit()
#        else:
#            print 'Glad you decided to stay'

#    def open_dialog(self):
#        dialog.CellDialog(_tkroot)
