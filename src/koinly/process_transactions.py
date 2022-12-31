import csv
import json
from collections import defaultdict, UserDict

import typer
from dateutil.parser import parse

from .config import DataDirectory
from .transaction import ReportTransactionSchema


class Row(UserDict):
    def get_none_if_zero(self, key):
        value = self.data[key]
        if value in {0, "0", 0.0, "0.0"}:
            return None
        return value


FIELDS = [
    "id",
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
    wallet = from_["wallet"]["name"]
    amount = from_["amount"]
    currency = from_["currency"]["symbol"]
    cost_basis = Row(from_).get_none_if_zero("cost_basis")
    return wallet, amount, currency, cost_basis


def _get_to_data(txn_dict):
    to = txn_dict.get("to")
    if to is None:
        return None, None, None, None
    wallet = to["wallet"]["name"]
    amount = to["amount"]
    currency = to["currency"]["symbol"]
    cost_basis = Row(to).get_none_if_zero("cost_basis")
    return wallet, amount, currency, cost_basis


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
    raw_transactions_map = defaultdict(list)
    bronze_files = DataDirectory.BRONZE.value.joinpath("koinly_transactions").glob("**/*.json")
    for bronze_file in bronze_files:
        typer.echo(f"Processing {bronze_file.parent.name}/{bronze_file.name}")
        with open(bronze_file) as file:
            file_rows = file.readlines()
        for row in file_rows:
            raw_transactions_map[f"{bronze_file.parent.name}"].extend(json.loads(row)["transactions"])

    report_transactions_map = defaultdict(list)
    schema = ReportTransactionSchema()
    for date_partition, raw_transactions in raw_transactions_map.items():
        for raw_txn in raw_transactions:
            txn = {}
            if raw_txn["ignored"] is True:
                continue
            txn["id"] = raw_txn["id"]
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
            txn["fee_value_usd"] = Row(raw_txn).get_none_if_zero("fee_value")

            txn["gain_usd"] = Row(raw_txn).get_none_if_zero("gain")
            txn["net_value_usd"] = raw_txn["net_value"]
            txn["tx_src"] = raw_txn["txsrc"]
            txn["tx_dest"] = raw_txn["txdest"]
            txn["tx_hash"] = raw_txn["txhash"]
            txn["description"] = raw_txn["description"]

            report_transaction = schema.load(txn)
            report_transactions_map[date_partition].append(report_transaction)

    # De-dup transactions by transaction id, keeping transaction from most recent date partition.
    transaction_ids_by_date_parition_map = {}
    for key in sorted(report_transactions_map.keys()):
        transaction_ids_by_date_parition_map |= {txn.id: txn for txn in report_transactions_map[key]}

    report_transactions = sorted(transaction_ids_by_date_parition_map.values(), key=lambda txn: txn.date)
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
