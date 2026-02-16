import json
import warnings

import bagit
from dcoraid.bagit import info, manifest


static_hashes = {
    "aaa": "9834876dcfb05cb167a5c24953eba58c4ac89b1adf57f28f2f9d09af107ee8f0",
    "abc": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    "äßé": "3c2c1fa6a81b3be946573478065cf438786267dba678fc57677505ec1686e468",
}


def test_get_payload_oxum(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    data_dir_2 = data_dir / "another"
    data_dir_2.mkdir()

    (data_dir / "a.txt").write_bytes(b"when ")
    (data_dir / "b.txt").write_bytes(b"the sun ")
    (data_dir / "c.txt").write_bytes(b"goes down ")

    (data_dir_2 / "a.txt").write_bytes(b"and the moon comes up")

    size = len("when the sun goes down and the moon comes up")
    num_files = 4

    assert info.get_payload_oxum(tmp_path) == f"{size}.{num_files}"


def test_write_bag_info(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "one.txt").write_text("aaa", encoding="utf-8")
    (data_dir / "two.json").write_text("abc", encoding="utf-8")
    (data_dir / "three.rtdc").write_text("äßé", encoding="utf-8",)

    ds_dict = {
        "resources": [
            {"name": "one.txt", "sha256": static_hashes["aaa"]},
            {"name": "two.json", "sha256": static_hashes["abc"]},
            {"name": "three.rtdc", "sha256": static_hashes["äßé"],
             "mimetype": "RT-DC"},
            ],
        "organization": {"name": "St. Johann im Pongau"},
        "name": "100-percent-fresh",
        "title": "The best dataset",
        }

    # write a condensed file
    (tmp_path / "data" / "three_condensed.rtdc").write_text("condensed")

    # write dataset.json
    (tmp_path / "data" / "dataset.json").write_text(json.dumps(ds_dict))

    info.write_bag_info(tmp_path, ds_dict)

    manifest.write_manifest(tmp_path, ds_dict)

    # self-contained checks
    assert (tmp_path / "manifest-sha256.txt").exists()
    assert (tmp_path / "bagit.txt").exists()
    assert (tmp_path / "tagmanifest-sha256.txt").exists()
    manifest.validate_tag_manifest(tmp_path)

    # use external bagit to verify bag as well
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bag = bagit.Bag(tmp_path)
        assert bag.is_valid()

    # change the oxum and make sure that bagit fails to verify
    bag_info = (tmp_path / "bag-info.txt").read_text(encoding="utf-8")
    (tmp_path / "bag-info.txt").write_text(bag_info.replace("466.5", "1.1"))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert not bag.is_valid()
