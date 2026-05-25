from oauth2_provider.oauth2_validators import OAuth2Validator


class AllianceAuthOAuth2Validator(OAuth2Validator):
    oidc_claim_scope = OAuth2Validator.oidc_claim_scope
    oidc_claim_scope.update({
        "groups": "profile",
        "character_id": "profile",
        "corporation_id": "profile",
        "corporation_name": "profile",
        "alliance_id": "profile",
        "alliance_name": "profile",
    })

    def get_additional_claims(self):
        def _main(request):
            return request.user.profile.main_character

        return {
            "name": lambda request: getattr(_main(request), 'character_name', None) or request.user.username,
            "email": lambda request: request.user.email,
            "character_id": lambda request: getattr(_main(request), 'character_id', None),
            "corporation_id": lambda request: getattr(_main(request), 'corporation_id', None),
            "corporation_name": lambda request: getattr(_main(request), 'corporation_name', None),
            "alliance_id": lambda request: getattr(_main(request), 'alliance_id', None),
            "alliance_name": lambda request: getattr(_main(request), 'alliance_name', None),
            "groups": lambda request: list(
                request.user.groups.values_list('name', flat=True)
            ) + [request.user.profile.state.name],
        }
