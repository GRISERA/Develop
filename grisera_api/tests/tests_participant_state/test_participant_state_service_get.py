import unittest
import unittest.mock as mock

from participant_state.participant_state_model import *
from models.not_found_model import *

from participant_state.participant_state_service import ParticipantStateService
from graph_api_service import GraphApiService


class TestParticipantStateServiceGet(unittest.TestCase):

    @mock.patch.object(GraphApiService, 'get_node')
    @mock.patch.object(GraphApiService, 'get_node_relationships')
    def test_get_participant_state_without_error(self, get_node_relationships_mock, get_node_mock):
        id_node = 1
        get_node_mock.return_value = {'id': id_node, 'labels': ['Participant State'],
                                      'properties': [{'key': 'age', 'value': 5},
                                                     {'key': 'test', 'value': 'test2'}],
                                      "errors": None, 'links': None}
        get_node_relationships_mock.return_value = {"relationships": [
                                                    {"start_node": id_node, "end_node": 19,
                                                     "name": "testRelation", "id": 0,
                                                     "properties": None},
                                                    {"start_node": 15, "end_node": id_node,
                                                     "name": "testReversedRelation", "id": 0,
                                                     "properties": None}]}
        additional_properties = [PropertyIn(key='test', value='test2')]
        participant_state = ParticipantStateOut(age=5, id=id_node,additional_properties=additional_properties,
                                                relations=[RelationInformation(second_node_id=19, name="testRelation",
                                                                               relation_id=0)],
                                                reversed_relations=[RelationInformation(second_node_id=15,
                                                                                        name="testReversedRelation",
                                                                                        relation_id=0)])
        participant_state_service = ParticipantStateService()

        result = participant_state_service.get_participant_state(id_node)

        self.assertEqual(result, participant_state)
        get_node_mock.assert_called_once_with(id_node)
        get_node_relationships_mock.assert_called_once_with(id_node)

    @mock.patch.object(GraphApiService, 'get_node')
    def test_get_participant_state_without_participant_label(self, get_node_mock):
        id_node = 1
        get_node_mock.return_value = {'id': id_node, 'labels': ['Test'], 'properties': None,
                                      "errors": None, 'links': None}
        not_found = NotFoundByIdModel(id=id_node, errors="Node not found.")
        participant_state_service = ParticipantStateService()

        result = participant_state_service.get_participant_state(id_node)

        self.assertEqual(result, not_found)
        get_node_mock.assert_called_once_with(id_node)

    @mock.patch.object(GraphApiService, 'get_node')
    def test_get_participant_state_with_error(self, get_node_mock):
        id_node = 1
        get_node_mock.return_value = {'id': id_node, 'errors': ['error'], 'links': None}
        not_found = NotFoundByIdModel(id=id_node, errors=['error'])
        participant_state_service = ParticipantStateService()

        result = participant_state_service.get_participant_state(id_node)

        self.assertEqual(result, not_found)
        get_node_mock.assert_called_once_with(id_node)

    @mock.patch.object(GraphApiService, 'get_nodes')
    def test_get_participant_states(self, get_nodes_mock):
        get_nodes_mock.return_value = {'nodes': [{'id': 1, 'labels': ['Participant State'],
                                                  'properties': [{'key': 'age', 'value': 5},
                                                                 {'key': 'test', 'value': 'test'}]},
                                                 {'id': 2, 'labels': ['Participant'],
                                                  'properties': [{'key': 'age', 'value': 10},
                                                                 {'key': 'test2', 'value': 'test3'}]}]}
        participant_state_one = BasicParticipantStateOut(id=1, age=5, additional_properties=[
            PropertyIn(key='test', value='test')])
        participant_state_two = BasicParticipantStateOut(id=2, age=10, additional_properties=[
            PropertyIn(key='test2', value='test3')])
        participant_states = ParticipantStatesOut(participant_states=[participant_state_one, participant_state_two])
        participant_states_service = ParticipantStateService()

        result = participant_states_service.get_participant_states()

        self.assertEqual(result, participant_states)
        get_nodes_mock.assert_called_once_with("`Participant State`")

    @mock.patch.object(GraphApiService, 'get_nodes')
    def test_get_participant_states_empty(self, get_nodes_mock):
        get_nodes_mock.return_value = {'nodes': []}
        participant_states = ParticipantStatesOut(participant_state=[])
        participant_states_service = ParticipantStateService()

        result = participant_states_service.get_participant_states()

        self.assertEqual(result, participant_states)
        get_nodes_mock.assert_called_once_with("`Participant State`")
