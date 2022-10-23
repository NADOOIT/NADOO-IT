from django.test import TestCase
from nadooit_api_executions_system.models import CustomerProgramExecution
from django.db.models.signals import post_save

from model_bakery import baker

# Create your tests here.
class CustomerProgramExecutionTestCase(TestCase):
    def setUp(self):

        self.customer_program_execution = baker.make(
            "nadooit_api_executions_system.CustomerProgramExecution",
            customer_program=baker.make(
                "nadooit_program_ownership_system.NadooitCustomerProgram",
                program=baker.make(
                    "nadooit_program.NadooitProgram",
                    name="test_program_for_tests",
                ),
                time_account=baker.make(
                    "nadooit_time_account.TimeAccount",
                    time_balance_in_seconds=1000,
                ),
            ),
            program_time_saved_in_seconds=100,
        )

    def test_using_model_bakery(self):
        self.assertIsInstance(self.customer_program_execution, CustomerProgramExecution)
