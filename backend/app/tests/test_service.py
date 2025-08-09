import pytest
from pathlib import Path
from app.service import DeploymentService
import app.service as service_mod
from models.payload import Payload
from models.oracle_cloud_config import OCIVars, FlexShape
from models.cloudflare_vars import CloudflareVars
from models.github_vars import GithubVars


@pytest.fixture
def sample_payload():
    """Create a complete sample payload for testing."""
    return Payload(
        oracle_cloud=OCIVars(
            tenancy_ocid="ocid1.tenancy.oc1..tenancy",
            user_ocid="ocid1.user.oc1..user",
            fingerprint="aa:bb:cc:dd:ee",
            region="us-phoenix-1",
            compartment_ocid="ocid1.compartment.oc1..compartment",
            flex_shape=FlexShape(shape="VM.Standard3.Flex", ocpus=2, memory_gb=8),
        ),
        cloudflare=CloudflareVars(
            cf_api_token="cf_token_123",
            cf_account_id="cf_account_456",
            cf_zone_id="cf_zone_789",
            domain="example.com",
        ),
        github=GithubVars(
            github_token="gh_token_123",
            github_owner="testuser",
            repo_name="testrepo",
            docker_image="ghcr.io/testuser/testrepo:latest",
        ),
        instance_name="test-vm",
        vm_username="testuser",
        vm_password="testpass",
    )


@pytest.fixture
def payload_no_flex():
    """Create a payload without flex shape configuration."""
    return Payload(
        oracle_cloud=OCIVars(
            tenancy_ocid="ocid1.tenancy.oc1..tenancy",
            user_ocid="ocid1.user.oc1..user",
            fingerprint="aa:bb:cc:dd:ee",
            region="us-phoenix-1",
            compartment_ocid="ocid1.compartment.oc1..compartment",
        ),
        cloudflare=CloudflareVars(
            cf_api_token="cf_token_123", cf_account_id="cf_account_456"
        ),
        github=GithubVars(
            github_token="gh_token_123",
            github_owner="testuser",
            repo_name="testrepo",
            docker_image="ghcr.io/testuser/testrepo:latest",
        ),
    )


@pytest.fixture
def payload_no_oracle():
    """Create a payload without Oracle Cloud configuration."""
    return Payload(
        cloudflare=CloudflareVars(
            cf_api_token="cf_token_123", cf_account_id="cf_account_456"
        ),
        github=GithubVars(
            github_token="gh_token_123",
            github_owner="testuser",
            repo_name="testrepo",
            docker_image="ghcr.io/testuser/testrepo:latest",
        ),
    )


