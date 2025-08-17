import pytest
from pathlib import Path
from app.service import DeploymentService
from app.models.payload import Payload
from app.models.oracle_cloud_config import OCIVars, FlexShape
from app.models.cloudflare_vars import CloudflareVars
from app.models.github_vars import GithubVars


@pytest.fixture
def mock_ssh_keys(monkeypatch):
    """Mock SSH key functions with consistent behavior."""

    def mock_decode_file(path):
        return f"ssh-rsa AAAAB3NzaC1yc2E...{path.stem}"

    def mock_read_file(path):
        return f"-----BEGIN PRIVATE KEY-----\n{path.stem}_content\n-----END PRIVATE KEY-----"

    monkeypatch.setattr("app.service.decode_file", mock_decode_file)
    monkeypatch.setattr("app.service.read_file", mock_read_file)
    return mock_decode_file, mock_read_file


@pytest.fixture
def mock_template(monkeypatch):
    """Mock template with captured context."""
    captured = {}

    class _FakeTemplate:
        def render(self, **kwargs):
            captured.update(kwargs)
            return f"RENDERED_{len(kwargs)}_VARS"

    def mock_build_template(provider=None):
        return _FakeTemplate()

    monkeypatch.setattr("app.service.build_template", mock_build_template)
    return captured


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


