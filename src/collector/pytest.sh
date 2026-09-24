#
# Title: pytest.sh
# Description: invoke pytest for collector
# 
source venv/bin/activate
python -m pytest -q test_collector.py
#