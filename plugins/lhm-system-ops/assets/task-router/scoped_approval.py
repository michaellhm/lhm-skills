"""Admission-only recognition of explicit provider requests with scoped exclusions.

Never use the admission projection as the worker instruction. The original message,
hash, author, discussion context and permission ceiling must remain intact.
"""
import re


def admission_text(instruction, provider):
    if provider is None:
        return instruction

    def exclusion(match):
        scope = match.group('scope').strip()
        # Recognise only a named action exclusion, never a global refusal or a
        # provider/stop instruction hidden inside an exception clause.
        if (len(scope) < 8 or len(scope) > 240
                or re.search(r"\b(?:send|use|push|switch|move|reroute|run|stop|cancel|hold|pause|not|never|don|approve|execute|implement|proceed|publish|claude|codex|anything|everything|any|all|nothing)\b", scope, re.I)
                or re.fullmatch(r'(?:this|it|(?:the |this )?(?:work|task|request|handoff|execution))', scope, re.I)):
            return match.group(0)
        return ' [scoped exclusion preserved in original instruction] '

    return re.sub(
        r"\b(?:except|excluding)\s+(?:that\s+)?(?:i\s+)?(?:do\s+not|don['’]t)\s+approve\s+(?P<scope>[^,.!?;\n]+)",
        exclusion, instruction, flags=re.I,
    )
