from graph_api_service import GraphApiService
from measure_name.measure_name_model import MeasureNameIn, MeasureNameOut, MeasureNamesOut, BasicMeasureNameOut


class MeasureNameService:
    """
    Object to handle logic of measure name requests

    Attributes:
        graph_api_service (GraphApiService): Service used to communicate with Graph API
    """
    graph_api_service = GraphApiService()

    def save_measure_name(self, measure_name: MeasureNameIn):
        """
        Send request to graph api to create new measure name

        Args:
            measure_name (MeasureNameIn): Measure name to be added

        Returns:
            Result of request as measure name object
        """
        create_response = self.graph_api_service.create_node("`Measure Name`")

        if create_response["errors"] is not None:
            return MeasureNameOut(name=measure_name.name, type=measure_name.type, errors=create_response["errors"])

        measure_name_id = create_response["id"]
        properties_response = self.graph_api_service.create_properties(measure_name_id, measure_name)
        if properties_response["errors"] is not None:
            return MeasureNameOut(name=measure_name.name, type=measure_name.type, errors=properties_response["errors"])

        return MeasureNameOut(name=measure_name.name, type=measure_name.type,  id=measure_name_id)

    def get_measure_names(self):
        """
        Send request to graph api to get all measure names

        Returns:
            Result of request as list of measure name objects
        """
        get_response = self.graph_api_service.get_nodes("`Measure Name`")
        if get_response["errors"] is not None:
            return MeasureNamesOut(errors=get_response["errors"])
        measure_names = [BasicMeasureNameOut(id=measure_name["id"], name=measure_name["properties"][0]["value"],
                         type=measure_name["properties"][1]["value"])
                         for measure_name in get_response["nodes"]]

        return MeasureNamesOut(measure_names=measure_names)