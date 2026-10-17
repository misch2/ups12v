codex execpolicy check --pretty `
     --rules .codex/rules/default.rules `
     -- python -B -m v4kicad.ipc_install preflight

codex execpolicy check --pretty `
     --rules .codex/rules/default.rules `
     -- python -B -m v4kicad.ipc_install apply --board ../foobar/whatever

