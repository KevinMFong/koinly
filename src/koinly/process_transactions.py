import typer

import csv
import json

from dateutil.parser import parse

from .transaction import ReportTransactionSchema
from .config import DataDirectory

FIELDS = [
    "date",
    "type",
    "label",
    "sending_wallet",
    "sent_amount",
    "sent_currency",
    "sent_cost_basis",
    "receiving_wallet",
    "received_amount",
    "received_currency",
    "received_cost_basis",
    "fee_amount",
    "fee_currency",
    "gain_usd",
    "net_value_usd",
    "fee_value_usd",
    "tx_src",
    "tx_dest",
    "tx_hash",
    "description",
]


def _get_from_data(txn_dict):
    from_ = txn_dict.get("from")
    if from_ is None:
        return None, None, None, None
    return from_["wallet"]["name"], from_["amount"], from_["currency"]["symbol"], from_["cost_basis"]


def _get_to_data(txn_dict):
    to = txn_dict.get("to")
    if to is None:
        return None, None, None, None
    cost_basis = to["cost_basis"]
    if cost_basis == "0.0":
        cost_basis = None
    return to["wallet"]["name"], to["amount"], to["currency"]["symbol"], cost_basis


def _get_fee_data(txn_dict):
    fee = txn_dict.get("fee")
    if fee is None:
        return None, None
    return fee["amount"], fee["currency"]["symbol"]


def process_transactions():
    """
    Process raw transaction data.
    """
    typer.echo("Processing raw transaction data.")
    raw_transactions = []
    bronze_files = DataDirectory.BRONZE.value.joinpath("koinly_transactions").glob("**/*.json")
    for bronze_file in bronze_files:
        typer.echo(f"Processing {bronze_file.parent.name}/{bronze_file.name}")
        with open(bronze_file) as file:
            file_rows = file.readlines()
        for row in file_rows:
            raw_transactions.extend(json.loads(row)["transactions"])

    report_transactions = []
    schema = ReportTransactionSchema()
    for raw_txn in raw_transactions:
        txn = {}
        if raw_txn["ignored"] is True:
            continue
        txn["date"] = str(parse(raw_txn["date"]))
        txn["type"] = raw_txn["type"]
        txn["label"] = raw_txn["label"]

        sending_wallet, sent_amount, sent_currency, sent_cost_basis = _get_from_data(raw_txn)
        txn["sending_wallet"] = sending_wallet
        txn["sent_amount"] = sent_amount
        txn["sent_currency"] = sent_currency
        txn["sent_cost_basis"] = sent_cost_basis

        receiving_wallet, received_amount, received_currency, received_cost_basis = _get_to_data(raw_txn)
        txn["receiving_wallet"] = receiving_wallet
        txn["received_amount"] = received_amount
        txn["received_currency"] = received_currency
        txn["received_cost_basis"] = received_cost_basis

        fee_amount, fee_currency = _get_fee_data(raw_txn)
        txn["fee_amount"] = fee_amount
        txn["fee_currency"] = fee_currency
        txn["fee_value_usd"] = raw_txn["fee_value"]

        txn["gain_usd"] = raw_txn["gain"]
        txn["net_value_usd"] = raw_txn["net_value"]
        txn["tx_src"] = raw_txn["txsrc"]
        txn["tx_dest"] = raw_txn["txdest"]
        txn["tx_hash"] = raw_txn["txhash"]
        txn["description"] = raw_txn["description"]

        report_transaction = schema.load(txn)
        report_transactions.append(report_transaction)

    with open(
        DataDirectory.SILVER.value.joinpath("koinly_transactions", "transactions_report.json"), "w"
    ) as file:
        file.write(schema.dumps(report_transactions, many=True, indent=2))

    with open(
        DataDirectory.SILVER.value.joinpath("koinly_transactions", "transactions_report.csv"), "w"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(schema.dump(report_transactions, many=True))

    typer.echo(f"Finished processing raw transaction data for {len(report_transactions)} transactions.")
