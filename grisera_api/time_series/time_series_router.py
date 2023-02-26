from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from hateoas import get_links
from time_series.time_series_model import TimeSeriesIn, TimeSeriesNodesOut, TimeSeriesOut, \
    TimeSeriesPropertyIn, TimeSeriesRelationIn
from time_series.time_series_service import TimeSeriesService
from typing import Union
from models.not_found_model import NotFoundByIdModel
from services import Services

router = InferringRouter()


@cbv(router)
class TimeSeriesRouter:
    """
    Class for routing time series based requests

    Attributes:
        time_series_service (TimeSeriesService): Service instance for time series
    """
    def __init__(self):
        self.time_series_service = Services().time_series_service()

    @router.post("/time_series", tags=["time series"], response_model=TimeSeriesOut)
    async def create_time_series(self, time_series: TimeSeriesIn, response: Response, database_name: str):
        """
        Create time series in database
        """

        create_response = self.time_series_service.save_time_series(time_series, database_name)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.get("/time_series", tags=["time series"], response_model=TimeSeriesNodesOut)
    async def get_time_series_nodes(self, response: Response, database_name: str):
        """
        Get time series nodes from database
        """

        get_response = self.time_series_service.get_time_series_nodes(database_name)

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/time_series/{time_series_id}", tags=["time series"],
                response_model=Union[TimeSeriesOut, NotFoundByIdModel])
    async def get_time_series(self, time_series_id: int, response: Response, database_name: str):
        """
        Get time series from database
        """

        get_response = self.time_series_service.get_time_series(time_series_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.delete("/time_series/{time_series_id}", tags=["time series"],
                   response_model=Union[TimeSeriesOut, NotFoundByIdModel])
    async def delete_time_series(self, time_series_id: int, response: Response, database_name: str):
        """
        Delete time series from database
        """
        get_response = self.time_series_service.delete_time_series(time_series_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.put("/time_series/{time_series_id}", tags=["time series"],
                response_model=Union[TimeSeriesOut, NotFoundByIdModel])
    async def update_time_series(self, time_series_id: int, time_series: TimeSeriesPropertyIn,
                                       response: Response, database_name: str):
        """
        Update time series model in database
        """
        update_response = self.time_series_service.update_time_series(time_series_id, time_series, database_name)
        if update_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response

    @router.put("/time_series/{time_series_id}/relationships", tags=["time series"],
                response_model=Union[TimeSeriesOut, NotFoundByIdModel])
    async def update_time_series_relationships(self, time_series_id: int, time_series: TimeSeriesRelationIn, response: Response, database_name: str):
        """
        Update time series relations in database
        """
        update_response = self.time_series_service.update_time_series_relationships(time_series_id, time_series, database_name)
        if update_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response
