"""Saved-baseline guards, fresh scratch directories, monitored native workers."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import threading


class ToolError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ToolError(message)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_hashes(directory, expected):
    require(bool(expected), 'Baseline hash manifest is empty; STOP')
    result = {}
    for name, wanted in expected.items():
        require(Path(name).name == name, f'Unsafe baseline manifest key {name}; STOP')
        path = Path(directory) / name
        require(path.is_file(), f'Baseline file missing: {path}; STOP')
        result[name] = digest(path)
        require(result[name] == wanted, f'Baseline hash mismatch: {path}; STOP')
    return result


def unlocked(board):
    board = Path(board)
    # KiCad lock names vary by document/version. False positives fail closed.
    locks = [p for p in board.parent.iterdir()
             if p.name.endswith('.lck') and board.stem in p.name]
    require(not locks, f'Scratch board may be open/locked: {locks}; STOP')


def prepare_scratch(board, manifest, output_dir):
    board = Path(board).resolve(strict=True)
    root = Path(output_dir).resolve()
    expected = read_json(manifest)['hashes']
    require(board.name in expected, 'Board is not bound by baseline manifest; STOP')
    verify_hashes(board.parent, expected)
    require(root != board.parent and board.parent not in root.parents,
            'Scratch output must be outside the production project directory; STOP')
    require(root not in board.parents, 'Scratch output cannot contain production; STOP')
    require(not root.exists(), f'Output already exists; choose a fresh scratch directory: {root}; STOP')
    sources = [board] + [board.with_suffix(ext) for ext in
                        ['.kicad_pro', '.kicad_sch', '.kicad_dru'] if board.with_suffix(ext).exists()]
    source_hashes = {p.name: digest(p) for p in sources}
    root.mkdir(parents=True, exist_ok=False)
    for source in sources:
        shutil.copy2(source, root / source.name)
    context = dict(schema_version=1, source=str(board), board=str(root / board.name),
                   source_hashes=source_hashes, accepted_hashes=expected)
    write_json(root / 'context.json', context)
    verify_context(root)
    return root


def verify_context(root):
    root = Path(root).resolve(strict=True)
    context = read_json(root / 'context.json')
    source = Path(context['source']).resolve(strict=True)
    target = Path(context['board']).resolve(strict=True)
    require(target.parent == root and target != source,
            'Scratch identity mismatch; production write refused; STOP')
    require(root != source.parent and source.parent not in root.parents,
            'Scratch overlaps production project; STOP')
    unlocked(target)
    verify_hashes(source.parent, context['accepted_hashes'])
    verify_hashes(source.parent, context['source_hashes'])
    for name, wanted in context['source_hashes'].items():
        if name != target.name:
            require(digest(root / name) == wanted,
                    f'Scratch project/schematic/rules unexpectedly changed: {name}; STOP')
    return context


FATAL_NATIVE = re.compile(
    r'assert\s+["\n].*?failed|assertion\s+(?:failed|failure)|AssertionError|'
    r'Failed to connect to KiCad|(?:IPC|KiCad connection)[^\r\n]*(?:failed|unreachable|refused)', re.I | re.S)


def run_monitored(command, log, timeout=120):
    """Stop only this newly launched worker on assertion/IPC failure; never retry.

    Capture full diagnostics to disk. Do not suppress wx assertions or interact
    with KiCad's editor. Byte-wise reads detect an assertion without a newline.
    """
    process = subprocess.Popen([str(x) for x in command], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, encoding='utf-8',
                               errors='replace', bufsize=1)
    parts = {'stdout': [], 'stderr': []}
    fatal = threading.Event()

    def consume(stream, key):
        window = ''
        while True:
            char = stream.read(1)
            if not char:
                break
            parts[key].append(char)
            window = (window + char)[-1500:]
            if FATAL_NATIVE.search(window):
                fatal.set()

    readers = [threading.Thread(target=consume, args=(stream, key), daemon=True)
               for stream, key in [(process.stdout, 'stdout'), (process.stderr, 'stderr')]]
    for reader in readers:
        reader.start()
    import time
    deadline = time.monotonic() + timeout
    reason = None
    while process.poll() is None:
        if fatal.wait(.02):
            reason = 'Native assertion or IPC failure'
            process.terminate()
            break
        if time.monotonic() > deadline:
            reason = 'Native worker timeout'
            process.terminate()
            break
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()  # Only the child created above; never a named/editor process.
        process.wait()
    for reader in readers:
        reader.join(timeout=5)
    process.stdout.close()
    process.stderr.close()
    output = {k: ''.join(v) for k, v in parts.items()}
    Path(log).write_text('COMMAND: ' + repr([str(x) for x in command]) + '\n' +
                         output['stdout'] + '\nSTDERR:\n' + output['stderr'], encoding='utf-8')
    if reason or fatal.is_set():
        raise ToolError(f'{reason or "Native assertion/IPC failure"}; worker stopped. '
                        f'No retry or editor recovery. Inspect {log}; owner approval required before resuming KiCad operations.')
    require(process.returncode == 0,
            f'Native worker failed (exit {process.returncode}); inspect {log}; STOP')
    return output
