"""Explicit optional tests against a real, separately started model (not mocked)."""
import os
import pytest
from reportlab.pdfgen import canvas
from services.api.engines import run_engine
pytestmark=pytest.mark.skipif(os.getenv('RUN_LIVE_AI_TESTS')!='1',reason='Set RUN_LIVE_AI_TESTS=1 and configure a real local provider')
@pytest.mark.parametrize('slug',['resumir-pdf','traduzir-pdf'])
def test_real_model_provider(tmp_path,slug):
 p=tmp_path/'source.pdf';c=canvas.Canvas(str(p));c.drawString(50,700,'Ana manages the project. The total budget is 120 dollars.');c.showPage();c.save()
 result=run_engine(slug,[p],{'summary_length':'short','target_language':'pt-BR'},tmp_path/'out')
 generated=(tmp_path/'out'/result['filename']).read_text();assert '120' in generated;assert 'Ana' in generated;assert 'Contract test' not in generated;assert 'projeto' in generated.lower();assert 'orçamento' in generated.lower()
 print(f'\n{slug}: {generated}')
