import asyncio
import unittest
import os
from owlready2 import get_ontology
from role.role_model import ObjectPropertyRoleModelIn, ObjectPropertyRoleModelOut
from role.role_router import RoleRouter
from fastapi import Response


class RoleRouterTestCase(unittest.TestCase):
    def test_add_object_property_role_without_error(self):
        role_router = RoleRouter()
        response = Response()
        model_id = 1
        onto = get_ontology("https://road.affectivese.org/documentation/owlAC.owl").load()
        src = onto["ParticipantState"]("ps")
        dst = onto["Participant"]("p")
        onto.save(file="database" + os.path.sep + f"{model_id}.owl", format="rdfxml")
        onto.destroy()
        model_in = ObjectPropertyRoleModelIn(src_instance_name="ps", dst_instance_name="p", role_name="hasParticipant")
        result = asyncio.run(role_router.add_object_property_role(model_id, model_in, response))
        self.assertEqual(response.status_code, 200)
        onto = get_ontology("database" + os.path.sep + f"{model_id}.owl").load()
        self.assertEqual(onto["ps"].hasParticipant, onto["p"])
        onto.destroy()
        os.remove("database" + os.path.sep + f"{model_id}.owl")

    def test_add_object_property_role_model_does_not_exist(self):
        role_router = RoleRouter()
        response = Response()
        model_in = ObjectPropertyRoleModelIn(src_instance_name="ps", dst_instance_name="p", role_name="hasParticipant")
        model_id = 1
        result = asyncio.run(role_router.add_object_property_role(model_id, model_in, response))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result.errors, f"Model with id {model_id} not found")

    def test_add_object_property_role_instance_not_found(self):
        role_router = RoleRouter()
        response = Response()
        model_id = 1
        onto = get_ontology("https://road.affectivese.org/documentation/owlAC.owl").load()
        onto.save(file="database" + os.path.sep + f"{model_id}.owl", format="rdfxml")
        onto.destroy()
        model_in = ObjectPropertyRoleModelIn(src_instance_name="ps", dst_instance_name="p", role_name="hasParticipant")
        result = asyncio.run(role_router.add_object_property_role(model_id, model_in, response))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(result.errors, f"Instance ps not found")
        os.remove("database" + os.path.sep + f"{model_id}.owl")