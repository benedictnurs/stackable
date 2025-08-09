import pytest
from pathlib import Path
from app.service import DeploymentService
import app.service as service_mod
from app.models.payload import Payload
from app.models.oracle_cloud_config import OCIVars, FlexShape
from app.models.cloudflare_vars import CloudflareVars
from app.models.github_vars import GithubVars


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

    def test_template_rendering_with_real_template(self, tmp_path, sample_payload):
        """Test that the service actually renders the Jinja2 template correctly."""
        svc = DeploymentService(directory=tmp_path)

        priv_key = Path("test_private_key")
        pub_key = Path("test_public_key")

        result = svc.set_payload(sample_payload, priv_key, pub_key)

        # Verify the template was rendered (should return a string)
        assert isinstance(result, str)
        assert len(result) > 0

        # Verify specific template content was rendered with our data
        assert "ocid1.tenancy.oc1..tenancy" in result
        assert "ocid1.user.oc1..user" in result
        assert "aa:bb:cc:dd:ee" in result
        assert "us-phoenix-1" in result
        assert "cf_token_123" in result
        assert "cf_account_456" in result
        assert "gh_token_123" in result
        assert "testuser" in result
        assert "testrepo" in result
        assert "test_private_key" in result
        assert "test_public_key" in result

    def test_template_contains_terraform_resources(self, tmp_path, sample_payload):
        """Test that the rendered template contains expected Terraform resources."""
        svc = DeploymentService(directory=tmp_path)

        priv_key = Path("private.key")
        pub_key = Path("public.key")

        result = svc.set_payload(sample_payload, priv_key, pub_key)

        # Verify Terraform provider blocks are rendered
        assert 'provider "oci"' in result
        assert 'provider "cloudflare"' in result
        assert 'provider "github"' in result

        # Verify OCI resources are rendered
        assert 'resource "oci_core_vcn"' in result
        assert 'resource "oci_core_instance"' in result
        assert 'resource "oci_core_subnet"' in result

        # Verify Cloudflare resources are rendered
        assert 'resource "cloudflare_zero_trust_tunnel_cloudflared"' in result
        assert 'resource "cloudflare_record"' in result

        # Verify GitHub resources are rendered
        assert 'resource "github_repository_file"' in result
        assert 'resource "github_actions_secret"' in result

    def test_template_variable_substitution(self, tmp_path, sample_payload):
        """Test that Jinja2 variables are properly substituted in the template."""
        svc = DeploymentService(directory=tmp_path)

        priv_key = Path("/path/to/private.pem")
        pub_key = Path("/path/to/public.pem")

        result = svc.set_payload(sample_payload, priv_key, pub_key)

        # Verify Oracle Cloud variables are substituted
        assert 'tenancy_ocid     = "ocid1.tenancy.oc1..tenancy"' in result
        assert 'user_ocid        = "ocid1.user.oc1..user"' in result
        assert 'fingerprint      = "aa:bb:cc:dd:ee"' in result
        assert 'region           = "us-phoenix-1"' in result
        assert 'private_key_path = "/path/to/private.pem"' in result

        # Verify Cloudflare variables are substituted
        assert 'api_token = "cf_token_123"' in result
        assert 'account_id = "cf_account_456"' in result

        # Verify GitHub variables are substituted
        assert 'token = "gh_token_123"' in result
        assert 'owner = "testuser"' in result

        # Verify VM variables are substituted
        assert "useradd -m -s /bin/bash testuser" in result
        assert "echo 'testuser:testpass'" in result

        # Verify flex shape variables are substituted
        assert 'shape                    = "VM.Standard3.Flex"' in result

    def test_template_github_actions_workflow_generation(
        self, tmp_path, sample_payload
    ):
        """Test that GitHub Actions workflow is properly generated in the template."""
        svc = DeploymentService(directory=tmp_path)

        priv_key = Path("deploy_key")
        pub_key = Path("deploy_key.pub")

        result = svc.set_payload(sample_payload, priv_key, pub_key)

        # Verify GitHub Actions workflow content
        assert "name: Build & Deploy Backend" in result
        assert "runs-on: ubuntu-latest" in result
        assert "uses: actions/checkout@v4" in result
        assert "uses: docker/build-push-action@v5" in result
        assert "uses: appleboy/ssh-action@master" in result

        # Verify GitHub Actions secrets are properly escaped
        assert "${{ secrets.REPO_OWNER }}" in result
        assert "${{ secrets.GHCR_TOKEN }}" in result
        assert "${{ secrets.DOCKER_IMAGE }}" in result
        assert "${{ secrets.DEPLOY_HOST }}" in result
        assert "${{ secrets.DEPLOY_KEY }}" in result

    def test_template_handles_empty_domain(self, tmp_path):
        """Test template handling when domain is empty."""
        payload = Payload(
            oracle_cloud=OCIVars(
                tenancy_ocid="ocid1.tenancy.test",
                user_ocid="ocid1.user.test",
                fingerprint="test:fingerprint",
                region="us-test-1",
                compartment_ocid="ocid1.compartment.test",
            ),
            cloudflare=CloudflareVars(
                cf_api_token="test_token",
                cf_account_id="test_account",
                cf_zone_id="",  # Empty zone
                domain="",  # Empty domain
            ),
            github=GithubVars(
                github_token="test_token",
                github_owner="testowner",
                repo_name="testrepo",
                docker_image="test_image",
            ),
        )

        svc = DeploymentService(directory=tmp_path)
        result = svc.set_payload(payload, Path("key"), Path("key.pub"))

        # Verify conditional rendering for empty domain
        assert 'count   = "" == "" ? 0 : 1' in result
        assert 'zone_id = ""' in result
        assert 'hostname = "api."' in result  # Empty domain results in "api."

    def test_template_with_custom_domain(self, tmp_path):
        """Test template rendering with a custom domain."""
        payload = Payload(
            oracle_cloud=OCIVars(
                tenancy_ocid="ocid1.tenancy.test",
                user_ocid="ocid1.user.test",
                fingerprint="test:fingerprint",
                region="us-test-1",
                compartment_ocid="ocid1.compartment.test",
            ),
            cloudflare=CloudflareVars(
                cf_api_token="test_token",
                cf_account_id="test_account",
                cf_zone_id="zone123",
                domain="myapp.com",
            ),
            github=GithubVars(
                github_token="test_token",
                github_owner="testowner",
                repo_name="testrepo",
                docker_image="test_image",
            ),
        )

        svc = DeploymentService(directory=tmp_path)
        result = svc.set_payload(payload, Path("key"), Path("key.pub"))

        # Verify custom domain is rendered
        assert 'count   = "myapp.com" == "" ? 0 : 1' in result
        assert 'zone_id = "zone123"' in result
        assert 'hostname = "api.myapp.com"' in result

    def test_template_flex_shape_configuration(self, tmp_path):
        """Test template rendering with different flex shape configurations."""
        # Test with custom flex shape
        payload_with_flex = Payload(
            oracle_cloud=OCIVars(
                tenancy_ocid="ocid1.tenancy.test",
                user_ocid="ocid1.user.test",
                fingerprint="test:fingerprint",
                region="us-test-1",
                compartment_ocid="ocid1.compartment.test",
                flex_shape=FlexShape(
                    shape="VM.Standard.E4.Flex", ocpus=4, memory_gb=16
                ),
            ),
            cloudflare=CloudflareVars(
                cf_api_token="test_token", cf_account_id="test_account"
            ),
            github=GithubVars(
                github_token="test_token",
                github_owner="testowner",
                repo_name="testrepo",
                docker_image="test_image",
            ),
        )

        svc = DeploymentService(directory=tmp_path)
        result = svc.set_payload(payload_with_flex, Path("key"), Path("key.pub"))

        # Verify custom flex shape is rendered
        assert 'shape                    = "VM.Standard.E4.Flex"' in result
        assert 'operating_system_version = "20.04"' in result
        assert 'shape                    = "VM.Standard.E4.Flex"' in result

    def test_template_error_handling_invalid_template(
        self, tmp_path, sample_payload, monkeypatch
    ):
        """Test error handling when template rendering fails."""
        svc = DeploymentService(directory=tmp_path)

        # Create a template that will fail to render
        class _FailingTemplate:
            def render(self, **kwargs):
                raise Exception("Template rendering failed")

        monkeypatch.setattr(service_mod, "TEMPLATE", _FailingTemplate(), raising=True)

        priv_key = Path("key")
        pub_key = Path("key.pub")

        # Verify that the exception is raised
        with pytest.raises(Exception, match="Template rendering failed"):
            svc.set_payload(sample_payload, priv_key, pub_key)
