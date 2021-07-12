from os.path import isfile
from typing import Callable

import win32con
from win32api import GetSystemMetrics  # package pywin32
from win32gui_struct import PackMENUITEMINFO

try:
    import winxpgui as win32gui
except ImportError:
    import win32gui


class SysTrayIcon:
    '''TODO'''
    QUIT = 'QUIT'
    SPECIAL_ACTIONS = [QUIT]

    FIRST_ID = 1023

    def __init__(self, icon: str, hover_text: str, menu_options: tuple[tuple[str, str, Callable[['SysTrayIcon'], None]]] = None, on_quit: Callable[['SysTrayIcon'], None] = None, default_menu_index: int = 0, window_class_name: str = 'SysTrayIconPy'):

        self.icon = icon
        self.hover_text = hover_text
        self.on_quit = on_quit

        self._next_action_id = self.FIRST_ID
        self.menu_actions_by_id = set()
        self.menu_options = self._add_ids_to_menu_options(list(menu_options + (('Quit', None, self.QUIT),) if menu_options else (('Quit', None, self.QUIT),)))
        self.menu_actions_by_id = dict(self.menu_actions_by_id)
        del self._next_action_id

        self.default_menu_index = default_menu_index
        self.window_class_name = window_class_name

        # Register the Window class.
        window_class = win32gui.WNDCLASS()
        hinst = window_class.hInstance = win32gui.GetModuleHandle(None)
        window_class.lpszClassName = self.window_class_name
        window_class.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        window_class.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        window_class.hbrBackground = win32con.COLOR_WINDOW
        window_class.lpfnWndProc = {win32gui.RegisterWindowMessage("TaskbarCreated"): self.restart,
            win32con.WM_DESTROY: self.destroy,
            win32con.WM_COMMAND: self.command,
            win32con.WM_USER + 20: self.notify}  # could also specify a wndproc.
        # Create the Window.
        self.hwnd = win32gui.CreateWindow(win32gui.RegisterClass(window_class), self.window_class_name, win32con.WS_OVERLAPPED | win32con.WS_SYSMENU, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        self.notify_id = None
        self.refresh_icon()

        win32gui.PumpMessages()

    def _add_ids_to_menu_options(self, menu_options: list[tuple[str, str, Callable[['SysTrayIcon'], None]]]) -> list[tuple[str, str, Callable[['SysTrayIcon'], None], int]]:
        result = []
        for menu_option in menu_options:
            option_text, option_icon, option_action = menu_option
            if callable(option_action) or option_action in self.SPECIAL_ACTIONS:
                self.menu_actions_by_id.add((self._next_action_id, option_action))
                result.append(menu_option + (self._next_action_id,))
            elif non_string_iterable(option_action):
                result.append((option_text, option_icon, self._add_ids_to_menu_options(option_action), self._next_action_id))
            else:
                print('Unknown item', option_text, option_icon, option_action)
            self._next_action_id += 1
        return result

    def refresh_icon(self):
        # Try and find a custom icon
        hinst = win32gui.GetModuleHandle(None)
        if self.icon and isfile(self.icon):
            hicon = win32gui.LoadImage(hinst, self.icon, win32con.IMAGE_ICON, 0, 0, win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE)
        else:
            print("Can't find icon file - using default.")
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        message = win32gui.NIM_MODIFY if self.notify_id else win32gui.NIM_ADD
        self.notify_id = (self.hwnd, 0, win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP, win32con.WM_USER + 20, hicon, self.hover_text)
        win32gui.Shell_NotifyIcon(message, self.notify_id)

    def restart(self, hwnd, msg, wparam, lparam: int):
        self.refresh_icon()

    def destroy(self, hwnd, msg, wparam, lparam: int):
        if self.on_quit:
            self.on_quit(self)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self.hwnd, 0))
        win32gui.PostQuitMessage(0)  # Terminate the app.

    def notify(self, hwnd, msg, wparam, lparam: int):
        if lparam == win32con.WM_LBUTTONDBLCLK:
            self.execute_menu_option(self.default_menu_index + self.FIRST_ID)
        elif lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        elif lparam == win32con.WM_LBUTTONUP:
            pass
        return True

    def show_menu(self):
        menu = win32gui.CreatePopupMenu()
        self.create_menu(menu, self.menu_options)
        # win32gui.SetMenuDefaultItem(menu, 1000, 0)

        pos = win32gui.GetCursorPos()
        # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winui/menus_0hdi.asp
        win32gui.SetForegroundWindow(self.hwnd)
        win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
        win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)

    def create_menu(self, menu, menu_options: list[tuple[str, str, Callable[['SysTrayIcon'], None], int]]):
        for option_text, option_icon, option_action, option_id in menu_options[::-1]:
            if option_icon:
                option_icon = self.prep_menu_icon(option_icon)

            if option_id in self.menu_actions_by_id:
                item, extras = PackMENUITEMINFO(text=option_text, hbmpItem=option_icon, wID=option_id)
                win32gui.InsertMenuItem(menu, 0, 1, item)
            else:
                submenu = win32gui.CreatePopupMenu()
                self.create_menu(submenu, option_action)
                item, extras = PackMENUITEMINFO(text=option_text, hbmpItem=option_icon, hSubMenu=submenu)
                win32gui.InsertMenuItem(menu, 0, 1, item)

    def prep_menu_icon(self, icon):
        # First load the icon.
        ico_x = GetSystemMetrics(win32con.SM_CXSMICON)
        ico_y = GetSystemMetrics(win32con.SM_CYSMICON)
        hicon = win32gui.LoadImage(0, icon, win32con.IMAGE_ICON, ico_x, ico_y, win32con.LR_LOADFROMFILE)

        hdcBitmap = win32gui.CreateCompatibleDC(0)
        hbm = win32gui.CreateCompatibleBitmap(win32gui.GetDC(0), ico_x, ico_y)
        hbmOld = win32gui.SelectObject(hdcBitmap, hbm)
        # Fill the background.
        win32gui.FillRect(hdcBitmap, (0, 0, 16, 16), win32gui.GetSysColorBrush(win32con.COLOR_MENU))
        # unclear if brush needs to be feed.  Best clue I can find is: "GetSysColorBrush returns a cached brush instead of allocating a new one." - implies no DeleteObject
        # draw the icon
        win32gui.DrawIconEx(hdcBitmap, 0, 0, hicon, ico_x, ico_y, 0, 0, win32con.DI_NORMAL)
        win32gui.SelectObject(hdcBitmap, hbmOld)
        win32gui.DeleteDC(hdcBitmap)

        return hbm

    def command(self, hwnd, msg, wparam, lparam: int):
        self.execute_menu_option(win32gui.LOWORD(wparam))

    def execute_menu_option(self, id: int):
        menu_action = self.menu_actions_by_id[id]
        if menu_action == self.QUIT:
            win32gui.DestroyWindow(self.hwnd)
        else:
            menu_action(self)


def non_string_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    else:
        return not isinstance(obj, str)


# Minimal self test. You'll need a bunch of ICO files in the current working directory in order for this to work...
if __name__ == '__main__':
    import itertools, glob

    icons = itertools.cycle(glob.glob('*.ico'))
    hover_text = "SysTrayIcon.py Demo"


    def hello(sysTrayIcon):
        print("Hello World.")


    def simon(sysTrayIcon):
        print("Hello Simon.")


    def switch_icon(sysTrayIcon):
        sysTrayIcon.icon = next(icons)
        sysTrayIcon.refresh_icon()


    menu_options = (('Say Hello', next(icons), hello),
                    ('Switch Icon', None, switch_icon),
                    ('A sub-menu', next(icons), (('Say Hello to Simon', next(icons), simon),
                                                 ('Switch Icon', next(icons), switch_icon),
                                                 ))
                    )


    def bye(sysTrayIcon):
        print('Bye, then.')


    SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1)
