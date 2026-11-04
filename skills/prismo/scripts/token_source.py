"""Localiza a fonte DTCG registrada, incluindo registros legados inequívocos."""
from pathlib import Path


def token_source(settings, root):
    paths = settings.get('paths', {})
    if paths.get('tokens'):
        return paths['tokens']
    candidates = []
    for entry in settings.get('reuse', []):
        if not isinstance(entry, str):
            continue
        candidate = entry.split(' — ', 1)[0].split(': ', 1)[0].strip()
        path = Path(candidate)
        if (not path.is_absolute() and '..' not in path.parts and path.suffix == '.json'
                and (Path(root) / path).is_file()):
            candidates.append(candidate)
    unique = set(candidates)
    return next(iter(unique)) if len(unique) == 1 else None
