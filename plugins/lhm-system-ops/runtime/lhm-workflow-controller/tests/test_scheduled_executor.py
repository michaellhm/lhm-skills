import hashlib
from pathlib import Path

import pytest

from lhm_workflow.scheduled_executor import compare_and_swap_tracker, snapshot_sources


def test_canonical_sources_drive_absolute_same_property_urls(tmp_path):
    project = tmp_path / "project.md"; project.write_text("Plan /services/seo and https://localhealthmarketing.com/about")
    operating = tmp_path / "operating.md"; operating.write_text("Canonical /contact")
    rollout = tmp_path / "rollout.md"; rollout.write_text("Next /blog/health")
    directory = tmp_path / "rollout"; directory.mkdir()
    (directory / "rollout-state.md").write_text("State /ahpra")
    (directory / "sitemap.json").write_text('{"url":"/locations/sydney"}')
    (directory / "LHM-Proposed-Sitemap.html").write_text('<a href="/services/web">Web</a>')
    records, urls = snapshot_sources([str(project), str(operating), str(rollout), str(directory)], tmp_path / "snapshots", "https://localhealthmarketing.com/")
    assert len(records) == 6
    assert "https://localhealthmarketing.com/services/seo" in urls
    assert "https://localhealthmarketing.com/locations/sydney" in urls
    assert all(url.startswith("https://localhealthmarketing.com/") for url in urls)
    assert all(Path(record["path"]).is_file() and len(record["sha256"]) == 64 for record in records)


def test_tracker_compare_and_swap_and_full_readback(tmp_path):
    tracker = tmp_path / "rollout-state.md"; tracker.write_bytes(b"old")
    expected = hashlib.sha256(b"old").hexdigest()
    receipt = compare_and_swap_tracker(tracker, expected, b"new")
    assert receipt["readback"] and tracker.read_bytes() == b"new"
    with pytest.raises(ValueError, match="conflict"):
        compare_and_swap_tracker(tracker, expected, b"duplicate")


def test_registered_configuration_is_readonly_and_native(tmp_path):
    import json
    registry = json.loads((Path(__file__).parents[1] / "integration" / "scheduled-workflows.json").read_text())
    definition = registry["workflows"]["local-health-marketing-seo"]
    assert definition["gsc"]["route"] == "seo_gsc_readonly"
    assert "request_indexing" not in definition["gsc"]["allowed_actions"]
    assert definition["profile_aliases"]["lhm_head_of_production"].endswith("/lhm_production")
    assert definition["profile_aliases"]["lhm_seo_lead"].endswith("/lhm_seo")
    assert definition["permission_ceiling"] == "non-production-preview"
