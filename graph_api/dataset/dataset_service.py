from database_service import DatabaseService
from database_config import database
from dataset.dataset_model import DatasetOut, DatasetIn, DatasetsOut, BasicDatasetOut
from property.property_model import PropertyIn
from typing import List
import random
import string


class DatasetService:
    """
    Object to handle logic of datasets requests

    Attributes:
        db (DatabaseService): Handles communication with Neo4j database
    """
    db: DatabaseService = DatabaseService()

    def create_dataset(self, name_by_user):
        """
        Send request to database by its API to create new dataset

        Returns:
            Result of request as dataset object
        """
        name_hash = self.generate_random_dataset_hash(10)

        create_dataset_response = self.db.create_dataset(name_hash)

        if len(create_dataset_response["errors"]) > 0:
            return DatasetOut(errors=create_dataset_response["errors"])

        return DatasetOut(name_hash=name_hash, name_by_user=name_by_user)

    def generate_random_dataset_hash(self, string_length: int):
        """
        Create a random string which will be used as the name of the dataset

        Args:
            string_length (str): length of the generated string

        Returns:
            Random string of lowercase letters
        """
        while True:
            name_hash = ''.join(random.choices(string.ascii_lowercase, k=string_length))
            # todo: solve this error
            #   if self.db.dataset_exists(name_hash) is False:
                #break
            break
        return name_hash

    def create_alias_for_database_with_name(self, name_hash, name_by_user):
        """
        Create nodes in dataset which hold additional information about the dataset

        Args:
            name_hash (str): Name of the dataset generated by the system (random string)
            name_by_user: (str): Name of the dataset given by user

        Returns:
            Model of dataset with detailed information
        """
        create_alias_name_response = self.db.create_alias_for_dataset("name_hash", name_hash, name_hash)

        if len(create_alias_name_response["errors"]) > 0:
            return DatasetOut(errors=create_alias_name_response["errors"])

        create_alias_hash_response = self.db.create_alias_for_dataset("name_by_user", name_by_user, name_hash)

        if len(create_alias_hash_response["errors"]) > 0:
            return DatasetOut(errors=create_alias_hash_response["errors"])

        return DatasetOut(name_hash=name_hash, name_by_user=name_by_user)

    def get_dataset(self, name_hash: str):
        """
        Send request to database by its API to acquire a dataset with given name

        Args:
            name_hash (string): Name of the database (dataset_name)

        Returns:
            List of acquired nodes in NodesOut model
        """
        # found = self.db.dataset_exists(name_hash)
        #
        # if not found:
        #     return DatasetOut(errors="Dataset not found")
        #
        # # get the alias from the DB
        # get_aliases_response = self.db.get_aliases_from_database(name_hash)
        # name_by_user = ""
        # for row in get_aliases_response["results"][0]["data"]:
        #     if "row" in row:
        #         if "name_by_user" in row['row'][0]:
        #             name_by_user = row['row'][0]['name_by_user']
        # return DatasetOut(name_hash=name_hash, name_by_user=name_by_user)

        response = self.db.get_aliases_from_database(name_hash)

        if len(response["errors"]) > 0:
            return DatasetOut(errors=response["errors"])

        name_by_user = ""
        for row in response["results"][0]["data"]:
            if "row" in row:
                if "name_by_user" in row['row'][0]:
                    name_by_user = row['row'][0]['name_by_user']

        result = DatasetOut(name_hash=name_hash, name_by_user=name_by_user)
        return result

    def get_datasets(self):
        """
        Send request to database by its API to acquire all datasets

        Returns:
            List of acquired datasets in DatasetsOut model
        """
        # It don't have to be 'neo4j', any existing database will work
        database_name = "neo4j"
        response = self.db.get_datasets(database_name)
        if len(response["errors"]) > 0:
            return DatasetsOut(errors=response["errors"])

        result = DatasetsOut(datasets=[])

        for dataset in response["results"][0]["data"]:
            result.datasets.append(BasicDatasetOut(name_hash=dataset['row'][0]))

        return result

    def delete_dataset(self, dataset_name: str):
        """
        Send request to database by its API to delete a dataset with given name

        Args:
            dataset_name (str):  Name of the dataset to be deleted

        Returns:
            Deleted dataset
        """
        dataset = self.get_dataset(dataset_name)
        response = self.db.delete_dataset(dataset_name)
        if len(response['errors']) > 0:
            return DatasetOut(errors=response['errors'])
        else:
            return DatasetOut(name_hash=dataset.name_hash, name_by_user=dataset.name_by_user)
