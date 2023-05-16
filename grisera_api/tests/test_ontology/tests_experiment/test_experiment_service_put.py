import unittest
import unittest.mock as mock

from ontology_api_service import OntologyApiService
from experiment.experiment_model import *
from experiment.experiment_service_ontology import ExperimentServiceOntology


class TestExperimentServicePut(unittest.TestCase):

    @mock.patch.object(OntologyApiService, 'add_role')
    @mock.patch.object(OntologyApiService, 'delete_roles')
    @mock.patch.object(ExperimentServiceOntology, 'get_experiment')
    def test_update_experiment_without_error(self, get_experiment_mock, delete_roles_mock, add_role_mock):
        model_id = 1
        experiment_name = "test"
        delete_roles_mock.return_value = {'errors': None}
        add_role_mock.return_value = {'errors': None}
        get_experiment_mock.return_value = {'relations': [], 'reversed_relations': [], 'errors': None}

        additional_properties = [PropertyIn(key='test', value='test')]
        experiment = ExperimentIn(experiment_name=experiment_name, additional_properties=additional_properties)
        experiment_service = ExperimentServiceOntology()

        result = experiment_service.update_experiment(experiment_name, experiment)

        self.assertEqual(result, ExperimentOut(experiment_name=experiment_name, additional_properties=additional_properties))

        add_role_mock.assert_called_once_with(model_id, 'test', 'test', 'test')
        delete_roles_mock.assert_called_once_with(model_id, 'test')
        get_experiment_mock.assert_called_once_with(experiment_name)

    @mock.patch.object(ExperimentServiceOntology, 'get_experiment')
    def test_update_experiment_with_error(self, get_experiment_mock):
        model_id = 1
        experiment_name = "test"
        get_experiment_mock.return_value = {'relations': [], 'reversed_relations': [], 'errors': 'error'}

        additional_properties = [PropertyIn(key='test', value='test')]
        experiment = ExperimentIn(experiment_name=experiment_name, additional_properties=additional_properties)
        experiment_service = ExperimentServiceOntology()

        result = experiment_service.update_experiment(experiment_name, experiment)

        self.assertEqual(result, ExperimentOut(experiment_name=experiment_name, additional_properties=additional_properties, errors='error'))

        get_experiment_mock.assert_called_once_with(experiment_name)