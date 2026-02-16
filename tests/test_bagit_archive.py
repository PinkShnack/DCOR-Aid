import warnings
import uuid

import bagit
from dcoraid.bagit import archive

from . import common


def test_bag_circle(tmp_path):
    api = common.get_api()
    # create a circle for this purpose
    circle = f"circle-bag-{uuid.uuid4()}"
    api.post("organization_create", data={"name": circle})
    common.make_dataset_for_download(circle=circle)
    common.make_dataset_for_download(circle=circle, add_text_file=True)
    archive.bag_circle(api=api,
                       circle_name=circle,
                       target_path=tmp_path,
                       )

    assert (tmp_path / "circle.jsonlines").exists()

    bags = sorted([d for d in tmp_path.glob("*") if d.is_dir()])
    assert (bags[1] / "data" / "text_file.txt").exists()

    for bag_path in bags:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            bag = bagit.Bag(bag_path)
            assert bag.is_valid()


def test_bag_dataset(tmp_path):
    api = common.get_api()
    ds_dict = common.make_dataset_for_download()

    archive.bag_dataset(
        api=api,
        ds_dict=ds_dict,
        bag_path=tmp_path,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bag = bagit.Bag(tmp_path)
        assert bag.is_valid()


def test_bag_dataset_multiple_resources(tmp_path):
    api = common.get_api()
    ds_dict = common.make_dataset_for_download(add_text_file=True)

    archive.bag_dataset(
        api=api,
        ds_dict=ds_dict,
        bag_path=tmp_path,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        bag = bagit.Bag(tmp_path)
        assert bag.is_valid()


def test_download_resource(tmp_path):
    api = common.get_api()
    ds_dict = common.make_dataset_for_download()
    res_dict = ds_dict["resources"][0]

    archive.download_resource(api=api,
                              bag_path=tmp_path,
                              res_dict=res_dict,
                              condensed=False,
                              )

    assert (tmp_path / "data" / res_dict["name"]).exists()
    assert (tmp_path / "data" / res_dict["name"]).stat().st_size == 899298
