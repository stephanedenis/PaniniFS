from __future__ import annotations
import typer

app = typer.Typer(help="Execution Orchestrator CLI")

@app.command()
def version():
    """Print version."""
    print("execution-orchestrator 0.1.0")

@app.command()
def run(mission: str, backend: str = typer.Option("local", help="local|colab|cloud")):
    """Run a mission on a backend (stub)."""
    print(f"RUN: mission={mission} backend={backend}")

if __name__ == "__main__":
    app()
