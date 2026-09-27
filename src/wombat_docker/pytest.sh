#
# Title: pytest.sh
# Description: invoke pytest for validator
#
source venv/bin/activate
python -m pytest -q test_validator.py
#