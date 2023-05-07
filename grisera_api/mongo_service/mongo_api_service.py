from typing import Union
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from grisera_api.mongo_service.utils import mongo_deep_iteration

from models.not_found_model import NotFoundByIdModel
from mongo_service.collection_mapping import get_collection_name
from mongo_service.mongodb_api_config import mongo_api_address, mongo_database_name


class MongoApiService:
    """
    Object that handles direct communication with mongodb
    """

    MONGO_ID_FIELD = "_id"
    MODEL_ID_FIELD = "id"

    def __init__(self):
        """
        Connect to MongoDB database
        """
        self.client = MongoClient(mongo_api_address)
        self.db = self.client[mongo_database_name]

    def create_document(self, data_in: BaseModel):
        """
        Create new document. Id fields are converted to ObjectId type.
        """
        collection_name = get_collection_name(type(data_in))
        data_as_dict = data_in.dict()
        self._fix_input_ids(data_as_dict)
        created_id = self.db[collection_name].insert_one(data_as_dict).inserted_id
        return str(created_id)

    def get_document(self, id: Union[str, int], model_class, *args, **kwargs):
        """
        Load single document. Output id fields are converted from ObjectId type to str.
        """
        collection_name = get_collection_name(model_class)
        result_dict = self.db[collection_name].find_one(
            {self.MONGO_ID_FIELD: ObjectId(id)}, *args, **kwargs
        )

        if result_dict is None:
            return NotFoundByIdModel(
                id=id,
                errors={"errors": "document not found"},
            )

        self._update_mongo_output_id(result_dict)
        return result_dict

    def get_documents(self, model_class, query: dict = {}, *args, **kwargs):
        """
        Load many documents. Output id fields are converted from ObjectId type to str.
        """
        collection_name = get_collection_name(model_class)
        self._fix_input_ids(query)
        results = list(self.db[collection_name].find(query, *args, **kwargs))

        [self._update_mongo_output_id(result) for result in results]

        return results

    def update_document(self, id: Union[str, int], data_to_update: BaseModel):
        """
        Update document.
        """
        collection_name = get_collection_name(type(data_to_update))
        data_as_dict = data_to_update.dict()
        self._update_document_with_dict(collection_name, id, data_as_dict)

    def _update_document_with_dict(
        self, collection_name: str, id: Union[str, int], new_document: dict
    ):
        """
        Update document with new document as dict. Id fields are converted to ObjectId type.
        """
        self._update_mongo_input_id(new_document)
        id = ObjectId(id)
        self.db[collection_name].replace_one(
            {self.MONGO_ID_FIELD: id},
            new_document,
        )

    def delete_document(self, object_to_delete: BaseModel):
        """
        Delete document in collection. Given model must have id field.
        """
        id_str = getattr(object_to_delete, self.MODEL_ID_FIELD, None)
        if id_str is None:
            raise TypeError(
                f"Given model object does not have '{self.MODEL_ID_FIELD}' field"
            )
        id = ObjectId(id_str)
        collection_name = get_collection_name(type(object_to_delete))
        self.db[collection_name].delete_one({self.MONGO_ID_FIELD: id})
        return id

    def _update_mongo_input_id(self, mongo_input: dict):
        """
        Mongo documents id fields are '_id' while models fields are 'id'. Here id field is
        renamed and other id fields (relation fields) types are converted.
        """
        if self.MODEL_ID_FIELD in mongo_input:
            mongo_input[self.MONGO_ID_FIELD] = ObjectId(
                mongo_input[self.MODEL_ID_FIELD]
            )
        del mongo_input[self.MODEL_ID_FIELD]
        self._fix_input_ids(mongo_input)

    def _update_mongo_output_id(self, mongo_output: dict):
        """
        Mongo documents id fields are '_id' while models fields are 'id'. Here id field is
        renamed and other id fields (relation fields) types are converted.
        """
        if self.MONGO_ID_FIELD in mongo_output:
            mongo_output[self.MODEL_ID_FIELD] = str(mongo_output[self.MONGO_ID_FIELD])
        del mongo_output[self.MONGO_ID_FIELD]
        self._fix_output_ids(mongo_output)

    @mongo_deep_iteration
    def _fix_input_ids(self, field):
        """
        Mongo uses ObjectId in id fields, while models use int/str. This function
        performs conversion on each id field in input query.
        """
        if self._field_is_id(field):
            return ObjectId(field)
        return field

    @mongo_deep_iteration
    def _fix_output_ids(self, field):
        """
        Mongo uses ObjectId in id fields, while models use int/str. This function
        performs conversion on each id field in output dict.
        """
        if self._field_is_id(field):
            return str(field)
        return field

    @staticmethod
    def _field_is_id(field):
        if type(field) is not str:
            return False
        return field == "id" or field[-3:] in ("_id", ".id")


mongo_api_service = MongoApiService()