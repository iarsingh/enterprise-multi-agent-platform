# enterprise-multi-agent-platform — project architecture

[README](README.md) · [Interview questions and answers](INTERVIEW_QA.md)

## Purpose and scope

This is a local laptop proof. It does not call a hosted model and it does not apply production changes.

This document describes files and symbols in this checkout. Deployment templates and statements in the original overview are distinguished from a verified running environment.

## Component diagram

```mermaid
flowchart LR
    M0["src/entmulti/__init__.py"]
    M1["src/entmulti/agent.py"]
    M2["src/entmulti/main.py"]
    M2 -->|imports| M1
```

For Python repositories, arrows show resolved local imports, not network calls or deployment order. Otherwise the diagram is a repository component map; containment arrows do not assert runtime integration.

## Components and responsibilities

| Component | Responsibility |
| --- | --- |
| [`src/entmulti/main.py`](src/entmulti/main.py) | HTTP handlers: `GET /healthz`, `POST /agent/run` |
| [`src/entmulti/agent.py`](src/entmulti/agent.py) | Functions: `run` |
| [`requirements.txt`](requirements.txt) | Implementation or supporting configuration |
| [`src/entmulti/__init__.py`](src/entmulti/__init__.py) | Implementation or supporting configuration |
| [`tests/test_agent.py`](tests/test_agent.py) | Executable checks and regression examples |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | GitHub Actions job definitions |
| [`README.md`](README.md) | Project explanations or operating notes |

## Request interface

| Method and path | Handler | Source |
| --- | --- | --- |
| `GET /healthz` | `healthz` | [`src/entmulti/main.py`](src/entmulti/main.py#L8) |
| `POST /agent/run` | `post_run` | [`src/entmulti/main.py`](src/entmulti/main.py#L13) |

The table lists literal route decorators found in the inspected Python modules. Router prefixes and middleware can add behavior; check the linked handler and application setup before calling an endpoint.

## Implementation walkthrough

### `run(goal, payload)`

Source: [`src/entmulti/agent.py`](src/entmulti/agent.py#L9).

Calls visible in this function: `InputError`, `any`, `goal.lower`, `goal.strip`, `isinstance`.

```python
def run(goal, payload):
    if not isinstance(goal, str) or not goal.strip():
        raise InputError("goal is empty")
    if any(word in goal.lower() for word in WRITES):
        return {"refused": True, "reason": "This agent only reads or plans. It does not write.", "tools": [], "wrote": False, "applied": False}
    result = TOOLS
    return {"refused": False, "tools": TOOLS, "roles": result, "wrote": False, "applied": False}
```

## Validation and failure paths

| Explicit exception | Source |
| --- | --- |
| `InputError('goal is empty')` | [`src/entmulti/agent.py`](src/entmulti/agent.py#L11) |
| `HTTPException(status_code=422, detail=str(exc))` | [`src/entmulti/main.py`](src/entmulti/main.py#L17) |

These are explicit exceptions in the inspected source, rather than a claim that every failure is handled. Follow the calling handler to see whether the exception becomes an HTTP response or propagates.

## Data and state

- [`src/entmulti/agent.py`](src/entmulti/agent.py) defines module-level containers: `TOOLS`.

Module-level dictionaries/lists live in a Python process. They can be fixtures or mutable state; inspect writes before treating them as persistent storage. A production extension would need to define persistence and concurrency behavior explicitly.

## Data flow and design decisions

### What is the input-to-output contract of `run`

In [`src/entmulti/agent.py`](src/entmulti/agent.py#L9), `run(goal, payload)` receives the inputs. The function computes these intermediate values:

- `result = TOOLS`

Its result is defined by:

- `{'refused': False, 'tools': TOOLS, 'roles': result, 'wrote': False, 'applied': False}`
- `{'refused': True, 'reason': 'This agent only reads or plans. It does not write.', 'tools': [], 'wrote': False, 'applied': False}`

### Which decision rules or boundary conditions should an interviewer challenge

The implementation in [`src/entmulti/agent.py`](src/entmulti/agent.py#L9) branches on:

- `not isinstance(goal, str) or not goal.strip()`
- `any((word in goal.lower() for word in WRITES))`

A useful extension is a table-driven test that covers each condition just below, at, and above its boundary where applicable. These expressions are the current rules; changing them changes behavior and should be justified by the project’s acceptance criteria.

## Setup and verification

The following commands are derived from the checked-in dependency/test contracts. Execute them from the repository root; the block prepares a local environment, not a cloud deployment.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
```

Python dependencies: [`requirements.txt`](requirements.txt).

Test entry points: [`tests/test_agent.py`](tests/test_agent.py).

Automation definitions: [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Read their triggers and job steps to determine what CI actually runs.

## Operating boundaries and design review

Before turning this checkout into a customer deployment, establish the input contract, data ownership, access controls, failure response, evaluation criteria, and rollback owner. Repository fixtures and unit tests demonstrate local behavior; they do not establish throughput, uptime, compliance, or business impact.

A useful architecture review starts with the linked implementation: identify where input enters, where a decision is made, which state can change, and which external dependency can fail. Add a deployment view only for infrastructure that is actually configured and exercised.
