from typing import Union

from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from hateoas import get_links
from models.not_found_model import NotFoundByIdModel
from activity_execution.activity_execution_model import ActivityExecutionIn, ActivityExecutionOut, \
    ActivityExecutionsOut, ActivityExecutionPropertyIn, ActivityExecutionRelationIn
from activity_execution.activity_execution_service import ActivityExecutionService
from services import Services

router = InferringRouter()


@cbv(router)
class ActivityExecutionRouter:
    """
    Class for routing activity execution based requests

    Attributes:
        activity_execution_service (ActivityExecutionService): Service instance for activity execution
    """

    def __init__(self):
        self.activity_execution_service = Services().activity_execution_service()

    @router.post("/activity_executions", tags=["activity executions"], response_model=ActivityExecutionOut)
    async def create_activity_execution(self, activity_execution: ActivityExecutionIn, response: Response, database_name: str):
        """
        Create activity execution in database
        """
        create_response = self.activity_execution_service.save_activity_execution(activity_execution,database_name)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.get("/activity_executions", tags=["activity executions"], response_model=ActivityExecutionsOut)
    async def get_activity_executions(self, response: Response, database_name: str):
        """
        Get activity executions from database
        """

        get_response = self.activity_execution_service.get_activity_executions(database_name)

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/activity_executions/{activity_execution_id}", tags=["activity executions"],
                response_model=Union[ActivityExecutionOut, NotFoundByIdModel])
    async def get_activity_execution(self, activity_execution_id: int, response: Response, database_name: str):
        """
        Get activity executions from database
        """

        get_response = self.activity_execution_service.get_activity_execution(activity_execution_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.delete("/activity_executions/{activity_execution_id}", tags=["activity executions"],
                   response_model=Union[ActivityExecutionOut, NotFoundByIdModel])
    async def delete_activity_execution(self, activity_execution_id: int, response: Response, database_name: str):
        """
        Delete activity executions from database
        """
        get_response = self.activity_execution_service.delete_activity_execution(activity_execution_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.put("/activity_executions/{activity_execution_id}", tags=["activity executions"],
                response_model=Union[ActivityExecutionOut, NotFoundByIdModel])
    async def update_activity_execution(self, activity_execution_id: int,
                                        activity_execution: ActivityExecutionPropertyIn,
                                        response: Response,
                                        database_name: str):
        """
        Update activity execution model in database
        """
        update_response = self.activity_execution_service.update_activity_execution(activity_execution_id,
                                                                                    activity_execution, database_name)
        if update_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response

    @router.put("/activity_executions/{activity_execution_id}/relationships", tags=["activity executions"],
                response_model=Union[ActivityExecutionOut, NotFoundByIdModel])
    async def update_activity_execution_relationships(self, activity_execution_id: int,
                                                      activity_execution: ActivityExecutionRelationIn,
                                                      response: Response,
                                                      database_name: str):
        """
        Update activity executions relations in database
        """
        update_response = self.activity_execution_service.update_activity_execution_relationships(activity_execution_id,
                                                                                                  activity_execution, database_name)
        if update_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response
