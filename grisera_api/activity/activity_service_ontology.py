from typing import Union

from activity.activity_model import ActivityIn, ActivityOut
from activity.activity_service import ActivityService
from models.relation_information_model import RelationInformation
from ontology_api_service import OntologyApiService


class ActivityServiceOntology(ActivityService):
    """
    Object to handle logic of activity requests

    Attributes:
    ontology_api_service (OntologyApiService): Service used to communicate with Ontology API
    """
    ontology_api_service = OntologyApiService()

    def save_activity(self, activity: ActivityIn):
        super().save_activity()

    def get_activities(self):
        super().get_activities()

    def get_activity(self, activity_id: Union[int, str], depth: int = 0):
        """
        Send request to graph api to get given activity
        Args:
            depth(int): specifies how many related entities will be traversed to create the response
            activity_id (int | str): identity of activity
        Returns:
            Result of request as activity object
        """
        model_id = 1
        instance_response_activity = self.ontology_api_service.get_instance(model_id=model_id, class_name="Activity",
                                                                            instance_label=activity_id)
        if instance_response_activity["errors"] is not None:
            return ActivityOut(ActivityIn(id=activity_id),
                               errors=instance_response_activity["errors"])

        roles_response_activity = self.ontology_api_service.get_roles(model_id, activity_id)
        if roles_response_activity["errors"] is not None:
            return ActivityOut(ActivityIn(activity_id),
                               errors=roles_response_activity["errors"])
        relations = []
        for prop in roles_response_activity['roles']:
            relations.append(RelationInformation(value=prop['value'], second_node_id=0, relation_id=0,
                                                 name=prop['role']))

        reversed_roles_response_activity = self.ontology_api_service.get_reversed_roles(model_id, activity_id)
        if reversed_roles_response_activity["errors"] is not None:
            return ActivityOut(ActivityIn(activity_name=activity_id),
                               errors=reversed_roles_response_activity["errors"])
        reversed_relations = []
        for prop in roles_response_activity['roles']:
            reversed_relations.append(
                RelationInformation(value=prop['instance_name'], second_node_id=0, relation_id=0, name=prop['role']))

        activity_result = {'activity_name': activity_id, 'additional_properties': [], 'relations': relations,
                           'reversed_relations': reversed_relations}

        return ActivityOut(**activity_result.dict())
