# author: sawyer-shi

from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class KlingAigcProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            access_key = credentials.get("access_key")
            secret_key = credentials.get("secret_key")
            if not access_key:
                raise ToolProviderCredentialValidationError("Access Key is required")
            if not secret_key:
                raise ToolProviderCredentialValidationError("Secret Key is required")

            api_token = self._encode_jwt_token(access_key, secret_key)
            if not api_token:
                raise ToolProviderCredentialValidationError("Failed to generate API token")

            self._test_kling_connection(api_token)
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Credential validation failed: {str(e)}"
            )

    @staticmethod
    def _encode_jwt_token(access_key: str, secret_key: str) -> str:
        import time

        import importlib

        try:
            jwt = importlib.import_module("jwt")
        except ImportError as exc:
            raise ToolProviderCredentialValidationError(
                "PyJWT is required. Please install dependencies."
            ) from exc

        headers = {
            "alg": "HS256",
            "typ": "JWT",
        }
        payload = {
            "iss": access_key,
            "exp": int(time.time()) + 1800,
            "nbf": int(time.time()) - 5,
        }
        return jwt.encode(payload, secret_key, headers=headers)

    def _test_kling_connection(self, api_token: str) -> None:
        url = "https://api-beijing.klingai.com/v1/videos/text2video"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}",
        }
        payload = {
            "model_name": "kling-v1",
            "prompt": "hello",
            "duration": "5",
            "aspect_ratio": "16:9",
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
        except requests.RequestException as req_err:
            raise ToolProviderCredentialValidationError(
                f"Unable to reach Kling AI service: {req_err}"
            )

        if response.status_code == 429:
            raise ToolProviderCredentialValidationError(
                "Kling AI API error 429: Account balance not enough"
            )

        if response.status_code not in (200, 400):
            try:
                data = response.json()
                error_message = data.get("message") or response.text
            except Exception:
                error_message = response.text
            raise ToolProviderCredentialValidationError(
                f"Kling AI API error {response.status_code}: {error_message}"
            )

        if response.status_code == 400:
            try:
                data = response.json()
                message = data.get("message", "")
                if "Authorization" in message or "token" in message:
                    raise ToolProviderCredentialValidationError(
                        f"Kling AI authentication failed: {message}"
                    )
            except ValueError:
                raise ToolProviderCredentialValidationError(
                    "Kling AI API returned non-JSON response"
                )


    @staticmethod
    def get_api_token(credentials: dict[str, Any]) -> str:
        access_key = credentials.get("access_key")
        secret_key = credentials.get("secret_key")
        if not access_key or not secret_key:
            raise ToolProviderCredentialValidationError(
                "Access Key and Secret Key are required"
            )
        return KlingAigcProvider._encode_jwt_token(access_key, secret_key)
