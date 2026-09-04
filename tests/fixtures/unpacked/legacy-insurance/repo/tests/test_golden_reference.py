from decimal import Decimal

def calculate(requested, cover, deductible, active=True):
    if not active:
        return ("REJECTED", Decimal("0.00"))
    approved = min(Decimal(requested), Decimal(cover))
    net = max(Decimal("0.00"), approved - Decimal(deductible))
    status = "MANUAL_REVIEW" if approved > Decimal("200000.00") else "APPROVED"
    return status, net

def test_coverage_and_deductible():
    assert calculate("100000.00", "500000.00", "5000.00") == ("APPROVED", Decimal("95000.00"))

def test_coverage_cap():
    assert calculate("600000.00", "500000.00", "5000.00") == ("MANUAL_REVIEW", Decimal("495000.00"))

def test_manual_review_threshold():
    assert calculate("250001.00", "500000.00", "5000.00") == ("MANUAL_REVIEW", Decimal("245001.00"))

def test_inactive_policy():
    assert calculate("50000.00", "250000.00", "2500.00", False) == ("REJECTED", Decimal("0.00"))
