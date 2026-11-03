"""Shared, versioned API integration contract between WalletCo and PartnerBank.

- wallet_bank_contract.json: the contract itself (actions, shapes, clause IDs)
- models.py: Pydantic models for the request/response shapes
- contract.py: loads the JSON and builds the public summary
"""
