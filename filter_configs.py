import yaml
import copy
import sys

def load_yaml(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(data, filepath):
    class Dumper(yaml.Dumper):
        def increase_indent(self, flow=False, *args, **kwargs):
            return super().increase_indent(flow=flow, indentless=False)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=Dumper, default_flow_style=False, sort_keys=False)

def main():
    compose_path = 'docker-compose.yml'
    kong_path = 'infrastructure/gateway/kong/kong.yml'
    
    compose = load_yaml(compose_path)
    
    # AI services to absolutely exclude
    ai_exclude = {
        'ollama', 'ollama-model-loader', 'vllm-deepseek', 'code-review-service',
        'mlflow', 'milvus', 'qdrant', 'ai-agents-core', 'ai-agents-service',
        'agent-registry', 'code-fix-agent', 'llm-orchestrator-service', 'mcp-server',
        'knowledge-graph-updater', 'ai-search-agent', 'code-review-agent'
    }
    
    services = compose.get('services', {})
    core_services = {}
    
    # Filter services
    for name, config in services.items():
        if name in ai_exclude:
            continue
        core_services[name] = copy.deepcopy(config)
        
        # Kong specific tweaks
        if name == 'kong':
            if 'volumes' in core_services[name]:
                new_volumes = []
                for vol in core_services[name]['volumes']:
                    if isinstance(vol, str) and 'kong.yml' in vol:
                        new_volumes.append('./infrastructure/gateway/kong/kong-core.yml:/kong/declarative/kong-core.yml:ro')
                    else:
                        new_volumes.append(vol)
                core_services[name]['volumes'] = new_volumes
                
            if 'environment' in core_services[name]:
                env = core_services[name]['environment']
                if isinstance(env, dict) and 'KONG_DECLARATIVE_CONFIG' in env:
                    env['KONG_DECLARATIVE_CONFIG'] = '/kong/declarative/kong-core.yml'
                elif isinstance(env, list):
                    new_env = []
                    for e in env:
                        if e.startswith('KONG_DECLARATIVE_CONFIG='):
                            new_env.append('KONG_DECLARATIVE_CONFIG=/kong/declarative/kong-core.yml')
                        else:
                            new_env.append(e)
                    core_services[name]['environment'] = new_env

    # Fix dangling depends_on and other missing references
    for name, config in core_services.items():
        if 'depends_on' in config:
            depends_on = config['depends_on']
            if isinstance(depends_on, dict):
                new_deps = {k: v for k, v in depends_on.items() if k in core_services}
                if new_deps:
                    config['depends_on'] = new_deps
                else:
                    del config['depends_on']
            elif isinstance(depends_on, list):
                new_deps = [dep for dep in depends_on if dep in core_services]
                if new_deps:
                    config['depends_on'] = new_deps
                else:
                    del config['depends_on']

    compose['services'] = core_services
    
    # Clean up volumes for excluded services
    if 'volumes' in compose and isinstance(compose['volumes'], dict):
        vols = list(compose['volumes'].keys())
        for v in vols:
            # simple heuristic: if volume name matches excluded service directly
            if any(ex in v for ex in ai_exclude) and 'postgres' not in v and 'redis' not in v:
                if 'mongo' not in v and 'kong' not in v:
                    del compose['volumes'][v]
                
    save_yaml(compose, 'docker-compose-core.yml')
    print("Created docker-compose-core.yml cleanly")
    
    # Congress routes
    kong = load_yaml(kong_path)
    k_services = kong.get('services', [])
    k_routes = kong.get('routes', [])
    k_plugins = kong.get('plugins', [])
    
    kept_k_services = []
    kept_service_ids = set()
    kept_service_names = set()
    
    for s in k_services:
        host = s.get('host')
        name = s.get('name')
        
        # also ignore any routing to the excluded systems
        if host in ai_exclude or name in ai_exclude:
            continue
            
        kept_k_services.append(s)
        if 'name' in s: kept_service_names.add(s['name'])
        
    # Since ID is often auto-generated or missing in declarative configs, match mainly by name
    kept_routes = []
    for r in k_routes:
        s_ref = r.get('service')
        if not s_ref:
            kept_routes.append(r)
            continue
            
        ref_name = None
        if isinstance(s_ref, dict):
            ref_name = s_ref.get('name')
        else:
            ref_name = s_ref
            
        if ref_name in kept_service_names:
            kept_routes.append(r)
            
    # keep general plugins, drop ones linked to dropped services
    kept_plugins = []
    for p in k_plugins:
        s_ref = p.get('service')
        if not s_ref:
            kept_plugins.append(p)
            continue
        
        ref_name = None
        if isinstance(s_ref, dict):
            ref_name = s_ref.get('name')
        else:
            ref_name = s_ref
            
        if ref_name in kept_service_names:
            kept_plugins.append(p)
            
    kong['services'] = kept_k_services
    kong['routes'] = kept_routes
    kong['plugins'] = kept_plugins
    
    save_yaml(kong, 'infrastructure/gateway/kong/kong-core.yml')
    print("Created infrastructure/gateway/kong/kong-core.yml cleanly")

if __name__ == "__main__":
    main()
