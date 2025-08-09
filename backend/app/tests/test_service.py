from app.service import DeploymentService
import app.service as service_mod


class _FakeOCI:
    def __init__(self, tenancy_ocid, user_ocid, fingerprint, region):
        self.tenancy_ocid = tenancy_ocid
        self.user_ocid = user_ocid
        self.fingerprint = fingerprint
        self.region = region


class _FakePayload:
    def __init__(self):
        self.oci = _FakeOCI(
            tenancy_ocid="ocid1.tenancy.oc1..tenancy",
            user_ocid="ocid1.user.oc1..user",
            fingerprint="aa:bb:cc",
            region="us-phoenix-1",
        )
        self.flex = {"shape": "VM.Standard3.Flex", "ocpus": 1, "memory_in_gbs": 1}


def test_set_payload_renders_with_expected_context(tmp_path, monkeypatch):
    svc = DeploymentService(directory=tmp_path)
    payload = _FakePayload()
    captured = {}

    class _FakeTemplate:
        def render(self, **kwargs):
            captured.update(kwargs)
            return "RENDERED_OK"

    monkeypatch.setattr(service_mod, "TEMPLATE", _FakeTemplate(), raising=True)

    priv = "id_rsa"
    pub = "id_rsa.pub"

    out = svc.set_payload(payload, private_key_path=priv, public_key_path=pub)

    assert out == "RENDERED_OK"
    assert svc.payload is payload
    assert captured["tenancy_ocid"] == "ocid1.tenancy.oc1..tenancy"
    assert captured["user_ocid"] == "ocid1.user.oc1..user"
    assert captured["fingerprint"] == "aa:bb:cc"
    assert captured["region"] == "us-phoenix-1"
    assert captured["flex"] == payload.flex
    assert captured["private_pem_path"] == str(priv)
    assert captured["public_pem_path"] == str(pub)


def test_cleanup_removes_directory(tmp_path, mocker):
    svc = DeploymentService(directory=tmp_path)
    rmtree = mocker.patch("app.service.shutil.rmtree")
    svc.cleanup()
    rmtree.assert_called_once_with(tmp_path, ignore_errors=True)
