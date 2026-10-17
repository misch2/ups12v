"""Inspect/close only a hash-bound saved editor launched for this migration.

OS lifecycle helper, no CAD serialization or KiCad API calls. Never force-kills,
responds to dialogs, closes a dirty window, or handles a stopped transaction.
"""
from pathlib import Path
import argparse
import ctypes
from ctypes import wintypes
import json
import time
from .safety import require, read_json, verify_hashes, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--launch',required=True,type=Path)
    parser.add_argument('--board',required=True,type=Path)
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--close',action='store_true')
    args = parser.parse_args()
    launch = read_json(args.launch)
    root = args.launch.parent
    require(not (root/'STOP.json').exists(), 'Stopped transaction: no editor lifecycle operation allowed')
    require(not args.output.exists(), 'Fresh lifecycle evidence required')
    hashes = read_json(args.manifest)['hashes']
    verify_hashes(args.board.parent,hashes)
    pid = launch['process_id']
    user = ctypes.WinDLL('user32',use_last_error=True)
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
    user.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    user.GetWindowTextW.argtypes = [wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
    user.GetClassNameW.argtypes = [wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
    rows = []
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
    def observe(hwnd, _):
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd,ctypes.byref(owner))
        if owner.value == pid:
            caption = ctypes.create_unicode_buffer(user.GetWindowTextLengthW(hwnd)+1)
            user.GetWindowTextW(hwnd,caption,len(caption))
            cls = ctypes.create_unicode_buffer(256)
            user.GetClassNameW(hwnd,cls,len(cls))
            if caption.value:
                rows.append(dict(hwnd=int(hwnd),title=caption.value,window_class=cls.value))
        return True
    user.EnumWindows(callback_type(observe),0)
    result = dict(pid=pid,board=str(args.board.resolve()),windows=rows,close_requested=False)
    if args.close:
        frames = [x for x in rows if 'PCB Editor' in x['title'] and args.board.stem in x['title']]
        dialogs = [x for x in rows if x['window_class']=='#32770' or
                   (x['window_class']=='wxWindowNR' and x not in frames and x['title']!='panel')]
        require(len(frames)==1 and not dialogs, 'Ambiguous editor/modal state; no close')
        require('*' not in frames[0]['title'], 'Unsaved editor changes; no close')
        user.PostMessageW.argtypes = [wintypes.HWND,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
        require(user.PostMessageW(frames[0]['hwnd'],0x0010,0,0), 'Normal WM_CLOSE request failed')
        result['close_requested'] = True
        time.sleep(1)
    write_json(args.output,result)
    verify_hashes(args.board.parent,hashes)
    print(json.dumps(result))


if __name__ == '__main__':
    main()
