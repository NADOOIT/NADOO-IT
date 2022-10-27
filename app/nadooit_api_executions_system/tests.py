from django.test import TestCase
from nadooit_program.models import NadooitProgram
from nadooit_time_account.models import TimeAccount
from nadooit_program_ownership_system.models import NadooitCustomerProgram
from nadooit_api_executions_system.models import CustomerProgramExecution
from django.db.models.signals import post_save

from model_bakery import baker

import pytest

# Create your tests here.
@pytest.mark.django_db
@pytest.fixture
def TimeAccountTestModel():
    return baker.make(
        TimeAccount,
        time_balance_in_seconds=1000,
    )


def test_using_model_bakery(TimeAccountTestModel):
    assert isinstance(TimeAccountTestModel, TimeAccount)
