import json

import pytest

from jwt_verify import Rejected, b64url_decode, b64url_encode, sign_hs256, verify

KEY = b"secret-key-for-tests-only-0123456"
NOW = 1000.0


def mint(key=KEY, *, alg="HS256", typ="at+jwt", signature=None, **claims):
    claims = {"iss": "auth", "aud": "api", "exp": NOW + 60, **claims}
    head = b64url_encode(json.dumps({"alg": alg, "typ": typ}).encode())
    body = b64url_encode(json.dumps(claims).encode())
    if signature is None:
        signature = sign_hs256(key, f"{head}.{body}")
    return f"{head}.{body}.{signature}"


def check(token):
    return verify(token, KEY, iss="auth", aud="api", now=NOW)


def test_rfc7515_appendix_a1_vector():
    header = b'{"typ":"JWT",\r\n "alg":"HS256"}'
    payload = b'{"iss":"joe",\r\n "exp":1300819380,\r\n "http://example.com/is_root":true}'
    key = b64url_decode("AyM1SysPpbyDfgZld3umj1qzKObwVMkoqQ-EstJQLr_T-1qS0gZH75aKtMN3Yj0iPS4hcgUuTwjAzZr1Z9CAow")
    signing_input = f"{b64url_encode(header)}.{b64url_encode(payload)}"
    signature = sign_hs256(key, signing_input)
    assert signature == "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    claims = verify(f"{signing_input}.{signature}", key, iss="joe", aud=None, typ="JWT", now=1300819379)
    assert claims["iss"] == "joe"


def test_good_token():
    assert check(mint())["aud"] == "api"


def test_audience_list():
    assert check(mint(aud=["other", "api"]))


def test_alg_none_rejected_with_any_signature():
    with pytest.raises(Rejected):
        check(mint(alg="none", signature=""))
    with pytest.raises(Rejected):
        check(mint(alg="none"))


def test_other_algorithm_rejected_even_if_signed_correctly():
    with pytest.raises(Rejected):
        check(mint(alg="HS512"))


def test_wrong_key_and_altered_body():
    with pytest.raises(Rejected):
        check(mint(key=b"another-key-of-the-same-length-00"))
    head, _, sig = mint().split(".")
    body = b64url_encode(json.dumps({"iss": "auth", "aud": "api", "exp": NOW + 9999}).encode())
    with pytest.raises(Rejected):
        check(f"{head}.{body}.{sig}")


@pytest.mark.parametrize("claims", [{"aud": "other"}, {"iss": "other"}, {"aud": ["other"]}])
def test_wrong_issuer_or_audience(claims):
    with pytest.raises(Rejected):
        check(mint(**claims))


def test_expiry_at_the_exact_second():
    with pytest.raises(Rejected):
        check(mint(exp=NOW))
    assert check(mint(exp=NOW + 1))


def test_missing_expiry_rejected():
    head = b64url_encode(json.dumps({"alg": "HS256", "typ": "at+jwt"}).encode())
    body = b64url_encode(json.dumps({"iss": "auth", "aud": "api"}).encode())
    with pytest.raises(Rejected):
        check(f"{head}.{body}.{sign_hs256(KEY, f'{head}.{body}')}")


def test_wrong_type():
    with pytest.raises(Rejected):
        check(mint(typ="JWT"))


@pytest.mark.parametrize("token", ["", "a.b", "a.b.c.d", "!!!.!!!.!!!"])
def test_malformed(token):
    with pytest.raises(Rejected):
        check(token)