class TestDeploymentService:

    def test_init(self, tmp_path):
        """Test service initialization."""
        svc = DeploymentService(directory=tmp_path)
        assert svc.directory == tmp_path
        assert svc.payload is None

    def test_set_payload_complete_data(
        self, tmp_path, sample_payload, mock_template, mock_ssh_keys
    ):
        """Test set_payload with complete payload data."""
        svc = DeploymentService(directory=tmp_path)
        captured = mock_template

        result = svc.set_payload(
            sample_payload, Path("id_rsa"), Path("id_rsa.pub"), "oracle"
        )

        # Verify return value and payload storage - now returns a tuple
        if isinstance(result, tuple):
            template_result, provider_result = result
            assert template_result.startswith("RENDERED_")
        else:
            assert result.startswith("RENDERED_")
        assert svc.payload is sample_payload

        # Verify key data is present
        assert captured["tenancy_ocid"] == "ocid1.tenancy.oc1..tenancy"
        assert captured["flex"]["shape"] == "VM.Standard3.Flex"
        assert captured["cf_api_token"] == "cf_token_123"
        assert captured["github_token"] == "gh_token_123"
        assert captured["ssh_public_key"] == "ssh-rsa AAAAB3NzaC1yc2E...id_rsa"

    def test_set_payload_without_flex_shape(
        self, tmp_path, mock_template, mock_ssh_keys
    ):
        """Test set_payload when flex_shape is not provided (uses defaults)."""
        payload = Payload(
            oracle_cloud=OCIVars(
                tenancy_ocid="test_tenancy",
                user_ocid="test_user",
                fingerprint="test:fingerprint",
                region="us-test-1",
                compartment_ocid="test_compartment",
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
        captured = mock_template

        svc.set_payload(payload, Path("key"), Path("key.pub"), "oracle")

        # Verify default flex shape values are used
        assert captured["flex"]["shape"] == "VM.Standard.E2.1.Micro"
        assert captured["flex"]["ocpus"] == 1
        assert captured["flex"]["memory_gb"] == 1

    def test_set_payload_without_oracle_cloud(
        self, tmp_path, mock_template, mock_ssh_keys
    ):
        """Test set_payload when oracle_cloud is None."""
        payload = Payload(
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
        captured = mock_template

        svc.set_payload(payload, Path("key"), Path("key.pub"), "oracle")

        # Oracle Cloud and flex fields should not be in context
        oracle_fields = [
            "tenancy_ocid",
            "user_ocid",
            "fingerprint",
            "region",
            "compartment_ocid",
            "flex",
        ]
        for field in oracle_fields:
            assert field not in captured

        # But other fields should still be present
        assert captured["cf_api_token"] == "test_token"
        assert captured["github_token"] == "test_token"

    def test_generate_tf_files(self, tmp_path, sample_payload, mock_ssh_keys):
        """Test generate_tf_files method."""
        svc = DeploymentService(directory=tmp_path)

        # Set payload and get template content
        result = svc.set_payload(
            sample_payload, Path("private_key"), Path("public_key"), "oracle"
        )

        # Handle tuple return from set_payload
        if isinstance(result, tuple):
            template_content, _ = result
        else:
            template_content = result

        # Create temp SSH key files
        private_key_path = tmp_path / "test_private_key"
        private_key_path.write_text("test private key content")

        result = svc.generate_tf_files(template_content, private_key_path, "main.tf")

        # Verify results
        assert result == tmp_path / "main.tf"
        assert result.exists()
        assert (tmp_path / "id_rsa").exists()
        assert (tmp_path / "id_rsa.pub").exists()

    def test_cleanup_removes_directory(self, tmp_path, monkeypatch):
        """Test cleanup removes the directory."""
        svc = DeploymentService(directory=tmp_path)
        calls = []

        monkeypatch.setattr(
            "app.service.shutil.rmtree",
            lambda path, ignore_errors: calls.append((path, ignore_errors)),
        )
        svc.cleanup()

        assert calls == [(tmp_path, True)]

    def test_template_rendering_integration(
        self, tmp_path, sample_payload, mock_ssh_keys
    ):
        """Test actual template rendering with real Jinja2 template."""
        svc = DeploymentService(directory=tmp_path)
        result = svc.set_payload(
            sample_payload, Path("test_key"), Path("test_key.pub"), "oracle"
        )

        # Handle tuple return from set_payload
        if isinstance(result, tuple):
            template_result, provider_result = result
            # Check that we have actual template content, not just our mock result
            assert isinstance(template_result, str) and len(template_result) > 0
            assert isinstance(provider_result, str) and len(provider_result) > 0
            main_content = template_result
            provider_content = provider_result
        else:
            assert isinstance(result, str) and len(result) > 0
            main_content = result
            provider_content = ""

        # Check key template elements are present in main template
        main_expected_content = [
            "terraform {",
            'provider "oci"',
            'provider "cloudflare"',
            'provider "github"',
            'resource "cloudflare_zero_trust_tunnel_cloudflared"',
            'resource "github_repository_file"',
            "ocid1.tenancy.oc1..tenancy",
            "cf_token_123",
            "testuser",
        ]
        for content in main_expected_content:
            assert content in main_content

        # Check Oracle-specific content in provider template (if tuple was returned)
        if isinstance(result, tuple):
            oracle_expected_content = [
                'resource "oci_core_vcn"',
                'resource "oci_core_instance"',
                "ssh-rsa AAAAB3NzaC1yc2E...test_key",
            ]
            for content in oracle_expected_content:
                assert content in provider_content

    def test_template_domain_handling(self, tmp_path, mock_ssh_keys):
        """Test template rendering with different domain configurations."""
        # Test empty domain
        empty_domain_payload = Payload(
            oracle_cloud=OCIVars(
                tenancy_ocid="test_tenancy",
                user_ocid="test_user",
                fingerprint="test:fp",
                region="us-test-1",
                compartment_ocid="test_comp",
            ),
            cloudflare=CloudflareVars(
                cf_api_token="token", cf_account_id="account", domain=""
            ),
            github=GithubVars(
                github_token="token",
                github_owner="owner",
                repo_name="repo",
                docker_image="image",
            ),
        )

        svc = DeploymentService(directory=tmp_path)
        result = svc.set_payload(
            empty_domain_payload, Path("key"), Path("key.pub"), "oracle"
        )

        # Handle tuple return from set_payload
        if isinstance(result, tuple):
            template_result, provider_result = result
            content_to_check = template_result
        else:
            content_to_check = result

        assert 'count           = "" == "" ? 0 : 1' in content_to_check
        assert 'hostname = "api."' in content_to_check

    def test_template_error_handling(
        self, tmp_path, sample_payload, mock_ssh_keys, monkeypatch
    ):
        """Test error handling when template rendering fails."""

        class _FailingTemplate:
            def render(self, **kwargs):
                raise Exception("Template rendering failed")

        monkeypatch.setattr("app.service.build_template", lambda: _FailingTemplate())

        svc = DeploymentService(directory=tmp_path)

        with pytest.raises(Exception, match="Template rendering failed"):
            svc.set_payload(sample_payload, Path("key"), Path("key.pub"), "oracle")
