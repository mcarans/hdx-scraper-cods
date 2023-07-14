import argparse
import logging
from os.path import expanduser, join

from cods import COD

from hdx.api.configuration import Configuration
from hdx.location.country import Country
from hdx.data.dataset import Dataset
from hdx.data.hdxobject import HDXError
from hdx.facades.keyword_arguments import facade
from hdx.utilities.downloader import Download
from hdx.utilities.errors_onexit import ErrorsOnExit
from hdx.utilities.path import temp_dir
from hdx.utilities.retriever import Retrieve

logger = logging.getLogger(__name__)

lookup = "hdx-scraper-cods"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-co", "--countries_override", default=None, help="Countries to run"
    )
    parser.add_argument(
        "-sv", "--save", default=False, action="store_true", help="Save downloaded data"
    )
    parser.add_argument(
        "-usv", "--use_saved", default=False, action="store_true", help="Use saved data",
    )
    args = parser.parse_args()
    return args


def main(
    countries_override,
    save,
    use_saved,
    **ignore,
):
    configuration = Configuration.read()
    with ErrorsOnExit() as errors:
        with temp_dir() as temp_folder:
            with Download() as downloader:
                retriever = Retrieve(
                    downloader, temp_folder, "saved_data", temp_folder, save, use_saved
                )
                cod = COD(
                    retriever,
                    configuration["ab_url"],
                    configuration["em_url"],
                    configuration["ps_url"],
                    errors,
                )

                boundary_jsons = cod.get_boundary_jsons()
                if len(boundary_jsons) < 2:
                    cod.errors.add("Could not get boundary service data")
                    return

                countries = Country.countriesdata()["countries"]
                if countries_override:
                    countries = {
                        country.upper(): countries.get(country.upper()) for country in countries_override
                    }
                dataset_types = ["ab", "em", "ps"]

                for country in countries:
                    for dataset_type in dataset_types:
                        try:
                            dataset = Dataset.read_from_hdx(f"cod-{dataset_type}-{country.lower()}")
                        except HDXError:
                            logger.warning(f"Could not read cod-{dataset_type}-{country.lower()}")
                            continue

                        if not dataset:
                            continue

                        updated_dataset = cod.update_dataset(dataset, countries[country], dataset_type, boundary_jsons)

                        if not updated_dataset:
                            continue

                        if save:
                            dataset.save_to_json(join("saved_data", f"dataset-{dataset['name']}.json"))
                            updated_dataset.save_to_json(join("saved_data", f"dataset-{dataset['name']}_updated.json"))

                        try:
                            updated_dataset.create_in_hdx(
                                hxl_update=False,
                                batch_mode="KEEP_OLD",
                                updated_by_script="HDX Scraper: CODS",
                                remove_additional_resources=True,
                                ignore_fields=["num_of_rows", "resource:description"],
                            )
                        except HDXError as ex:
                            logger.exception(f"Dataset: {updated_dataset['name']} could not be uploaded")
                            errors.add(f"Dataset: {updated_dataset['name']}, error: {ex}")


if __name__ == "__main__":
    args = parse_args()
    if args.countries_override:
        countries_override = args.countries_override.split(",")
    else:
        countries_override = None
    facade(
        main,
        hdx_site="prod",
        user_agent_config_yaml=join(expanduser("~"), ".useragents.yml"),
        user_agent_lookup=lookup,
        project_config_yaml=join("config", "project_configuration.yml"),
        countries_override=countries_override,
        save=args.save,
        use_saved=args.use_saved,
    )
