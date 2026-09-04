from .models import Authority, EffectIntent

class AuthorityDenied(PermissionError):
    pass


def authorize(intent: EffectIntent, granted: Authority) -> bool:
    if granted.value < intent.required_authority.value:
        raise AuthorityDenied(f"required={intent.required_authority.name}; granted={granted.name}")
    return True
