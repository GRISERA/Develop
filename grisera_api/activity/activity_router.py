from typing import Union

from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from hateoas import get_links
from activity.activity_model import ActivityIn, ActivityOut, BasicActivityOut, ActivitiesOut
from activity.activity_service import ActivityService
from models.not_found_model import NotFoundByIdModel

router = InferringRouter()


@cbv(router)
class ActivityRouter:
    """
    Class for routing activity based requests

    Attributes:
    activity_service (ActivityService): Service instance for activity
    """
    activity_service = ActivityService()

    @router.get("/activities/{activity_id}", tags=["activities"],
                response_model=Union[ActivityOut, NotFoundByIdModel])
    async def get_activity(self, activity_id: int, response: Response):
        """
        Get activity from database
        """
        get_response = self.activity_service.get_activity(activity_id)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/activities", tags=["activities"], response_model=ActivitiesOut)
    async def get_activities(self, response: Response):
        """
        Get activities from database
        """

        get_response = self.activity_service.get_activities()

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response