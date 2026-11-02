import shutil
import subprocess
from pathlib import Path
def to_mermaid(graph):
    nodes = set(graph)
    for children in graph.values():
        nodes.update(children)

    identifiers = {
        name: f"n{index}"
        for index, name in enumerate(sorted(nodes))
    }
    lines = ["flowchart TD"]

    for name in sorted(nodes):
        label = (
            name.replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        lines.append(f'    {identifiers[name]}["{label}"]')

    for parent, children in sorted(graph.items()):
        for child in sorted(children):
            lines.append(
                f"    {identifiers[parent]} --> {identifiers[child]}"
            )

    return "\n".join(lines) + "\n"



def save_mermaid(graph, output):
    filename = Path(output).with_suffix(".mmd")
    try:
        filename.write_text(to_mermaid(graph), encoding="utf-8")
    except OSError as error:
        raise ValueError("Не удалось сохранить Mermaid-файл") from error
    return filename


def render_png(source, output):
    executable = shutil.which("mmdc")
    if executable is None:
        raise ValueError("Mermaid CLI не найден. Установите mmdc.")

    try:
        subprocess.run(
            [
                executable,
                "-i", str(source),
                "-o", str(output),
            ],
            check=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("Превышено время создания PNG") from error
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Не удалось создать PNG через Mermaid") from error