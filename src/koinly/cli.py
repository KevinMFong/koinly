import typer
from .process_transactions import process_transactions

app = typer.Typer()


@app.callback()
def callback():
    """
    Koinly command-line interface
    """


app.command(name="process-transactions")(process_transactions)
