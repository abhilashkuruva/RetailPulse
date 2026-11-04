from retailpulse.config.settings import Settings


def test_gcp_configuration_is_explicit():
    assert not Settings(gcp_project_id="", gcs_bucket_name="").has_gcp_configuration
    assert Settings(gcp_project_id="project", gcs_bucket_name="bucket").has_gcp_configuration
