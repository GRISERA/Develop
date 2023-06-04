from typing import Union
from pydantic import BaseModel
import pymongo
from bson import ObjectId
from datetime import datetime, timezone

from time_series.time_series_model import (
    SignalIn,
    SignalValueNodesIn,
    TimeSeriesIn,
)
from models.not_found_model import NotFoundByIdModel
from mongo_service.collection_mapping import get_collection_name, Collections
from mongo_service.mongodb_api_config import mongo_api_address, mongo_database_name


class MongoApiService:
    """
    Object that handles direct communication with mongodb
    """

    MONGO_ID_FIELD = "_id"
    MODEL_ID_FIELD = "id"
    TIMESTAMP_FIELD = "timestamp"
    METADATA_FIELD = "metadata"

    def __init__(self):
        """
        Connect to MongoDB database
        """
        self.client = pymongo.MongoClient(mongo_api_address)
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

    def get_document(self, id: Union[str, int], collection_name: str, *args, **kwargs):
        """
        Load single document. Output id fields are converted from ObjectId type to str.
        """
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

    def get_documents(self, collection_name: str, query: dict = {}, *args, **kwargs):
        """
        Load many documents. Output id fields are converted from ObjectId type to str.
        """
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

    def create_time_series(self, time_series_in: TimeSeriesIn):
        collection_name = Collections.TIME_SERIES
        self._create_ts_collection_if_missing(collection_name)
        ts_id = ObjectId()
        ts_documents = self._time_series_into_documents(time_series_in, ts_id)
        self.db[collection_name].insert_many(ts_documents)
        return ts_id

    def get_time_series(
        self,
        ts_id: Union[str, int],
        signal_min_value: int = None,
        signal_max_value: int = None,
    ):
        """
        Return dict with single time series data
        """
        collection_name = Collections.TIME_SERIES
        query = self._create_ts_query(ts_id, signal_min_value, signal_max_value)
        time_series_documents = list(self.db[collection_name].find(query))
        if len(time_series_documents) == 0:
            return NotFoundByIdModel(
                id=ts_id,
                errors={"errors": "time series not found"},
            )
        return self._time_series_documents_to_dict(time_series_documents)

    def get_many_time_series(self, query={}):
        self._fix_input_ids(query)
        ts_documents = self._get_many_ts(query)
        return [
            self._time_series_documents_to_dict(ts_document["value"])
            for ts_document in ts_documents
        ]

    def update_time_series_metadata(
        self, fields_to_update: dict, time_series_id: Union[int, str]
    ):
        ts_id = ObjectId(time_series_id)
        query = {f"{self.METADATA_FIELD}.id": ts_id}
        update_dict = {
            f"{self.METADATA_FIELD}.{field}": value
            for field, value in fields_to_update.items()
        }
        return self.db[Collections.TIME_SERIES].update_many(
            filter=query, update={"$set": update_dict}
        )

    def update_time_series_properties(
        self, new_time_series: dict, time_series_id: Union[int, str]
    ):
        existing_ts = self.get_time_series(time_series_id)
        new_time_series["observable_information_id"] = existing_ts[
            "observable_information_id"
        ]
        new_time_series["measure_id"] = existing_ts["measure_id"]

        self._replace_ts(new_time_series, time_series_id)
        return new_time_series

    def delete_time_series(self, time_series_id: Union[int, str]):
        ts_id = ObjectId(time_series_id)
        query = {f"{self.METADATA_FIELD}.id": ts_id}
        return self.db[Collections.TIME_SERIES].delete_many(filter=query)

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

    def _fix_input_ids(self, mongo_query):
        """
        Mongo uses ObjectId in id fields, while models use int/str. This function
        performs conversion on each id field in input query.
        """

        def fix_input_id(field, value):
            if self._field_is_id(field) and value is not None:
                return ObjectId(value)
            return value

        self._mongo_object_deep_iterate(mongo_query, fix_input_id)

    def _fix_output_ids(self, mongo_document):
        """
        Mongo uses ObjectId in id fields, while models use int/str. This function
        performs conversion on each id field in output dict.
        """

        def fix_output_id(field, value):
            if self._field_is_id(field) and value is not None:
                return str(value)
            return value

        self._mongo_object_deep_iterate(mongo_document, fix_output_id)

    @staticmethod
    def _field_is_id(field):
        if type(field) is not str:
            return False
        return field == "id" or field[-3:] in ("_id", ".id")

    def _mongo_object_deep_iterate(self, mongo_object: dict, func):
        """
        Call a function on each primitive value in mongo output document or input query
        dict. Mongo document field values are either primitives, dicts or arrays.
        """
        if type(mongo_object) is not dict:
            return
        for field, value in mongo_object.items():
            if type(value) is dict:
                self._mongo_object_deep_iterate(value, func)
            elif type(value) is list:
                for list_elem in value:
                    self._mongo_object_deep_iterate(list_elem, func)
            else:
                mongo_object[field] = func(field, mongo_object[field])

    def _create_ts_collection_if_missing(self, collection_name: str):
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(
                collection_name,
                timeseries={
                    "timeField": self.TIMESTAMP_FIELD,
                    "metaField": self.METADATA_FIELD,
                },
            )

    def _time_series_into_documents(
        self, time_series_in: TimeSeriesIn, time_series_id: ObjectId
    ):
        signal_values = time_series_in.signal_values

        time_series_in.signal_values = []  # avoid unnecessary parsing of signal values
        metadata = self._get_time_series_metadata(time_series_in, time_series_id)
        return [
            {
                self.TIMESTAMP_FIELD: datetime.fromtimestamp(
                    signal.timestamp, tz=timezone.utc
                ),
                self.METADATA_FIELD: metadata,
                **signal.signal_value.dict(),
            }
            for signal in signal_values
        ]

    def _get_time_series_metadata(
        self, time_series_in: TimeSeriesIn, time_series_id: ObjectId
    ):
        time_series_dict = time_series_in.dict()
        time_series_dict.pop("signal_values")
        metadata = time_series_dict

        self._fix_input_ids(metadata)
        metadata["id"] = time_series_id
        return metadata

    def _time_series_documents_to_dict(self, ts_documents: list[dict]):
        """
        Convert documents from single time series to BasicTimeSeriesOut
        """
        signal_values = [
            self._signal_from_ts_document(document) for document in ts_documents
        ]
        result = {
            "signal_values": signal_values,
            **ts_documents[0][self.METADATA_FIELD],
        }
        self._fix_output_ids(result)
        return result

    def _signal_from_ts_document(self, document):
        return SignalIn(
            timestamp=document[self.TIMESTAMP_FIELD]
            .replace(tzinfo=timezone.utc)
            .timestamp(),
            signal_value=SignalValueNodesIn(
                value=document["value"],
                additional_properties=document["additional_properties"],
            ),
        )

    def _create_ts_query(
        self,
        ts_id: Union[str, int],
        signal_min_value: int = None,
        signal_max_value: int = None,
    ):
        query = {f"{self.METADATA_FIELD}.id": ObjectId(ts_id)}

        value_query = {}
        if signal_min_value is not None:
            value_query["$gte"] = signal_min_value
        if signal_max_value is not None:
            value_query["$lte"] = signal_max_value
        if len(value_query) > 0:
            query["value"] = value_query

        return query

    def _get_many_ts(self, query={}):
        aggregation = [
            {"$match": query},
            {"$group": {"_id": "$metadata.id", "value": {"$push": "$$ROOT"}}},
        ]
        return self.db[Collections.TIME_SERIES].aggregate(aggregation)

    def _replace_ts(self, new_time_series: dict, time_series_id: Union[int, str]):
        with self.client.start_session() as session:
            with session.start_transaction():
                self.delete_time_series(time_series_id)
                self.create_time_series(TimeSeriesIn(**new_time_series))