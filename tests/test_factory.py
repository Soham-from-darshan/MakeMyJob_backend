from Application import create_app
from instance import DeploymentConfiguration, TestingConfiguration, DevelopmentConfiguration
import pytest


class TestApplicationFactory:
    configClasses = [DeploymentConfiguration, DevelopmentConfiguration, TestingConfiguration]

    @staticmethod
    @pytest.mark.parametrize('configClass', configClasses)
    def testConfigurationApplied(configClass):
        app = create_app(configClass=configClass)
        configurations = [field for field in dir(configClass) if field.isupper() and not field.startswith('_')]        
        for config in configurations:
            assert app.config[config] == getattr(configClass, config)