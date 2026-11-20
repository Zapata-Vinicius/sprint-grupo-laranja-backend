import hashlib
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import requests

from app.integrations.gtfs.cliente_gtfs import GTFS_URL_PADRAO, calcular_hash_gtfs
from app.services.verificacao_gtfs import verificar_gtfs


class Resposta:
    def __init__(self, partes):
        self.partes = partes

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def raise_for_status(self):
        pass

    def iter_content(self, chunk_size):
        return iter(self.partes)


class TesteCliente(unittest.TestCase):
    def test_hash_do_zip_em_partes(self):
        partes = [b"PK", b"\x03\x04conteudo"]
        with patch("app.integrations.gtfs.cliente_gtfs.requests.get", return_value=Resposta(partes)):
            self.assertEqual(calcular_hash_gtfs("https://example.org/gtfs.zip"), hashlib.sha256(b"".join(partes)).hexdigest())

    def test_rejeita_html(self):
        with patch("app.integrations.gtfs.cliente_gtfs.requests.get", return_value=Resposta([b"<html>login</html>"])):
            with self.assertRaises(ValueError):
                calcular_hash_gtfs("https://example.org/gtfs.zip")


class TesteVerificacao(unittest.IsolatedAsyncioTestCase):
    async def test_compara_e_preserva_resultado_em_falha(self):
        estado = SimpleNamespace(gtfs=None, gtfs_erro=None)
        with patch("app.services.verificacao_gtfs.load_dotenv"), patch.dict("os.environ", {"GTFS_URL": "https://example.org/gtfs.zip"}), patch("app.services.verificacao_gtfs.calcular_hash_gtfs", side_effect=["a", "a", "b", requests.ConnectionError()]) as calcular:
            await verificar_gtfs(estado)
            self.assertIsNone(estado.gtfs["alterado"])
            await verificar_gtfs(estado)
            self.assertFalse(estado.gtfs["alterado"])
            await verificar_gtfs(estado)
            self.assertTrue(estado.gtfs["alterado"])
            ultimo = estado.gtfs.copy()
            await verificar_gtfs(estado)
            self.assertEqual(estado.gtfs, ultimo)
            self.assertIsNotNone(estado.gtfs_erro)
            calcular.assert_called_with("https://example.org/gtfs.zip")

    async def test_url_padrao(self):
        estado = SimpleNamespace(gtfs=None, gtfs_erro=None)
        with patch("app.services.verificacao_gtfs.load_dotenv"), patch.dict("os.environ", {}, clear=True), patch("app.services.verificacao_gtfs.calcular_hash_gtfs", return_value="a") as calcular:
            await verificar_gtfs(estado)
        calcular.assert_called_once_with(GTFS_URL_PADRAO)


if __name__ == "__main__":
    unittest.main()
