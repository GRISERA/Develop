from typing import Union

from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from hateoas import get_links
from personality.personality_model import PersonalityBigFiveIn, BasicPersonalityBigFiveOut, PersonalityBigFiveOut, \
    PersonalityPanasIn, BasicPersonalityPanasOut, PersonalityPanasOut, PersonalitiesOut
from personality.personality_service import PersonalityService
from models.not_found_model import NotFoundByIdModel

router = InferringRouter()


@cbv(router)
class PersonalityRouter:
    """
    Class for routing personality based requests

    Attributes:
        personality_service (PersonalityService): Service instance for personality
    """
    personality_service = PersonalityService()

    @router.post("/personality/big_five_model", tags=["personality"], response_model=PersonalityBigFiveOut)
    async def create_personality_big_five(self, personality: PersonalityBigFiveIn, response: Response):
        """
        Create personality big five model in database
        """

        create_response = self.personality_service.save_personality_big_five(personality)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.post("/personality/panas_model", tags=["personality"], response_model=PersonalityPanasOut)
    async def create_personality_panas(self, personality: PersonalityPanasIn, response: Response):
        """
        Create personality panas model in database
        """

        create_response = self.personality_service.save_personality_panas(personality)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.get("/personality/{personality_id}", tags=["personality"],
                response_model=Union[PersonalityBigFiveOut, PersonalityPanasOut, NotFoundByIdModel])
    async def get_personality(self, personality_id: int, response: Response):
        """
        Get personality from database
        """

        get_response = self.personality_service.get_personality(personality_id)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/personality", tags=["personality"], response_model=PersonalitiesOut)
    async def get_personalities(self, response: Response):
        """
        Get personalities from database
        """

        get_response = self.personality_service.get_personalities()

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.delete("/personality/{personality_id}", tags=["personality"],
                   response_model=Union[PersonalityBigFiveOut, PersonalityPanasOut, NotFoundByIdModel])
    async def delete_personality(self, personality_id: int, response: Response):
        """
        Delete personality from database
        """
        get_response = self.personality_service.delete_personality(personality_id)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.put("/personality/big_five_model/{personality_id}", tags=["personality"],
                response_model=Union[PersonalityBigFiveOut, NotFoundByIdModel])
    async def update_personality_big_five(self, personality_id: int, personality: PersonalityBigFiveIn,
                                          response: Response):
        """
        Update personality big five model in database
        """
        update_response = self.personality_service.update_personality_big_five(personality_id, personality)
        if update_response.errors is not None:
            response.status_code = 404 if type(update_response) == NotFoundByIdModel else 422

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response

    @router.put("/personality/panas_model/{personality_id}", tags=["personality"],
                response_model=Union[PersonalityPanasOut, NotFoundByIdModel])
    async def update_personality_panas(self, personality_id: int, personality: PersonalityPanasIn, response: Response):
        """
        Update personality panas model in database
        """
        update_response = self.personality_service.update_personality_panas(personality_id, personality)
        if update_response.errors is not None:
            response.status_code = 404 if type(update_response) == NotFoundByIdModel else 422

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response
