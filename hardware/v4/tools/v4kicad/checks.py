"""Native CLI checks and strict, reusable JSON result parsing."""
from pathlib import Path
from .safety import read_json, require, run_monitored, verify_context, write_json


def parse_check(report, kind):
    require(isinstance(report, dict), 'Invalid native report object; STOP')
    if kind == 'drc':
        required = ['violations', 'unconnected_items', 'schematic_parity', 'ignored_checks']
        require(all(isinstance(report.get(k), list) for k in required),
                'Incomplete/unsupported native DRC JSON schema; STOP')
        violations = report['violations']
        result = dict(unconnected=len(report['unconnected_items']),
                      parity=len(report['schematic_parity']), ignored_checks=report['ignored_checks'])
    elif kind == 'erc':
        require(isinstance(report.get('sheets'), list), 'Unsupported native ERC JSON schema; STOP')
        require(bool(report['sheets']), 'Native ERC has no sheet coverage; STOP')
        require(all(isinstance(sheet.get('violations'), list) for sheet in report['sheets']),
                'Incomplete native ERC sheet report; STOP')
        violations = [v for sheet in report['sheets'] for v in sheet['violations']]
        result = dict(sheets=len(report['sheets']))
    else:
        raise ValueError(kind)
    require(all(v.get('severity') in ['error', 'warning', 'info', 'exclusion'] for v in violations),
            'Unknown/missing violation severity; STOP')
    result.update(errors=sum(v['severity'] == 'error' for v in violations),
                  warnings=sum(v['severity'] == 'warning' for v in violations))
    return result


def run_check(root, executable, kind):
    """Checks operate solely on the recorded fresh scratch project."""
    root = Path(root)
    context = verify_context(root)
    board = Path(context['board'])
    report = root / (kind + '.json')
    require(not report.exists(), f'Check report already exists: {report}; STOP')
    if kind == 'drc':
        require(board.with_suffix('.kicad_sch').is_file(), 'Scratch schematic missing for DRC parity; STOP')
        command = [executable, 'pcb', 'drc', '--format', 'json', '--all-track-errors',
                   '--schematic-parity', '--refill-zones', '--save-board',
                   '--output', report, board]
    else:
        schematic = board.with_suffix('.kicad_sch')
        require(schematic.exists(), 'Scratch schematic missing for ERC; STOP')
        command = [executable, 'sch', 'erc', '--format', 'json', '--output', report, schematic]
    run_monitored(command, root / (kind + '.log'))
    verify_context(root)
    require(report.is_file(), f'Native {kind.upper()} produced no report; STOP')
    result = parse_check(read_json(report), kind)
    write_json(root / (kind + '-summary.json'), result)
    return result


def run_review_check(root, executable, kind, allow_target_change=False):
    """Run ERC/DRC against a fresh owner-review copy only."""
    from .safety import verify_review_context
    root = Path(root)
    context = verify_review_context(root, allow_target_change=allow_target_change)
    board = Path(context['board'])
    report = root / (kind + '.json')
    require(not report.exists(), f'Check report already exists: {report}; STOP')
    if kind == 'drc':
        require(board.with_suffix('.kicad_sch').is_file(), 'Review schematic missing for DRC parity; STOP')
        command = [executable, 'pcb', 'drc', '--format', 'json', '--all-track-errors',
                   '--schematic-parity', '--refill-zones', '--save-board',
                   '--output', report, board]
    elif kind == 'erc':
        schematic = board.with_suffix('.kicad_sch')
        require(schematic.exists(), 'Review schematic missing for ERC; STOP')
        command = [executable, 'sch', 'erc', '--format', 'json', '--output', report, schematic]
    else:
        raise ValueError(kind)
    run_monitored(command, root / (kind + '.log'))
    # DRC's --refill-zones --save-board is the one bounded mutation allowed
    # in this review copy.  Its post-refill native object comparison runs in
    # the caller before any later CAD inspection.
    verify_review_context(root, allow_target_change=(allow_target_change or kind == 'drc'))
    require(report.is_file(), f'Native review {kind.upper()} produced no report; STOP')
    result = parse_check(read_json(report), kind)
    write_json(root / (kind + '-summary.json'), result)
    return result
