"""Business transformation and classification utilities for Olist data."""

import numpy as np
import pandas as pd


def classify_route(customer_state: pd.Series, seller_state: pd.Series) -> pd.Series:
    """Classify delivery route into 'Same State' vs 'Inter-State'.

    Returns:
        pd.Series: Categorical classification of the delivery route.
    """
    conditions = [
        customer_state.isna() | seller_state.isna(),
        customer_state.str.upper().str.strip() == seller_state.str.upper().str.strip(),
    ]
    choices = ["Unknown", "Same State"]
    return pd.Series(
        np.select(conditions, choices, default="Inter-State"),
        index=customer_state.index,
    )


def classify_delivery_delay(
    delivered_date: pd.Series, estimated_date: pd.Series
) -> pd.Series:
    """Classify order fulfillment timing against carrier estimates.

    Returns:
        pd.Series: 'Early / On-Time', 'Delayed', or 'In-Transit / Unknown'
    """
    delivered = pd.to_datetime(delivered_date, errors="coerce")
    estimated = pd.to_datetime(estimated_date, errors="coerce")

    conditions = [
        delivered.isna(),
        delivered <= estimated,
        delivered > estimated,
    ]
    choices = ["In-Transit / Unknown", "Early / On-Time", "Delayed"]
    return pd.Series(
        np.select(conditions, choices, default="In-Transit / Unknown"),
        index=delivered_date.index,
    )


def classify_loyalty_tier(order_counts: pd.Series) -> pd.Series:
    """Classify customers into One-Time Buyer vs Repeat Buyer based on order count.

    Returns:
        pd.Series: 'Repeat Buyer' if order_count > 1 else 'One-Time Buyer'
    """
    counts = pd.to_numeric(order_counts, errors="coerce").fillna(0)
    return pd.Series(
        np.where(counts > 1, "Repeat Buyer", "One-Time Buyer"),
        index=order_counts.index,
    )
