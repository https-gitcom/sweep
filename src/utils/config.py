from pydantic import BaseModel

class SweepConfig(BaseModel):
    include_dirs: list[str] = []
    exclude_dirs: list[str] = [".git", "node_modules", "venv"]
    include_exts: list[str] = ['.cs', '.csharp', '.py', '.md', '.txt', '.ts', '.tsx', '.js', '.jsx', '.mjs']
    exclude_exts: list[str] = ['.min.js', '.min.js.map', '.min.css', '.min.css.map']
    max_file_limit: int = 60_000

    def get_exclusion_list(self):
        try:
            with open('exclusion.txt', 'r') as f:
                return [line.strip() for line in f]
        except FileNotFoundError:
            return []