import pytest
from backend.app.logic.verification import VerificadorRFID



# ------------------------
# Tests VerificadorRFID
# ------------------------

@pytest.fixture
def rfid_verificador():
    return VerificadorRFID()

def test_rfid_codigo_existente(rfid_verificador):
    result = rfid_verificador.verificar({"Codigo": "ABC123"})
    assert result == (True, 1)

def test_rfid_otro_codigo_existente(rfid_verificador):
    result = rfid_verificador.verificar({"Codigo": "XYZ789"})
    assert result == (True, 2)

def test_rfid_codigo_inexistente(rfid_verificador):
    result = rfid_verificador.verificar({"Codigo": "NOEXISTE"})
    assert result == (False, None)

def test_rfid_sin_codigo(rfid_verificador):
    result = rfid_verificador.verificar({})
    assert result == (False, None)