class TestDeploymentService:

    def test_init(self, tmp_path):
        """Test service initialization."""
        svc = DeploymentService(directory=tmp_path)
        assert svc.directory == tmp_path
        assert svc.payload is None

    def test_set_payload_with_complete_data(
        self, tmp_path, sample_payload, monkeypatch
    ):
        """Test set_payload with complete payload data."""
        svc = DeploymentService(directory=tmp_path)
        captured = {}

        class _FakeTemplate:
            def render(self, **kwargs):
                captured.update(kwargs)
                return "RENDERED_COMPLETE"

        monkeypatch.setattr(service_mod, "TEMPLATE", _FakeTemplate(), raising=True)

        priv_key = Path("id_rsa")
        pub_key = Path("id_rsa.pub")

        result = svc.set_payload(sample_payload, priv_key, pub_key)

        # Verify return value
        assert result == "RENDERED_COMPLETE"
        assert svc.payload is sample_payload

        # Verify Oracle Cloud data is flattened correctly
        assert captured["tenancy_ocid"] == "ocid1.tenancy.oc1..tenancy"
        assert captured["user_ocid"] == "ocid1.user.oc1..user"
        assert captured["fingerprint"] == "aa:bb:cc:dd:ee"
        assert captured["region"] == "us-phoenix-1"
        assert captured["compartment_ocid"] == "ocid1.compartment.oc1..compartment"

        # Verify flex shape data
        assert captured["flex"]["shape"] == "VM.Standard3.Flex"
        assert captured["flex"]["ocpus"] == 2
        assert captured["flex"]["memory_gb"] == 8

        # Verify Cloudflare data is flattened correctly
        assert captured["cf_api_token"] == "cf_token_123"
        assert captured["cf_account_id"] == "cf_account_456"
        assert captured["cf_zone_id"] == "cf_zone_789"
        assert captured["domain"] == "example.com"

        # Verify GitHub data is flattened correctly
        assert captured["github_token"] == "gh_token_123"
        assert captured["github_owner"] == "testuser"
        assert captured["repo_name"] == "testrepo"
        assert captured["docker_image"] == "ghcr.io/testuser/testrepo:latest"

        # Verify VM instance data
        assert captured["instance_name"] == "test-vm"
        assert captured["vm_username"] == "testuser"
        assert captured["vm_password"] == "testpass"

        # Verify path data
        assert captured["pem_path"] == str(priv_key)
        assert captured["private_pem_path"] == str(priv_key)
        assert captured["public_pem_path"] == str(pub_key)

    def test_set_payload_without_flex_shape(
        self, tmp_path, payload_no_flex, monkeypatch
    ):
        """Test set_payload when flex_shape is not provided (uses defaults)."""
        svc = DeploymentService(directory=tmp_path)
        captured = {}

        class _FakeTemplate:
            def render(self, **kwargs):
                captured.update(kwargs)
                return "RENDERED_NO_FLEX"

        monkeypatch.setattr(service_mod, "TEMPLATE", _FakeTemplate(), raising=True)

        priv_key = Path("id_rsa")
        pub_key = Path("id_rsa.pub")

        result = svc.set_payload(payload_no_flex, priv_key, pub_key)

        assert result == "RENDERED_NO_FLEX"

        # Verify default flex shape values are used
        assert captured["flex"]["shape"] == "VM.Standard.E2.1.Micro"
        assert captured["flex"]["ocpus"] == 1
        assert captured["flex"]["memory_gb"] == 1

    def test_set_payload_without_oracle_cloud(
        self, tmp_path, payload_no_oracle, monkeypatch
    ):
        """Test set_payload when oracle_cloud is None."""
        svc = DeploymentService(directory=tmp_path)
        captured = {}

        class _FakeTemplate:
            def render(self, **kwargs):
                captured.update(kwargs)
                return "RENDERED_NO_ORACLE"

        monkeypatch.setattr(service_mod, "TEMPLATE", _FakeTemplate(), raising=True)

        priv_key = Path("id_rsa")
        pub_key = Path("id_rsa.pub")

        result = svc.set_payload(payload_no_oracle, priv_key, pub_key)

        assert result == "RENDERED_NO_ORACLE"

        # Oracle Cloud fields should not be in context
        oracle_fields = [
            "tenancy_ocid",
            "user_ocid",
            "fingerprint",
            "region",
            "compartment_ocid",
        ]
        for field in oracle_fields:
            assert field not in captured

        # Flex should not be in context either
        assert "flex" not in captured

        # But other fields should still be present
        assert captured["cf_api_token"] == "cf_token_123"
        assert captured["github_token"] == "gh_token_123"

    def test_generate_tf_files(self, tmp_path):
        """Test generate_tf_files method (placeholder)."""
        svc = DeploymentService(directory=tmp_path)
        # Currently just a pass, so should not raise any exception
        result = svc.generate_tf_files()
        assert result is None

    def test_deploy(self, tmp_path):
        """Test deploy method (placeholder)."""
        svc = DeploymentService(directory=tmp_path)
        # Currently just a pass, so should not raise any exception
        result = svc.deploy()
        assert result is None

    def test_cleanup_removes_directory(self, tmp_path, monkeypatch):
        """Test cleanup removes the directory."""
        svc = DeploymentService(directory=tmp_path)

        # Track calls to rmtree
        calls = []

        def mock_rmtree(path, ignore_errors=False):
            calls.append((path, ignore_errors))

        monkeypatch.setattr("app.service.shutil.rmtree", mock_rmtree)

        svc.cleanup()

        # Verify rmtree was called with correct arguments
        assert len(calls) == 1
        assert calls[0] == (tmp_path, True)

    def test_path_conversion_to_string(self, tmp_path, sample_payload, monkeypatch):
        """Test that Path objects are converted to strings in context data."""
        svc = DeploymentService(directory=tmp_path)
        captured = {}

        class _FakeTemplate:
            def render(self, **kwargs):
                captured.update(kwargs)
                return "RENDERED"

        monkeypatch.setattr(service_mod, "TEMPLATE", _FakeTemplate(), raising=True)

        priv_key = Path("/home/user/.ssh/id_rsa")
        pub_key = Path("/home/user/.ssh/id_rsa.pub")

        svc.set_payload(sample_payload, priv_key, pub_key)

        # Verify all path values are strings
        assert isinstance(captured["pem_path"], str)
        assert isinstance(captured["private_pem_path"], str)
        assert isinstance(captured["public_pem_path"], str)

        assert captured["pem_path"] == "/home/user/.ssh/id_rsa"
        assert captured["private_pem_path"] == "/home/user/.ssh/id_rsa"
        assert captured["public_pem_path"] == "/home/user/.ssh/id_rsa.pub"
