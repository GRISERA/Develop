from typing import Union

from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from hateoas import get_links
from observable_information.observable_information_model import ObservableInformationIn, ObservableInformationOut, \
    BasicObservableInformationOut, ObservableInformationsOut
from observable_information.observable_information_service import ObservableInformationService
from models.not_found_model import NotFoundByIdModel

router = InferringRouter()


@cbv(router)
class ObservableInformationRouter:
    """
    Class for routing observable information based requests

    Attributes:
    observable_information_service (ObservableInformationService): Service instance for observable information
    """
    observable_information_service = ObservableInformationService()

    @router.post("/observable_information", tags=["observable information"], response_model=ObservableInformationOut)
    async def create_observable_information(self, observable_information: ObservableInformationIn, response: Response):
        """
        Create observable information in database
        """
        create_response = self.observable_information_service.save_observable_information(observable_information)
        if create_response.errors is not None:
            response.status_code = 422

        # add links from hateoas
        create_response.links = get_links(router)

        return create_response

    @router.get("/observable_information", tags=["observable information"], response_model=ObservableInformationsOut)
    async def get_observable_informations(self, response: Response):
        """
        Get observable information from database
        """

        get_response = self.observable_information_service.get_observable_informations()

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/observable_information/{observable_information_id}", tags=["observable information"],
                response_model=Union[ObservableInformationOut, NotFoundByIdModel])
    async def get_observable_information(self, observable_information_id: int, response: Response):
        """
        Get observable information from database
        """

        get_response = self.observable_information_service.get_observable_information(observable_information_id)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.delete("/observable_information/{observable_information_id}", tags=["observable information"],
                   response_model=Union[ObservableInformationOut, NotFoundByIdModel])
    async def delete_observable_information(self, observable_information_id: int, response: Response):
        """
        Delete observable information from database
        """
        get_response = self.observable_information_service.delete_observable_information(observable_information_id)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.put("/observable_information/{observable_information_id}/relationships", tags=["observable information"],
                response_model=Union[ObservableInformationOut, NotFoundByIdModel])
    async def update_observable_information_relationships(self, observable_information_id: int,
                                                          observable_information: ObservableInformationIn,
                                                          response: Response):
        """
        Update observable information relations in database
        """
        update_response = self.observable_information_service.update_observable_information_relationships(
            observable_information_id,
            observable_information)
        if update_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        update_response.links = get_links(router)

        return update_response
