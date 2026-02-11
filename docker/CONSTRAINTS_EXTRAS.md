# Constraints File - Package Extras Handling

## Issue
Pip constraints files (`-c constraints.txt`) do NOT support package extras (e.g., `package[extra]`).

## Solution
The `docker/constraints-ai.txt` file contains only base package names with version constraints:
```
uvicorn>=0.30.0,<1.0.0          # NOT uvicorn[standard]
redis>=7.1.0,<8.0.0             # NOT redis[hiredis]
python-jose>=3.3.0,<4.0.0       # NOT python-jose[cryptography]
```

## Installing with Extras
Individual `requirements.txt` files can (and should) specify extras:
```
# In requirements.txt
uvicorn[standard]>=0.30.0,<1.0.0
redis[hiredis]>=7.1.0,<8.0.0
python-jose[cryptography]>=3.3.0,<4.0.0
```

## Installation Command
```bash
# This works correctly:
pip install -c constraints-ai.txt -r requirements.txt

# The constraints file constrains versions, but requirements.txt provides the extras
```

## Removed Extras
The following extras were removed from constraints-ai.txt:
- `uvicorn[standard]` → `uvicorn` (standard extras: watchfiles, websockets, httptools, uvloop)
- `redis[hiredis]` → `redis` (hiredis for faster performance)
- `python-jose[cryptography]` → `python-jose` (cryptography backend)

These extras are still specified in individual service requirements.txt files.
