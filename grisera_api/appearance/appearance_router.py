from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from typing import Union
from hateoas import get_links
from appearance.appearance_model import AppearanceOcclusionIn, AppearanceOcclusionOut, BasicAppearanceOcclusionOut, \
     AppearanceSomatotypeIn, AppearanceSomatotypeOut, BasicAppearanceSomatotypeOut, AppearancesOut
from appearance.appearance_service import AppearanceService
from models.not_found_model import NotFoundByIdModel
from services import Services

router = InferringRouter()


@cbv(router)
class AppearanceRouter:
    """
    Class for routing appearance based requests

    Attributes:
        appearance_service (AppearanceService): Service instance for appearance
    """

    def __init__(self):
        self.appearance_service = Services().appearance_service()

    @router.post("/appearance/occlusion_model", tags=["appearance"], response_model=AppearanceOcclusionOut)
    async def create_appearance_occlusion(self, appearance: AppearanceOcclusionIn, response: Response, database_name: str):
        """
        Create appearance occlusion model in database
        """

        create_response = self.appearance_service.save_appearance_occlusion(appearance, database_name)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.post("/appearance/somatotype_model", tags=["appearance"], response_model=AppearanceSomatotypeOut)
    async def create_appearance_somatotype(self, appearance: AppearanceSomatotypeIn, response: Response, database_name: str):
        """
        Create appearance somatotype model in database
        """

        create_response = self.appearance_service.save_appearance_somatotype(appearance, database_name)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.get("/appearance", tags=["appearance"], response_model=AppearancesOut)
    async def get_appearances(self, response: Response, database_name: str):
        """
        Get appearances from database
        """

        get_response = self.appearance_service.get_appearances(database_name)

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/appearance/{appearance_id}", tags=["appearance"],
                response_model=Union[AppearanceSomatotypeOut, AppearanceOcclusionOut, NotFoundByIdModel])
    async def get_appearance(self, appearance_id: int, response: Response, database_name: str):
        """
        Get appearance from database
        """

        get_response = self.appearance_service.get_appearance(appearance_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.delete("/appearance/{appearance_id}", tags=["appearance"],
                   response_model=Union[AppearanceSomatotypeOut, AppearanceOcclusionOut, NotFoundByIdModel])
    async def delete_appearance(self, appearance_id: int, response: Response, database_name: str):
        """
        Delete appearance from database
        """
        get_response = self.appearance_service.delete_appearance(appearance_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.put("/appearance/occlusion_model/{appearance_id}", tags=["appearance"],
                response_model=Union[AppearanceOcclusionOut, NotFoundByIdModel])
    async def update_appearance_occlusion(self, appearance_id: int, appearance: AppearanceOcclusionIn,
                                          response: Response, database_name: str):
        """
        Update appearance occlusion model in database
        """
        update_response = self.appearance_service.update_appearance_occlusion(appearance_id, appearance, database_name)
        if update_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response

    @router.put("/appearance/somatotype_model/{appearance_id}", tags=["appearance"],
                response_model=Union[AppearanceSomatotypeOut, NotFoundByIdModel])
    async def update_appearance_somatotype(self, appearance_id: int, appearance: AppearanceSomatotypeIn,
                                           response: Response, database_name: str):
        """
        Update appearance somatotype model in database
        """
        update_response = self.appearance_service.update_appearance_somatotype(appearance_id, appearance, database_name)
        if update_response.errors is not None:
            response.status_code = 404 if type(update_response) == NotFoundByIdModel else 422

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response
