# ghpush

Push any folder to a new GitHub repo in one command. Python 3.10+, standard library only.

```
$ ghpush ~/projects/sorting-visualizer
```

## Requirements

- `git` ≥ 2.28 and the GitHub CLI `gh`
- `gh auth login` done once
- `git config --global user.name` / `user.email` set

## Usage

```bash
./ghpush.py <folder>            # interactive
./ghpush.py <folder> --dry-run  # everything except creating/pushing the repo
./ghpush.py <folder> -y         # accept defaults, no prompts
./ghpush.py <folder> --license mit --topics c,graphics --org my-org --web
```

| Flag | Effect |
|---|---|
| `--dry-run` | run everything except creating and pushing the repo |
| `-y`, `--yes` | accept defaults (an existing `origin` remote aborts instead of being replaced) |
| `--license mit\|gpl-3.0\|apache-2.0` | add a LICENSE file |
| `--org NAME` | create the repo under an organization |
| `--topics a,b` | set GitHub topics after pushing |
| `--web` | open the repo in the browser when done |

Files named `*.example`, `*.sample`, `*.template` or `*.dist` (e.g. `.env.example`) are not treated as secrets.

## What it does

1. Pre-flight: git, gh, gh login, git identity
2. Asks for repo name, description, visibility (rejects names you already own)
3. Detects the language (marker files, then file extensions)
4. Creates `.gitignore` (GitHub template, built-in fallback) if missing
5. Creates a sample `README.md` if missing, with a warning
6. Scans for secrets (`.env`, `*.pem`, …) and files > 100 MB
7. `git init` / `add` / `commit`, then `gh repo create --source --push`

## Install as a command

```bash
mkdir -p ~/.local/bin
ln -s "$PWD/ghpush.py" ~/.local/bin/ghpush
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The end-to-end tests run the real CLI against a fake `gh`, so they need no network or GitHub account.

## License

MIT
