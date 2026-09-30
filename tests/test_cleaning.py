import pandas as pd

from e_commerce_sales_analysis.cleaning import (
    clean_city,
    classify_delivery_delay,
    classify_loyalty_tier,
    classify_route,
)


def test_clean_city_state_suffix():
    cities = pd.Series(["Sao Paulo - SP", "Rio de Janeiro/RJ"])
    result = clean_city(cities)
    assert result[0] == "Sao Paulo"
    assert result[1] == "Rio De Janeiro"


def test_clean_city_hyphen_and_spaces():
    cities = pd.Series(["Belo-Horizonte", "  Curitiba   "])
    result = clean_city(cities)
    assert result[0] == "Belo Horizonte"
    assert result[1] == "Curitiba"


def test_clean_city_accents():
    cities = pd.Series(["São Paulo", "Brasília", "Poços de Caldas"])
    result = clean_city(cities)
    assert result[0] == "Sao Paulo"
    assert result[1] == "Brasilia"
    assert result[2] == "Pocos De Caldas"


def test_clean_city_nulls():
    cities = pd.Series([None, "Sao Paulo"])
    result = clean_city(cities)
    assert pd.isna(result[0])
    assert result[1] == "Sao Paulo"


def test_clean_city_digits_and_mixed_case():
    cities = pd.Series(["campinas 123", "sALVADOR"])
    result = clean_city(cities)
    assert result[0] == "Campinas"
    assert result[1] == "Salvador"


def test_classify_route():
    cust_states = pd.Series(["SP", "RJ", "MG", None])
    seller_states = pd.Series(["SP", "SP", "RJ", "MG"])
    routes = classify_route(cust_states, seller_states)
    assert routes[0] == "Same State"
    assert routes[1] == "Inter-State"
    assert routes[2] == "Inter-State"
    assert routes[3] == "Unknown"


def test_classify_delivery_delay():
    delivered = pd.Series(["2017-02-10", "2017-03-25", None])
    estimated = pd.Series(["2017-02-15", "2017-03-20", "2017-04-01"])
    delays = classify_delivery_delay(delivered, estimated)
    assert delays[0] == "Early / On-Time"
    assert delays[1] == "Delayed"
    assert delays[2] == "In-Transit / Unknown"


def test_classify_loyalty_tier():
    counts = pd.Series([1, 2, 5, 0])
    tiers = classify_loyalty_tier(counts)
    assert tiers[0] == "One-Time Buyer"
    assert tiers[1] == "Repeat Buyer"
    assert tiers[2] == "Repeat Buyer"
    assert tiers[3] == "One-Time Buyer"
