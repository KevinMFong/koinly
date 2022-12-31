import typer


app = typer.Typer()


@app.callback()
def callback():
    """
    Koinly command-line interface
    """


@app.command(name="process-transactions")
def process_transactions():
    """
    Process raw transaction data.
    """
    typer.echo("Process raw transaction data")
