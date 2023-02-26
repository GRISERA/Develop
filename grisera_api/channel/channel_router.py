from typing import Union

from fastapi import Response
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from hateoas import get_links
from channel.channel_model import ChannelIn, ChannelOut, BasicChannelOut, ChannelsOut
from channel.channel_service import ChannelService
from models.not_found_model import NotFoundByIdModel
from services import Services

router = InferringRouter()


@cbv(router)
class ChannelRouter:
    """
    Class for routing channel based requests

    Attributes:
        channel_service (ChannelService): Service instance for channel
    """
    def __init__(self):
        self.channel_service = Services().channel_service()

    @router.get("/channels/{channel_id}", tags=["channels"],
                response_model=Union[ChannelOut, NotFoundByIdModel])
    async def get_channel(self, channel_id: int, response: Response, database_name: str):
        """
        Get channel from database
        """
        get_response = self.channel_service.get_channel(channel_id, database_name)
        if get_response.errors is not None:
            response.status_code = 404

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response

    @router.get("/channels", tags=["channels"], response_model=ChannelsOut)
    async def get_channels(self, response: Response, database_name: str):
        """
        Get channels from database
        """

        get_response = self.channel_service.get_channels(database_name)

        # add links from hateoas
        get_response.links = get_links(router)

        return get_response
