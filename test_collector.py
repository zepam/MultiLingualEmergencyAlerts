import os
import json
import tempfile
import logging
import shutil
import pytest
from collector import Collector

class DummyLogger:
    def __init__(self):
        self.messages = []
    def info(self, msg):
        self.messages.append(('info', msg))
    def error(self, msg):
        self.messages.append(('error', msg))

@pytest.fixture
def temp_output_file():
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, "output.json")
    yield output_file
    shutil.rmtree(temp_dir)

def test_add_response_non_google_translate(temp_output_file):
    logger = DummyLogger()
    collector = Collector(output_file=temp_output_file, logger=logger, batch_size=2)
    collector.add_response("chatgpt", "spanish", "flood", "prompt_simple.txt", "respuesta1")
    collector.add_response("chatgpt", "spanish", "flood", "prompt_simple.txt", "respuesta2")
    # Should trigger save after 2nd response
    assert os.path.exists(temp_output_file)
    with open(temp_output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "chatgpt" in data
    assert "spanish" in data["chatgpt"]
    assert "flood" in data["chatgpt"]["spanish"]
    assert "prompt_simple.txt" in data["chatgpt"]["spanish"]["flood"]
    responses = data["chatgpt"]["spanish"]["flood"]["prompt_simple.txt"]
    assert len(responses) == 2
    assert all("response" in r and "timestamp" in r for r in responses)

def test_add_response_google_translate(temp_output_file):
    logger = DummyLogger()
    collector = Collector(output_file=temp_output_file, logger=logger, batch_size=1)
    collector.add_response("google_translate", "spanish", "flood", None, "traduccion1")
    assert os.path.exists(temp_output_file)
    with open(temp_output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "google_translate" in data
    assert "spanish" in data["google_translate"]
    assert "flood" in data["google_translate"]["spanish"]
    responses = data["google_translate"]["spanish"]["flood"]
    assert isinstance(responses, list)
    assert len(responses) == 1
    assert "response" in responses[0] and "timestamp" in responses[0]

def test_save_remaining(temp_output_file):
    logger = DummyLogger()
    collector = Collector(output_file=temp_output_file, logger=logger, batch_size=10)
    collector.add_response("chatgpt", "spanish", "fire", "prompt1.txt", "respuestaX")
    # Should not save yet
    assert not os.path.exists(temp_output_file)
    collector.save_remaining()
    assert os.path.exists(temp_output_file)
    with open(temp_output_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "chatgpt" in data
    assert "fire" in data["chatgpt"]["spanish"]
    assert "prompt1.txt" in data["chatgpt"]["spanish"]["fire"]
    responses = data["chatgpt"]["spanish"]["fire"]["prompt1.txt"]
    assert len(responses) == 1
    assert "response" in responses[0] and "timestamp" in responses[0]

def test_directory_creation_and_error_handling(monkeypatch, tmp_path):
    logger = DummyLogger()
    output_file = tmp_path / "subdir" / "output.json"
    collector = Collector(str(output_file), logger=logger, batch_size=1)
    # Simulate OSError on directory creation
    def bad_makedirs(*args, **kwargs):
        raise OSError("fail mkdir")
    monkeypatch.setattr(os, "makedirs", bad_makedirs)
    collector.add_response("chatgpt", "spanish", "flood", "prompt.txt", "respuesta")
    # Should log an error
    assert any("fail mkdir" in msg for level, msg in logger.messages if level == "error")

