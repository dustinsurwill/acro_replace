from functools import partial
from os import startfile
from os.path import exists
from sys import argv

from keyboard import unhook_all, write, _State, KEY_UP, all_modifiers, hook, _word_listeners
from systrayicon import SysTrayIcon

CONFIG = f'{argv[0]}.config'


def open_config(_):
    if not exists(CONFIG):
        with open(CONFIG, 'w'):
            pass
    startfile(CONFIG)


def load_config(_):
    def w(replace, event):
        write(replace + event.replace('space', ' '))

    unhook_all()
    if not exists(CONFIG):
        with open(CONFIG, 'w'):
            pass
    with open(CONFIG, 'rt') as file:
        for pair in file:
            source, replace = pair.replace('\n', '').split(',', 1)
            replace = '\b' * (len(source) + 1) + replace
            add_word_listener(source, partial(w, replace), ['space', '.', ',', '?', '!', '-', '_', ')', ':', ';', '"'])


def main():
    load_config(None)
    SysTrayIcon(None, 'Text Replace', (('Open Config', None, open_config), ('Reload Config', None, load_config),))


def add_word_listener(word, callback, triggers=['space'], match_suffix=False, timeout=2):
    """
    Invokes a callback every time a sequence of characters is typed (e.g. 'pet') and followed by a trigger key (e.g. space). Modifiers (e.g. alt, ctrl, shift) are ignored.

    - `word` the typed text to be matched. E.g. 'pet'.
    - `callback` is an argument-less function to be invoked each time the word is typed.
    - `triggers` is the list of keys that will cause a match to be checked. If the user presses some key that is not a character (len>1) and not in triggers, the characters so far will be discarded. By default the trigger is only `space`.
    - `match_suffix` defines if endings of words should also be checked instead of only whole words. E.g. if true, typing 'carpet'+space will trigger the listener for 'pet'. Defaults to false, only whole words are checked.
    - `timeout` is the maximum number of seconds between typed characters before the current word is discarded. Defaults to 2 seconds.

    Returns the event handler created. To remove a word listener use `remove_word_listener(word)` or `remove_word_listener(handler)`.

    Note: all actions are performed on key down. Key up events are ignored.
    Note: word matches are **case sensitive**.
    """
    state = _State()
    state.current = ''
    state.time = -1

    def handler(event):
        name = event.name
        if event.event_type == KEY_UP or name in all_modifiers:
            return
        if timeout and event.time - state.time > timeout:
            state.current = ''
        state.time = event.time
        matched = state.current == word or (match_suffix and state.current.endswith(word))
        if name in triggers and matched:
            callback(name)
            state.current = ''
        elif len(name) > 1:
            state.current = ''
        else:
            state.current += name

    hooked = hook(handler)

    def remove():
        hooked()
        del _word_listeners[word]
        del _word_listeners[handler]
        del _word_listeners[remove]
    _word_listeners[word] = _word_listeners[handler] = _word_listeners[remove] = remove
    # TODO: allow multiple word listeners and removing them correctly.
    return remove


if __name__ == '__main__':
    main()
