from graph_api_service import GraphApiService
from channel.channel_service_graphdb import ChannelServiceGraphDB
from registered_channel.registered_channel_service import RegisteredChannelService
from registered_data.registered_data_service_graphdb import RegisteredDataServiceGraphDB
from registered_channel.registered_channel_model import BasicRegisteredChannelOut, RegisteredChannelsOut, \
    RegisteredChannelOut, RegisteredChannelIn
from models.not_found_model import NotFoundByIdModel
from models.relation_information_model import RelationInformation


class RegisteredChannelServiceGraphDB(RegisteredChannelService):
    """
    Object to handle logic of registered channels requests

    Attributes:
    graph_api_service (GraphApiService): Service used to communicate with Graph API
    channel_service (ChannelService): Service to send channel requests
    registered_data_service (RegisteredDataService): Service to send registered data requests
    """
    graph_api_service = GraphApiService()
    channel_service = ChannelServiceGraphDB()
    registered_data_service = RegisteredDataServiceGraphDB()

    def save_registered_channel(self, registered_channel: RegisteredChannelIn, database_name: str):
        """
        Send request to graph api to create new registered channel

        Args:
            registered_channel (RegisteredChannelIn): Registered channel to be added

        Returns:
            Result of request as registered channel object
        """
        node_response = self.graph_api_service.create_node("`Registered Channel`", database_name)

        if node_response["errors"] is not None:
            return RegisteredChannelOut(errors=node_response["errors"])
        registered_channel_id = node_response["id"]

        if registered_channel.channel_id is not None and \
                type(self.channel_service.get_channel(registered_channel.channel_id, database_name)) is not NotFoundByIdModel:
            self.graph_api_service.create_relationships(start_node=registered_channel_id,
                                                        end_node=registered_channel.channel_id,
                                                        name="hasChannel",
                                                        database_name=database_name)
        if registered_channel.registered_data_id is not None and \
                type(self.registered_data_service.get_registered_data(registered_channel.registered_data_id, database_name)) \
                is not NotFoundByIdModel:
            self.graph_api_service.create_relationships(start_node=registered_channel_id,
                                                        end_node=registered_channel.registered_data_id,
                                                        name="hasRegisteredData",
                                                        database_name=database_name)

        return self.get_registered_channel(registered_channel_id, database_name)

    def get_registered_channels(self, database_name: str):
        """
        Send request to graph api to get registered channels

        Returns:
            Result of request as list of registered channels objects
        """
        get_response = self.graph_api_service.get_nodes("`Registered Channel`", database_name)

        registered_channels = []

        for registered_channel_node in get_response["nodes"]:
            properties = {'id': registered_channel_node['id']}
            for property in registered_channel_node["properties"]:
                if property["key"] == "age":
                    properties[property["key"]] = property["value"]
            registered_channel = BasicRegisteredChannelOut(**properties)
            registered_channels.append(registered_channel)

        return RegisteredChannelsOut(registered_channels=registered_channels)

    def get_registered_channel(self, registered_channel_id: int, database_name: str):
        """
        Send request to graph api to get given registered channel

        Args:
            registered_channel_id (int): Id of registered channel

        Returns:
            Result of request as registered channel object
        """
        get_response = self.graph_api_service.get_node(registered_channel_id, database_name)

        if get_response["errors"] is not None:
            return NotFoundByIdModel(id=registered_channel_id, errors=get_response["errors"])
        if get_response["labels"][0] != "Registered Channel":
            return NotFoundByIdModel(id=registered_channel_id, errors="Node not found.")

        registered_channel = {'id': get_response['id'], 'relations': [],
                              'reversed_relations': []}
        for property in get_response["properties"]:
            if property["key"] == "age":
                registered_channel[property["key"]] = property["value"]

        relations_response = self.graph_api_service.get_node_relationships(registered_channel_id, database_name)

        for relation in relations_response["relationships"]:
            if relation["start_node"] == registered_channel_id:
                registered_channel['relations'].append(RelationInformation(second_node_id=relation["end_node"],
                                                                           name=relation["name"],
                                                                           relation_id=relation["id"]))
            else:
                registered_channel['reversed_relations'].append(
                    RelationInformation(second_node_id=relation["start_node"],
                                        name=relation["name"],
                                        relation_id=relation["id"]))

        return RegisteredChannelOut(**registered_channel)

    def delete_registered_channel(self, registered_channel_id: int, database_name: str):
        """
        Send request to graph api to delete given registered channel

        Args:
            registered_channel_id (int): Id of registered channel

        Returns:
            Result of request as registered channel object
        """
        get_response = self.get_registered_channel(registered_channel_id, database_name)

        if type(get_response) is NotFoundByIdModel:
            return get_response

        self.graph_api_service.delete_node(registered_channel_id, database_name)
        return get_response

    def update_registered_channel_relationships(self, registered_channel_id: int,
                                                registered_channel: RegisteredChannelIn, database_name: str):
        """
        Send request to graph api to update given registered channel

        Args:
            registered_channel_id (int): Id of registered channel
            registered_channel (RegisteredChannelIn): Relationships to update

        Returns:
            Result of request as registered channel object
        """
        get_response = self.get_registered_channel(registered_channel_id, database_name)

        if type(get_response) is NotFoundByIdModel:
            return get_response

        if registered_channel.channel_id is not None and \
                type(self.channel_service.get_channel(registered_channel.channel_id, database_name)) is not NotFoundByIdModel:
            self.graph_api_service.create_relationships(start_node=registered_channel_id,
                                                        end_node=registered_channel.channel_id,
                                                        name="hasChannel",
                                                        database_name=database_name)
        if registered_channel.registered_data_id is not None and \
                type(self.registered_data_service.get_registered_data(registered_channel.registered_data_id, database_name)) \
                is not NotFoundByIdModel:
            self.graph_api_service.create_relationships(start_node=registered_channel_id,
                                                        end_node=registered_channel.registered_data_id,
                                                        name="hasRegisteredData",
                                                        database_name=database_name)

        return self.get_registered_channel(registered_channel_id, database_name)
