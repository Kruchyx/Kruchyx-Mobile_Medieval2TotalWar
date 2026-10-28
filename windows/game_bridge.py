"""Opt-in assisted pasting into a user-opened Medieval II console on Windows.
No injection, memory reads, hidden input, or background polling.
"""
import os

class GameNotFocused(RuntimeError): pass

def foreground_window_title():
    if os.name != 'nt':
        raise RuntimeError('Asystowane wklejanie działa tylko na Windows.')
    import ctypes
    u = ctypes.windll.user32
    hwnd=u.GetForegroundWindow()
    buf=ctypes.create_unicode_buffer(512)
    u.GetWindowTextW(hwnd,buf,len(buf))
    return buf.value

def is_probable_game_title(title):
    t=title.lower()
    return any(word in t for word in ('medieval ii','medieval 2','medieval2','total war','kingdoms'))

def paste_to_focused_game():
    """Send Ctrl+V only when an expected game window is in foreground.

    Does NOT open console or press Enter; caller is responsible for putting
    clipboard content in place and the user opening the console beforehand.
    """
    title=foreground_window_title()
    if not is_probable_game_title(title):
        raise GameNotFocused('Aktywne okno nie wygląda na Medieval II: '+(title or '[bez nazwy]'))
    import ctypes
    u=ctypes.windll.user32
    VK_CONTROL=0x11; VK_V=0x56; KEYUP=0x0002
    u.keybd_event(VK_CONTROL,0,0,0)
    u.keybd_event(VK_V,0,0,0)
    u.keybd_event(VK_V,0,KEYUP,0)
    u.keybd_event(VK_CONTROL,0,KEYUP,0)
    return title
