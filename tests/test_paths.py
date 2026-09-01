import pytest
from pathlib import Path

from bahatanong_mcp.paths import BAHAMAP_PROCESSED, DATA_DIR


def test_data_dir_is_package_data():
    assert DATA_DIR.name == "data"
    assert DATA_DIR.parent.name == "bahatanong_mcp"
    assert DATA_DIR.is_dir()


@pytest.mark.skipif(not BAHAMAP_PROCESSED.exists(), reason="BahaMap checkout not present (CI)")
def test_bahamap_processed_exists_with_inputs():
    assert (BAHAMAP_PROCESSED / "barangay_master.parquet").exists()
    assert (BAHAMAP_PROCESSED / "briefs.json").exists()
