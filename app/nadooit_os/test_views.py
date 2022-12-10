# This file contains the tests for the views of the nadooit app.

# The tests are written using pytest.
# The tests are run using the pytest-django plugin.
# The tests are run using the pytest-cov plugin.
# The tests are run using the pytest-mock plugin.

import pytest
from model_bakery import baker

from nadooit_os.views import get__user__roles_and_rights__for__User


def test_get__user__roles_and_rights__for__User():
    # Arrange
    user = baker.make("nadooit_auth.User")

    # Act
    # Assert
    assert get__user__roles_and_rights__for__User(user) == {}
