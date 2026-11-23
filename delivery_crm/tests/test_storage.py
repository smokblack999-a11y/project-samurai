import pytest

from delivery_crm.storage import DeliveryStore


def test_manual_payment_and_delivery_lifecycle(tmp_path):
    store = DeliveryStore(str(tmp_path / "orders.sqlite3"))
    order_id = store.create_order(1001, "Customer", "Two boxes", "+77001234567", "Almaty, Abay 10")

    assert store.get_order(order_id)["status"] == "awaiting_details"
    assert not store.approve(order_id)
    assert store.submit_receipt(order_id, 1001, "receipt-file-id")
    assert not store.submit_receipt(order_id, 1002, "other-user-file-id")
    assert store.approve(order_id)
    assert not store.approve(order_id)
    assert store.assign(order_id, 2002)
    assert not store.assign(order_id, 2003)
    assert store.mark_delivered(order_id, 2002, "delivery-photo-id")["status"] == "delivered"
    assert store.mark_delivered(order_id, 2002, "second-photo-id") is None


def test_receipt_required_before_approval(tmp_path):
    store = DeliveryStore(str(tmp_path / "orders.sqlite3"))
    order_id = store.create_order(1001, "Customer", "Order", "+77001234567", "Almaty, Abay 10")
    assert not store.approve(order_id)


def test_invalid_courier_cannot_complete_order(tmp_path):
    store = DeliveryStore(str(tmp_path / "orders.sqlite3"))
    order_id = store.create_order(1001, "Customer", "Order", "+77001234567", "Almaty, Abay 10")
    store.submit_receipt(order_id, 1001, "receipt")
    store.approve(order_id)
    store.assign(order_id, 2002)
    assert store.mark_delivered(order_id, 9999, "photo") is None


def test_database_file_is_owner_only(tmp_path):
    import os
    import pytest

    if os.name != "posix":
        pytest.skip("POSIX file permissions are not available")
    db_path = tmp_path / "private-orders.sqlite3"
    DeliveryStore(str(db_path))
    assert db_path.stat().st_mode & 0o777 == 0o600
