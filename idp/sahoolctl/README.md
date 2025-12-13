# sahoolctl

Create a new service quickly.

## Example
```bash
python3 idp/sahoolctl/sahoolctl.py ndvi-preprocessor --template python-fastapi --port 8099 --layer decision
```

Output:
- `apps/ndvi-preprocessor/` with runnable skeleton
- `apps/ndvi-preprocessor/deploy/values.snippet.yaml` for Helm wiring
