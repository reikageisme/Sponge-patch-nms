# Dùng: make tables | make check | make package   (Windows không có make: chạy trực tiếp các lệnh python bên dưới)
PY ?= python -X utf8
tables:
	$(PY) tables/make_tables.py
check:
	$(PY) tables/check_numbers.py --all
package: check
	$(PY) build_submission.py
