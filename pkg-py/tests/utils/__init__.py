from pathlib import Path

def path_examples(*args) -> Path:
    repo_root = Path(__file__).parent.parent.parent.parent 
    return repo_root / "examples" / Path(*args)
