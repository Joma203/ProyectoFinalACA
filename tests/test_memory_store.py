"""Tests para app/storage/memory_store.py"""
import uuid

from app.storage.memory_store import get_report, save_report


class TestMemoryStore:

    def test_save_returns_string_id(self):
        report_id = save_report({"x": 1})
        assert isinstance(report_id, str)

    def test_save_returns_valid_uuid(self):
        report_id = save_report({"x": 1})
        # Si no es un UUID válido, lanza ValueError
        uuid.UUID(report_id)

    def test_get_returns_saved_data(self):
        data = {"summary": {"critical": 1}, "vulnerabilities": []}
        report_id = save_report(data)
        assert get_report(report_id) == data

    def test_get_nonexistent_returns_none(self):
        assert get_report("no-existe") is None

    def test_each_save_gets_unique_id(self):
        ids = {save_report({}) for _ in range(20)}
        assert len(ids) == 20  # todos únicos

    def test_save_does_not_mutate_input(self):
        data = {"a": 1}
        save_report(data)
        assert data == {"a": 1}
