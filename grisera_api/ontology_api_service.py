import requests
from ontology_api_config import ontology_api_address


class OntologyApiService:
    """
    Object that handles communication with Ontology API

    Attributes:
        ontology_api_url (str): Ontology API URL
    """
    ontology_api_url = ontology_api_address

    def post(self, url_part, request_body):
        """
        Send a POST request to Ontology API
        Args:
            url_part (str): Part to add at the end of the url
            request_body:

        Returns: Request result
        """
        response = requests.post(url=self.ontology_api_url + url_part,
                                 json=request_body).json()
        return response

    def get(self, url_part, params):
        """
        Send a GET request to Ontology API
        Args:
            url_part (str): Part to add at the end of the url
            params (dict): Request parameters

        Returns: Request result
        """
        response = requests.get(url=self.ontology_api_url + url_part,
                                params=params).json()
        return response

    def delete(self, url_part, params):
        """
        Send request get to Graph API

        Args:
            url_part (str): Part to add at the end of url
            params (dict): Parameters of request

        Returns:
            Result of request
        """

        response = requests.delete(url=self.ontology_api_url + url_part,
                                   params=params).json()
        return response

    def add_instance(self, model_id, class_name, instance_label):
        """
        Send a request to add an instance to Ontology API
        Args:
            instance_label (str): Label of instance
            model_id (int): ID of the model to which the instance is to be added
            class_name (str): Name of the class of the instance

        Returns: Request result
        """
        request_body = {"name": instance_label}
        return self.post(f"/models/{model_id}/classes/{class_name}/instances", request_body)

    def delete_roles(self, model_id, instance_label):
        """
        Send a request to delete roles of the instance to Ontology API
        Args:
            instance_label (str): Label of instance
            model_id (int): ID of the model to which the instance is to be added

        Returns: Request result
        """
        return self.delete(f"/models/{model_id}/instances/{instance_label}/roles", {})

    def add_role(self, model_id, role, instance_label, value):
        """
        Send a request to add role of the instance to Ontology API
        Args:
            model_id (int): ID of the model to which the instance is to be added
            instance_label (str): Label of instance
            value (int | str): Value of this relationship
            role (str): Name of property

        Returns: Request result
        """
        request_body = {"role": role, "instance_name": instance_label, "value": value}
        return self.post(f"/models/{model_id}/roles", request_body)

    def get_instance(self, model_id, class_name, instance_label):
        """
        Send a request to get an instance from Ontology API
        Args:
            instance_label (str): Label of instance
            class_name (str): Name of the class of the instance
            model_id (int): ID of the model to which the instance is to be added

        Returns: Request result
        """
        return self.get(f"/models/{model_id}/classes/{class_name}/instances/{instance_label}", {})

    def get_roles(self, model_id, experiment_label):
        """
        Send a GET request to get roles from Ontology API
        Args:
            model_id (int): id of the model
            experiment_label (str): label of experiment

        Returns: Request result
        """
        url_part = f"/models/{model_id}/instances/{experiment_label}/roles"
        return self.get(url_part, {})

    def get_reversed_roles(self, model_id, experiment_label):
        """
        Send a GET request to get reversed roles from Ontology API
        Args:
            model_id (int): id of the model
            experiment_label (str): label of experiment

        Returns: Request result
        """
        url_part = f"/models/{model_id}/instances/{experiment_label}/reversed_roles"
        return self.get(url_part, {})
